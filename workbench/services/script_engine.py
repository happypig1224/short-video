"""
F-01: Script and Creative Storyboard Decomposition Engine.
Uses lightweight LLM (Gemini 3.8 Flash) to split raw story into structured Shot entities.
"""

import json
import re
from typing import List, Optional, Dict, Any
from workbench.config import settings
from workbench.domain.entities import Shot, ShotStatus
from workbench.domain.exceptions import ExternalAPIError


class ScriptEngine:
    def __init__(self, api_client=None):
        self.api_client = api_client
        self.model_name = settings.LLM_MODEL

    def _build_system_prompt(self, target_shots: Optional[int] = None) -> str:
        count_clause = f"严格拆解为 {target_shots} 个镜头。" if target_shots else "按叙事节奏拆解为 3~8 个镜头。"
        return (
            "你是一位好莱坞级影视分镜导演。请将输入的剧本或创意拆解为结构化分镜列表。\n"
            f"{count_clause}\n"
            "每个分镜必须为图生视频（First-and-Last Frame I2V）量身定制，包含起幅（开始画面）和落幅（结束画面）。\n"
            "必须直接返回 JSON 数组，严禁包含任何前缀、解释或额外 Markdown 标记。\n"
            "每个镜头对象的数据格式如下：\n"
            "[\n"
            "  {\n"
            '    "sequence_index": 1,\n'
            '    "scene_summary": "场记摘要说明",\n'
            '    "camera_motion": "运镜方式（如缓缓推近 Push In / 环绕 Orbit）",\n'
            '    "duration_seconds": 5,\n'
            '    "start_frame_prompt": "Cinematic visual description for Frame 0 (English)",\n'
            '    "end_frame_prompt": "Cinematic visual description for Frame 1 (English)",\n'
            '    "dynamic_guidance": "从起幅到落幅的平滑动态过渡说明",\n'
            '    "motion_strength": 5\n'
            "  }\n"
            "]"
        )

    def parse_llm_json_response(self, raw_text: str) -> List[Dict[str, Any]]:
        """Extract and parse JSON array safely from model output."""
        cleaned = raw_text.strip()
        # Remove markdown fences if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()

        # Find bracketed array
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)

        try:
            data = json.loads(cleaned, strict=False)
            if not isinstance(data, list):
                raise ValueError("Parsed JSON is not a list")
            return data
        except Exception as e:
            raise ExternalAPIError("ScriptEngine", 422, f"Failed to parse LLM JSON: {e}, raw: {raw_text[:200]}")

    def split_screenplay(
        self,
        project_id: str,
        screenplay_raw: str,
        target_shots: Optional[int] = None
    ) -> List[Shot]:
        """
        Decomposes raw screenplay into a list of verified Shot entities.
        """
        if not screenplay_raw or not screenplay_raw.strip():
            raise ValueError("Screenplay text cannot be empty.")

        system_prompt = self._build_system_prompt(target_shots)

        if self.api_client:
            raw_response = self.api_client.generate_text(
                model=self.model_name,
                system_prompt=system_prompt,
                user_prompt=screenplay_raw
            )
        else:
            # Fallback mock for self-contained execution when client is not injected
            raw_response = json.dumps([
                {
                    "sequence_index": 1,
                    "scene_summary": "上古祭坛破晓，凶兽饕餮在浓雾中苏醒",
                    "camera_motion": "缓缓推近并伴随低角度仰拍 (Push In & Low Angle Tilt Up)",
                    "duration_seconds": 5,
                    "start_frame_prompt": "Cinematic wide shot, ancient stone altar covered with moss, heavy morning mist, mythical beast Taotie silhouette awakening, glowing amber eyes, volumetric dawn light, 8k octane render, hyper-detailed textures",
                    "end_frame_prompt": "Cinematic close-up shot, Taotie head emerging through the mist, razor-sharp fangs, intricate bone armor plates, piercing glowing eyes, dust particles floating in golden sunrise, photorealistic 8k",
                    "dynamic_guidance": "从大远景浓雾剪影平滑推进到头部特写，雾气流向两侧散开，动作平缓无突变",
                    "motion_strength": 5
                }
            ], ensure_ascii=False)

        parsed_items = self.parse_llm_json_response(raw_response)

        shots: List[Shot] = []
        for idx, item in enumerate(parsed_items, start=1):
            shot = Shot(
                project_id=project_id,
                sequence_index=item.get("sequence_index", idx),
                scene_summary=item.get("scene_summary", f"Shot {idx}"),
                camera_motion=item.get("camera_motion", "Static"),
                duration_seconds=item.get("duration_seconds", settings.DEFAULT_DURATION_SECONDS),
                start_prompt=item.get("start_frame_prompt", ""),
                end_prompt=item.get("end_frame_prompt", ""),
                motion_prompt=item.get("dynamic_guidance", ""),
                motion_strength=item.get("motion_strength", 5),
                video_status=ShotStatus.SCRIPT_SPLIT
            )
            shots.append(shot)

        return shots
