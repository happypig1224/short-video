import pytest
from workbench.services.review_engine import ReviewEngine
from workbench.services.keyframe_engine import KeyframeEngine
from workbench.services.finops_guard import FinOpsGuard
from workbench.domain.entities import Shot, ShotStatus, SourceType
from workbench.domain.exceptions import InpaintingExceededError, InvalidStateTransitionError


def create_sample_shot() -> Shot:
    return Shot(
        id="shot_review_01",
        project_id="proj_01",
        sequence_index=1,
        scene_summary="Review test scene",
        camera_motion="Static",
        start_prompt="start prompt text",
        end_prompt="end prompt text",
        motion_prompt="motion text"
    )


def test_keyframe_candidates_creation():
    finops = FinOpsGuard()
    kf_engine = KeyframeEngine(finops_guard=finops)
    shot = create_sample_shot()

    kf_engine.generate_candidates_for_shot(shot)

    assert len(shot.start_candidates) == 2
    assert len(shot.end_candidates) == 2
    assert shot.video_status == ShotStatus.REVIEW_PENDING
    assert shot.selected_start_frame_id is not None
    assert shot.selected_end_frame_id is not None
    assert shot.accumulated_cost_usd > 0


def test_inpainting_redo_success():
    finops = FinOpsGuard()
    kf_engine = KeyframeEngine(finops_guard=finops)
    review_engine = ReviewEngine(finops_guard=finops)
    shot = create_sample_shot()
    kf_engine.generate_candidates_for_shot(shot)

    target_id = shot.end_candidates[0].id
    mask_url = "https://mock-oss.302.ai/masks/mask_hand.png"
    prompt = "Fix 6 fingers into natural fist"

    updated_shot, new_cand = review_engine.submit_inpainting_redo(
        shot=shot,
        target_candidate_id=target_id,
        mask_url=mask_url,
        feedback_prompt=prompt
    )

    assert updated_shot.inpaint_retry_count == 1
    assert len(updated_shot.end_candidates) == 3
    assert new_cand.source_type == SourceType.INPAINTED
    assert new_cand.revision_version == 2
    assert updated_shot.selected_end_frame_id == new_cand.id


def test_inpainting_max_retries_exceeded():
    finops = FinOpsGuard()
    kf_engine = KeyframeEngine(finops_guard=finops)
    review_engine = ReviewEngine(finops_guard=finops)
    shot = create_sample_shot()
    kf_engine.generate_candidates_for_shot(shot)

    target_id = shot.end_candidates[0].id
    mask_url = "https://mock-oss.302.ai/masks/mask.png"

    # Execute 3 allowed retries
    for _ in range(3):
        review_engine.submit_inpainting_redo(
            shot=shot,
            target_candidate_id=target_id,
            mask_url=mask_url,
            feedback_prompt="Fix defect"
        )
    assert shot.inpaint_retry_count == 3

    # 4th retry must be blocked by Circuit Breaker
    with pytest.raises(InpaintingExceededError) as exc_info:
        review_engine.submit_inpainting_redo(
            shot=shot,
            target_candidate_id=target_id,
            mask_url=mask_url,
            feedback_prompt="Attempting 4th retry"
        )
    assert "exceeded maximum inpainting retries" in str(exc_info.value)


def test_approve_keyframes_advances_state():
    finops = FinOpsGuard()
    kf_engine = KeyframeEngine(finops_guard=finops)
    review_engine = ReviewEngine(finops_guard=finops)
    shot = create_sample_shot()
    kf_engine.generate_candidates_for_shot(shot)

    sel_start = shot.start_candidates[1].id
    sel_end = shot.end_candidates[0].id

    review_engine.approve_keyframes(shot, sel_start, sel_end)
    assert shot.video_status == ShotStatus.KEYFRAMES_APPROVED
    assert shot.selected_start_frame_id == sel_start
    assert shot.selected_end_frame_id == sel_end


def test_approve_keyframes_invalid_id():
    finops = FinOpsGuard()
    kf_engine = KeyframeEngine(finops_guard=finops)
    review_engine = ReviewEngine(finops_guard=finops)
    shot = create_sample_shot()
    kf_engine.generate_candidates_for_shot(shot)

    with pytest.raises(ValueError) as exc_info:
        review_engine.approve_keyframes(shot, "nonexistent_start_id", shot.end_candidates[0].id)
    assert "not in start candidates pool" in str(exc_info.value)
