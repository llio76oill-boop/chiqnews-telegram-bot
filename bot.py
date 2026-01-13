import os
import logging
import asyncio
import aiohttp
import openai
import re
from flask import Flask, request
from threading import Thread
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SOURCE_CHANNELS = [ch.strip() for ch in os.getenv("SOURCE_CHANNELS", "").split(",")]
DESTINATION_CHANNEL = os.getenv("DESTINATION_CHANNEL")
REWRITE_STYLE = os.getenv("REWRITE_STYLE", "professional")
PORT = int(os.getenv("PORT", 5000))

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize Flask
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# Telegram API URLs
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
TELEGRAM_SEND_MESSAGE_URL = f"{TELEGRAM_API_URL}/sendMessage"
TELEGRAM_SET_WEBHOOK_URL = f"{TELEGRAM_API_URL}/setWebhook"
TELEGRAM_GET_WEBHOOK_INFO_URL = f"{TELEGRAM_API_URL}/getWebhookInfo"

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
        payload = {
            "chat_id": channel,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(TELEGRAM_SEND_MESSAGE_URL, json=payload) as response:
                if response.status == 200:
                    logger.info(f"✅ تم الإرسال بنجاح إلى {channel}!")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ فشل الإرسال: {error_text}")
                    return False
    except Exception as e:
        logger.error(f"❌ خطأ في الإرسال: {e}")
        return False

def process_update_async(update: dict):
    """Process update in a separate thread"""
    try:
        if "channel_post" not in update:
            return
        
        message = update["channel_post"]
        chat = message.get("chat", {})
        chat_username = chat.get("username", "").strip().lower()
        message_id = message.get("message_id")
        text = message.get("text", "").strip()
        
        # Skip if no text
        if not text:
            logger.info("📄 رسالة بدون نص، سيتم تجاهلها.")
            return
        
        logger.info(f"📩 رسالة جديدة من @{chat_username}")
        
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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        rewritten_text = loop.run_until_complete(rewrite_text_with_ai(text))
        
        # Build final message with custom format
        # Add "عاجل" in red at the beginning
        final_text = f"<b><span style='color: red;'>🔴 عاجل</span></b>\n\n{rewritten_text}\n\n<b>تابعنا لتكن أول بأول تعلم ما حولك</b>\n@AjeelNewsIq"
        
        # Send to destination
        loop.run_until_complete(send_message_to_channel(final_text, DESTINATION_CHANNEL))
        
        loop.close()
        
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة التحديث: {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    """Webhook endpoint for Telegram updates"""
    try:
        update = request.get_json()
        
        # Process update in background thread
        thread = Thread(target=process_update_async, args=(update,))
        thread.daemon = True
        thread.start()
        
        return {"ok": True}, 200
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الـ webhook: {e}")
        return {"ok": False}, 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return {"status": "ok"}, 200

if __name__ == "__main__":
    logger.info("▶️ جاري تشغيل البوت...")
    logger.info(f"👂 البوت يستمع للرسائل من: {', '.join(SOURCE_CHANNELS)}")
    logger.info(f"📤 البوت سيرسل الرسائل إلى: {DESTINATION_CHANNEL}")
    
    # Run Flask app
    app.run(host="0.0.0.0", port=PORT, debug=False)
