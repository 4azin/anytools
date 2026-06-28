#!/usr/bin/env python3
"""에듀싸피 강의 자동 다운로드 도구"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.table import Table

from scraper import crawl_lectures
from downloader import download_lecture

load_dotenv()
console = Console()


def get_credentials() -> tuple[str, str]:
    ssafy_id = os.getenv("SSAFY_ID") or Prompt.ask("[bold]에듀싸피 아이디[/]")
    ssafy_pw = os.getenv("SSAFY_PW") or Prompt.ask("[bold]에듀싸피 비밀번호[/]", password=True)
    return ssafy_id, ssafy_pw


async def main():
    console.print(Panel.fit(
        "[bold cyan]에듀싸피 강의 자동 다운로더[/]\n"
        "강의 페이지에서 시작해 '아랫글'을 따라가며 연속 다운로드합니다.",
        border_style="cyan"
    ))

    ssafy_id, ssafy_pw = get_credentials()
    output_dir = os.getenv("DOWNLOAD_DIR", "./downloads")

    start_url = Prompt.ask("\n[bold]시작할 강의 URL[/]").strip()
    max_count = IntPrompt.ask("[bold]최대 다운로드 강의 수[/]", default=50)

    os.makedirs(output_dir, exist_ok=True)

    console.print(f"\n[dim]저장 폴더: {os.path.abspath(output_dir)}[/]")
    console.print(f"[dim]Headless 브라우저로 로그인 후 강의를 순서대로 다운로드합니다.[/]\n")

    downloaded = 0
    failed = 0

    async def on_lecture_found(entry: dict):
        nonlocal downloaded, failed
        idx = entry["index"]
        title = entry["title"]
        m3u8 = entry["m3u8_url"]

        console.rule(f"[bold magenta]강의 {idx}[/]")
        console.print(f"  제목: [cyan]{title}[/]")

        if not m3u8:
            console.print("  [red]✗ 스트림 URL을 찾지 못했습니다.[/]")
            failed += 1
            return

        console.print(f"  스트림: [dim]{m3u8[:70]}...[/]")
        console.print("  [yellow]다운로드 중...[/]")
        path = download_lecture(m3u8, title, output_dir)
        if path:
            console.print(f"  [green]✓ 저장됨:[/] {path}")
            downloaded += 1
        else:
            console.print("  [red]✗ ffmpeg 다운로드 실패[/]")
            failed += 1

    try:
        await crawl_lectures(
            ssafy_id=ssafy_id,
            ssafy_pw=ssafy_pw,
            start_url=start_url,
            max_count=max_count,
            headless=False,
            on_found=on_lecture_found,
        )
    except RuntimeError as e:
        console.print(f"\n[bold red]오류:[/] {e}")
        sys.exit(1)

    # 결과 요약
    table = Table(title="\n완료 요약")
    table.add_column("항목", style="cyan")
    table.add_column("수", justify="right")
    table.add_row("성공", f"[green]{downloaded}[/]")
    table.add_row("실패", f"[red]{failed}[/]")
    table.add_row("저장 위치", output_dir)
    console.print(table)


if __name__ == "__main__":
    asyncio.run(main())
