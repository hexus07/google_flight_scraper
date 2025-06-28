from typing import Any
import asyncio


async def fetch_with_playwright(url: str) -> str:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--single-process",
                "--disable-dev-shm-usage",
                "--no-zygote",
                "--disable-setuid-sandbox",
                "--disable-accelerated-2d-canvas",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-client-side-phishing-detection",
                "--disable-component-update",
                "--disable-default-apps",
                "--disable-domain-reliability",
                "--disable-features=AudioServiceOutOfProcess",
                "--disable-hang-monitor",
                "--disable-ipc-flooding-protection",
                "--disable-popup-blocking",
                "--disable-prompt-on-repost",
                "--disable-renderer-backgrounding",
                "--disable-sync",
                "--force-color-profile=srgb",
                "--metrics-recording-only",
                "--mute-audio",
                "--no-pings",
                "--use-gl=swiftshader",
                "--window-size=1280,1696"
            ])
        

        # Accept cookies and navigate to the URL
        #await browser.cookies(url);
        page = await browser.new_page()
        await page.goto(url)
        if page.url.startswith("https://consent.google.com"):
            await page.click('text="Accept all"')
        
        # Taking locator
        locator = page.locator('.eQ35Ce')
        await locator.wait_for()

        # Buttons selector - for showing detailed flght info
        buttons = page.locator("div[jsname='IWWDBc'] ul.Rk10dc button[jsname='LgbsSe']")

        # Get the number of matched buttons
        count = await buttons.count()

        seen_labels = set()
        for i in range(count):
            button = buttons.nth(i)
            
            # Check if it's unique 
            aria_label = await button.get_attribute('aria-label')
            
            if aria_label not in seen_labels:
                #print(f"Button {i}: {aria_label}")
                seen_labels.add(aria_label)
                await button.scroll_into_view_if_needed()
                await button.dispatch_event('click')  
                #print(f"Button {i}: {await button.inner_text()}")
            else: break

        body = await locator.evaluate("element => element.innerHTML")
        
    return body

def local_playwright_fetch(params: dict) -> Any:
    url = "https://www.google.com/travel/flights?" + "&".join(f"{k}={v}" for k, v in params.items())
    body = asyncio.run(fetch_with_playwright(url))

    class DummyResponse:
        status_code = 200
        text = body
        text_markdown = body

    return DummyResponse
