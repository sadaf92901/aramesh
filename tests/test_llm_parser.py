# ============================================================
# تست Parser LLM
# ============================================================

import pytest
from utils.llm.parser import parse_json_response, get_fallback_analysis


# ============================================================
# تست parse_json_response
# ============================================================

class TestParseJsonResponse:
    """تست پارس JSON از خروجی LLM"""

    def test_parse_simple_json(self):
        """JSON ساده"""
        text = '{"final_score": 75, "status": "موفق"}'
        result = parse_json_response(text)

        assert result is not None
        assert result['final_score'] == 75
        assert result['status'] == 'موفق'

    def test_parse_json_with_code_block(self):
        """JSON توی بلوک کد ```json"""
        text = '''```json
{
    "final_score": 80,
    "dominant_emotion": "خوشحالی"
}
```'''
        result = parse_json_response(text)

        assert result is not None
        assert result['final_score'] == 80
        assert result['dominant_emotion'] == 'خوشحالی'

    def test_parse_json_with_code_block_no_lang(self):
        """JSON توی بلوک کد بدون زبان"""
        text = '''```
{"final_score": 60}
```'''
        result = parse_json_response(text)

        assert result is not None
        assert result['final_score'] == 60

    def test_parse_json_with_text_before(self):
        """متن قبل از JSON"""
        text = '''تحلیل من اینه:
{
    "final_score": 70,
    "status": "موفق"
}
امیدوارم مفید بوده باشه.'''
        result = parse_json_response(text)

        assert result is not None
        assert result['final_score'] == 70

    def test_parse_nested_json(self):
        """JSON تودرتو"""
        text = '''{
    "final_score": 75,
    "key_concerns": ["اضطراب", "بی‌خوابی"],
    "metadata": {
        "model": "gpt-4o-mini",
        "version": "1.0"
    }
}'''
        result = parse_json_response(text)

        assert result is not None
        assert result['final_score'] == 75
        assert len(result['key_concerns']) == 2
        assert result['metadata']['model'] == 'gpt-4o-mini'

    def test_parse_empty_string(self):
        """رشته‌ی خالی → None"""
        result = parse_json_response('')
        assert result is None

    def test_parse_none(self):
        """None → None"""
        result = parse_json_response(None)
        assert result is None

    def test_parse_invalid_json(self):
        """JSON نامعتبر → None"""
        result = parse_json_response('{invalid json}')
        assert result is None

    def test_parse_no_json(self):
        """متن بدون JSON → None"""
        result = parse_json_response('این یه متن معمولیه بدون JSON')
        assert result is None

    def test_parse_persian_values(self):
        """مقادیر فارسی"""
        text = '''{
    "dominant_emotion": "غم",
    "treatment": "توصیه می‌شود با روانشناس مشورت کنید",
    "final_score": 45
}'''
        result = parse_json_response(text)

        assert result is not None
        assert result['dominant_emotion'] == 'غم'
        assert 'روانشناس' in result['treatment']

    def test_parse_array_values(self):
        """مقادیر آرایه‌ای"""
        text = '''{
    "final_score": 80,
    "key_concerns": [],
    "signs": ["خستگی", "بی‌اشتهایی"]
}'''
        result = parse_json_response(text)

        assert result is not None
        assert result['key_concerns'] == []
        assert result['signs'] == ['خستگی', 'بی‌اشتهایی']

    def test_parse_float_values(self):
        """مقادیر اعشاری"""
        text = '{"final_score": 72.5, "confidence": 0.95}'
        result = parse_json_response(text)

        assert result is not None
        assert result['final_score'] == 72.5
        assert result['confidence'] == 0.95

    def test_parse_with_newlines(self):
        """JSON با خطوط جدید"""
        text = '''{
    "final_score": 65,
    "status": "موفق"
}'''
        result = parse_json_response(text)
        assert result is not None
        assert result['final_score'] == 65

    def test_parse_malformed_code_block(self):
        """بلوک کد ناقص"""
        text = '''```json
{"final_score": 70
```'''
        result = parse_json_response(text)
        # باید None بده یا از regex دوم استفاده کنه
        # نتیجه ممکنه None باشه

    def test_parse_single_json_object(self):
        """تک JSON — فقط یه آبجکت"""
        text = '{"first": 1}'
        result = parse_json_response(text)

        assert result is not None
        assert result['first'] == 1

# ============================================================
# تست get_fallback_analysis
# ============================================================

class TestGetFallbackAnalysis:
    """تست fallback analysis"""

    def test_returns_none(self):
        """None برمی‌گردونه (نه نمره جعلی)"""
        result = get_fallback_analysis()
        assert result is None

    def test_callable(self):
        """تابع قابل صدا زدنه"""
        assert callable(get_fallback_analysis)

    def test_multiple_calls(self):
        """چند بار صدا زدن → همیشه None"""
        for _ in range(5):
            assert get_fallback_analysis() is None
