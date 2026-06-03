from pathlib import Path
import shutil
import subprocess
import time

import yt_dlp


OUTPUT_DIR = Path(__file__).resolve().parent / "downloads"
QUALITY_CHOICES = {
    "1": 2160,
    "2": 1440,
    "3": 1080,
    "4": 720,
    "5": 480,
    "6": 360,
}
MODE_CHOICES = {
    "1": "all",
    "2": "merged",
    "3": "video",
    "4": "audio",
}
AUDIO_FORMAT_CHOICES = {
    "1": "mp3",
    "2": "wav",
}


def build_video_format(quality):
    if quality is None:
        return (
            "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
            "bestvideo+bestaudio/"
            "best[ext=mp4][vcodec!=none][acodec!=none]/"
            "best[vcodec!=none][acodec!=none]"
        )

    return (
        f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/"
        f"bestvideo[height<={quality}]+bestaudio/"
        f"best[height<={quality}][vcodec!=none][acodec!=none]"
    )


def build_video_only_format(quality):
    if quality is None:
        return "bestvideo[ext=mp4]/bestvideo"

    return f"bestvideo[height<={quality}][ext=mp4]/bestvideo[height<={quality}]"


def download_with_options(url, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def find_latest_output(pattern, started_at):
    matches = [
        path
        for path in OUTPUT_DIR.glob(pattern)
        if path.stat().st_mtime >= started_at - 1
    ]
    if not matches:
        return None
    return max(matches, key=lambda path: path.stat().st_mtime)


def has_audio_stream(file_path):
    if shutil.which("ffprobe") is None:
        return None

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            str(file_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return bool(result.stdout.strip())


def verify_merged_audio(started_at):
    merged_file = find_latest_output("*_merged.mp4", started_at)
    if merged_file is None:
        print("Could not find the merged output file to verify audio.")
        return

    audio_state = has_audio_stream(merged_file)
    if audio_state is None:
        print("Could not verify audio stream because ffprobe is unavailable.")
        return
    if not audio_state:
        raise RuntimeError(f"Merged file has no audio stream: {merged_file}")

    print(f"Audio stream verified: {merged_file.name}")


def make_common_options(output_suffix):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return {
        "outtmpl": str(OUTPUT_DIR / f"%(title)s_{output_suffix}.%(ext)s"),
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
    }


def download_merged_video(url, quality):
    started_at = time.time()
    ydl_opts = {
        **make_common_options("merged"),
        "format": build_video_format(quality),
        "merge_output_format": "mp4",
        "format_sort": ["res", "ext:mp4:m4a"],
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
    }
    download_with_options(url, ydl_opts)
    verify_merged_audio(started_at)


def download_video_only(url, quality):
    ydl_opts = {
        **make_common_options("video_only"),
        "format": build_video_only_format(quality),
        "merge_output_format": "mp4",
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
    }
    download_with_options(url, ydl_opts)


def download_audio_only(url, audio_format):
    ydl_opts = {
        **make_common_options("audio_only"),
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": "192",
            }
        ],
    }
    download_with_options(url, ydl_opts)


def choose_quality():
    print("\nSelect video quality.")
    print("0. Best available")
    print("1. Up to 2160p")
    print("2. Up to 1440p")
    print("3. Up to 1080p")
    print("4. Up to 720p")
    print("5. Up to 480p")
    print("6. Up to 360p")

    choice = input("Select [default: 3 = 1080p]: ").strip() or "3"
    if choice == "0":
        return None
    return QUALITY_CHOICES.get(choice, 1080)


def choose_mode():
    print("\nSelect output mode.")
    print("1. Create all: merged.mp4 + video_only.mp4 + audio_only")
    print("2. Merged video only")
    print("3. Video only")
    print("4. Audio only")

    choice = input("Select [default: 1 = create all]: ").strip() or "1"
    return MODE_CHOICES.get(choice, "all")


def choose_audio_format():
    print("\nSelect audio format.")
    print("1. mp3")
    print("2. wav")

    choice = input("Select [default: 1 = mp3]: ").strip() or "1"
    return AUDIO_FORMAT_CHOICES.get(choice, "mp3")


def download_youtube(url, quality, mode, audio_format):
    if mode in ("all", "merged"):
        print("\n[1/3] Downloading merged video.")
        download_merged_video(url, quality)

    if mode in ("all", "video"):
        print("\n[2/3] Downloading video only.")
        download_video_only(url, quality)

    if mode in ("all", "audio"):
        print("\n[3/3] Downloading audio only.")
        download_audio_only(url, audio_format)


def main():
    url = input("Enter YouTube video URL: ").strip()
    if not url:
        print("URL is empty.")
        return

    quality = choose_quality()
    mode = choose_mode()
    audio_format = choose_audio_format() if mode in ("all", "audio") else "mp3"

    print(f"\nOutput directory: {OUTPUT_DIR}")
    try:
        download_youtube(url, quality, mode, audio_format)
    except Exception as exc:
        print(f"\nError: {exc}")
        print("Please check that yt-dlp and ffmpeg are installed.")
        return

    print("\nDone.")


if __name__ == "__main__":
    main()
