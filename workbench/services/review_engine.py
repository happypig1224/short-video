"""
F-03: Human Review Station and Inpainting Rejection Engine.
Handles candidate selection, canvas mask generation, inpainting retry enforcement (<=3),
and state transition to KEYFRAMES_APPROVED.
"""

from typing import Optional, Tuple
from workbench.config import settings
from workbench.domain.entities import (
    Shot, KeyframeCandidate, FrameType, SourceType, ReviewLog, ReviewActionType, ShotStatus
)
from workbench.domain.exceptions import (
    InpaintingExceededError, InvalidStateTransitionError, OpticalConflictError
)
from workbench.services.finops_guard import FinOpsGuard


class ReviewEngine:
    def __init__(self, api_client=None, finops_guard: FinOpsGuard = None):
        self.api_client = api_client
        self.finops = finops_guard or FinOpsGuard()
        self.max_retries = settings.MAX_INPAINT_RETRIES_PER_SHOT
        self.inpaint_cost = settings.COST_INPAINT_PER_FRAME

    def compute_onion_skin_alignment(self, shot: Shot) -> float:
        """
        Simulate/evaluate spatial consistency alignment between selected start & end frames.
        Returns a confidence score between 0.0 and 1.0.
        """
        if not shot.selected_start_frame_id or not shot.selected_end_frame_id:
            return 0.0
        # In real runtime, visual optical flow or embeddings compare distance
        return 0.88

    def submit_inpainting_redo(
        self,
        shot: Shot,
        target_candidate_id: str,
        mask_url: str,
        feedback_prompt: str
    ) -> Tuple[Shot, KeyframeCandidate]:
        """
        Executes localized inpainting on a flagged candidate frame.
        Guards against infinite redo loops by enforcing max_retries limit.
        """
        if shot.inpaint_retry_count >= self.max_retries:
            raise InpaintingExceededError(
                shot_id=shot.id,
                retry_count=shot.inpaint_retry_count,
                max_retries=self.max_retries
            )

        # 寻找目标候选帧
        target_cand: Optional[KeyframeCandidate] = None
        is_start = False
        for c in shot.start_candidates:
            if c.id == target_candidate_id:
                target_cand = c
                is_start = True
                break
        if not target_cand:
            for c in shot.end_candidates:
                if c.id == target_candidate_id:
                    target_cand = c
                    is_start = False
                    break

        if not target_cand:
            raise ValueError(f"Candidate {target_candidate_id} not found in shot {shot.id}")

        shot.video_status = ShotStatus.INPAINTING_RUNNING
        shot.inpaint_retry_count += 1

        # 记录评审日志
        review_log = ReviewLog(
            shot_id=shot.id,
            target_candidate_id=target_candidate_id,
            action_type=ReviewActionType.INPAINT_REDO,
            feedback_note=feedback_prompt,
            mask_url=mask_url
        )

        # 调用外部 Inpainting 算力
        if self.api_client:
            new_image_url = self.api_client.inpaint_image(
                base_image_url=target_cand.image_url,
                mask_url=mask_url,
                prompt=feedback_prompt
            )
        else:
            new_image_url = f"{target_cand.image_url}_inpainted_v{shot.inpaint_retry_count}.png"

        # 记录算力账本
        self.finops.record_transaction(
            shot.id, settings.INPAINT_MODEL, "INPAINT_REVISION", self.inpaint_cost
        )

        # 创建新版本候选帧
        new_cand = KeyframeCandidate(
            shot_id=shot.id,
            frame_type=target_cand.frame_type,
            candidate_slot=target_cand.candidate_slot,
            image_url=new_image_url,
            source_type=SourceType.INPAINTED,
            mask_url=mask_url,
            feedback_note=feedback_prompt,
            cost_usd=self.inpaint_cost,
            revision_version=target_cand.revision_version + 1
        )

        if is_start:
            shot.start_candidates.append(new_cand)
            shot.selected_start_frame_id = new_cand.id
        else:
            shot.end_candidates.append(new_cand)
            shot.selected_end_frame_id = new_cand.id

        shot.video_status = ShotStatus.REVIEW_PENDING
        shot.accumulated_cost_usd = self.finops.get_shot_accumulated_cost(shot.id)
        return shot, new_cand

    def approve_keyframes(
        self,
        shot: Shot,
        selected_start_id: str,
        selected_end_id: str
    ) -> Shot:
        """
        Approves both start and end frames for video rendering.
        Advances state from REVIEW_PENDING to KEYFRAMES_APPROVED.
        """
        if shot.video_status not in [ShotStatus.REVIEW_PENDING, ShotStatus.KEYFRAME_GENERATING]:
            raise InvalidStateTransitionError(
                current_state=shot.video_status.value,
                target_state=ShotStatus.KEYFRAMES_APPROVED.value,
                reason="Shot must be in REVIEW_PENDING state to approve keyframes."
            )

        start_ids = [c.id for c in shot.start_candidates]
        end_ids = [c.id for c in shot.end_candidates]

        if selected_start_id not in start_ids:
            raise ValueError(f"Start frame ID {selected_start_id} is not in start candidates pool.")
        if selected_end_id not in end_ids:
            raise ValueError(f"End frame ID {selected_end_id} is not in end candidates pool.")

        shot.selected_start_frame_id = selected_start_id
        shot.selected_end_frame_id = selected_end_id
        shot.video_status = ShotStatus.KEYFRAMES_APPROVED
        return shot
