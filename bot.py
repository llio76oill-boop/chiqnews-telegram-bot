import os
import logging
import asyncio
import openai
import re
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SOURCE_CHANNELS = [ch.strip() for ch in os.getenv("SOURCE_CHANNELS", "").split(",")]
DESTINATION_CHANNEL = os.getenv("DESTINATION_CHANNEL")
REWRITE_STYLE = os.getenv("REWRITE_STYLE", "professional")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize Telegram Bot
bot = Bot(token=BOT_TOKEN)

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
        
        prompt = f"""أعد صياغة النص الإخباري التالي بأسلوب {REWRITE_STYLE} واحترافي وموضوعي. يجب أن تكون النتيجة بالعربية.
النص الأصلي:
{text}

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

async def send_message_to_channel(text: str, channel: str):
    """Send message to Telegram channel"""
    try:
        await bot.send_message(
            chat_id=channel,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        logger.info(f"✅ تم الإرسال بنجاح إلى {channel}!")
        return True
    except Exception as e:
        logger.error(f"❌ خطأ في الإرسال: {e}")
        return False

async def process_update(update):
    """Process a single update"""
    try:
        # Check if it's a channel post
        if not update.channel_post:
            return
        
        message = update.channel_post
        chat = message.chat
        chat_username = chat.username.strip().lower() if chat.username else ""
        message_id = message.message_id
        text = message.text or ""
        
        # Create unique message identifier
        msg_key = f"{chat_username}_{message_id}"
        
        # Skip if already processed
        if msg_key in processed_messages:
            return
        
        processed_messages.add(msg_key)
        
        # Skip if no text
        if not text:
            logger.info("📄 رسالة بدون نص، سيتم تجاهلها.")
            return
        
        logger.info(f"📩 رسالة جديدة من @{chat_username}: {text[:50]}...")
        
        # Check if from source channels
        is_from_source = False
        for source_channel in SOURCE_CHANNELS:
            if source_channel.lower() in chat_username:
                is_from_source = True
                break
        
        if not is_from_source:
            logger.info(f"⏭️ تجاهل الرسالة - ليست من قنوات المصادر")
            return
        
        # Check if it's an advertisement or unwanted content
        if is_advertisement(text):
            logger.info(f"🚫 تجاهل الرسالة - إعلان أو محتوى غير مرغوب")
            return
        
        # Rewrite text
        rewritten_text = await rewrite_text_with_ai(text)
        
        # Build final message with custom format
        final_text = f"<b><span style='color: red;'>🔴 عاجل</span></b>\n\n{rewritten_text}\n\n<b>تابعنا لتكن أول بأول تعلم ما حولك</b>\n@AjeelNewsIq"
        
        # Send to destination
        await send_message_to_channel(final_text, DESTINATION_CHANNEL)
        
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة التحديث: {e}")

async def main():
    """Main function - start polling for updates"""
    logger.info("▶️ جاري تشغيل البوت...")
    logger.info(f"👂 البوت يستمع للرسائل من: {', '.join(SOURCE_CHANNELS)}")
    logger.info(f"📤 البوت سيرسل الرسائل إلى: {DESTINATION_CHANNEL}")
    
    offset = 0
    
    while True:
        try:
            # Get updates from Telegram
            updates = await bot.get_updates(offset=offset, timeout=30)
            
            if updates:
                logger.info(f"📨 استقبال {len(updates)} تحديث(ات)")
                
                for update in updates:
                    await process_update(update)
                    offset = update.update_id + 1
            
            # Keep the connection alive
            await asyncio.sleep(1)
            
        except TelegramError as e:
            logger.error(f"❌ خطأ Telegram: {e}")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"❌ خطأ غير متوقع: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
