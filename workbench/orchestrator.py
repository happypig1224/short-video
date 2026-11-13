"""
Workbench Orchestrator: Central coordinating pipeline for Phase 1.
Chains F-01 (Script), F-02 (Keyframes), F-03 (Review & Inpaint),
F-04 (Synthesis), and F-05 (FinOps Pre-flight).
"""

from typing import List, Optional
from workbench.domain.entities import Project, Shot, ShotStatus
from workbench.domain.exceptions import InsufficientBalanceError
from workbench.services.finops_guard import FinOpsGuard
from workbench.services.script_engine import ScriptEngine
from workbench.services.keyframe_engine import KeyframeEngine
from workbench.services.review_engine import ReviewEngine
from workbench.services.video_synthesis_engine import VideoSynthesisEngine


class WorkbenchOrchestrator:
    def __init__(self, api_client=None, user_balance: float = 10.0):
        self.api_client = api_client
        self.user_balance = user_balance
        self.finops = FinOpsGuard()
        self.script_engine = ScriptEngine(api_client=self.api_client)
        self.keyframe_engine = KeyframeEngine(api_client=self.api_client, finops_guard=self.finops)
        self.review_engine = ReviewEngine(api_client=self.api_client, finops_guard=self.finops)
        self.video_engine = VideoSynthesisEngine(api_client=self.api_client, finops_guard=self.finops)

    def create_project(self, title: str, screenplay_raw: str) -> Project:
        return Project(title=title, screenplay_raw=screenplay_raw)

    def step_decompose(self, project: Project, target_shots: Optional[int] = None) -> Project:
        """F-01: Split screenplay into shots."""
        shots = self.script_engine.split_screenplay(
            project_id=project.id,
            screenplay_raw=project.screenplay_raw,
            target_shots=target_shots
        )
        project.shots = shots
        return project

    def step_generate_keyframes_batch(self, project: Project) -> Project:
        """
        F-05 & F-02: Pre-flight check balance first, then generate dual keyframes for each shot.
        """
        # 1. FinOps 熔断核验
        self.finops.pre_flight_check(
            current_balance=self.user_balance,
            num_shots=len(project.shots)
        )

        # 2. 并行/循环生成关键帧
        for shot in project.shots:
            self.keyframe_engine.generate_candidates_for_shot(shot)

        return project

    def step_inpaint_shot(
        self,
        shot: Shot,
        candidate_id: str,
        mask_url: str,
        feedback_prompt: str
    ) -> Shot:
        """F-03: Inpaint specific flawed frame."""
        updated_shot, _ = self.review_engine.submit_inpainting_redo(
            shot=shot,
            target_candidate_id=candidate_id,
            mask_url=mask_url,
            feedback_prompt=feedback_prompt
        )
        return updated_shot

    def step_approve_and_synthesize(
        self,
        shot: Shot,
        selected_start_id: str,
        selected_end_id: str
    ) -> Shot:
        """
        F-03 & F-04: Approve keyframes and execute I2V synthesis.
        """
        # 1. 核准关键帧
        approved_shot = self.review_engine.approve_keyframes(
            shot=shot,
            selected_start_id=selected_start_id,
            selected_end_id=selected_end_id
        )

        # 2. 调度合成任务
        task_id = self.video_engine.dispatch_synthesis_job(approved_shot)

        # 3. 轮询收敛
        ready_shot = self.video_engine.reconcile_task_status(approved_shot, task_id)
        return ready_shot
