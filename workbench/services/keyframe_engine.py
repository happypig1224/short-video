"""
F-02: Keyframe Dual-Candidate Pool Generator.
Generates Candidate A and B for both Frame 0 (Start) and Frame 1 (End),
enforcing image-to-image consistency between Start and End frames.
"""

from typing import List, Tuple
from workbench.config import settings
from workbench.domain.entities import (
    Shot, KeyframeCandidate, FrameType, CandidateSlot, SourceType, ShotStatus
)
from workbench.services.finops_guard import FinOpsGuard


class KeyframeEngine:
    def __init__(self, api_client=None, finops_guard: FinOpsGuard = None):
        self.api_client = api_client
        self.finops = finops_guard or FinOpsGuard()
        self.model_name = settings.IMAGE_MODEL

    def generate_candidates_for_shot(self, shot: Shot) -> Shot:
        """
        Generate 2 Start Candidates (A, B) and 2 End Candidates (A, B) for the shot.
        Updates shot status to REVIEW_PENDING.
        """
        shot.video_status = ShotStatus.KEYFRAME_GENERATING

        # 1. 生成起幅双候选 (Candidate A, B)
        start_a_url = self._call_text_to_image(shot.start_prompt, seed_offset=1)
        start_b_url = self._call_text_to_image(shot.start_prompt, seed_offset=2)

        cand_start_a = KeyframeCandidate(
            shot_id=shot.id,
            frame_type=FrameType.START,
            candidate_slot=CandidateSlot.A,
            image_url=start_a_url,
            cost_usd=settings.COST_IMAGE_PER_FRAME,
            revision_version=1
        )
        cand_start_b = KeyframeCandidate(
            shot_id=shot.id,
            frame_type=FrameType.START,
            candidate_slot=CandidateSlot.B,
            image_url=start_b_url,
            cost_usd=settings.COST_IMAGE_PER_FRAME,
            revision_version=1
        )
        self.finops.record_transaction(
            shot.id, self.model_name, "KEYFRAME_START_A", settings.COST_IMAGE_PER_FRAME
        )
        self.finops.record_transaction(
            shot.id, self.model_name, "KEYFRAME_START_B", settings.COST_IMAGE_PER_FRAME
        )

        # 2. 生成落幅双候选 (以起幅 A 为视觉一致性底图，注入 end_prompt)
        end_a_url = self._call_image_to_image(
            prompt=shot.end_prompt, reference_image_url=start_a_url, seed_offset=3
        )
        end_b_url = self._call_image_to_image(
            prompt=shot.end_prompt, reference_image_url=start_a_url, seed_offset=4
        )

        cand_end_a = KeyframeCandidate(
            shot_id=shot.id,
            frame_type=FrameType.END,
            candidate_slot=CandidateSlot.A,
            image_url=end_a_url,
            cost_usd=settings.COST_IMAGE_PER_FRAME,
            revision_version=1
        )
        cand_end_b = KeyframeCandidate(
            shot_id=shot.id,
            frame_type=FrameType.END,
            candidate_slot=CandidateSlot.B,
            image_url=end_b_url,
            cost_usd=settings.COST_IMAGE_PER_FRAME,
            revision_version=1
        )
        self.finops.record_transaction(
            shot.id, self.model_name, "KEYFRAME_END_A", settings.COST_IMAGE_PER_FRAME
        )
        self.finops.record_transaction(
            shot.id, self.model_name, "KEYFRAME_END_B", settings.COST_IMAGE_PER_FRAME
        )

        # 挂载候选帧到镜头
        shot.start_candidates = [cand_start_a, cand_start_b]
        shot.end_candidates = [cand_end_a, cand_end_b]
        
        # 默认选中 Candidate A 作为预激活帧
        shot.selected_start_frame_id = cand_start_a.id
        shot.selected_end_frame_id = cand_end_a.id
        
        shot.video_status = ShotStatus.REVIEW_PENDING
        shot.accumulated_cost_usd = self.finops.get_shot_accumulated_cost(shot.id)
        return shot

    def _call_text_to_image(self, prompt: str, seed_offset: int) -> str:
        if self.api_client:
            return self.api_client.generate_image(prompt=prompt, seed=seed_offset)
        return f"https://mock-oss.302.ai/images/cand_{seed_offset}.png"

    def _call_image_to_image(self, prompt: str, reference_image_url: str, seed_offset: int) -> str:
        if self.api_client:
            return self.api_client.generate_image_to_image(
                prompt=prompt, reference_url=reference_image_url, seed=seed_offset
            )
        return f"https://mock-oss.302.ai/images/cand_i2i_{seed_offset}.png"
