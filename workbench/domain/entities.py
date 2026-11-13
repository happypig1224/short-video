"""
Domain entities and data contracts for AI Video Workbench Phase 1.
Strictly typed via Pydantic v2.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, ConfigDict


class ShotStatus(str, Enum):
    DRAFT = "DRAFT"
    SCRIPT_SPLIT = "SCRIPT_SPLIT"
    KEYFRAME_GENERATING = "KEYFRAME_GENERATING"
    REVIEW_PENDING = "REVIEW_PENDING"
    INPAINTING_RUNNING = "INPAINTING_RUNNING"
    KEYFRAMES_APPROVED = "KEYFRAMES_APPROVED"
    VIDEO_SYNTHESIZING = "VIDEO_SYNTHESIZING"
    READY = "READY"
    FAILED = "FAILED"


class FrameType(str, Enum):
    START = "START"
    END = "END"


class CandidateSlot(str, Enum):
    A = "A"
    B = "B"


class SourceType(str, Enum):
    ORIGINAL = "ORIGINAL"
    INPAINTED = "INPAINTED"


class ReviewActionType(str, Enum):
    INPAINT_REDO = "INPAINT_REDO"
    FULL_REGENERATE = "FULL_REGENERATE"
    APPROVED = "APPROVED"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class KeyframeCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    shot_id: str
    frame_type: FrameType
    candidate_slot: CandidateSlot
    image_url: str
    source_type: SourceType = SourceType.ORIGINAL
    mask_url: Optional[str] = None
    feedback_note: Optional[str] = None
    cost_usd: float = 0.02228
    revision_version: int = 1
    created_at: str = Field(default_factory=utc_now_iso)


class ReviewLog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    shot_id: str
    target_candidate_id: str
    action_type: ReviewActionType
    feedback_note: str = ""
    mask_url: Optional[str] = None
    created_at: str = Field(default_factory=utc_now_iso)


class Shot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    sequence_index: int
    scene_summary: str
    camera_motion: str
    duration_seconds: int = 5
    
    # 提示词与动态引导
    start_prompt: str
    end_prompt: str
    motion_prompt: str
    motion_strength: int = 5
    
    # 关键帧候选资源
    start_candidates: List[KeyframeCandidate] = Field(default_factory=list)
    end_candidates: List[KeyframeCandidate] = Field(default_factory=list)
    selected_start_frame_id: Optional[str] = None
    selected_end_frame_id: Optional[str] = None
    
    # 状态与产物
    video_task_id: Optional[str] = None
    video_url: Optional[str] = None
    video_status: ShotStatus = ShotStatus.DRAFT
    
    # 财务与重试审计
    inpaint_retry_count: int = 0
    accumulated_cost_usd: float = 0.0
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)


class Project(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    screenplay_raw: str
    shots: List[Shot] = Field(default_factory=list)
    budget_ceiling_usd: float = 5.0
    created_at: str = Field(default_factory=utc_now_iso)


class FinOpsLedgerEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    shot_id: str
    service_provider: str = "302.AI"
    model_name: str
    task_type: str
    cost_usd: float
    external_task_id: Optional[str] = None
    logged_at: str = Field(default_factory=utc_now_iso)
