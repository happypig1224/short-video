import pytest
from workbench.services.video_synthesis_engine import VideoSynthesisEngine
from workbench.services.keyframe_engine import KeyframeEngine
from workbench.services.review_engine import ReviewEngine
from workbench.services.finops_guard import FinOpsGuard
from workbench.domain.entities import Shot, ShotStatus
from workbench.domain.exceptions import InvalidStateTransitionError


def create_approved_shot() -> Shot:
    finops = FinOpsGuard()
    kf_engine = KeyframeEngine(finops_guard=finops)
    review_engine = ReviewEngine(finops_guard=finops)

    shot = Shot(
        id="shot_vid_01",
        project_id="proj_01",
        sequence_index=1,
        scene_summary="Video synthesis test",
        camera_motion="Push In",
        start_prompt="start prompt text",
        end_prompt="end prompt text",
        motion_prompt="motion text"
    )
    kf_engine.generate_candidates_for_shot(shot)
    review_engine.approve_keyframes(
        shot, shot.start_candidates[0].id, shot.end_candidates[0].id
    )
    return shot


def test_dispatch_synthesis_requires_approved_state():
    engine = VideoSynthesisEngine()
    unapproved_shot = Shot(
        id="shot_unapp",
        project_id="proj_01",
        sequence_index=1,
        scene_summary="Unapproved",
        camera_motion="Static",
        start_prompt="s",
        end_prompt="e",
        motion_prompt="m",
        video_status=ShotStatus.REVIEW_PENDING
    )
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        engine.dispatch_synthesis_job(unapproved_shot)
    assert "keyframes must be approved" in str(exc_info.value)


def test_dispatch_and_reconcile_success():
    finops = FinOpsGuard()
    shot = create_approved_shot()
    engine = VideoSynthesisEngine(finops_guard=finops)

    task_id = engine.dispatch_synthesis_job(shot)
    assert task_id.startswith("task_")
    assert shot.video_status == ShotStatus.VIDEO_SYNTHESIZING

    ready_shot = engine.reconcile_task_status(shot, task_id, max_poll_attempts=5, poll_interval=0.01)
    assert ready_shot.video_status == ShotStatus.READY
    assert ready_shot.video_url.endswith(".mp4")


def test_idempotency_deduplication():
    finops = FinOpsGuard()
    shot = create_approved_shot()
    engine = VideoSynthesisEngine(finops_guard=finops)

    # First dispatch & finish
    task_id = engine.dispatch_synthesis_job(shot)
    engine.reconcile_task_status(shot, task_id, poll_interval=0.01)

    initial_tx_count = len(finops.ledger)

    # Second dispatch with identical frames must return cached task without billing
    shot.video_status = ShotStatus.KEYFRAMES_APPROVED
    task_id_2 = engine.dispatch_synthesis_job(shot)

    assert task_id_2 == task_id
    assert len(finops.ledger) == initial_tx_count  # No duplicate billing!
    assert shot.video_status == ShotStatus.READY
