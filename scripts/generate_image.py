#!/usr/bin/env python3
"""
302.ai Gemini Image Generation Tool
Model: gemini-3.1-flash-lite-image
Endpoint: /google/v1/models/gemini-3.1-flash-lite-image
"""

import argparse
import base64
import http.client
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

def get_api_key(api_key: str | None = None) -> str:
    if api_key and api_key.strip():
        return api_key.strip()
    key = (
        os.getenv("VIVIBON_302_IMAGE_API_KEY", "")
        or os.getenv("AI_302_API_KEY", "")
        or os.getenv("AI302_API_KEY", "")
    )
    if key:
        return key.strip()
    # Check .env in current and parent directories
    search_dirs = [
        Path.cwd(),
        Path(__file__).resolve().parent,
        Path(__file__).resolve().parents[1],
        Path(__file__).resolve().parents[2],
    ]
    for p in search_dirs:
        env_file = p / ".env"
        if env_file.exists():
            try:
                for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if line.startswith("AI_302_API_KEY="):
                        val = line.split("=", 1)[1].strip()
                        if val:
                            return val
                    elif line.startswith("VIVIBON_302_IMAGE_API_KEY="):
                        val = line.split("=", 1)[1].strip()
                        if val:
                            return val
            except Exception:
                pass
    return ""


DEFAULT_API_KEY = get_api_key()
API_HOST = "api.302.ai"
# Note: Do not use response_format=null as it causes 302.ai to discard image payload.
API_PATH = "/google/v1/models/gemini-3.1-flash-lite-image?response_format=b64_json"


def sanitize_filename(text: str, max_length: int = 40) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", text).strip().replace(" ", "_")
    return cleaned[:max_length] if cleaned else "image"


def parse_response_parts(response_json: dict) -> tuple[list[dict], list[str]]:
    """
    Extracts image payloads (either inline base64 or CDN URLs) and text parts.
    """
    images = []
    text_contents = []

    candidates = response_json.get("candidates", [])
    for candidate in candidates:
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        for part in parts:
            if "text" in part:
                text_contents.append(part["text"])

            inline_data = part.get("inlineData") or part.get("inline_data")
            if inline_data and "data" in inline_data:
                mime_type = inline_data.get("mimeType") or inline_data.get("mime_type", "image/jpeg")
                b64_data = inline_data["data"]
                images.append({"type": "base64", "mime_type": mime_type, "data": b64_data})

            if "url" in part:
                images.append({"type": "url", "url": part["url"]})

    return images, text_contents


def generate_image(
    prompt: str,
    api_key: str | None = None,
    image_paths: list[str | Path] | str | Path | None = None,
    negative_prompt: str | None = None,
    aspect_ratio: str = "4:3",
    output_dir: str | Path | None = None,
    filename_prefix: str | None = None,
    timeout: int = 120,
) -> list[Path]:
    resolved_key = get_api_key(api_key)
    if not resolved_key:
        raise ValueError("Missing API key. Set AI_302_API_KEY or supply via --key argument.")

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / "output"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    parts = []

    # Handle input/reference images if provided
    if image_paths:
        if isinstance(image_paths, (str, Path)):
            image_paths = [image_paths]
        for img_path_input in image_paths:
            img_path = Path(img_path_input).resolve()
            if not img_path.exists():
                raise FileNotFoundError(f"Input image not found: {img_path}")

            suffix = img_path.suffix.lower()
            mime_type = "image/jpeg"
            if suffix == ".png":
                mime_type = "image/png"
            elif suffix == ".webp":
                mime_type = "image/webp"

            img_bytes = img_path.read_bytes()
            b64_str = base64.b64encode(img_bytes).decode("utf-8")
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64_str,
                }
            })
            print(f"Attached reference image: {img_path.name} ({len(img_bytes)} bytes)")

    full_prompt = prompt.strip()
    if negative_prompt and negative_prompt.strip():
        full_prompt += f"\n\n[Negative Prompt / Elements to Avoid]:\n{negative_prompt.strip()}"

    parts.append({
        "text": full_prompt,
    })

    payload = {
        "contents": [
            {
                "parts": parts,
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
            },
        },
    }

    headers = {
        "Authorization": f"Bearer {resolved_key.strip()}",
        "Content-Type": "application/json",
    }

    print(f"Connecting to {API_HOST}...")
    print(f"Prompt: {prompt.strip()[:200]}...")
    if negative_prompt:
        print(f"Negative prompt: {negative_prompt.strip()[:100]}...")
    print(f"Aspect ratio: {aspect_ratio}")

    start_time = time.time()
    conn = http.client.HTTPSConnection(API_HOST, timeout=timeout)

    try:
        conn.request("POST", API_PATH, json.dumps(payload), headers)
        res = conn.getresponse()
        raw_data = res.read().decode("utf-8")
    finally:
        conn.close()

    elapsed = time.time() - start_time
    print(f"Response status: {res.status} {res.reason} (elapsed: {elapsed:.2f}s)")

    if res.status != 200:
        print(f"Error details: {raw_data}", file=sys.stderr)
        raise RuntimeError(f"HTTP {res.status}: {raw_data}")

    try:
        response_json = json.loads(raw_data)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse response JSON: {raw_data}") from exc

    images, text_parts = parse_response_parts(response_json)

    if text_parts:
        print("Model text response:")
        for t in text_parts:
            print(f"  {t.strip()}")

    if not images:
        print("No image payload found in response. Raw response dump:")
        print(json.dumps(response_json, indent=2, ensure_ascii=False))
        return []

    saved_paths = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_slug = sanitize_filename(filename_prefix or prompt)

    for idx, img_info in enumerate(images, 1):
        if img_info["type"] == "base64":
            mime_type = img_info.get("mime_type", "image/jpeg")
            ext = "jpg"
            if "png" in mime_type:
                ext = "png"
            elif "webp" in mime_type:
                ext = "webp"

            filename = f"{timestamp}_{prompt_slug}_{idx}.{ext}"
            out_file = output_dir / filename

            img_bytes = base64.b64decode(img_info["data"])
            with open(out_file, "wb") as f:
                f.write(img_bytes)

            print(f"Saved image ({len(img_bytes)} bytes): {out_file.resolve()}")
            saved_paths.append(out_file)

        elif img_info["type"] == "url":
            img_url = img_info["url"]
            ext = "jpg"
            if ".png" in img_url:
                ext = "png"
            elif ".webp" in img_url:
                ext = "webp"

            filename = f"{timestamp}_{prompt_slug}_{idx}.{ext}"
            out_file = output_dir / filename

            print(f"Downloading from URL: {img_url}")
            urllib.request.urlretrieve(img_url, out_file)
            file_size = out_file.stat().st_size
            print(f"Saved image ({file_size} bytes): {out_file.resolve()}")
            saved_paths.append(out_file)

    return saved_paths


def main():
    parser = argparse.ArgumentParser(description="Call 302.ai Gemini image generation model")
    parser.add_argument(
        "prompt_pos",
        nargs="?",
        help="Prompt text for generating the image (positional)",
    )
    parser.add_argument(
        "-p", "--prompt",
        dest="prompt_flag",
        help="Prompt text for generating the image (flag option)",
    )
    parser.add_argument(
        "-i", "--image",
        dest="images",
        action="append",
        help="Input reference image file path for image-to-image or editing (can specify multiple times)",
    )
    parser.add_argument(
        "-n", "--negative-prompt",
        default=None,
        help="Negative prompt / elements to avoid",
    )
    parser.add_argument(
        "-r", "--aspect-ratio",
        default="4:3",
        choices=["1:1", "3:4", "4:3", "9:16", "16:9"],
        help="Aspect ratio of the generated image (default: 4:3)",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=None,
        help="Target output directory (default: scripts/image_gen/output)",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Custom prefix for saved output filenames",
    )
    parser.add_argument(
        "-k", "--key",
        default=None,
        help="302.ai API key (overrides AI302_API_KEY environment variable and default key)",
    )

    args = parser.parse_args()

    prompt = args.prompt_flag or args.prompt_pos
    if not prompt:
        prompt = input("Enter prompt: ").strip()

    if not prompt:
        print("Error: Prompt cannot be empty.", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key(args.key)

    try:
        saved = generate_image(
            prompt=prompt,
            api_key=api_key,
            image_paths=args.images,
            negative_prompt=args.negative_prompt,
            aspect_ratio=args.aspect_ratio,
            output_dir=args.output_dir,
            filename_prefix=args.prefix,
        )
        if not saved:
            sys.exit(2)
        print(f"Generation successful. {len(saved)} image(s) created.")
    except Exception as err:
        print(f"Execution failed: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
