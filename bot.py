import os
import logging
import asyncio
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import openai

from dotenv import load_dotenv
# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNELS = [ch.strip() for ch in os.getenv("SOURCE_CHANNELS", "").split(",")]
DESTINATION_CHANNEL = os.getenv("DESTINATION_CHANNEL")
FOOTER_TEXT = os.getenv("FOOTER_TEXT", "")

# Initialize OpenAI client (using Manus API)
import openai
if not OPENAI_API_KEY:
    logger.error("❌ OPENAI_API_KEY not found in environment variables!")
    exit(1)
openai.api_key = OPENAI_API_KEY


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

def clean_text(text: str) -> str:
    """Clean text by removing common prefixes"""
    text = text.strip()
    
    # Remove "عاجل" and variations
    if text.startswith("عاجل"):
        text = text[4:].strip()
    
    # Remove red circle emoji
    if text.startswith("🔴"):
        text = text[1:].strip()
    
    # Remove pipes and separators
    if text.startswith("|"):
        text = text[1:].strip()
    
    return text

async def rewrite_text_with_ai(text: str) -> str:
    """Rewrite text using OpenAI (Manus API)"""
    try:
        logger.info("✍️ جاري إعادة صياغة النص...")
        
        # Clean the text first
        text_to_rewrite = clean_text(text)
        
        if not text_to_rewrite:
            logger.warning("⚠️ النص فارغ بعد التنظيف")
            return text
        
        prompt = f"""أعد صياغة النص الإخباري التالي بأسلوب {REWRITE_STYLE} واحترافي وموضوعي وشامل. يجب أن تكون النتيجة بالعربية وطويلة وتفصيلية.

النص الأصلي:
{text_to_rewrite}

النص المعاد صياغته:"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "أنت محرر أخبار احترافي متخصص في إعادة صياغة الأخبار بأسلوب احترافي وموضوعي."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        rewritten = response.choices[0].message.content.strip()
        
        if rewritten:
            logger.info("✨ تمت إعادة الصياغة بنجاح!")
            return rewritten
        else:
            logger.warning("⚠️ الرد من OpenAI فارغ")
            return text_to_rewrite
            
    except Exception as e:
        logger.error(f"❌ فشلت إعادة الصياغة: {e}")
        return text

async def send_message_to_channel(client, text: str, channel: str):
    """Send message to Telegram channel"""
    try:
        # Remove @ if present
        channel_name = channel.lstrip('@')
        
        # Build final message with red emoji and footer
        final_text = f"🔴 {text}"
        
        if FOOTER_TEXT:
            final_text += f"\n\n{FOOTER_TEXT}"
        
        await client.send_message(
            channel_name,
            final_text,
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
        
        logger.info(f"👂 البوت يستمع للرسائل من: {', '.join(SOURCE_CHANNELS)}")
        logger.info(f"📤 البوت سيرسل الرسائل إلى: {DESTINATION_CHANNEL}")
        logger.info("🤖 استخدام OpenAI API (Manus) لإعادة الصياغة")
        
        @client.on(events.NewMessage(chats=SOURCE_CHANNELS))
        async def handle_new_message(event):
            """Handle new messages from source channels"""
            try:
                message_text = event.message.text
                
                # Skip if no text
                if not message_text:
                    return
                
                message_id = event.message.id
                
                # Skip if already processed
                if message_id in processed_messages:
                    return
                
                processed_messages.add(message_id)
                
                logger.info(f"📨 رسالة جديدة من {event.chat_id}: {message_text[:100]}...")
                
                # Skip if it's an advertisement
                if is_advertisement(message_text):
                    logger.info(f"🚫 تم تجاهل إعلان: {message_text[:50]}...")
                    return
                
                # Rewrite the message
                rewritten_message = await rewrite_text_with_ai(message_text)
                
                # Send to destination channel
                await send_message_to_channel(client, rewritten_message, DESTINATION_CHANNEL)
                
            except Exception as e:
                logger.error(f"❌ خطأ في معالجة الرسالة: {e}")
        
        # Keep the client running
        logger.info("🚀 البوت جاهز للاستقبال...")
        await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
