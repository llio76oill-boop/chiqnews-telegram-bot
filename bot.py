'_# bot.py - Simple Telegram News Forwarder_
import os
import asyncio
from telethon import TelegramClient, events
import telegram
import openai
from dotenv import load_dotenv

# ------------------ 1. الإعدادات والتحميل ------------------ #
print("⏳ جاري تحميل الإعدادات...")
load_dotenv()

# --- تحميل متغيرات البيئة ---
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SOURCE_CHANNELS_STR = os.getenv("SOURCE_CHANNELS")
DESTINATION_CHANNEL = os.getenv("DESTINATION_CHANNEL")
REWRITE_STYLE = os.getenv("REWRITE_STYLE", "professional")

# --- التحقق من المتغيرات الأساسية ---
if not all([API_ID, API_HASH, PHONE, BOT_TOKEN, OPENAI_API_KEY, SOURCE_CHANNELS_STR, DESTINATION_CHANNEL]):
    print("❌ خطأ: يرجى ملء جميع المتغيرات في ملف .env")
    exit()

# --- تحويل القنوات إلى قائمة ---
SOURCE_CHANNELS = [channel.strip() for channel in SOURCE_CHANNELS_STR.split(',')]

# --- تهيئة المكتبات ---
print("🔌 جاري تهيئة المكتبات...")
client = TelegramClient("bot_session", int(API_ID), API_HASH)
bot = telegram.Bot(token=BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

print("✅ الإعدادات جاهزة.")

# ------------------ 2. دوال الذكاء الاصطناعي ------------------ #

async def rewrite_text_with_ai(text: str) -> str:
    """إعادة صياغة النص باستخدام OpenAI"""
    print(f"✍️ جاري إعادة صياغة النص: {text[:30]}...")
    prompt = f"""Rewrite the following news text in a professional and objective tone. The output must be in Arabic.\n\nOriginal Text:\n{text}\n\nRewritten Text:"""
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024,
        )
        rewritten = response.choices[0].message.content.strip()
        print("✨ تمت إعادة الصياغة بنجاح.")
        return rewritten
    except Exception as e:
        print(f"⚠️ فشلت إعادة الصياغة: {e}. سيتم استخدام النص الأصلي.")
        return text

# ------------------ 3. معالج الرسائل ------------------ #

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handle_new_message(event):
    """معالجة الرسائل الجديدة عند وصولها"""
    message = event.message
    original_text = message.text

    if not original_text:
        print("📄 رسالة بدون نص، سيتم تجاهلها.")
        return

    print(f"📩 رسالة جديدة من قناة: {message.chat.username}")

    # --- إعادة صياغة النص ---
    rewritten_text = await rewrite_text_with_ai(original_text)

    # --- إضافة رابط المصدر ---
    source_link = f"https://t.me/{message.chat.username}/{message.id}"
    final_text = f"{rewritten_text}\n\n<a href='{source_link}'>🔗 المصدر</a>"

    # --- إرسال الرسالة النهائية ---
    try:
        print(f"🚀 جاري إرسال الرسالة إلى {DESTINATION_CHANNEL}...")
        await bot.send_message(
            chat_id=DESTINATION_CHANNEL,
            text=final_text,
            parse_mode=telegram.ParseMode.HTML,
            disable_web_page_preview=True
        )
        print("✅ تم الإرسال بنجاح!")
    except Exception as e:
        print(f"❌ فشل إرسال الرسالة: {e}")

# ------------------ 4. نقطة البداية ------------------ #

async def main():
    """الدالة الرئيسية لتشغيل البوت"""
    print("▶️ جاري تشغيل البوت...")
    await client.start(phone=PHONE)
    print(f"👂 البوت يستمع الآن للرسائل من: {", ".join(SOURCE_CHANNELS)}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ValueError, TypeError) as e:
        # هذا الخطأ يحدث غالباً إذا كانت قيم API ID/Hash غير صحيحة
        print(f"❌ خطأ فادح في الإعدادات: {e}")
        print("   يرجى التأكد من أن قيم TELEGRAM_API_ID و TELEGRAM_API_HASH صحيحة في ملف .env")
    except Exception as e:
        print(f"🛑 توقف البوت بسبب خطأ غير متوقع: {e}")

print("👋 البوت توقف عن العمل.")
'
