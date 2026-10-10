# ============================================================
# تست توابع کمکی
# ============================================================

import pytest
from utils.helpers import (
    sanitize_input,
    is_allowed_file,
    get_persian_date,
    calculate_stats
)


# ============================================================
# تست sanitize_input
# ============================================================

class TestSanitizeInput:
    """تست پاک‌سازی ورودی"""

    def test_empty_input(self):
        """ورودی خالی"""
        assert sanitize_input('') == ''
        assert sanitize_input(None) == ''

    def test_remove_html_tags(self):
        """حذف تگ‌های HTML"""
        assert sanitize_input('<b>bold</b>') == 'bold'
        assert sanitize_input('<i>italic</i>') == 'italic'
        assert sanitize_input('<p>paragraph</p>') == 'paragraph'

    def test_remove_script_tags(self):
        """حذف تگ‌های script"""
        result = sanitize_input('<script>alert("xss")</script>')
        assert '<script>' not in result
        assert '</script>' not in result
        assert 'alert' in result
        assert 'xss' in result

    def test_remove_dangerous_chars(self):
        """حذف کاراکترهای خطرناک"""
        result = sanitize_input('test<>{ }[]')
        assert '<' not in result
        assert '>' not in result
        assert '{' not in result
        assert '}' not in result
        assert '[' not in result
        assert ']' not in result

    def test_remove_parentheses(self):
        """حذف پرانتزها (برای امنیت)"""
        result = sanitize_input('test()')
        assert '(' not in result
        assert ')' not in result

    def test_max_length(self):
        """محدودیت طول"""
        long_text = 'a' * 2000
        result = sanitize_input(long_text)
        assert len(result) <= 1000

    def test_whitespace_trim(self):
        """حذف فاصله‌های اضافی"""
        assert sanitize_input('  hello  ') == 'hello'
        assert sanitize_input('\n\ntext\n\n') == 'text'

    def test_persian_text(self):
        """متن فارسی"""
        result = sanitize_input('سلام، خوبی؟')
        assert 'سلام' in result
        assert 'خوبی' in result

    def test_mixed_content(self):
        """محتوای ترکیبی"""
        result = sanitize_input('<b>سلام</b> <script>bad</script>')
        assert '<b>' not in result
        assert '<script>' not in result
        assert 'سلام' in result


# ============================================================
# تست is_allowed_file
# ============================================================

class TestIsAllowedFile:
    """تست بررسی فایل مجاز"""

    def test_wav_allowed(self):
        assert is_allowed_file('audio.wav', {'wav', 'mp3'}) is True

    def test_mp3_allowed(self):
        assert is_allowed_file('audio.mp3', {'wav', 'mp3'}) is True

    def test_ogg_allowed(self):
        assert is_allowed_file('audio.ogg', {'wav', 'mp3', 'ogg'}) is True

    def test_exe_not_allowed(self):
        assert is_allowed_file('virus.exe', {'wav', 'mp3'}) is False

    def test_png_not_allowed(self):
        assert is_allowed_file('image.png', {'wav', 'mp3'}) is False

    def test_no_extension(self):
        assert is_allowed_file('file', {'wav', 'mp3'}) is False

    def test_case_insensitive(self):
        assert is_allowed_file('audio.WAV', {'wav'}) is True
        assert is_allowed_file('audio.WaV', {'wav'}) is True

    def test_multiple_dots(self):
        assert is_allowed_file('my.audio.file.wav', {'wav'}) is True


# ============================================================
# تست get_persian_date
# ============================================================

class TestGetPersianDate:
    """تست تاریخ شمسی"""

    def test_returns_dict(self):
        result = get_persian_date()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = get_persian_date()
        assert 'year' in result
        assert 'month' in result
        assert 'day' in result
        assert 'month_name' in result
        assert 'full' in result

    def test_year_is_valid(self):
        result = get_persian_date()
        assert 1400 <= result['year'] <= 1500

    def test_month_is_valid(self):
         result = get_persian_date()
         assert 1 <= result['month'] <= 12

    def test_day_is_valid(self):
         result = get_persian_date()
         assert 1 <= result['day'] <= 31

    def test_month_name_is_persian(self):
        result = get_persian_date()
        persian_months = [
                'فروردین', 'اردیبهشت', 'خرداد',
                'تیر', 'مرداد', 'شهریور',
                'مهر', 'آبان', 'آذر',
                'دی', 'بهمن', 'اسفند'
        ]
        assert result['month_name'] in persian_months

    def test_full_date_format(self):
         result = get_persian_date()
         assert isinstance(result['full'], str)
         assert str(result['year']) in result['full']

    # ============================================================
    # تست calculate_stats
    # ============================================================

    class TestCalculateStats:
        """تست محاسبه آمار"""

        def test_empty_data(self):
            result = calculate_stats({})
            assert result['total'] == 0
            assert result['average'] == 0

        def test_single_mood(self):
            result = calculate_stats({'2026-01-01': 0})
            assert result['total'] == 1
            assert result['average'] == 0
            assert result['healthy'] == 1
            assert result['mild'] == 0

        def test_multiple_moods(self):
            data = {
                '2026-01-01': 0,
                '2026-01-02': 1,
                '2026-01-03': 2,
                '2026-01-04': 3,
            }
            result = calculate_stats(data)
            assert result['total'] == 4
            assert result['healthy'] == 1
            assert result['mild'] == 1
            assert result['moderate'] == 1
            assert result['severe'] == 1

        def test_all_healthy(self):
            data = {f'2026-01-0{i}': 0 for i in range(1, 6)}
            result = calculate_stats(data)
            assert result['total'] == 5
            assert result['healthy'] == 5
            assert result['average'] == 0

        def test_all_severe(self):
            data = {f'2026-01-0{i}': 3 for i in range(1, 6)}
            result = calculate_stats(data)
            assert result['total'] == 5
            assert result['severe'] == 5
            assert result['average'] == 3

        def test_average_calculation(self):
            data = {
                '2026-01-01': 0,
                '2026-01-02': 2,
            }
            result = calculate_stats(data)
            assert result['average'] == 1.0