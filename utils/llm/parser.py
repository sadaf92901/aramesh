# ============================================================
# Parse کردن JSON از خروجی LLM
# ============================================================

import json
import re
from utils.logger import logger

def parse_json_response(text):
    """
    استخراج JSON از خروجی LLM

    Args:
        text: متن خروجی LLM

    Returns:
        dict یا None
    """
    if not text:
        return None

    try:
        # ===== ۱. جستجوی بلوک کد ```json ... ``` =====
        code_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if code_match:
            return json.loads(code_match.group(1))

        # ===== ۲. جستجوی {} مستقیم =====
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        # ===== ۳. تلاش مستقیم =====
        return json.loads(text)

    except (json.JSONDecodeError, AttributeError) as e:
        logger.warning(f"⚠️ خطا در parse JSON: {e}")
        return None

def get_fallback_analysis():
    """پاسخ پیش‌فرض وقتی LLM کار نمی‌کنه — None برمی‌گردونه تا نمره‌ی جعلی نده"""
    return None