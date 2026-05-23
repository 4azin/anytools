from pathlib import Path

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
        return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"

    return (
        f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/"
        f"bestvideo[height<={quality}]+bestaudio/"
        f"best[height<={quality}]"
    )


def build_video_only_format(quality):
    if quality is None:
        return "bestvideo[ext=mp4]/bestvideo"

    return f"bestvideo[height<={quality}][ext=mp4]/bestvideo[height<={quality}]"


def download_with_options(url, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def make_common_options(output_suffix):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return {
        "outtmpl": str(OUTPUT_DIR / f"%(title)s_{output_suffix}.%(ext)s"),
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
    }


def download_merged_video(url, quality):
    ydl_opts = {
        **make_common_options("merged"),
        "format": build_video_format(quality),
        "merge_output_format": "mp4",
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
    }
    download_with_options(url, ydl_opts)


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
