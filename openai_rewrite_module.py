# -*- coding: utf-8 -*-

"""
نظام الصياغة عبر OpenAI API
OpenAI-based Text Rewriting System
"""

import os
import logging
import requests
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class OpenAIRewriter:
    """
    نظام صياغة متقدم باستخدام OpenAI API
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"
        
        if not self.api_key:
            logger.warning("⚠️ OpenAI API Key غير محدد!")
    
    def rewrite(self, text: str, style: str = 'professional') -> Tuple[str, bool]:
        """
        إعادة صياغة النص باستخدام OpenAI API
        
        Args:
            text: النص الأصلي
            style: أسلوب الصياغة
        
        Returns:
            (النص المعاد صياغته، هل نجح)
        """
        if not self.api_key:
            logger.warning("⚠️ لا يمكن استخدام OpenAI API بدون API Key")
            return text, False
        
        try:
            # إنشاء الـ prompt
            prompt = self._create_prompt(text, style)
            
            # إرسال الطلب إلى OpenAI
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "أنت محرر نصوص احترافي متخصص في إعادة الصياغة. أعد صياغة النص بأسلوب احترافي مع الحفاظ على المعنى الأصلي."
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
                logger.info("✨ تمت إعادة الصياغة بنجاح عبر OpenAI!")
                return rewritten_text, True
            else:
                error_msg = f"خطأ OpenAI: {response.status_code} - {response.text}"
                logger.error(f"❌ {error_msg}")
                return text, False
        
        except Exception as e:
            logger.error(f"❌ خطأ في الاتصال بـ OpenAI: {str(e)}")
            return text, False
    
    def _create_prompt(self, text: str, style: str) -> str:
        """
        إنشاء prompt لـ OpenAI
        """
        if style == 'professional':
            return f"""أعد صياغة النص التالي بأسلوب احترافي وموضوعي مع تغيير الكلمات والتراكيب بشكل بسيط:

النص الأصلي:
{text}

المتطلبات:
1. غير الأسلوب والتراكيب بشكل بسيط
2. احتفظ بالمعنى الأصلي تماماً
3. لا تضيف معلومات جديدة
4. اجعل النص أكثر وضوحاً واحترافية

أعد الصياغة مباشرة بدون تعليقات:"""
        
        elif style == 'casual':
            return f"""أعد صياغة النص التالي بأسلوب بسيط وسهل:

النص الأصلي:
{text}

أعد الصياغة مباشرة بدون تعليقات:"""
        
        else:  # formal
            return f"""أعد صياغة النص التالي بأسلوب رسمي وفخم:

النص الأصلي:
{text}

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
