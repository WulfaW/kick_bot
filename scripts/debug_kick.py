import asyncio
import os
import json
from playwright.async_api import async_playwright

async def debug_kick():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="chrome", args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
        with open("cookies.json", "r", encoding="utf-8") as f:
            cookies = json.load(f)
        for c in cookies:
            if 'sameSite' in c and c['sameSite'] not in ['Strict', 'Lax', 'None']: del c['sameSite']
            if 'hostOnly' in c: del c['hostOnly']
            if 'session' in c: del c['session']
            if 'storeId' in c: del c['storeId']
            if 'partitionKey' in c: del c['partitionKey']
            if 'expirationDate' in c:
                c['expires'] = c['expirationDate']
                del c['expirationDate']
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        print("Navigating to Kick...")
        await page.goto("https://kick.com/wulfa")
        
        print("Waiting for 10 seconds for page to load...")
        await asyncio.sleep(10)
        
        print("Taking screenshot...")
        os.makedirs(r"C:\Users\trexg\.gemini\antigravity\brain\dd174a8f-fd62-4668-bd2d-438af3e596a1\scratch", exist_ok=True)
        await page.screenshot(path=r"C:\Users\trexg\.gemini\antigravity\brain\dd174a8f-fd62-4668-bd2d-438af3e596a1\scratch\kick_debug.png", full_page=True)
        
        print("Finding chat input...")
        inputs = await page.locator('div[contenteditable="true"]').count()
        print(f"Found {inputs} contenteditable divs.")
        
        await browser.close()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(debug_kick())
