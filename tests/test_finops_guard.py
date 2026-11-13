import pytest
from workbench.services.finops_guard import FinOpsGuard
from workbench.domain.exceptions import InsufficientBalanceError
from workbench.domain.entities import Shot, ShotStatus


def test_cost_calculation():
    guard = FinOpsGuard()
    cost_1 = guard.calculate_estimated_cost(1)
    # 0.0003 + 4*0.02228 + 0.5*0.02228 + 0.1890 = 0.0003 + 0.08912 + 0.01114 + 0.1890 = 0.28956 -> 0.2896
    assert 0.28 <= cost_1 <= 0.32
    assert cost_1 < 0.35

    cost_10 = guard.calculate_estimated_cost(10)
    assert round(cost_10, 2) == round(cost_1 * 10, 2)


def test_pre_flight_check_allows_when_balance_sufficient():
    guard = FinOpsGuard()
    # 1 shot est ~ 0.2896, * 1.2 = 0.3475
    estimated = guard.pre_flight_check(current_balance=1.0, num_shots=1)
    assert estimated > 0


def test_pre_flight_check_blocks_when_balance_insufficient():
    guard = FinOpsGuard()
    # 10 shots est ~ 2.896, * 1.2 = ~ 3.475
    with pytest.raises(InsufficientBalanceError) as exc_info:
        guard.pre_flight_check(current_balance=2.0, num_shots=10)
    assert "Pre-flight FinOps Gate Blocked" in str(exc_info.value)
    assert exc_info.value.current_balance == 2.0


def test_ledger_transactions_and_cost_ceiling():
    guard = FinOpsGuard()
    shot_id = "shot_test_01"

    guard.record_transaction(shot_id, "gemini-3.8-flash", "LLM_SPLIT", 0.0003)
    guard.record_transaction(shot_id, "gpt-image-sunburst", "KEYFRAME_START_A", 0.02228)
    guard.record_transaction(shot_id, "gpt-image-sunburst", "KEYFRAME_START_B", 0.02228)
    guard.record_transaction(shot_id, "gpt-image-sunburst", "KEYFRAME_END_A", 0.02228)
    guard.record_transaction(shot_id, "gpt-image-sunburst", "KEYFRAME_END_B", 0.02228)
    guard.record_transaction(shot_id, "gpt-image-sunburst", "INPAINT_REDO", 0.02228)
    guard.record_transaction(shot_id, "kling-v1-6", "VIDEO_I2V", 0.1890)

    total_cost = guard.get_shot_accumulated_cost(shot_id)
    assert total_cost <= 0.35  # Must not exceed PRD $0.35 limit

    shot = Shot(
        id=shot_id,
        project_id="proj_01",
        sequence_index=1,
        scene_summary="Test",
        camera_motion="Push In",
        start_prompt="start",
        end_prompt="end",
        motion_prompt="motion",
        video_status=ShotStatus.READY
    )

    # Fitness function check
    assert guard.assert_cost_ceiling([shot], max_cost_per_shot=0.35) is True
