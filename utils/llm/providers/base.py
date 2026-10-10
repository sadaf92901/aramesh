# ============================================================
# Interface پایه برای Providerهای LLM
# ============================================================


class LLMProvider:
    """
    Interface مشترک همه‌ی Providerهای LLM.

    هر Provider باید این متدها رو پیاده‌سازی کنه:
    - analyze_text()
    - chat()
    - weekly_summary()
    """

    def analyze_text(self, text_answers):
        """تحلیل پاسخ‌های کاربر"""
        raise NotImplementedError("analyze_text پیاده‌سازی نشده")

    def chat(self, message):
        """پاسخ چت‌بات"""
        raise NotImplementedError("chat پیاده‌سازی نشده")

    def weekly_summary(self, data):
        """جمع‌بندی هفتگی"""
        raise NotImplementedError("weekly_summary پیاده‌سازی نشده")

    def is_available(self):
        """آیا Provider آماده‌ی استفاده‌ست؟"""
        raise NotImplementedError("is_available پیاده‌سازی نشده")