"""
F-04: First-and-Last Frame Image-to-Video (I2V) Synthesis Engine.
Orchestrates asynchronous rendering, idempotency deduplication, and polling reconciliation.
"""

import hashlib
import time
from typing import Dict, Optional, Tuple
from workbench.config import settings
from workbench.domain.entities import Shot, ShotStatus
from workbench.domain.exceptions import InvalidStateTransitionError, ExternalAPIError
from workbench.services.finops_guard import FinOpsGuard


class VideoSynthesisEngine:
    def __init__(self, api_client=None, finops_guard: FinOpsGuard = None):
        self.api_client = api_client
        self.finops = finops_guard or FinOpsGuard()
        self.model_name = settings.VIDEO_MODEL
        self.video_cost = settings.COST_VIDEO_PER_SHOT
        # In-memory idempotency cache for deduplication
        self.idempotency_cache: Dict[str, Tuple[str, str]] = {}

    def compute_idempotency_key(self, shot: Shot, start_url: str, end_url: str) -> str:
        raw_seed = f"{shot.id}:{start_url}:{end_url}:{shot.motion_prompt}:{shot.duration_seconds}"
        return hashlib.sha256(raw_seed.encode("utf-8")).hexdigest()

    def dispatch_synthesis_job(self, shot: Shot) -> str:
        """
        Dispatches I2V synthesis task.
        Enforces KEYFRAMES_APPROVED precondition and idempotency check.
        Returns external_task_id or job_id.
        """
        if shot.video_status != ShotStatus.KEYFRAMES_APPROVED:
            raise InvalidStateTransitionError(
                current_state=shot.video_status.value,
                target_state=ShotStatus.VIDEO_SYNTHESIZING.value,
                reason="Shot keyframes must be approved before video synthesis."
            )

        # Retrieve verified frame URLs
        start_cand = next((c for c in shot.start_candidates if c.id == shot.selected_start_frame_id), None)
        end_cand = next((c for c in shot.end_candidates if c.id == shot.selected_end_frame_id), None)

        if not start_cand or not end_cand:
            raise ValueError(f"Shot {shot.id} lacks approved start or end frame candidate.")

        # Compute idempotency key
        idem_key = self.compute_idempotency_key(shot, start_cand.image_url, end_cand.image_url)
        if idem_key in self.idempotency_cache:
            cached_task_id, cached_url = self.idempotency_cache[idem_key]
            shot.video_task_id = cached_task_id
            shot.video_url = cached_url
            shot.video_status = ShotStatus.READY
            return cached_task_id

        shot.video_status = ShotStatus.VIDEO_SYNTHESIZING

        # 调用外部 302.AI 接口
        if self.api_client:
            task_id = self.api_client.submit_i2v_task(
                model=self.model_name,
                prompt=shot.motion_prompt or shot.scene_summary,
                image_start_url=start_cand.image_url,
                image_tail_url=end_cand.image_url,
                duration=shot.duration_seconds
            )
        else:
            task_id = f"task_{hashlib.md5(shot.id.encode()).hexdigest()[:12]}"

        shot.video_task_id = task_id

        # 记入账本
        self.finops.record_transaction(
            shot.id, self.model_name, "VIDEO_I2V_SYNTHESIS", self.video_cost, external_task_id=task_id
        )
        return task_id

    def reconcile_task_status(
        self,
        shot: Shot,
        task_id: str,
        max_poll_attempts: int = settings.POLL_MAX_ATTEMPTS,
        poll_interval: float = 0.05
    ) -> Shot:
        """
        Polls until the rendering task finishes or fails.
        """
        attempts = 0
        while attempts < max_poll_attempts:
            attempts += 1
            if self.api_client:
                status, video_url = self.api_client.query_i2v_task(task_id)
            else:
                status, video_url = "success", f"https://mock-oss.302.ai/videos/{shot.id}.mp4"

            if status == "success":
                shot.video_url = video_url
                shot.video_status = ShotStatus.READY
                # Update idempotency cache
                start_cand = next((c for c in shot.start_candidates if c.id == shot.selected_start_frame_id), None)
                end_cand = next((c for c in shot.end_candidates if c.id == shot.selected_end_frame_id), None)
                if start_cand and end_cand:
                    idem_key = self.compute_idempotency_key(shot, start_cand.image_url, end_cand.image_url)
                    self.idempotency_cache[idem_key] = (task_id, video_url)
                shot.accumulated_cost_usd = self.finops.get_shot_accumulated_cost(shot.id)
                return shot

            elif status == "failed":
                shot.video_status = ShotStatus.FAILED
                shot.accumulated_cost_usd = self.finops.get_shot_accumulated_cost(shot.id)
                raise ExternalAPIError("302.AI", 500, f"Video rendering task {task_id} failed externally.")

            time.sleep(poll_interval)

        # 超时处理
        shot.video_status = ShotStatus.FAILED
        raise TimeoutError(f"Video synthesis task {task_id} timed out after {attempts} attempts.")
