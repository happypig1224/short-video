"""
302.ai 可灵图片O3 (Kling Image O3) 生图脚本
接口地址: POST https://api.302.ai/klingai/mmu_omni_3_image
任务轮询: GET  https://api.302.ai/klingai/task/{task_id}/fetch
文件上传: POST https://api.302.ai/302/upload-file (用于本地参考图自动上传)

功能特性:
1. 支持文本生图 (文生图) 与参考图生图 (图生图，支持 1-10 张参考图)
2. 本地参考图自动通过 302.ai 文件上传接口转换为网络 URL，同时也直接支持远程 http/https URL
3. 支持画质分辨率参数 (img_resolution: 1k, 2k, 4k)
4. 支持画面比例/尺寸参数 (aspect_ratio: auto, 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3)
5. 支持生成数量参数 (imageCount: 1-4)
6. 自动异步轮询任务状态并下载结果图片到本地
7. 既可作为命令行独立脚本运行，也可作为 Python 模块供外部调用
"""

import os
import sys
import time
import json
import argparse
from typing import List, Optional, Union
import requests
from dotenv import load_dotenv

load_dotenv()

# 默认配置
DEFAULT_BASE_URLS = ["https://api.302.ai", "https://api.302ai.com"]
DEFAULT_API_KEY = os.getenv("VIVIBON_302_IMAGE_API_KEY") or os.getenv("API_302_KEY") or ""


class KlingImageO3Client:
    """302.ai 可灵 O3 生图客户端"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or DEFAULT_API_KEY
        if not self.api_key:
            raise ValueError("未配置 302.ai API Key，请设置环境变量 VIVIBON_302_IMAGE_API_KEY 或传入 api_key 参数")
        
        self.base_urls = [base_url.rstrip("/")] if base_url else DEFAULT_BASE_URLS
        self.current_base_url = self.base_urls[0]
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 KlingO3Client/1.0"
        })

    @property
    def base_url(self) -> str:
        return self.current_base_url

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """带域名重试与容错的网络请求"""
        last_error = None
        for base in self.base_urls:
            url = f"{base}{endpoint}"
            for attempt in range(2):
                try:
                    resp = self.session.request(method, url, timeout=60, **kwargs)
                    if resp.status_code in [200, 400, 404, 500]:
                        self.current_base_url = base
                        return resp
                except Exception as e:
                    last_error = e
                    time.sleep(1)
        raise RuntimeError(f"网络请求失败 [{method} {endpoint}]: {last_error}")

    def upload_local_image(self, file_path: str) -> str:
        """
        将本地图片上传至 302.ai 文件服务器，返回公共访问 URL
        接口: POST https://api.302.ai/302/upload-file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"本地参考图文件不存在: {file_path}")

        file_name = os.path.basename(file_path)
        file_size_kb = os.path.getsize(file_path) / 1024

        print(f"[*] 正在上传本地参考图: {file_name} ({file_size_kb:.1f} KB)...")
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f)}
            resp = self._request("POST", "/302/upload-file", files=files)

        if resp.status_code != 200:
            raise RuntimeError(f"参考图上传失败 [HTTP {resp.status_code}]: {resp.text}")

        res_json = resp.json()
        if res_json.get("code") == 200 and "data" in res_json:
            remote_url = res_json["data"]
            print(f"[+] 参考图上传成功: {remote_url}")
            return remote_url
        else:
            raise RuntimeError(f"参考图上传返回异常: {res_json}")

    def prepare_reference_images(self, images: Optional[List[str]]) -> List[str]:
        """
        处理传入的参考图列表:
        若是本地文件路径则自动上传；若是 http/https URL 则直接使用
        """
        if not images:
            return []

        processed_urls = []
        for img in images:
            img = img.strip()
            if not img:
                continue
            if img.startswith("http://") or img.startswith("https://"):
                processed_urls.append(img)
            else:
                uploaded_url = self.upload_local_image(img)
                processed_urls.append(uploaded_url)
        return processed_urls

    def submit_task(
        self,
        prompt: str,
        images: Optional[List[str]] = None,
        aspect_ratio: str = "1:1",
        img_resolution: str = "1k",
        image_count: int = 1,
        story_mode: bool = False
    ) -> str:
        """
        向 302.ai 提交可灵 O3 生图任务 (对接最新 v3 神经渲染集群)
        :param prompt: 提示词 (必填)
        :param images: 参考图列表 (可传本地路径或远程 URL，最多 10 张)
        :param aspect_ratio: 画面比例 (auto, 9:16, 2:3, 3:4, 1:1, 4:3, 3:2, 16:9)
        :param img_resolution: 分辨率画质 (1k, 2k, 4k)
        :param image_count: 生成张数 (1-4)
        :param story_mode: 是否启用组图模式 (默认 False)
        :return: task_id 任务ID
        """
        # 清理提示词与参数格式化
        clean_prompt = prompt.strip()
        norm_resolution = img_resolution.lower().strip() if img_resolution else "1k"
        norm_aspect_ratio = "1:1" if aspect_ratio == "auto" or not aspect_ratio else aspect_ratio.strip()
        count = max(1, min(4, int(image_count)))

        # 处理参考图
        processed_images = self.prepare_reference_images(images)

        if processed_images:
            # 参考图编辑 / 图生图模式
            endpoint = "/ws/api/v3/kwaivgi/kling-image-o3/edit"
            payload = {
                "images": processed_images,
                "prompt": clean_prompt,
                "aspect_ratio": norm_aspect_ratio,
                "resolution": norm_resolution,
                "num_images": count,
                "output_format": "png"
            }
            print(f"[*] 采用【可灵 O3 参考图生图】模式，共传入 {len(processed_images)} 张参考图")
        else:
            # 纯文本生图模式
            endpoint = "/ws/api/v3/kwaivgi/kling-image-o3/text-to-image"
            payload = {
                "prompt": clean_prompt,
                "aspect_ratio": norm_aspect_ratio,
                "resolution": norm_resolution,
                "num_images": count,
                "output_format": "png"
            }
            print(f"[*] 采用【可灵 O3 纯文生图】模式")

        print(f"[*] 提交参数: 比例={norm_aspect_ratio}, 画质={norm_resolution}, 数量={count}")
        print(f"[*] 提示词: {clean_prompt}")

        headers = {"Content-Type": "application/json"}
        resp = self._request("POST", endpoint, json=payload, headers=headers)

        if resp.status_code != 200:
            raise RuntimeError(f"任务提交失败 [HTTP {resp.status_code}]: {resp.text}")

        res_json = resp.json()
        code = res_json.get("code")
        data = res_json.get("data", {})
        task_id = data.get("id") or data.get("task_id") or res_json.get("task_id")

        if (code == 0 or code == 200) and task_id:
            print(f"[+] 任务提交成功！Task ID: {task_id}")
            return task_id
        else:
            raise RuntimeError(f"提交响应异常: {res_json}")

    def fetch_task_result(self, task_id: str) -> dict:
        """单次拉取任务最新状态与结果 (兼容 v3 predictions 与旧版 fetch 接口)"""
        # 1. 优先调用 v3 predictions 接口
        try:
            resp = self._request("GET", f"/ws/api/v3/predictions/{task_id}/result")
            if resp.status_code == 200:
                res_json = resp.json()
                data = res_json.get("data", {})
                status = data.get("status", "")
                outputs = data.get("outputs", [])
                
                # 状态映射
                if status in ["succeeded", "completed"]:
                    return {"status": "succeed", "images": outputs, "msg": "生图渲染完成"}
                elif status in ["failed", "error"]:
                    return {"status": "failed", "images": [], "msg": data.get("error") or "任务渲染失败"}
                else:
                    return {"status": "processing", "images": [], "msg": "计算节点正在渲染中..."}
        except Exception:
            pass

        # 2. 兼容旧版 klingai fetch 接口
        try:
            resp = self._request("GET", f"/klingai/task/{task_id}/fetch")
            if resp.status_code == 200:
                res_json = resp.json()
                data = res_json.get("data", {})
                status = data.get("task_status") or str(data.get("status", ""))
                if status in ["99", "succeed", "success", "completed"]:
                    images = []
                    tr = data.get("task_result", {})
                    if "images" in tr:
                        images = [item.get("url") if isinstance(item, dict) else item for item in tr["images"]]
                    elif "outputs" in data:
                        images = data["outputs"]
                    return {"status": "succeed", "images": images, "msg": "生图渲染完成"}
                elif status in ["50", "failed", "error"]:
                    return {"status": "failed", "images": [], "msg": data.get("task_status_msg") or "任务失败"}
                else:
                    return {"status": "processing", "images": [], "msg": "排队渲染中..."}
        except Exception:
            pass

        return {"status": "processing", "images": [], "msg": "任务查询中..."}

    def poll_task(self, task_id: str, poll_interval: int = 5, timeout: int = 300) -> List[str]:
        """
        轮询可灵生图任务状态并获取生成图片的 URL 列表
        """
        print(f"[*] 开始轮询任务结果 (间隔 {poll_interval}s, 超时 {timeout}s)...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            res = self.fetch_task_result(task_id)
            status = res["status"]
            elapsed = int(time.time() - start_time)

            print(f"  [{elapsed:3d}s] 任务状态: {status} ({res.get('msg', '')})")

            if status == "succeed":
                image_urls = res.get("images", [])
                if not image_urls:
                    raise RuntimeError(f"任务标记成功，但未解析出图片链接: {res}")
                print(f"[🎉] 生图完成！共生成 {len(image_urls)} 张图片")
                return image_urls
            elif status == "failed":
                raise RuntimeError(f"可灵生图任务失败: {res.get('msg', '未知错误')}")

            time.sleep(poll_interval)

        raise TimeoutError(f"任务轮询超时 ({timeout} 秒)，任务可能仍在后台运行，Task ID: {task_id}")

    def download_images(self, urls: List[str], output_dir: str, filename_prefix: str = "kling_o3") -> List[str]:
        """下载生成的图片到本地"""
        os.makedirs(output_dir, exist_ok=True)
        saved_paths = []

        for i, url in enumerate(urls):
            ext = ".png"
            if ".jpg" in url.lower() or ".jpeg" in url.lower():
                ext = ".jpg"
            elif ".webp" in url.lower():
                ext = ".webp"

            out_filename = f"{filename_prefix}_{int(time.time())}_{i+1}{ext}" if len(urls) > 1 else f"{filename_prefix}_{int(time.time())}{ext}"
            out_path = os.path.join(output_dir, out_filename)

            print(f"[*] 正在下载图片 [{i+1}/{len(urls)}] -> {out_path} ...")
            img_resp = requests.get(url, timeout=60)
            if img_resp.status_code == 200:
                with open(out_path, "wb") as f:
                    f.write(img_resp.content)
                size_kb = os.path.getsize(out_path) / 1024
                print(f"[+] 下载完成: {out_path} ({size_kb:.1f} KB)")
                saved_paths.append(out_path)
            else:
                print(f"[!] 下载图片失败 (HTTP {img_resp.status_code}): {url}")

        return saved_paths

    def generate(
        self,
        prompt: str,
        images: Optional[Union[str, List[str]]] = None,
        aspect_ratio: str = "1:1",
        img_resolution: str = "1k",
        image_count: int = 1,
        story_mode: bool = False,
        output_dir: str = "./outputs",
        filename_prefix: str = "kling_o3"
    ) -> List[str]:
        """
        一站式端到端生图接口: 准备素材 -> 提交任务 -> 轮询结果 -> 下载保存
        """
        # 兼容单张参考图传入字符串格式
        img_list = None
        if images:
            if isinstance(images, str):
                img_list = [images]
            elif isinstance(images, list):
                img_list = images

        # 1. 提交任务
        task_id = self.submit_task(
            prompt=prompt,
            images=img_list,
            aspect_ratio=aspect_ratio,
            img_resolution=img_resolution,
            image_count=image_count,
            story_mode=story_mode
        )

        # 2. 轮询等待
        result_urls = self.poll_task(task_id)

        # 3. 下载图片
        saved_files = self.download_images(result_urls, output_dir=output_dir, filename_prefix=filename_prefix)
        return saved_files


def main():
    parser = argparse.ArgumentParser(description="302.ai 可灵图片 O3 (Kling Image O3) 生图脚本")
    parser.add_argument("--prompt", "-p", required=True, type=str, help="生图提示词 (Prompt)")
    parser.add_argument("--images", "-i", nargs="*", default=None, help="参考图路径或URL (可传1-10个，支持本地文件路径自动上传)")
    parser.add_argument("--aspect-ratio", "-ar", default="1:1",
                        choices=["auto", "9:16", "2:3", "3:4", "1:1", "4:3", "3:2", "16:9"],
                        help="画面宽高比，默认 1:1")
    parser.add_argument("--resolution", "-r", default="1k",
                        choices=["1k", "2k", "4k"],
                        help="图片画质分辨率 (1k/2k/4k)，默认 1k")
    parser.add_argument("--count", "-c", type=int, default=1, choices=[1, 2, 3, 4],
                        help="生成图片数量 (1-4)，默认 1")
    parser.add_argument("--output-dir", "-o", default="./outputs", help="图片保存目录，默认 ./outputs")
    parser.add_argument("--prefix", default="kling_o3", help="输出图片文件名前缀")
    parser.add_argument("--api-key", default=None, help="302.ai API Key (不传则默认读取环境变量)")
    parser.add_argument("--story-mode", action="store_true", help="是否开启组图模式 (默认 False)")

    args = parser.parse_args()

    client = KlingImageO3Client(api_key=args.api_key)
    print("=" * 65)
    print(" 🚀 302.ai 可灵图片 O3 生图任务启动")
    print("=" * 65)

    try:
        saved_files = client.generate(
            prompt=args.prompt,
            images=args.images,
            aspect_ratio=args.aspect_ratio,
            img_resolution=args.resolution,
            image_count=args.count,
            story_mode=args.story_mode,
            output_dir=args.output_dir,
            filename_prefix=args.prefix
        )
        print("=" * 65)
        print(" ✅ 全部完成！生成文件列表:")
        for f in saved_files:
            print(f"  -> {os.path.abspath(f)}")
        print("=" * 65)
    except Exception as e:
        print(f"\n❌ 执行失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

