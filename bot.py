import os
import logging
import asyncio
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SOURCE_CHANNELS = [ch.strip() for ch in os.getenv("SOURCE_CHANNELS", "").split(",")]
DESTINATION_CHANNEL = os.getenv("DESTINATION_CHANNEL")
REWRITE_STYLE = os.getenv("REWRITE_STYLE", "professional")
SESSION_STRING = os.getenv("SESSION_STRING", "")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# Track processed messages to avoid duplicates
processed_messages = set()

def is_advertisement(text: str) -> bool:
    """Check if text is advertisement or unwanted content"""
    if not text:
        return False
    
    ad_keywords = [
        "اشترك",
        "subscribe",
        "تحميل",
        "download",
        "رابط",
        "link",
        "كود",
        "code",
        "حساب",
        "account",
        "دخول",
        "login",
        "تفعيل",
        "activate",
        "جرب مجاني",
        "free trial",
        "مجاني",
        "free",
    ]
    
    text_lower = text.lower()
    
    # Check for advertisement keywords
    for keyword in ad_keywords:
        if keyword in text_lower:
            return True
    
    # Check for URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    if re.search(url_pattern, text):
        return True
    
    # Check for telegram links and mentions
    if re.search(r'@\w+|t\.me/\w+', text):
        return True
    
    return False

async def rewrite_text_with_ai(text: str) -> str:
    """Rewrite text using OpenAI"""
    try:
        logger.info("✍️ جاري إعادة صياغة النص...")
        
        # Remove "عاجل" from the beginning if it exists
        text_to_rewrite = text.strip()
        if text_to_rewrite.startswith("عاجل"):
            text_to_rewrite = text_to_rewrite[4:].strip()
        if text_to_rewrite.startswith("|"):
            text_to_rewrite = text_to_rewrite[1:].strip()
        
        prompt = f"""أعد صياغة النص الإخباري التالي بأسلوب {REWRITE_STYLE} واحترافي وموضوعي. يجب أن تكون النتيجة بالعربية. لا تكرر كلمة 'عاجل' في البداية.
النص الأصلي:
{text_to_rewrite}

النص المعاد صياغته:"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024,
        )
        
        rewritten = response.choices[0].message.content.strip()
        logger.info("✨ تمت إعادة الصياغة بنجاح!")
        return rewritten
    except Exception as e:
        logger.warning(f"⚠️ فشلت إعادة الصياغة: {e}")
        return text

async def send_message_to_channel(client, text: str, channel: str):
    """Send message to Telegram channel"""
    try:
        # Remove @ if present
        channel_name = channel.lstrip('@')
        
        await client.send_message(
            channel_name,
            text,
            parse_mode='html',
            link_preview=False
        )
        logger.info(f"✅ تم الإرسال بنجاح إلى {channel}!")
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في الإرسال: {e}")
        return False

async def main():
    """Main function - connect and listen for messages"""
    
    # Create Telethon client
    if SESSION_STRING:
        # Use existing session
        client = TelegramClient(StringSession(SESSION_STRING), TELEGRAM_API_ID, TELEGRAM_API_HASH)
        logger.info("📱 استخدام جلسة موجودة...")
    else:
        # Create new session
        client = TelegramClient('session_name', TELEGRAM_API_ID, TELEGRAM_API_HASH)
        logger.info("📱 إنشاء جلسة جديدة...")
    
    async with client:
        # Connect and authenticate
        if not SESSION_STRING:
            logger.info("🔐 جاري تسجيل الدخول...")
            await client.start(phone=TELEGRAM_PHONE)
            
            # Get session string for future use
            session_string = client.session.save()
            logger.info(f"📝 SESSION_STRING: {session_string}")
            logger.info("⚠️ يرجى حفظ SESSION_STRING في متغيرات البيئة")
        
        logger.info("▶️ جاري تشغيل البوت...")
        logger.info(f"👂 البوت يستمع للرسائل من: {', '.join(SOURCE_CHANNELS)}")
        logger.info(f"📤 البوت سيرسل الرسائل إلى: {DESTINATION_CHANNEL}")
        
        @client.on(events.NewMessage(chats=SOURCE_CHANNELS))
        async def handle_new_message(event):
            """Handle new messages from source channels"""
            try:
                # Get message text
                text = event.message.text or ""
                
                # Skip if no text
                if not text:
                    logger.info("📄 رسالة بدون نص، سيتم تجاهلها.")
                    return
                
                # Get sender info
                sender = await event.get_sender()
                sender_name = sender.username or sender.first_name or "Unknown"
                
                logger.info(f"📩 رسالة جديدة من @{sender_name}: {text[:50]}...")
                
                # Create unique message identifier
                msg_key = f"{sender_name}_{event.message.id}"
                
                # Skip if already processed
                if msg_key in processed_messages:
                    logger.info("⏭️ تجاهل الرسالة - تم معالجتها مسبقاً")
                    return
                
                processed_messages.add(msg_key)
                
                # Check if it's an advertisement or unwanted content
                if is_advertisement(text):
                    logger.info(f"🚫 تجاهل الرسالة - إعلان أو محتوى غير مرغوب")
                    return
                
                # Rewrite text
                rewritten_text = await rewrite_text_with_ai(text)
                
                # Build final message with custom format
                final_text = f"<b>🔴 عاجل</b>\n\n{rewritten_text}\n\n<b>تابعنا لتكن أول بأول تعلم ما حولك</b>\n@AjeelNewsIq"
                
                # Send to destination
                await send_message_to_channel(client, final_text, DESTINATION_CHANNEL)
                
            except Exception as e:
                logger.error(f"❌ خطأ في معالجة الرسالة: {e}")
        
        # Keep the client running
        logger.info("🎯 البوت جاهز ويستقبل الرسائل...")
        await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 تم إيقاف البوت")
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
