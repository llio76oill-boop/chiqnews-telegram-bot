# -*- coding: utf-8 -*-

"""
نظام الصياغة عبر DeepSeek API
DeepSeek-based Text Rewriting System
"""

import os
import logging
import requests
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class DeepSeekRewriter:
    """
    نظام صياغة متقدم باستخدام DeepSeek API
    """
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.model = "deepseek-chat"
        
        if not self.api_key:
            logger.warning("⚠️ DeepSeek API Key غير محدد!")
    
    def rewrite(self, text: str, style: str = 'professional') -> Tuple[str, bool]:
        """
        إعادة صياغة النص باستخدام DeepSeek API
        
        Args:
            text: النص الأصلي
            style: أسلوب الصياغة
        
        Returns:
            (النص المعاد صياغته، هل نجح)
        """
        if not self.api_key:
            logger.warning("⚠️ لا يمكن استخدام DeepSeek API بدون API Key")
            return text, False
        
        try:
            # إنشاء الـ prompt
            prompt = self._create_prompt(text, style)
            
            # إرسال الطلب إلى DeepSeek
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "أنت محرر نصوص احترافي متخصص في إعادة الصياغة. أعد صياغة النص بأسلوب احترافي مع الحفاظ على المعنى الأصلي. غير الأسلوب والتراكيب بشكل واضح."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                rewritten_text = result['choices'][0]['message']['content'].strip()
                logger.info("✨ تمت إعادة الصياغة بنجاح عبر DeepSeek!")
                return rewritten_text, True
            else:
                error_msg = f"خطأ DeepSeek: {response.status_code} - {response.text}"
                logger.error(f"❌ {error_msg}")
                return text, False
        
        except Exception as e:
            logger.error(f"❌ خطأ في الاتصال بـ DeepSeek: {str(e)}")
            return text, False
    
    def _create_prompt(self, text: str, style: str) -> str:
        """
        إنشاء prompt لـ DeepSeek
        """
        if style == 'professional':
            return f"""أعد صياغة النص التالي بأسلوب احترافي وموضوعي مع تغيير الكلمات والتراكيب بشكل واضح:

النص الأصلي:
{text}

المتطلبات:
1. غير الأسلوب والتراكيب بشكل واضح وملحوظ
2. احتفظ بالمعنى الأصلي تماماً
3. لا تضيف معلومات جديدة
4. اجعل النص أكثر وضوحاً واحترافية
5. استخدم مرادفات مختلفة للكلمات الرئيسية

أعد الصياغة مباشرة بدون تعليقات:"""
        
        elif style == 'casual':
            return f"""أعد صياغة النص التالي بأسلوب بسيط وسهل مع تغيير الكلمات:

النص الأصلي:
{text}

المتطلبات:
1. استخدم كلمات بسيطة وسهلة
2. احتفظ بالمعنى الأصلي
3. غير التراكيب بشكل واضح

أعد الصياغة مباشرة بدون تعليقات:"""
        
        else:  # formal
            return f"""أعد صياغة النص التالي بأسلوب رسمي وفخم مع تغيير الكلمات والتراكيب:

النص الأصلي:
{text}

المتطلبات:
1. استخدم لغة رسمية وفخمة
2. احتفظ بالمعنى الأصلي
3. غير التراكيب بشكل واضح

أعد الصياغة مباشرة بدون تعليقات:"""
    
    def get_rewrite_stats(self, original: str, rewritten: str) -> Dict:
        """
        حساب إحصائيات إعادة الصياغة
        """
        original_words = len(original.split())
        rewritten_words = len(rewritten.split())
        
        # حساب نسبة التشابه البسيطة
        original_set = set(original.split())
        rewritten_set = set(rewritten.split())
        
        if len(original_set) > 0:
            similarity = len(original_set & rewritten_set) / len(original_set | rewritten_set)
            change_ratio = 1 - similarity
        else:
            change_ratio = 0
        
        return {
            'change_ratio': change_ratio,
            'original_length': original_words,
            'rewritten_length': rewritten_words,
            'similarity': similarity
        }
