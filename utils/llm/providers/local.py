# ============================================================
# Local Provider — استفاده از LLM محلی (Qwen)
# ============================================================

import torch
from .base import LLMProvider
from ..prompts import PROMPTS
from ..parser import parse_json_response, get_fallback_analysis
from config import get_config


class LocalProvider(LLMProvider):
    """Provider بر اساس LLM محلی (Qwen 2.5)"""

    def __init__(self):
        self.config = get_config()
        self.model = None
        self.tokenizer = None
        self.device = None
        self._loaded = False

        # ===== اگر LLM_ENABLED=False، لود نکن =====
        if not self.config.LLM_ENABLED:
            print("⚠️ LocalProvider غیرفعاله")
            return

        try:
            self._load_model()
        except Exception as e:
            print(f"❌ خطا در لود مدل: {e}")
            self.model = None

    def _load_model(self):
        """لود مدل Qwen"""
        from transformers import AutoModelForCausalLM, AutoTokenizer

        model_name = self.config.LOCAL_LLM_MODEL
        device = self.config.LOCAL_LLM_DEVICE

        print(f"🔄 در حال لود مدل {model_name}...")
        print("   (این ممکنه چند دقیقه طول بکشه)")

        # ===== توکنایزر =====
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )

        # ===== مدل =====
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
            device_map=device,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )

        # ===== تنظیمات =====
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.device = device
        self._loaded = True

        print(f"✅ مدل Qwen لود شد: {model_name}")
        print(f"   دستگاه: {device}")

    def is_available(self):
        return self._loaded and self.model is not None

    # ============================================================
    # تولید متن
    # ============================================================

    def _generate(self, prompt, max_new_tokens=300):
        """تولید پاسخ با مدل"""
        if not self.is_available():
            return None

        try:
            # ===== Chat Template =====
            messages = [{"role": "user", "content": prompt}]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            # ===== توکنایز =====
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)

            # ===== تولید =====
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=self.config.LLM_TEMPERATURE,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # ===== استخراج =====
            response = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            )

            return response.strip()

        except Exception as e:
            print(f"❌ خطا در تولید متن: {e}")
            return None

    # ============================================================
    # تحلیل متن
    # ============================================================

    def analyze_text(self, text_answers):
        """تحلیل پاسخ‌های کاربر"""
        if not self.is_available():
            return get_fallback_analysis()

        try:
            prompt = PROMPTS['analysis'].format(
                answer1=text_answers[0] if len(text_answers) > 0 else '',
                answer2=text_answers[1] if len(text_answers) > 1 else '',
                answer3=text_answers[2] if len(text_answers) > 2 else '',
            )

            response = self._generate(prompt, max_new_tokens=300)

            if not response:
                return get_fallback_analysis()

            result = parse_json_response(response)

            if not result:
                print(f"⚠️ JSON parse نشد: {response[:200]}")
                return get_fallback_analysis()

            return {
                'dominant_emotion': result.get('dominant_emotion', 'نامشخص'),
                'emotion_intensity': result.get('emotion_intensity', 5),
                'depression_score': result.get('depression_score', 0),
                'anxiety_score': result.get('anxiety_score', 0),
                'protective_factors_score': result.get('protective_factors_score', 0),
                'risk_factors_score': result.get('risk_factors_score', 0),
                'final_score': result.get('final_score', 50),
                'key_concerns': result.get('key_concerns', []),
                'treatment': result.get('treatment', ''),
                'status': 'موفق'
            }

        except Exception as e:
            print(f"❌ خطا در تحلیل: {e}")
            return get_fallback_analysis()

    # ============================================================
    # چت
    # ============================================================

    def chat(self, message):
        """پاسخ چت‌بات"""
        if not self.is_available():
            return None

        try:
            prompt = PROMPTS['chat'].format(message=message)
            response = self._generate(prompt, max_new_tokens=200)
            return response if response else None

        except Exception as e:
            print(f"❌ خطا در چت: {e}")
            return None

    # ============================================================
    # جمع‌بندی هفتگی
    # ============================================================

    def weekly_summary(self, data):
        """جمع‌بندی هفتگی"""
        if not self.is_available():
            return None

        try:
            prompt = PROMPTS['weekly_summary'].format(**data)
            response = self._generate(prompt, max_new_tokens=400)
            return response if response else None

        except Exception as e:
            print(f"❌ خطا در جمع‌بندی: {e}")
            return None
