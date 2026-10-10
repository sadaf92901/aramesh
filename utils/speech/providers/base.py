# ============================================================
# Interface پایه برای Providerهای Speech
# ============================================================


class SpeechProvider:
    """
    Interface مشترک همه‌ی Providerهای Speech.
    """

    def transcribe(self, audio_path):
        """تبدیل صوت به متن"""
        raise NotImplementedError

    def analyze_emotion(self, audio_path):
        """تحلیل احساسات از صوت"""
        raise NotImplementedError

    def is_available(self):
        raise NotImplementedError