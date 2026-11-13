"""
High-fidelity Mock Gateway for 302.AI API.
Provides deterministic simulation of multi-model inference, async task lifecycle,
rate limiting, and balance exhaustion for integration & E2E testing.
"""

from typing import Dict, Any, Tuple, Optional
import uuid
import json


class Mock302AIGateway:
    def __init__(self, initial_balance: float = 10.0):
        self.balance = initial_balance
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.fail_next_video: bool = False
        self.rate_limit_next: bool = False

    def get_balance(self) -> float:
        return self.balance

    def deduct_balance(self, amount: float):
        if self.balance < amount:
            raise RuntimeError(f"302.AI API error: err_code: -10004, Insufficient balance (current: {self.balance})")
        self.balance = round(self.balance - amount, 4)

    def generate_text(self, model: str, system_prompt: str, user_prompt: str) -> str:
        if self.rate_limit_next:
            self.rate_limit_next = False
            raise RuntimeError("302.AI API HTTP 429: Rate limit exceeded")
        self.deduct_balance(0.0003)
        return json.dumps([
            {
                "sequence_index": 1,
                "scene_summary": "上古祭坛破晓，凶兽饕餮在浓雾中苏醒",
                "camera_motion": "缓缓推近并伴随低角度仰拍 (Push In & Low Angle Tilt Up)",
                "duration_seconds": 5,
                "start_frame_prompt": "Cinematic wide shot, ancient stone altar covered with moss, heavy morning mist, mythical beast Taotie silhouette awakening",
                "end_frame_prompt": "Cinematic close-up shot, Taotie head emerging through mist, glowing eyes, razor fangs",
                "dynamic_guidance": "从大远景浓雾剪影平滑推进到头部特写，动作平缓无突变",
                "motion_strength": 5
            },
            {
                "sequence_index": 2,
                "scene_summary": "饕餮昂首长啸，金色晨曦刺破黑云",
                "camera_motion": "环绕运镜 (Orbit 180)",
                "duration_seconds": 5,
                "start_frame_prompt": "Cinematic medium shot, Taotie head tilted upward, throat glowing amber",
                "end_frame_prompt": "Epic wide shot, golden dawn rays breaking clouds, Taotie standing triumphant on cliff",
                "dynamic_guidance": "环绕饕餮旋转半周，晨曦光芒自天际倾泻而下",
                "motion_strength": 6
            }
        ], ensure_ascii=False)

    def generate_image(self, prompt: str, seed: int = 1) -> str:
        self.deduct_balance(0.02228)
        img_id = uuid.uuid4().hex[:8]
        return f"https://file.302.ai/generated/t2i_{img_id}_s{seed}.png"

    def generate_image_to_image(self, prompt: str, reference_url: str, seed: int = 1) -> str:
        self.deduct_balance(0.02228)
        img_id = uuid.uuid4().hex[:8]
        return f"https://file.302.ai/generated/i2i_{img_id}_ref_{seed}.png"

    def inpaint_image(self, base_image_url: str, mask_url: str, prompt: str) -> str:
        self.deduct_balance(0.02228)
        img_id = uuid.uuid4().hex[:8]
        return f"{base_image_url}_inpaint_{img_id}.png"

    def submit_i2v_task(
        self,
        model: str,
        prompt: str,
        image_start_url: str,
        image_tail_url: str,
        duration: int = 5
    ) -> str:
        self.deduct_balance(0.1890)
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        self.tasks[task_id] = {
            "status": "processing",
            "polls_left": 2,  # Takes 2 polls to complete
            "video_url": f"https://file.302.ai/video/{task_id}_output.mp4"
        }
        return task_id

    def query_i2v_task(self, task_id: str) -> Tuple[str, Optional[str]]:
        if task_id not in self.tasks:
            raise KeyError(f"Task {task_id} not found")

        task = self.tasks[task_id]
        if self.fail_next_video:
            self.fail_next_video = False
            task["status"] = "failed"
            return "failed", None

        if task["polls_left"] > 0:
            task["polls_left"] -= 1
            return "processing", None
        else:
            task["status"] = "success"
            return "success", task["video_url"]
