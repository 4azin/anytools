import subprocess
import os
import re
from pathlib import Path


def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip()


def download_hls(m3u8_url: str, output_path: str, headers: dict | None = None) -> bool:
    """ffmpeg로 HLS 스트림을 MP4로 다운로드"""
    cmd = ["ffmpeg", "-y"]

    if headers:
        for key, value in headers.items():
            cmd += ["-headers", f"{key}: {value}"]

    cmd += [
        "-i", m3u8_url,
        "-c", "copy",
        "-bsf:a", "aac_adtstoasc",
        "-movflags", "+faststart",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode == 0


def download_lecture(m3u8_url: str, title: str, output_dir: str = "./downloads") -> str | None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(title) + ".mp4"
    output_path = os.path.join(output_dir, filename)

    success = download_hls(m3u8_url, output_path)
    return output_path if success else None
