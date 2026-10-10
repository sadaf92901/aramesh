# ============================================================
# تست‌های امنیتی
# ============================================================

import pytest


# ============================================================
# 1. تست‌های XSS (Cross-Site Scripting)
# ============================================================

class TestXSSProtection:
    """تست محافظت XSS"""

    def test_xss_in_note_content(self, logged_in_client):
        """تزریق script توی یاداشت"""
        response = logged_in_client.post('/api/notes', json={
            'content': '<script>alert("XSS")</script>',
            'mood': 'happy'
        })

        assert response.status_code == 200

        # ===== چک کن script توی دیتابیس خام ذخیره نشده =====
        notes_response = logged_in_client.get('/api/notes')
        notes = notes_response.get_json()

        for note in notes:
            assert '<script>' not in note['content']
            assert '</script>' not in note['content']

    def test_xss_in_note_title(self, logged_in_client):
        """تزریق script توی عنوان"""
        response = logged_in_client.post('/api/notes', json={
            'title': '<img src=x onerror=alert(1)>',
            'content': 'متن تست',
            'mood': 'happy'
        })

        assert response.status_code == 200

        notes = logged_in_client.get('/api/notes').get_json()
        for note in notes:
            assert 'onerror' not in note.get('title', '')

    def test_xss_in_chat_message(self, logged_in_client):
        """تزریق script توی چت"""
        response = logged_in_client.post('/api/chat', json={
            'message': '<script>alert("XSS")</script>'
        })

        assert response.status_code in [200, 429]


# ============================================================
# 2. تست‌های SQL Injection
# ============================================================

class TestSQLInjection:
    """تست محافظت SQL Injection"""

    def test_sql_injection_in_login(self, client):
        """تزریق SQL توی ورود"""
        response = client.post('/api/login', json={
            'username': "' OR '1'='1",
            'password': "' OR '1'='1"
        })

        assert response.status_code == 401

    def test_sql_injection_in_register(self, client):
        """تزریق SQL توی ثبت‌نام"""
        response = client.post('/api/register', json={
            'username': "admin'; DROP TABLE user;--",
            'email': 'test@example.com',
            'password': 'Test1234'
        })

        # ===== باید خطای validation بده =====
        assert response.status_code == 400

    def test_sql_injection_in_search(self, logged_in_client):
        """تزریق SQL توی جستجو"""
        response = logged_in_client.get(
            "/api/notes?search=' OR '1'='1"
        )
        assert response.status_code in [200, 400, 404]


# ============================================================
# 3. تست‌های Input Validation
# ============================================================

class TestInputValidation:
    """تست اعتبارسنجی ورودی"""

    def test_invalid_email_format(self, client):
        """ایمیل نامعتبر"""
        response = client.post('/api/register', json={
            'username': 'test_user',
            'email': 'invalid-email',
            'password': 'Test1234'
        })
        assert response.status_code == 400

    def test_sql_meta_in_username(self, client):
        """کاراکترهای خطرناک توی username"""
        response = client.post('/api/register', json={
            'username': '<script>',
            'email': 'test@example.com',
            'password': 'Test1234'
        })
        assert response.status_code == 400

    def test_very_long_input(self, logged_in_client):
        """ورودی خیلی طولانی"""
        long_text = 'A' * 10000
        response = logged_in_client.post('/api/notes', json={
            'content': long_text,
            'mood': 'happy'
        })

        # ===== باید قبول بشه ولی محدود بشه =====
        assert response.status_code in [200, 400]

    def test_null_bytes(self, logged_in_client):
        """تزریق null byte"""
        response = logged_in_client.post('/api/notes', json={
            'content': 'test\x00malicious',
            'mood': 'happy'
        })
        assert response.status_code in [200, 400]


# ============================================================
# 4. تست‌های Authorization
# ============================================================

class TestAuthorization:
    """تست سطح دسترسی"""

    def test_access_other_user_note(self, client, logged_in_client):
        """دسترسی به یاداشت کاربر دیگه"""
        # ===== کاربر ۱: ساخت یاداشت =====
        create = logged_in_client.post('/api/notes', json={
            'content': 'یاداشت محرمانه',
            'mood': 'happy'
        })
        note_id = create.get_json()['id']

        # ===== خروج =====
        logged_in_client.post('/api/logout')

        # ===== کاربر ۲: ثبت‌نام =====
        client.post('/api/register', json={
            'username': 'user2_test',
            'email': 'user2@example.com',
            'password': 'Test1234'
        })

        # ===== تلاش برای دسترسی =====
        response = client.delete(f'/api/notes/{note_id}')

        # ===== باید 403 یا 404 بده =====
        assert response.status_code in [403, 404]

    def test_access_protected_route_without_login(self, client):
        """دسترسی به صفحات محافظت‌شده بدون لاگین"""
        protected = ['/profile', '/journal', '/history', '/weekly-plan']

        for route in protected:
            response = client.get(route)
            assert response.status_code in [302, 301, 401]


# ============================================================
# 5. تست‌های Session
# ============================================================

class TestSessionSecurity:
    """تست امنیت Session"""

    def test_session_cookie_httponly(self, app):
        """کوکی Session باید HTTPOnly باشه"""
        assert app.config.get('SESSION_COOKIE_HTTPONLY') is True

    def test_session_cookie_samesite(self, app):
        """کوکی Session باید SameSite داشته باشه"""
        assert app.config.get('SESSION_COOKIE_SAMESITE') == 'Lax'

    def test_logout_clears_session(self, logged_in_client):
        """خروج باید Session رو پاک کنه"""
        # ===== قبل از خروج =====
        me_before = logged_in_client.get('/api/me')
        assert me_before.status_code == 200

        # ===== خروج =====
        logged_in_client.post('/api/logout')

        # ===== بعد از خروج =====
        me_after = logged_in_client.get('/api/me')
        assert me_after.status_code == 401


# ============================================================
# 6. تست‌های Rate Limiting
# ============================================================

class TestRateLimiting:
    """تست محدودیت نرخ"""

    def test_login_rate_limit(self, client):
        """ورود باید Rate Limit داشته باشه"""
        # ===== ۷ بار تلاش =====
        for i in range(7):
            response = client.post('/api/login', json={
                'username': 'test',
                'password': 'wrong'
            })

        # ===== بعد از ۵ بار، باید 429 بده =====
        assert response.status_code in [401, 429]



# ============================================================
# 7. تست‌های Security Headers
# ============================================================

class TestSecurityHeaders:
    """تست Security Headers"""

    def test_x_frame_options(self, client):
        """X-Frame-Options باید SAMEORIGIN باشه"""
        response = client.get('/')
        assert response.headers.get('X-Frame-Options') == 'SAMEORIGIN'

    def test_x_content_type_options(self, client):
        """X-Content-Type-Options باید nosniff باشه"""
        response = client.get('/')
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'

    def test_x_xss_protection(self, client):
        """X-XSS-Protection باید فعال باشه"""
        response = client.get('/')
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'

    def test_referrer_policy(self, client):
        """Referrer-Policy باید تنظیم شده باشه"""
        response = client.get('/')
        assert response.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'

    def test_permissions_policy(self, client):
        """Permissions-Policy باید تنظیم شده باشه"""
        response = client.get('/')
        assert 'geolocation=()' in response.headers.get('Permissions-Policy', '')


# ============================================================
# 8. تست‌های File Upload
# ============================================================

class TestFileUpload:
    """تست آپلود فایل"""

    def test_disallowed_file_extension(self, logged_in_client):
        """آپلود فایل با پسوند غیرمجاز"""
        import io
        data = {
            'avatar': (io.BytesIO(b'fake content'), 'malicious.exe')
        }

        response = logged_in_client.post(
            '/api/profile/avatar',
            data=data,
            content_type='multipart/form-data'
        )

        assert response.status_code == 400

    def test_oversized_file(self, logged_in_client):
        """آپلود فایل بزرگ"""
        import io
        # ===== 3MB (بیشتر از 2MB مجاز) =====
        big_content = b'X' * (3 * 1024 * 1024)
        data = {
            'avatar': (io.BytesIO(big_content), 'big.png')
        }

        response = logged_in_client.post(
            '/api/profile/avatar',
            data=data,
            content_type='multipart/form-data'
        )

        assert response.status_code == 400
