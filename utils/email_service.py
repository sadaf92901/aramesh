# ============================================================
# سرویس ایمیل
# ============================================================

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import get_config
from utils.logger import logger

class EmailService:
    """
    سرویس ایمیل

    دو حالت داره:
    - mock: فقط توی Console چاپ می‌کنه (برای development)
    - smtp: واقعاً ایمیل می‌فرسته (برای production)
    """

    def __init__(self):
        self.config = get_config()
        self.enabled = self.config.EMAIL_ENABLED
        self.provider = self.config.EMAIL_PROVIDER

    # ============================================================
    # ارسال ایمیل
    # ============================================================

    def send_email(self, to_email, subject, body):
        """
        ارسال ایمیل

        Args:
            to_email: ایمیل گیرنده
            subject: موضوع
            body: متن (HTML)

        Returns:
            bool: موفقیت
        """
        if not self.enabled:
            logger.warning("⚠️ ایمیل غیرفعاله")
            return False

        if self.provider == 'mock':
            return self._mock_send(to_email, subject, body)
        elif self.provider == 'smtp':
            return self._smtp_send(to_email, subject, body)
        else:
            logger.error(f"❌ Provider ناشناخته: {self.provider}")
            return False

    # ============================================================
    # Mock (برای development)
    # ============================================================

    def _mock_send(self, to_email, subject, body):
        """ارسال Mock — فقط چاپ توی Console"""
        logger.info("\n" + "=" * 60)
        logger.info("📧 ایمیل (Mock)")
        logger.info("=" * 60)
        logger.info(f"به: {to_email}")
        logger.info(f"موضوع: {subject}")
        logger.info("-" * 60)
        logger.info(body)
        logger.info("=" * 60 + "\n")
        return True

    # ============================================================
    # SMTP (برای production)
    # ============================================================

    def _smtp_send(self, to_email, subject, body):
        """
        ارسال واقعی با SMTP

        Args:
            to_email: ایمیل گیرنده
            subject: موضوع
            body: HTML body

        Returns:
            bool: موفقیت
        """
        # ===== چک تنظیمات =====
        if not self.config.SMTP_HOST:
            logger.error("❌ SMTP_HOST تنظیم نشده")
            return False

        if not self.config.SMTP_USER or not self.config.SMTP_PASSWORD:
            logger.error("❌ SMTP_USER یا SMTP_PASSWORD تنظیم نشده")
            return False

        try:
            # ===== ساخت پیام =====
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.SMTP_FROM or self.config.SMTP_USER
            msg['To'] = to_email

            # ===== HTML body =====
            html_part = MIMEText(body, 'html', 'utf-8')
            msg.attach(html_part)

            # ===== اتصال به SMTP =====
            if self.config.SMTP_PORT == 465:
                # ===== SSL (پورت ۴۶۵) =====
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(
                    self.config.SMTP_HOST,
                    self.config.SMTP_PORT,
                    context=context,
                    timeout=30
                ) as server:
                    server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
                    server.send_message(msg)
            else:
                # ===== STARTTLS (پورت ۵۸۷) =====
                with smtplib.SMTP(
                    self.config.SMTP_HOST,
                    self.config.SMTP_PORT,
                    timeout=30
                ) as server:
                    server.ehlo()
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
                    server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
                    server.send_message(msg)

            logger.info(f"✅ ایمیل ارسال شد به {to_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("❌ خطا در احراز هویت SMTP — یوزر/پسورد رو چک کن")
            return False

        except smtplib.SMTPException as e:
            logger.error(f"❌ خطای SMTP: {e}")
            return False

        except Exception as e:
            logger.error(f"❌ خطای غیرمنتظره در ایمیل: {e}")
            return False

    # ============================================================
    # توابع کمکی
    # ============================================================

    def send_password_reset(self, to_email, username, reset_link):
        """ارسال لینک بازیابی رمز"""
        subject = "بازیابی رمز عبور — همراه آرامش"

        body = f"""
        <div style="font-family: Tahoma; direction: rtl; padding: 20px;">
            <h2 style="color: #8B5CF6;">🌿 همراه آرامش</h2>
            <p>سلام {username} عزیز،</p>
            <p>درخواست بازیابی رمز عبور برای حساب شما ثبت شد.</p>
            <p>برای تغییر رمز، روی لینک زیر کلیک کنید:</p>
            <p style="text-align: center; margin: 20px 0;">
                <a href="{reset_link}"
                   style="background: #8B5CF6; color: white; padding: 12px 30px;
                          text-decoration: none; border-radius: 50px; display: inline-block;">
                    🔒 تغییر رمز عبور
                </a>
            </p>
            <p style="color: #64748b; font-size: 13px;">
                این لینک ۱ ساعت معتبره.
            </p>
            <p style="color: #64748b; font-size: 13px;">
                اگه شما این درخواست رو ندادی، این ایمیل رو نادیده بگیر.
            </p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
            <p style="color: #94a3b8; font-size: 12px;">
                همراه آرامش — ساخته شده با 💚
            </p>
        </div>
        """

        return self.send_email(to_email, subject, body)


# ============================================================
# Singleton
# ============================================================

_email_service = None


def get_email_service():
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
