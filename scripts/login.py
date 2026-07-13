import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

async def main():
    load_dotenv()
    kick_channel = os.getenv("KICK_CHANNEL", "")
    
    print("=====================================================")
    print("KICK BOT GİRİŞ İŞLEMİ (ONE-TIME SETUP)")
    print("=====================================================")
    print("1. Birazdan bir tarayıcı penceresi açılacak.")
    print("2. Kick.com açıldığında LÜTFEN KENDİ BOT HESABINIZLA GİRİŞ YAPIN.")
    print("3. Giriş yaptıktan ve sohbet ekranını gördükten sonra bu terminale gelip ENTER'a basın.")
    print("=====================================================")
    
    auth_file = "auth.json"

    async with async_playwright() as p:
        # Kick'in bot korumasını aşmak için normal Chrome'u kullanıyoruz
        browser = await p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await page.goto(f"https://kick.com/{kick_channel}")
        
        # Kullanıcının manuel olarak login olmasını bekle
        input("\n[BEKLENİYOR] Hesabınıza giriş yaptıktan sonra devam etmek için ENTER tuşuna basın...")

        # Oturum çerezlerini kaydet
        await context.storage_state(path=auth_file)
        print(f"\n[BAŞARILI] Oturum bilgileri '{auth_file}' dosyasına kaydedildi!")
        print("Artık bot arka planda bu oturumu kullanarak çalışabilir.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
