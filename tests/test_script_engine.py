import pytest
from workbench.services.script_engine import ScriptEngine
from workbench.domain.entities import ShotStatus


def test_parse_llm_json_response_clean():
    engine = ScriptEngine()
    sample = """[
        {
            "sequence_index": 1,
            "scene_summary": "Scene 1",
            "camera_motion": "Pan Right",
            "duration_seconds": 5,
            "start_frame_prompt": "start prompt",
            "end_frame_prompt": "end prompt",
            "dynamic_guidance": "guidance",
            "motion_strength": 5
        }
    ]"""
    result = engine.parse_llm_json_response(sample)
    assert len(result) == 1
    assert result[0]["sequence_index"] == 1


def test_parse_llm_json_response_with_markdown_fence():
    engine = ScriptEngine()
    sample = """```json
    [
        {
            "sequence_index": 2,
            "scene_summary": "Scene 2",
            "camera_motion": "Zoom In",
            "duration_seconds": 5,
            "start_frame_prompt": "prompt 2",
            "end_frame_prompt": "prompt 2 end",
            "dynamic_guidance": "guidance 2",
            "motion_strength": 6
        }
    ]
    ```"""
    result = engine.parse_llm_json_response(sample)
    assert len(result) == 1
    assert result[0]["sequence_index"] == 2


def test_split_screenplay_creates_valid_shots():
    engine = ScriptEngine()
    shots = engine.split_screenplay(
        project_id="proj_alpha",
        screenplay_raw="混沌之初，古钟破晓，饕餮苏醒长啸"
    )
    assert len(shots) >= 1
    shot = shots[0]
    assert shot.project_id == "proj_alpha"
    assert shot.video_status == ShotStatus.SCRIPT_SPLIT
    assert shot.duration_seconds == 5
    assert len(shot.start_prompt) > 0
    assert len(shot.end_prompt) > 0
