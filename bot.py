#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import re
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

# إعداد السجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# البيانات من متغيرات البيئة
TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID', ''))
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH', '')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE', '')
SOURCE_CHANNELS = os.getenv('SOURCE_CHANNELS', 'AjaNews,llio76ioll,AlarabyTvBrk').split(',')
DESTINATION_CHANNEL = os.getenv('DESTINATION_CHANNEL', '@AjeelNewsIq')
SESSION_STRING = os.getenv('SESSION_STRING', '')

# إنشاء العميل باستخدام StringSession لتجنب مشاكل قاعدة البيانات
if SESSION_STRING:
    session = StringSession(SESSION_STRING)
else:
    session = StringSession()  # جلسة جديدة

client = TelegramClient(session, TELEGRAM_API_ID, TELEGRAM_API_HASH)

def clean_text(text):
    """تنظيف النص من الرموز الزائدة"""
    # إزالة الرموز الخاصة الزائدة
    text = re.sub(r'[^\w\s\u0600-\u06FF\.\,\!\?\-\(\)\:\;]', '', text)
    # إزالة المسافات الزائدة
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def rewrite_text(text):
    """
    إعادة صياغة النص باستخدام معالجة محلية متقدمة
    """
    try:
        # تنظيف النص
        text = clean_text(text)
        
        # تقسيم النص إلى جمل
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # معالجة كل جملة
        processed_sentences = []
        for sentence in sentences:
            if len(sentence.strip()) > 0:
                # إزالة الكلمات المكررة
                words = sentence.split()
                unique_words = []
                for word in words:
                    if word not in unique_words or len(unique_words) < 3:
                        unique_words.append(word)
                
                # إعادة بناء الجملة
                processed_sentence = ' '.join(unique_words)
                
                # إضافة علامات ترقيم إذا لزم الأمر
                if not processed_sentence.endswith(('.', '!', '?')):
                    processed_sentence += '.'
                
                processed_sentences.append(processed_sentence)
        
        # دمج الجمل المعاد صياغتها
        rewritten = ' '.join(processed_sentences)
        
        logger.info("✨ تمت إعادة الصياغة بنجاح محلياً!")
        return rewritten
    
    except Exception as e:
        logger.warning(f"⚠️ خطأ في إعادة الصياغة: {e}")
        return text

def replace_reporter_names(text):
    """استبدال أسماء المراسلين بـ 'مراسلنا'"""
    # قائمة الأنماط الشائعة لأسماء المراسلين
    patterns = [
        r'مراسل\s+\w+',
        r'مراسلتنا\s+\w+',
        r'مراسلنا\s+\w+',
        r'المراسل\s+\w+',
        r'المراسلة\s+\w+',
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, 'مراسلنا', text)
    
    return text

def is_advertisement(text):
    """التحقق من أن النص ليس إعلاناً"""
    ad_keywords = [
        'اشتري', 'اشترِ', 'شراء', 'عرض خاص', 'خصم', 'توفير',
        'اتصل الآن', 'اطلب الآن', 'اضغط هنا', 'رابط', 'لينك',
        'تطبيق', 'تحميل', 'download', 'app', 'click',
        'إعلان', 'sponsore', 'promoted', 'iklan'
    ]
    
    text_lower = text.lower()
    for keyword in ad_keywords:
        if keyword in text_lower:
            return True
    
    return False

async def process_message(event):
    """معالجة الرسالة الواردة"""
    try:
        # الحصول على النص
        text = event.message.text
        
        if not text:
            return
        
        logger.info(f"📨 رسالة جديدة: {text[:50]}...")
        
        # التحقق من أنها ليست إعلاناً
        if is_advertisement(text):
            logger.info("🚫 تم تجاهل الرسالة (إعلان)")
            return
        
        # إعادة صياغة النص
        logger.info("✍️ جاري إعادة صياغة النص محلياً...")
        rewritten_text = rewrite_text(text)
        
        # استبدال أسماء المراسلين
        rewritten_text = replace_reporter_names(rewritten_text)
        
        # إضافة البادئة والخاتمة
        final_text = f"🔴 {rewritten_text}\n\nتابعنا على @AjeelNewsIq"
        
        # إرسال الرسالة
        await client.send_message(DESTINATION_CHANNEL, final_text)
        logger.info("✅ تم الإرسال بنجاح إلى @AjeelNewsIq!")
    
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الرسالة: {e}")

async def main():
    """الدالة الرئيسية"""
    try:
        # الاتصال بـ Telegram
        logger.info("✅ جاري الاتصال بـ Telegram...")
        await client.start(phone=TELEGRAM_PHONE)
        logger.info("✅ تم التفويض بنجاح!")
        
        # تسجيل المستمعين
        logger.info(f"👂 البوت يستمع للرسائل من: {', '.join(SOURCE_CHANNELS)}")
        logger.info(f"📤 البوت سيرسل الرسائل إلى: {DESTINATION_CHANNEL}")
        logger.info("🤖 استخدام معالجة نصية محلية متقدمة لإعادة الصياغة")
        logger.info("🚀 البوت جاهز للاستقبال...")
        
        # إضافة معالج الأحداث لكل قناة
        for channel in SOURCE_CHANNELS:
            channel = channel.strip()
            @client.on(events.NewMessage(chats=channel))
            async def handler(event):
                await process_message(event)
        
        # الاستماع للرسائل
        await client.run_until_disconnected()
    
    except SessionPasswordNeededError:
        logger.error("❌ كلمة المرور مطلوبة!")
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
