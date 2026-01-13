#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
بوت معالجة الأخبار المتقدم
Advanced News Processing Bot with Smart Filtering and Professional Rewriting
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from filter_module import SmartFilter
from rewrite_module import AdvancedRewriter
from openai_rewrite_module import OpenAIRewriter

# ============================================================================
# إعداد السجلات
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# متغيرات البيئة
# ============================================================================

TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH', '')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE', '')
SESSION_STRING = os.getenv('SESSION_STRING', '')
SOURCE_CHANNELS = [ch.strip() for ch in os.getenv('SOURCE_CHANNELS', 'AjaNews,llio76ioll,AlarabyTvBrk').split(',')]
DESTINATION_CHANNEL = os.getenv('DESTINATION_CHANNEL', '@AjeelNewsIq')
REWRITE_STYLE = os.getenv('REWRITE_STYLE', 'professional')

# ============================================================================
# نظام الأولويات
# ============================================================================

# قائمة الأولويات (من الأعلى إلى الأقل)
CHANNEL_PRIORITIES = {
    'AjaNews': 1,           # الأولوية الأولى (الأعلى)
    'AlarabyTvBrk': 2,      # الأولوية الثانية
    'llio76ioll': 3         # الأولوية الثالثة (الأقل)
}

def get_channel_priority(channel_name):
    """الحصول على أولوية القناة"""
    return CHANNEL_PRIORITIES.get(channel_name, 999)  # 999 للقنوات غير المعروفة

# ============================================================================
# تهيئة المكونات
# ============================================================================

filter_system = SmartFilter()
rewriter = AdvancedRewriter()
openai_rewriter = OpenAIRewriter()  # نظام الصياغة عبر OpenAI
stored_texts = []  # لتخزين النصوص المعالجة

# إنشاء عميل Telegram باستخدام StringSession
if SESSION_STRING:
    session = StringSession(SESSION_STRING)
else:
    session = StringSession()

client = TelegramClient(session, TELEGRAM_API_ID, TELEGRAM_API_HASH)

# ============================================================================
# دوال المعالجة
# ============================================================================

def process_message(text: str) -> dict:
    """
    معالجة شاملة للرسالة
    
    Returns:
        {
            'passed': bool,
            'original': str,
            'rewritten': str,
            'filter_result': dict,
            'rewrite_stats': dict,
            'errors': [str]
        }
    """
    errors = []
    
    try:
        # 1. الفلترة الذكية
        logger.info("🔍 جاري فحص الرسالة...")
        filter_result = filter_system.filter_text(text, stored_texts)
        
        if not filter_result['passed']:
            logger.warning(f"❌ الرسالة لم تمر الفلترة:")
            for reason in filter_result['reasons']:
                logger.warning(f"   {reason}")
            
            return {
                'passed': False,
                'original': text,
                'rewritten': None,
                'filter_result': filter_result,
                'rewrite_stats': None,
                'errors': filter_result['reasons']
            }
        
        logger.info(f"✅ الرسالة موثوقة: {filter_result['reasons'][0]}")
        
        # 2. إعادة الصياغة
        logger.info("✍️ جاري إعادة صياغة النص...")
        
        # محاولة استخدام OpenAI API أولاً
        rewritten, openai_success = openai_rewriter.rewrite(text, style=REWRITE_STYLE)
        
        # إذا فشل OpenAI، استخدم النظام المحلي
        if not openai_success:
            logger.info("⚠️ استخدام نظام الصياغة المحلي كـ fallback...")
            rewritten = rewriter.rewrite(text, style=REWRITE_STYLE)
        
        # 3. حساب الإحصائيات
        rewrite_stats = rewriter.get_rewrite_stats(text, rewritten)
        
        logger.info(f"📊 إحصائيات الصياغة:")
        logger.info(f"   - نسبة التغيير: {rewrite_stats['change_ratio']:.0%}")
        logger.info(f"   - عدد الكلمات: {rewrite_stats['original_length']} → {rewrite_stats['rewritten_length']}")
        
        # 4. إضافة إلى قائمة النصوص المخزنة
        stored_texts.append(text)
        if len(stored_texts) > 100:  # الاحتفاظ بآخر 100 نص فقط
            stored_texts.pop(0)
        
        return {
            'passed': True,
            'original': text,
            'rewritten': rewritten,
            'filter_result': filter_result,
            'rewrite_stats': rewrite_stats,
            'errors': []
        }
    
    except Exception as e:
        error_msg = f"❌ خطأ في المعالجة: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
        
        return {
            'passed': False,
            'original': text,
            'rewritten': None,
            'filter_result': None,
            'rewrite_stats': None,
            'errors': errors
        }


def format_message(text: str) -> str:
    """
    تنسيق الرسالة للنشر
    """
    # استبدال أسماء المراسلين
    text = text.replace('مراسل', 'مراسلنا')
    text = text.replace('مراسلة', 'مراسلتنا')
    text = text.replace('المراسل', 'مراسلنا')
    text = text.replace('المراسلة', 'مراسلتنا')
    
    # إضافة البادئة
    text = f"🔴 {text}"
    
    # إضافة الخاتمة
    text = f"{text}\n\nتابعنا على @AjeelNewsIq"
    
    return text


async def send_to_destination(text: str) -> bool:
    """
    إرسال الرسالة إلى قناة الوجهة
    """
    try:
        logger.info(f"📤 جاري الإرسال إلى {DESTINATION_CHANNEL}...")
        
        await client.send_message(DESTINATION_CHANNEL, text)
        
        logger.info("✅ تم الإرسال بنجاح!")
        return True
    
    except Exception as e:
        logger.error(f"❌ خطأ في الإرسال: {str(e)}")
        return False


# ============================================================================
# معالجات الأحداث
# ============================================================================

async def handle_new_message(event):
    """
    معالج الرسائل الجديدة من القنوات المصدر
    """
    try:
        message_text = event.message.text
        
        if not message_text:
            return
        
        # الحصول على اسم القناة
        chat = await event.get_chat()
        channel_name = chat.title or chat.username or str(chat.id)
        channel_priority = get_channel_priority(channel_name)
        
        logger.info(f"📨 رسالة جديدة من {channel_name} (الأولوية: {channel_priority})")
        logger.info(f"   النص: {message_text[:50]}...")
        
        # معالجة الرسالة
        result = process_message(message_text)
        
        if not result['passed']:
            logger.warning(f"⏭️ تم تجاهل الرسالة")
            return
        
        # تنسيق الرسالة
        formatted_text = format_message(result['rewritten'])
        
        # إرسال الرسالة
        success = await send_to_destination(formatted_text)
        
        if success:
            logger.info("✅ تمت معالجة الرسالة بنجاح!")
        else:
            logger.error("❌ فشل إرسال الرسالة")
    
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الرسالة: {str(e)}")


# ============================================================================
# البرنامج الرئيسي
# ============================================================================

async def main():
    """
    البرنامج الرئيسي
    """
    logger.info("🚀 جاري بدء البوت المتقدم...")
    
    # التحقق من المتغيرات المطلوبة
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        logger.error("❌ خطأ: TELEGRAM_API_ID أو TELEGRAM_API_HASH غير محددة")
        return
    
    try:
        # الاتصال بـ Telegram
        logger.info("🔌 جاري الاتصال بـ Telegram...")
        await client.start(phone=TELEGRAM_PHONE)
        
        logger.info("✅ تم الاتصال بنجاح!")
        logger.info(f"📡 القنوات المراقبة: {', '.join(SOURCE_CHANNELS)}")
        logger.info(f"📤 قناة الوجهة: {DESTINATION_CHANNEL}")
        logger.info(f"🎨 أسلوب الصياغة: {REWRITE_STYLE}")
        logger.info(f"🔍 نظام الفلترة الذكية: مفعل")
        logger.info(f"✍️ نظام الصياغة المتقدمة: مفعل")
        
        # إضافة معالج الأحداث لكل قناة
        for channel in SOURCE_CHANNELS:
            @client.on(events.NewMessage(chats=channel))
            async def handler(event):
                await handle_new_message(event)
        
        logger.info("👂 جاري الاستماع للرسائل...")
        logger.info("🟢 البوت جاهز للعمل!")
        
        # الاستماع للرسائل
        await client.run_until_disconnected()
    
    except SessionPasswordNeededError:
        logger.error("❌ كلمة المرور مطلوبة!")
    except Exception as e:
        logger.error(f"❌ خطأ حرج: {str(e)}")
    finally:
        await client.disconnect()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ تم إيقاف البوت")
    except Exception as e:
        logger.error(f"❌ خطأ: {str(e)}")
