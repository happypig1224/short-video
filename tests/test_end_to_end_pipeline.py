import pytest
from workbench.orchestrator import WorkbenchOrchestrator
from workbench.mock_gateway import Mock302AIGateway
from workbench.domain.entities import ShotStatus
from workbench.domain.exceptions import InsufficientBalanceError


def test_e2e_golden_pipeline_closure():
    """
    TC-E2E-01: End-to-end Golden Path verification.
    Validates complete flow from raw screenplay to final MP4 delivery,
    including candidate generation, inpainting feedback loop, and FinOps budget compliance.
    """
    mock_api = Mock302AIGateway(initial_balance=10.0)
    orchestrator = WorkbenchOrchestrator(api_client=mock_api, user_balance=10.0)

    # 1. 创意输入与项目创建
    raw_idea = "上古洪荒，饕餮破晓苏醒，巨口吞云吐雾，金色晨曦映照青铜鳞甲。"
    project = orchestrator.create_project(title="饕餮神话", screenplay_raw=raw_idea)
    assert project.id is not None

    # 2. F-01: 智能分镜拆解
    project = orchestrator.step_decompose(project)
    assert len(project.shots) == 2
    shot_1 = project.shots[0]
    assert shot_1.video_status == ShotStatus.SCRIPT_SPLIT

    # 3. F-05 & F-02: 事前熔断核验 + 双关键帧候选池生成
    project = orchestrator.step_generate_keyframes_batch(project)
    shot_1 = project.shots[0]
    assert shot_1.video_status == ShotStatus.REVIEW_PENDING
    assert len(shot_1.start_candidates) == 2
    assert len(shot_1.end_candidates) == 2

    # 4. F-03: 人工审核评审台与局部缺陷打回
    flawed_cand_id = shot_1.end_candidates[0].id
    mask_url = "https://mock-oss.302.ai/masks/taotie_horn_defect.png"
    feedback = "将骨角断裂处修复为完整黑金巨角，增强微光纹理"

    shot_1 = orchestrator.step_inpaint_shot(
        shot=shot_1,
        candidate_id=flawed_cand_id,
        mask_url=mask_url,
        feedback_prompt=feedback
    )
    assert shot_1.inpaint_retry_count == 1
    assert len(shot_1.end_candidates) == 3
    new_inpainted_cand_id = shot_1.selected_end_frame_id

    # 5. F-03 & F-04: 核准确认 + 首尾帧插值视频渲染
    chosen_start_id = shot_1.start_candidates[0].id
    chosen_end_id = new_inpainted_cand_id

    ready_shot = orchestrator.step_approve_and_synthesize(
        shot=shot_1,
        selected_start_id=chosen_start_id,
        selected_end_id=chosen_end_id
    )

    # 6. 业务闭环与指标断言 (Strict Acceptance Assertions)
    assert ready_shot.video_status == ShotStatus.READY
    assert ready_shot.video_url is not None
    assert ready_shot.video_url.endswith(".mp4")
    assert ready_shot.accumulated_cost_usd > 0

    # 验证单镜头总成本严格低于 PRD $0.35 目标
    assert ready_shot.accumulated_cost_usd <= 0.35, (
        f"Actual cost ${ready_shot.accumulated_cost_usd} exceeded $0.35 threshold"
    )
    print(f"\n[E2E Verification Succeeded] Shot 1 Total Cost: ${ready_shot.accumulated_cost_usd:.4f} <= $0.35 ceiling.")


def test_e2e_negative_insufficient_balance_blocks():
    """
    TC-E2E-02: Negative Path verification.
    Simulates insufficient account balance ($0.20),
    asserting 100% interception before any billable API calls.
    """
    mock_api = Mock302AIGateway(initial_balance=0.20)
    orchestrator = WorkbenchOrchestrator(api_client=mock_api, user_balance=0.20)

    raw_idea = "测试低余额拦截场景"
    project = orchestrator.create_project(title="测试", screenplay_raw=raw_idea)
    project = orchestrator.step_decompose(project)

    # 2 个镜头预估开销约 $0.60，120% 需约 $0.72，当前余额仅 $0.20
    with pytest.raises(InsufficientBalanceError) as exc_info:
        orchestrator.step_generate_keyframes_batch(project)

    assert "Pre-flight FinOps Gate Blocked" in str(exc_info.value)
    # 验证关键帧生成被 100% 拦截，候选池仍为空
    assert len(project.shots[0].start_candidates) == 0
    print("\n[Negative Path Verification Succeeded] Blocked 100% of billable calls on low balance.")
