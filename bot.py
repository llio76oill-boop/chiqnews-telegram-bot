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
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
REWRITE_STYLE = os.getenv("REWRITE_STYLE", "احترافي وموضوعي")
FOOTER_TEXT = os.getenv("FOOTER_TEXT", "تابعنا على @AjeelNewsIq")

# Groq API endpoint
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

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
    
    # Check for telegram links and mentions
    if re.search(r'@\w+|t\.me/\w+', text):
        return True
    
    return False

def replace_reporter_names(text: str) -> str:
    """Replace reporter names from other channels with 'مراسلنا'"""
    # List of reporter names to replace
    reporter_patterns = [
        (r'مراسل\s+الجزيرة', 'مراسلنا'),
        (r'مراسل\s+قناة\s+الجزيرة', 'مراسلنا'),
        (r'مراسل\s+العربي', 'مراسلنا'),
        (r'مراسل\s+قناة\s+العربي', 'مراسلنا'),
        (r'مراسل\s+الاخبار', 'مراسلنا'),
        (r'مراسل\s+قناة\s+الاخبار', 'مراسلنا'),
        (r'مراسل\s+\w+', 'مراسلنا'),  # Any other reporter
        (r'وفقا\s+ل(?:قناة)?\s+\w+', ''),  # Remove "وفقاً لـ"
        (r'حسب\s+(?:قناة)?\s+\w+', ''),  # Remove "حسب"
        (r'حسب\s+تقارير\s+\w+', ''),  # Remove "حسب تقارير"
    ]
    
    for pattern, replacement in reporter_patterns:
        text = re.sub(pattern, replacement, text)
    
    return text

def clean_text(text: str) -> str:
    """Clean text by removing common prefixes"""
    text = text.strip()
    
    # Replace reporter names first
    text = replace_reporter_names(text)
    
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

async def rewrite_text_with_groq(text: str) -> str:
    """Rewrite text using Groq API"""
    try:
        logger.info("✍️ جاري إعادة صياغة النص باستخدام Groq...")
        
        # Clean the text first
        text_to_rewrite = clean_text(text)
        
        if not text_to_rewrite:
            logger.warning("⚠️ النص فارغ بعد التنظيف")
            return text
        
        if not GROQ_API_KEY:
            logger.error("❌ GROQ_API_KEY غير موجود")
            return text_to_rewrite
        
        prompt = f"""أنت محرر أخبار محترف متخصص في إعادة صياغة الأخبار بأسلوب احترافي وأصلي وموضوعي.

أعد صياغة النص الإخباري التالي بأسلوب {REWRITE_STYLE} واحترافي وموضوعي وشامل. يجب أن تكون النتيجة:
- بالعربية الفصحى
- طويلة وتفصيلية
- أصلية وغير منقولة
- خالية من أسماء المصادر الأخرى

النص الأصلي:
{text_to_rewrite}

النص المعاد صياغته:"""
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",  # Fast and reliable model (currently supported)
            "messages": [
                {"role": "system", "content": "أنت محرر أخبار محترف متخصص في إعادة صياغة الأخبار بشكل احترافي وأصلي"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500,
            "top_p": 0.9
        }
        
        response = requests.post(
            GROQ_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                rewritten = result["choices"][0]["message"]["content"].strip()
                
                if rewritten:
                    logger.info("✨ تمت إعادة الصياغة بنجاح عبر Groq!")
                    return rewritten
                else:
                    logger.warning("⚠️ الرد من Groq فارغ")
                    return text_to_rewrite
            else:
                logger.warning(f"⚠️ رد غير متوقع من Groq: {result}")
                return text_to_rewrite
        else:
            logger.error(f"❌ خطأ من Groq: {response.status_code} - {response.text}")
            return text_to_rewrite
            
    except requests.exceptions.Timeout:
        logger.error("⏱️ انتهت مهلة الاتصال بـ Groq")
        return text
    except requests.exceptions.ConnectionError:
        logger.error("🔌 فشل الاتصال بـ Groq")
        return text
    except Exception as e:
        logger.error(f"❌ خطأ في إعادة الصياغة: {e}")
        return text

async def send_to_destination(text: str):
    """Send the rewritten text to the destination channel"""
    try:
        # Add red circle emoji and footer
        final_text = f"🔴 {text}\n\n{FOOTER_TEXT}"
        
        await client.send_message(DESTINATION_CHANNEL, final_text)
        logger.info(f"✅ تم الإرسال بنجاح إلى {DESTINATION_CHANNEL}!")
        
    except Exception as e:
        logger.error(f"❌ فشل الإرسال: {e}")

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handle_new_message(event):
    """Handle new messages from source channels"""
    try:
        text = event.message.text
        
        if not text:
            return
        
        logger.info(f"📨 رسالة جديدة من {event.chat_id}: {text[:100]}...")
        
        # Check if it's spam
        if is_spam(text):
            logger.info("🚫 تم تجاهل الرسالة (إعلان أو محتوى غير مرغوب)")
            return
        
        # Rewrite the text using Groq
        rewritten_text = await rewrite_text_with_groq(text)
        
        # Send to destination
        await send_to_destination(rewritten_text)
        
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الرسالة: {e}")

async def main():
    """Main function"""
    try:
        if not client:
            logger.error("❌ عميل Telegram غير متوفر")
            return
        
        logger.info("📱 استخدام جلسة موجودة...")
        
        await client.connect()
        
        logger.info("✅ جاري الاتصال بـ Telegram...")
        
        if await client.is_user_authorized():
            logger.info("✅ تم التفويض بنجاح!")
        else:
            logger.error("❌ فشل التفويض")
            return
        
        # Clean up source channels list
        source_channels_clean = [ch.strip() for ch in SOURCE_CHANNELS if ch.strip()]
        
        logger.info(f"👂 البوت يستمع للرسائل من: {', '.join(source_channels_clean)}")
        logger.info(f"📤 البوت سيرسل الرسائل إلى: {DESTINATION_CHANNEL}")
        logger.info(f"🤖 استخدام Groq API لإعادة الصياغة (مجاني وسريع)")
        logger.info("🚀 البوت جاهز للاستقبال...")
        
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"❌ خطأ في البوت: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
