# -*- coding: utf-8 -*-

"""
نظام الفلترة الذكية
Advanced Filtering System for News Content
"""

import re
from typing import Tuple, Dict

class SmartFilter:
    """
    نظام فلترة ذكي لكشف الإعلانات والمحتوى غير المرغوب
    """
    
    def __init__(self):
        # كلمات مفتاحية للإعلانات
        self.ad_keywords = [
            'اشتري', 'شراء', 'عرض خاص', 'خصم', 'تخفيف', 'توفير',
            'اضغط هنا', 'انقر هنا', 'رابط', 'زيارة', 'موقع',
            'تحميل', 'تنزيل', 'تطبيق', 'برنامج', 'إعلان',
            'إعلانات', 'دعاية', 'تسويق', 'عرض', 'ترويج',
            'مجاني', 'بدون تكلفة', 'احصل على', 'اربح', 'جائزة',
            'يانصيب', 'سحب', 'فوز', 'محظوظ', 'حظك',
            'اتصل', 'هاتف', 'واتس', 'تليجرام', 'بريد',
            'عنوان', 'موقع', 'فرع', 'فروع', 'مقر',
            'سعر', 'ثمن', 'تكلفة', 'قيمة', 'دفع',
            'بطاقة', 'حساب', 'تحويل', 'تمويل', 'قرض',
            'استثمار', 'أرباح', 'عائد', 'فائدة', 'رأس مال',
            'عمل', 'وظيفة', 'توظيف', 'فرصة عمل', 'تدريب',
            'دورة', 'كورس', 'تعليم', 'شهادة', 'درجة',
            'صحة', 'علاج', 'دواء', 'طبي', 'طبيب',
            'جمال', 'مستحضرات', 'كريم', 'عطر', 'مكياج',
            'ملابس', 'أحذية', 'حقائب', 'إكسسوارات', 'مجوهرات',
            'سيارة', 'سيارات', 'عقار', 'عقارات', 'بيت', 'منزل',
            'فندق', 'سفر', 'رحلة', 'تذاكر', 'حجز',
            'طعام', 'مطعم', 'وجبة', 'قهوة', 'مشروب',
            'ألعاب', 'رياضة', 'ترفيه', 'حفلة', 'حدث',
            'كازينو', 'مراهنة', 'قمار', 'رهان', 'لعب',
            'عملة', 'بيتكوين', 'كريبتو', 'استثمار رقمي',
            'شبكة', 'تسويق شبكي', 'mlm', 'بيزنس', 'مشروع',
            'أونلاين', 'إنترنت', 'ويب', 'موقع إلكتروني',
            'تطبيق', 'برنامج', 'سوفتوير', 'تقنية', 'تكنولوجيا',
            'ساعة', 'عطر', 'نظارة', 'حقيبة', 'منتج',
            'جديد', 'حصري', 'محدود', 'نادر', 'فريد',
            'الأفضل', 'الأسرع', 'الأرخص', 'الأقوى', 'الأجمل',
            'مضمون', 'مجرب', 'موثوق', 'معتمد', 'أصلي',
            'الآن', 'فقط اليوم', 'لفترة محدودة', 'قبل انتهاء', 'عجل',
            'لا تفوت', 'لا تتأخر', 'سريع', 'فوري', 'فاجل'
        ]
        
        # أنماط الروابط
        self.url_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            r'www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}',
            r'bit\.ly/\w+',
            r'tinyurl\.com/\w+',
            r'@\w+',  # mentions
            r'#\w+',  # hashtags
        ]
        
        # كلمات مفتاحية للمحتوى الموثوق
        self.trusted_keywords = [
            'وكالة', 'رويترز', 'ap', 'afp', 'bbc', 'cnn', 'الجزيرة',
            'الحدث', 'الأخبار', 'عاجل', 'تقرير', 'تحقيق',
            'بيان', 'إعلان رسمي', 'وزارة', 'حكومة', 'سفارة',
            'مسؤول', 'رسمي', 'حكومي', 'دولي', 'عالمي',
            'أمم متحدة', 'يونسكو', 'الاتحاد الأوروبي', 'ناتو',
            'اقتصاد', 'سياسة', 'رياضة', 'ثقافة', 'علوم',
            'تكنولوجيا', 'صحة', 'بيئة', 'تعليم', 'قانون'
        ]
    
    def is_advertisement(self, text: str) -> Tuple[bool, str]:
        """
        كشف إذا كان النص إعلاناً
        
        Returns:
            (is_ad, reason)
        """
        text_lower = text.lower()
        
        # فحص الكلمات المفتاحية للإعلانات
        ad_count = 0
        for keyword in self.ad_keywords:
            if keyword in text_lower:
                ad_count += 1
        
        if ad_count >= 3:
            return True, "كلمات إعلانية متعددة"
        
        # فحص الروابط
        for pattern in self.url_patterns:
            if re.search(pattern, text):
                return True, "يحتوي على روابط"
        
        # فحص الأسعار والأرقام المشبوهة
        if re.search(r'\d+\s*(ريال|دولار|يورو|جنيه|دينار)', text_lower):
            return True, "يحتوي على أسعار"
        
        # فحص الأرقام الهاتفية
        if re.search(r'(\+\d{1,3})?[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{4}', text):
            return True, "يحتوي على أرقام هاتفية"
        
        return False, "نص موثوق"
    
    def is_low_quality(self, text: str) -> Tuple[bool, str]:
        """
        كشف إذا كان النص منخفض الجودة
        
        Returns:
            (is_low_quality, reason)
        """
        # فحص الطول
        words = text.split()
        if len(words) < 10:
            return True, "نص قصير جداً"
        
        if len(words) > 500:
            return True, "نص طويل جداً"
        
        # فحص الأحرف الخاصة الزائدة
        special_chars = len(re.findall(r'[!@#$%^&*()_+=\[\]{};:\'",.<>?/\\|`~-]', text))
        if special_chars > len(words) * 0.3:
            return True, "أحرف خاصة زائدة"
        
        # فحص الأحرف المكررة
        if re.search(r'(.)\1{4,}', text):
            return True, "أحرف مكررة"
        
        # فحص الكلمات المكررة
        words_lower = [w.lower() for w in words]
        unique_ratio = len(set(words_lower)) / len(words_lower)
        if unique_ratio < 0.5:
            return True, "كلمات مكررة كثيراً"
        
        # فحص الأحرف الكبيرة الزائدة
        uppercase_ratio = sum(1 for c in text if c.isupper()) / len(text)
        if uppercase_ratio > 0.5:
            return True, "أحرف كبيرة زائدة"
        
        return False, "جودة جيدة"
    
    def is_duplicate(self, text: str, stored_texts: list) -> Tuple[bool, str]:
        """
        كشف إذا كان النص مكرراً
        
        Returns:
            (is_duplicate, reason)
        """
        text_lower = text.lower()
        
        for stored_text in stored_texts:
            stored_lower = stored_text.lower()
            
            # حساب التشابه
            similarity = self.calculate_similarity(text_lower, stored_lower)
            
            if similarity > 0.8:
                return True, f"نص مكرر (تشابه: {similarity:.0%})"
        
        return False, "نص جديد"
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        حساب نسبة التشابه بين نصين
        """
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def get_quality_score(self, text: str) -> float:
        """
        حساب درجة جودة النص (0-100)
        """
        score = 100.0
        
        # فحص الطول
        words = text.split()
        if len(words) < 20:
            score -= 20
        elif len(words) > 400:
            score -= 10
        
        # فحص الأحرف الخاصة
        special_chars = len(re.findall(r'[!@#$%^&*()_+=\[\]{};:\'",.<>?/\\|`~-]', text))
        if special_chars > len(words) * 0.2:
            score -= 15
        
        # فحص الكلمات المكررة
        words_lower = [w.lower() for w in words]
        unique_ratio = len(set(words_lower)) / len(words_lower)
        if unique_ratio < 0.6:
            score -= 20
        
        # فحص الأحرف الكبيرة
        uppercase_ratio = sum(1 for c in text if c.isupper()) / len(text)
        if uppercase_ratio > 0.3:
            score -= 10
        
        # فحص الجمل
        sentences = re.split(r'[.!?]', text)
        if len(sentences) < 2:
            score -= 15
        
        return max(0, score)
    
    def filter_text(self, text: str, stored_texts: list = None) -> Dict:
        """
        فلترة شاملة للنص
        
        Returns:
            {
                'passed': bool,
                'reasons': [str],
                'quality_score': float,
                'is_ad': bool,
                'is_low_quality': bool,
                'is_duplicate': bool
            }
        """
        if stored_texts is None:
            stored_texts = []
        
        reasons = []
        passed = True
        
        # فحص الإعلانات
        is_ad, ad_reason = self.is_advertisement(text)
        if is_ad:
            passed = False
            reasons.append(f"❌ إعلان: {ad_reason}")
        
        # فحص الجودة
        is_low_quality, quality_reason = self.is_low_quality(text)
        if is_low_quality:
            passed = False
            reasons.append(f"❌ جودة منخفضة: {quality_reason}")
        
        # فحص التكرار
        is_duplicate, duplicate_reason = self.is_duplicate(text, stored_texts)
        if is_duplicate:
            passed = False
            reasons.append(f"❌ تكرار: {duplicate_reason}")
        
        # حساب درجة الجودة
        quality_score = self.get_quality_score(text)
        
        if passed:
            reasons.append(f"✅ نص موثوق (درجة الجودة: {quality_score:.0f}/100)")
        
        return {
            'passed': passed,
            'reasons': reasons,
            'quality_score': quality_score,
            'is_ad': is_ad,
            'is_low_quality': is_low_quality,
            'is_duplicate': is_duplicate
        }


# اختبار سريع
if __name__ == "__main__":
    filter_system = SmartFilter()
    
    # اختبار 1: نص إعلاني
    test1 = "اشتري الآن! عرض خاص على المنتجات. اضغط هنا: www.example.com"
    result1 = filter_system.filter_text(test1)
    print(f"الاختبار 1: {result1}")
    
    # اختبار 2: نص موثوق
    test2 = "أعلنت وزارة الصحة اليوم عن تطعيم جديد للأطفال. قال المسؤول الرسمي أن البرنامج سيبدأ الشهر القادم."
    result2 = filter_system.filter_text(test2)
    print(f"الاختبار 2: {result2}")
    
    # اختبار 3: نص قصير
    test3 = "خبر"
    result3 = filter_system.filter_text(test3)
    print(f"الاختبار 3: {result3}")
