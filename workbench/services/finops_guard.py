"""
F-05: Pre-flight FinOps Gate and Cost Guard.
Enforces 120% balance circuit breaking, budget estimations, and ledger auditing.
"""

from typing import List
from workbench.config import settings
from workbench.domain.entities import FinOpsLedgerEntry, Shot
from workbench.domain.exceptions import InsufficientBalanceError


class FinOpsGuard:
    def __init__(self, buffer_ratio: float = settings.FINOPS_BUFFER_RATIO):
        self.buffer_ratio = buffer_ratio
        self.ledger: List[FinOpsLedgerEntry] = []

    def calculate_estimated_cost(self, num_shots: int, include_inpainting_buffer: bool = True) -> float:
        """
        Calculate total estimated cost for a given number of shots based on PRD unit economics.
        """
        if num_shots <= 0:
            return 0.0

        # LLM拆解 + 起幅2张 + 落幅2张 + 预估0.5次局部修复缓冲 + 首尾帧视频
        single_shot_cost = (
            settings.COST_LLM_PER_SHOT
            + (4 * settings.COST_IMAGE_PER_FRAME)
            + (0.5 * settings.COST_INPAINT_PER_FRAME if include_inpainting_buffer else 0.0)
            + settings.COST_VIDEO_PER_SHOT
        )
        return round(num_shots * single_shot_cost, 4)

    def pre_flight_check(self, current_balance: float, num_shots: int) -> float:
        """
        Evaluate account balance before any billable API calls.
        Raises InsufficientBalanceError if current_balance < Cost_est * 120%.
        Returns estimated cost if check passes.
        """
        estimated_cost = self.calculate_estimated_cost(num_shots)
        required_balance = round(estimated_cost * self.buffer_ratio, 4)

        if current_balance < required_balance:
            raise InsufficientBalanceError(
                current_balance=current_balance,
                estimated_cost=estimated_cost,
                required_balance=required_balance
            )
        return estimated_cost

    def record_transaction(
        self,
        shot_id: str,
        model_name: str,
        task_type: str,
        cost_usd: float,
        external_task_id: str = None
    ) -> FinOpsLedgerEntry:
        """
        Record an immutable billing transaction in the ledger.
        """
        entry = FinOpsLedgerEntry(
            shot_id=shot_id,
            model_name=model_name,
            task_type=task_type,
            cost_usd=cost_usd,
            external_task_id=external_task_id
        )
        self.ledger.append(entry)
        return entry

    def get_shot_accumulated_cost(self, shot_id: str) -> float:
        """Return total spend accumulated for a specific shot."""
        total = sum(entry.cost_usd for entry in self.ledger if entry.shot_id == shot_id)
        return round(total, 4)

    def get_total_accumulated_cost(self) -> float:
        """Return total spend across all recorded transactions."""
        total = sum(entry.cost_usd for entry in self.ledger)
        return round(total, 4)

    def assert_cost_ceiling(self, shots: List[Shot], max_cost_per_shot: float = 0.35) -> bool:
        """
        Fitness Function: Asserts that every completed shot satisfies the <= $0.35 ceiling.
        """
        for shot in shots:
            actual_cost = self.get_shot_accumulated_cost(shot.id)
            if actual_cost > max_cost_per_shot:
                raise AssertionError(
                    f"Shot {shot.id} exceeded cost ceiling! Actual: ${actual_cost:.4f}, Ceiling: ${max_cost_per_shot:.4f}"
                )
        return True
