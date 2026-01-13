# -*- coding: utf-8 -*-

"""
نظام الصياغة المتقدمة
Advanced Text Rewriting System
"""

import re
import random
from typing import List, Dict, Tuple

class AdvancedRewriter:
    """
    نظام صياغة متقدم لإعادة صياغة النصوص بأسلوب احترافي
    """
    
    def __init__(self):
        # قاموس المرادفات
        self.synonyms = {
            'قال': ['أفاد', 'ذكر', 'صرح', 'أعلن', 'أشار'],
            'أعلن': ['أفصح', 'كشف', 'أظهر', 'بين', 'وضح'],
            'يوم': ['أمس', 'غداً', 'الأمس', 'الغد', 'اليوم'],
            'قطاع': ['مجال', 'حقل', 'ميدان', 'نطاق', 'مساحة'],
            'مشكلة': ['قضية', 'معضلة', 'إشكالية', 'تحدي', 'عائق'],
            'حل': ['معالجة', 'تدبير', 'إجراء', 'خطوة', 'تصرف'],
            'تأثير': ['تأثر', 'انعكاس', 'نتيجة', 'عاقبة', 'أثر'],
            'أهمية': ['أولوية', 'جدية', 'قيمة', 'وزن', 'دلالة'],
            'زيادة': ['ارتفاع', 'تصاعد', 'نمو', 'تضاعف', 'تعاظم'],
            'انخفاض': ['تراجع', 'هبوط', 'تقهقر', 'تناقص', 'تدني'],
            'تطور': ['تقدم', 'نمو', 'ازدهار', 'تحسن', 'تطوير'],
            'أزمة': ['أزمة', 'كارثة', 'محنة', 'ملمة', 'شدة'],
            'سلبي': ['سيء', 'ضار', 'مؤذي', 'مقلق', 'مثير للقلق'],
            'إيجابي': ['جيد', 'مفيد', 'مشجع', 'مبشر', 'واعد'],
            'رسمي': ['حكومي', 'رسمي', 'مسؤول', 'معتمد', 'موثق'],
            'غير رسمي': ['شعبي', 'عام', 'شفاهي', 'غير موثق', 'تقليدي'],
            'بداية': ['انطلاق', 'بدء', 'ابتداء', 'بيان', 'انعقاد'],
            'نهاية': ['انتهاء', 'إغلاق', 'توقف', 'ختام', 'إنهاء'],
            'عالمي': ['دولي', 'عام', 'شامل', 'جماعي', 'عام'],
            'محلي': ['إقليمي', 'وطني', 'محدود', 'خاص', 'جزئي'],
            'كبير': ['ضخم', 'عملاق', 'هائل', 'ضخم', 'كبير الحجم'],
            'صغير': ['ضئيل', 'محدود', 'بسيط', 'قليل', 'طفيف'],
            'سريع': ['فوري', 'عاجل', 'حاني', 'سريع الخطى', 'متسارع'],
            'بطيء': ['متأني', 'تدريجي', 'بطيء الخطى', 'متمهل', 'متراخي'],
            'جديد': ['حديث', 'طري', 'معاصر', 'عصري', 'مستحدث'],
            'قديم': ['عتيق', 'أثري', 'تراثي', 'تقليدي', 'موروث'],
            'قوي': ['قوي البنية', 'متين', 'صلب', 'راسخ', 'محكم'],
            'ضعيف': ['واهن', 'هش', 'رقيق', 'ناعم', 'لين'],
            'واضح': ['جلي', 'بين', 'صريح', 'صريح', 'ظاهر'],
            'غامض': ['غير واضح', 'ملتبس', 'غير محدد', 'غير صريح', 'مبهم'],
            'مهم': ['حاسم', 'بالغ الأهمية', 'ضروري', 'لازم', 'أساسي'],
            'ثانوي': ['فرعي', 'إضافي', 'تكميلي', 'هامشي', 'ملحق'],
            'ناجح': ['ناجح', 'موفق', 'منتصر', 'فائز', 'ظافر'],
            'فاشل': ['خاسر', 'مهزوم', 'مخفق', 'متعثر', 'منكسر'],
            'آمن': ['آمن', 'محمي', 'مأمون', 'آمن', 'سالم'],
            'خطر': ['مخيف', 'مهدد', 'مقلق', 'مثير للقلق', 'مريب'],
            'صحيح': ['صحيح', 'دقيق', 'سليم', 'صائب', 'موثوق'],
            'خاطئ': ['خطأ', 'غير صحيح', 'مغلوط', 'خاطئ', 'مشوه'],
        }
        
        # أنماط الجمل
        self.sentence_patterns = [
            "أشارت التقارير إلى أن {content}",
            "بحسب المعلومات المتاحة، {content}",
            "في تطور جديد، {content}",
            "أفادت المصادر بأن {content}",
            "كشفت التحقيقات عن {content}",
            "أظهرت النتائج أن {content}",
            "وفقاً للمعطيات، {content}",
            "تشير المؤشرات إلى أن {content}",
            "بناءً على التقارير، {content}",
            "يبدو أن {content}",
        ]
        
        # كلمات الربط
        self.connectors = [
            'علاوة على ذلك', 'بالإضافة إلى ذلك', 'كذلك', 'أيضاً',
            'من جهة أخرى', 'من ناحية أخرى', 'بالمقابل', 'في المقابل',
            'مع ذلك', 'غير أن', 'لكن', 'إلا أن', 'بيد أن',
            'لذلك', 'بالتالي', 'من ثم', 'وبناءً عليه', 'نتيجة لذلك',
            'أولاً', 'ثانياً', 'ثالثاً', 'أخيراً', 'في البداية',
            'في الوسط', 'في النهاية', 'في الحقيقة', 'في الواقع',
        ]
        
        # كلمات التأكيد
        self.emphasis_words = [
            'بكل تأكيد', 'بلا شك', 'بدون ريب', 'حقاً', 'فعلاً',
            'بالفعل', 'بالتأكيد', 'بالطبع', 'بالفعل', 'بلا ريب',
        ]
    
    def clean_text(self, text: str) -> str:
        """
        تنظيف النص من الرموز والمسافات الزائدة
        """
        # إزالة المسافات الزائدة
        text = re.sub(r'\s+', ' ', text)
        
        # إزالة الأحرف الخاصة الزائدة
        text = re.sub(r'([!?.])\1+', r'\1', text)
        
        # تصحيح المسافات قبل علامات الترقيم
        text = re.sub(r'\s+([.!?,;:])', r'\1', text)
        
        return text.strip()
    
    def split_sentences(self, text: str) -> List[str]:
        """
        تقسيم النص إلى جمل
        """
        # تقسيم بناءً على علامات الترقيم
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # تنظيف الجمل الفارغة
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def replace_words(self, text: str) -> str:
        """
        استبدال الكلمات بمرادفات
        """
        words = text.split()
        rewritten_words = []
        
        for word in words:
            # البحث عن مرادف
            word_lower = word.lower()
            
            if word_lower in self.synonyms:
                # اختيار مرادف عشوائي
                synonym = random.choice(self.synonyms[word_lower])
                
                # الحفاظ على حالة الأحرف الأصلية
                if word[0].isupper():
                    synonym = synonym.capitalize()
                
                rewritten_words.append(synonym)
            else:
                rewritten_words.append(word)
        
        return ' '.join(rewritten_words)
    
    def reorder_sentences(self, sentences: List[str]) -> List[str]:
        """
        إعادة ترتيب الجمل بشكل منطقي
        """
        if len(sentences) <= 2:
            return sentences
        
        # الحفاظ على الجملة الأولى والأخيرة
        first = sentences[0]
        last = sentences[-1]
        middle = sentences[1:-1]
        
        # إعادة ترتيب الجمل الوسطية
        random.shuffle(middle)
        
        return [first] + middle + [last]
    
    def improve_style(self, text: str) -> str:
        """
        تحسين أسلوب النص
        """
        # إضافة كلمات ربط
        if random.random() > 0.5:
            connector = random.choice(self.connectors)
            text = f"{connector}، {text[0].lower()}{text[1:]}"
        
        # إضافة كلمات تأكيد
        if random.random() > 0.7:
            emphasis = random.choice(self.emphasis_words)
            text = f"{emphasis} {text}"
        
        return text
    
    def rewrite(self, text: str, style: str = 'professional') -> str:
        """
        إعادة صياغة شاملة للنص
        
        Args:
            text: النص الأصلي
            style: أسلوب الصياغة ('professional', 'casual', 'formal')
        
        Returns:
            النص المعاد صياغته
        """
        # تنظيف النص
        text = self.clean_text(text)
        
        # تقسيم إلى جمل
        sentences = self.split_sentences(text)
        
        if not sentences:
            return text
        
        # إعادة صياغة كل جملة
        rewritten_sentences = []
        
        for sentence in sentences:
            # استبدال الكلمات
            rewritten = self.replace_words(sentence)
            
            # تحسين الأسلوب
            if style == 'professional':
                rewritten = self.improve_style(rewritten)
            
            rewritten_sentences.append(rewritten)
        
        # إعادة ترتيب الجمل (بحذر)
        if len(rewritten_sentences) > 3:
            rewritten_sentences = self.reorder_sentences(rewritten_sentences)
        
        # دمج الجمل
        result = ' '.join(rewritten_sentences)
        
        return result
    
    def get_rewrite_stats(self, original: str, rewritten: str) -> Dict:
        """
        حساب إحصائيات إعادة الصياغة
        """
        original_words = original.split()
        rewritten_words = rewritten.split()
        
        # حساب نسبة التغيير
        changed_words = sum(1 for o, r in zip(original_words, rewritten_words) if o.lower() != r.lower())
        change_ratio = changed_words / len(original_words) if original_words else 0
        
        return {
            'original_length': len(original_words),
            'rewritten_length': len(rewritten_words),
            'changed_words': changed_words,
            'change_ratio': change_ratio,
            'original_chars': len(original),
            'rewritten_chars': len(rewritten),
        }


# اختبار سريع
if __name__ == "__main__":
    rewriter = AdvancedRewriter()
    
    # اختبار 1: نص بسيط
    test1 = "قال الوزير إن الحكومة تعمل على حل المشكلة. أعلن عن خطة جديدة للتطوير."
    result1 = rewriter.rewrite(test1)
    print(f"الأصلي: {test1}")
    print(f"المعاد صياغته: {result1}")
    print(f"الإحصائيات: {rewriter.get_rewrite_stats(test1, result1)}\n")
    
    # اختبار 2: نص أطول
    test2 = "أعلنت الشركة عن نتائج جديدة. قال المدير إن الأرباح زادت بشكل كبير. هذا يعكس نجاح الاستراتيجية الجديدة."
    result2 = rewriter.rewrite(test2)
    print(f"الأصلي: {test2}")
    print(f"المعاد صياغته: {result2}")
    print(f"الإحصائيات: {rewriter.get_rewrite_stats(test2, result2)}\n")
