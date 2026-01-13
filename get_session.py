import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")

async def main():
    """Get SESSION_STRING from Telegram"""
    
    # Create a StringSession
    session = StringSession()
    client = TelegramClient(session, TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    async with client:
        print("🔐 جاري تسجيل الدخول إلى Telegram...")
        print(f"📱 رقم الهاتف: {TELEGRAM_PHONE}")
        print()
        
        await client.start(phone=TELEGRAM_PHONE)
        
        # Get session string
        session_string = client.session.save()
        
        print()
        print("=" * 80)
        print("✅ تم الحصول على SESSION_STRING بنجاح!")
        print("=" * 80)
        print()
        print("📝 SESSION_STRING:")
        print(session_string)
        print()
        print("=" * 80)
        print("⚠️ يرجى نسخ SESSION_STRING أعلاه وإضافته إلى متغيرات البيئة في Render")
        print("=" * 80)
        
        # Save to file for reference
        if session_string:
            with open('/home/ubuntu/simple_bot/SESSION_STRING.txt', 'w') as f:
                f.write(session_string)
            print()
            print("✅ تم حفظ SESSION_STRING في SESSION_STRING.txt")
        else:
            print()
            print("⚠️ لم يتم الحصول على SESSION_STRING")

if __name__ == "__main__":
    asyncio.run(main())
