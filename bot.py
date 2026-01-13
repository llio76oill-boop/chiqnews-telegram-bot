import os
import re
import logging
import asyncio
import requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# Get environment variables
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")
SOURCE_CHANNELS = os.getenv("SOURCE_CHANNELS", "").split(",")
DESTINATION_CHANNEL = os.getenv("DESTINATION_CHANNEL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
REWRITE_STYLE = os.getenv("REWRITE_STYLE", "احترافي وموضوعي")
FOOTER_TEXT = os.getenv("FOOTER_TEXT", "تابعنا على @AjeelNewsIq")

# OpenAI API endpoint
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Initialize Telegram client
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), TELEGRAM_API_ID, TELEGRAM_API_HASH)
else:
    logger.error("❌ SESSION_STRING غير موجود! يجب تعيين SESSION_STRING في متغيرات البيئة!")
    client = None

def is_spam(text: str) -> bool:
    """Check if text is spam or advertisement"""
    spam_keywords = [
        "اشترك", "تابع", "لايك", "شير", "كومنت", "اضغط", "رابط",
        "موقع", "تطبيق", "تحميل", "إعلان", "عرض", "خصم", "سعر"
    ]
    
    text_lower = text.lower()
    for keyword in spam_keywords:
        if keyword in text_lower:
            return True
    
    # Check for URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    if re.search(url_pattern, text):
        return True
    
    return False

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove prefixes
    text = re.sub(r'^(عاجل|🔴|⚠️|📢|🚨)\s*\|\s*', '', text)
    text = re.sub(r'^(عاجل|🔴|⚠️|📢|🚨)\s*', '', text)
    
    # Remove reporter names and replace with "مراسلنا"
    reporter_patterns = [
        r'(مراسل|مراسلة|مراسلنا|مراسليك|مراسل\w+)',
        r'(من\s+\w+)',
    ]
    
    for pattern in reporter_patterns:
        text = re.sub(pattern, 'مراسلنا', text, flags=re.IGNORECASE)
    
    # Clean extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def rewrite_text_with_openai(text: str) -> str:
    """Rewrite text using OpenAI API"""
    if not OPENAI_API_KEY:
        logger.warning("⚠️ OpenAI API Key غير موجود!")
        return clean_text(text)
    
    try:
        logger.info("✍️ جاري إعادة صياغة النص باستخدام OpenAI...")
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "أنت محرر أخبار محترف متخصص في إعادة صياغة الأخبار بشكل احترافي وأصلي وموضوعي"},
                {"role": "user", "content": f"أعد صياغة هذا الخبر بشكل احترافي وأصلي:\n\n{text}"}
            ],
            "temperature": 0.7,
            "max_tokens": 500,
            "top_p": 0.9
        }
        
        response = requests.post(
            OPENAI_API_URL,
            json=payload,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            rewritten = result['choices'][0]['message']['content'].strip()
            logger.info("✨ تمت إعادة الصياغة بنجاح!")
            return rewritten
        else:
            logger.warning(f"⚠️ خطأ من OpenAI: {response.status_code} - {response.text}")
            return clean_text(text)
            
    except Exception as e:
        logger.error(f"❌ خطأ في إعادة الصياغة: {e}")
        return clean_text(text)

async def process_message(message):
    """Process and forward message"""
    try:
        text = message.text
        
        if not text or is_spam(text):
            logger.info("🚫 تم تجاهل الرسالة (إعلان أو محتوى غير مرغوب)")
            return
        
        logger.info(f"📨 رسالة جديدة: {text[:50]}...")
        
        # Rewrite text
        rewritten_text = rewrite_text_with_openai(text)
        
        # Add prefix and footer
        final_text = f"🔴 {rewritten_text}\n\n{FOOTER_TEXT}"
        
        # Send to destination
        await client.send_message(DESTINATION_CHANNEL, final_text)
        logger.info("✅ تم الإرسال بنجاح إلى @AjeelNewsIq!")
        
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الرسالة: {e}")

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    """Handle new messages from source channels"""
    await process_message(event.message)

async def main():
    """Main function"""
    if not client:
        logger.error("❌ لم يتم تهيئة Telegram client!")
        return
    
    try:
        logger.info("✅ جاري الاتصال بـ Telegram...")
        await client.connect()
        logger.info("✅ تم التفويض بنجاح!")
        
        logger.info(f"👂 البوت يستمع للرسائل من: {', '.join(SOURCE_CHANNELS)}")
        logger.info(f"📤 البوت سيرسل الرسائل إلى: {DESTINATION_CHANNEL}")
        logger.info("🤖 استخدام OpenAI API لإعادة الصياغة")
        logger.info("🚀 البوت جاهز للاستقبال...")
        
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
