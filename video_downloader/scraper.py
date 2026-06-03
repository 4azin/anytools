import asyncio
import re
from playwright.async_api import async_playwright, Page

SSAFY_LOGIN_URL = "https://edu.ssafy.com/comm/login/SecurityLoginForm.do"


async def login(page: Page, ssafy_id: str, ssafy_pw: str) -> bool:
    await page.goto(SSAFY_LOGIN_URL, wait_until="domcontentloaded")
    await page.wait_for_selector('input[name="userId"], input[id="userId"]', timeout=10000)
    await page.fill('input[name="userId"], input[id="userId"]', ssafy_id)
    await page.fill('input[name="userPwd"], input[id="userPwd"], input[type="password"]', ssafy_pw)

    clicked = False
    for sel in ['button[type="submit"]', '.btn-login', 'a.btn-login', 'input[type="submit"]', '.login-btn', '#loginBtn']:
        try:
            btn = page.locator(sel)
            if await btn.count() > 0:
                await btn.first.click()
                clicked = True
                break
        except Exception:
            pass
    if not clicked:
        await page.keyboard.press("Enter")

    await page.wait_for_load_state("networkidle")
    return "login" not in page.url.lower()


def _make_m3u8_listener(found_event: asyncio.Event):
    m3u8_holder = [None]

    def handle_request(request):
        req_url = request.url
        if ".m3u8" not in req_url or not req_url.startswith("http"):
            return
        if m3u8_holder[0] is None:
            m3u8_holder[0] = req_url
        # 마스터 플레이리스트가 오면 덮어쓰고 확정
        if any(k in req_url for k in ["master", "playlist", "index"]) and "/chunk" not in req_url:
            m3u8_holder[0] = req_url
        if not found_event.is_set():
            found_event.set()

    return handle_request, m3u8_holder


async def _wait_for_m3u8(page: Page, action, timeout: int = 30) -> str | None:
    """
    action()을 실행하기 전에 M3U8 리스너를 달고,
    action 후 M3U8이 잡힐 때까지 기다린다.
    """
    found_event = asyncio.Event()
    handler, holder = _make_m3u8_listener(found_event)
    page.on("request", handler)

    await action()

    try:
        await asyncio.wait_for(found_event.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        # autoplay가 막힌 경우 수동 클릭 시도
        for selector in ['.mpv-play-toggle-btn', '.mpv-osd-toggle']:
            try:
                btn = page.locator(selector)
                if await btn.count() > 0:
                    await btn.first.click()
                    await asyncio.wait_for(found_event.wait(), timeout=10)
                    break
            except Exception:
                pass

    page.remove_listener("request", handler)
    return holder[0]


async def get_lecture_title(page: Page) -> str:
    for selector in ['span.title', '.board-title', '.lect-title', 'h3.tit', 'h2.tit', '.view-tit', 'h3', 'h2']:
        try:
            el = page.locator(selector)
            if await el.count() > 0:
                text = (await el.first.inner_text()).strip()
                if text and len(text) < 200:
                    return text
        except Exception:
            pass
    seq = re.search(r'brdItmSeq=(\d+)', page.url)
    return f"lecture_{seq.group(1)}" if seq else "lecture_unknown"


async def has_next(page: Page) -> bool:
    return await page.locator('a:has-text("아랫글")').count() > 0


async def click_next(page: Page):
    """'아랫글' 클릭. full navigation이든 AJAX든 둘 다 처리."""
    btn = page.locator('a:has-text("아랫글")')
    try:
        async with page.expect_navigation(wait_until="domcontentloaded", timeout=8000):
            await btn.first.click()
    except Exception:
        # AJAX 방식 → navigation 이벤트 없이 콘텐츠만 교체됨
        await btn.first.click()
        await page.wait_for_timeout(2000)


async def crawl_lectures(
    ssafy_id: str,
    ssafy_pw: str,
    start_url: str,
    max_count: int = 100,
    headless: bool = False,
    on_found=None,
) -> list[dict]:
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        if not await login(page, ssafy_id, ssafy_pw):
            await browser.close()
            raise RuntimeError("로그인 실패: 아이디/비밀번호를 확인하세요.")

        # 첫 강의: goto로 이동하면서 M3U8 캡처
        m3u8_url = await _wait_for_m3u8(
            page,
            action=lambda: page.goto(start_url, wait_until="domcontentloaded"),
        )
        title = await get_lecture_title(page)
        entry = {"index": 1, "title": title, "m3u8_url": m3u8_url, "page_url": page.url}
        results.append(entry)
        if on_found:
            await on_found(entry)

        # 2번째부터: 아랫글 클릭으로 이동
        for i in range(1, max_count):
            if not await has_next(page):
                break

            m3u8_url = await _wait_for_m3u8(
                page,
                action=lambda: click_next(page),
            )
            title = await get_lecture_title(page)
            entry = {"index": i + 1, "title": title, "m3u8_url": m3u8_url, "page_url": page.url}
            results.append(entry)
            if on_found:
                await on_found(entry)

        await browser.close()

    return results
