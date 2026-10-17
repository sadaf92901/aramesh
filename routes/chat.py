from utils.logger import logger
from extensions import limiter
from flask import Blueprint, request, jsonify, session
from utils.llm.service import get_llm_service
import random

chat_bp = Blueprint('chat', __name__)


# ============================================================
# پاسخ‌های fallback (اگه LLM کار نکنه)
# ============================================================

FALLBACK_RESPONSES = {
    "greeting": [
        "سلام! 👋 خوشحالم که پیام دادی. چطور می‌تونم امروز بهت کمک کنم؟",
        "درود! 🌸 چه خوب که اومدی. امروز چه احساسی داری؟",
        "سلام عزیزم! 😊 از دیدن پیامت خوشحالم. بگو چطور می‌تونم کمکت کنم؟"
    ],
    "default": [
        "ممنون که با من حرف می‌زنی 💬 چه چیزی امروز برات مهمه؟",
        "خوب که اینجایی. چه موضوعی رو می‌خوای با من در میان بذاری؟ 🤔",
        "هر چی دلت میخواد بگو، من گوش می‌دم و قضاوت نمی‌کنم. 🫂"
    ]
}

# ============================================================
# پروتکل بحران
# ============================================================

CRISIS_KEYWORDS = [
    'خودکشی', 'خودکش', 'خودم را بکشم', 'خودمو بکشم',
    'بمیرم', 'می‌خوام بمیرم', 'میخوام بمیرم',
    'نمی‌خوام زنده بمونم', 'نمیخوام زنده بمونم',
    'زندگی نمی‌خوام', 'زندگیمو نمی‌خوام',
    'آسیب به خود', 'به خودم آسیب',
    'تمومش کنم', 'تمومش کنم',
    'دیگه نمی‌خوام ادامه بدم',
    'خسته‌ام از زندگی', 'خسته ام از زندگی',
    'راحت بشم', 'خلاص بشم'
]

CRISIS_RESPONSE = """🆘 من نگرانتم. چیزی که گفتی خیلی مهمه و تو تنها نیستی.

لطفاً همین الان با این شماره‌ها تماس بگیر:

📞 اورژانس اجتماعی: ۱۲۳
📞 صدای مشاور: ۱۴۸۰

این افراد آموزش‌دیده هستن و می‌تونن کمکت کنن. 
تو ارزشمند هستی و کمک در دسترسه. 💚

اگه دوستی یا عضوی از خانواده داری، لطفاً بهشون بگو که به کمک نیاز داری."""


# ============================================================
# /api/chat
# ============================================================

@chat_bp.route('/api/chat', methods=['POST'])
@limiter.limit("50 per day")
def chat():
    # ===== چک لاگین (مهمان نمی‌تونه چت کنه) =====
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'برای چت باید وارد شوید'}), 401

    try:
        user_message = request.json.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'پیامی ارسال نشده'}), 400

        # ===== چک پروتکل بحران =====
        if any(kw in user_message for kw in CRISIS_KEYWORDS):
            logger.warning(f"🆘 پیام بحرانی شناسایی شد")
            return jsonify({
                'response': CRISIS_RESPONSE,
                'source': 'crisis',
                'is_crisis': True
            })

        # ===== تلاش برای استفاده از LLM =====
        llm_service = get_llm_service()

        if llm_service.is_available():
            response = llm_service.chat(user_message)

            if response:
                return jsonify({
                    'response': response,
                    'source': 'llm'
                })

        # ===== fallback: keyword-based =====
        response = get_fallback_response(user_message)
        return jsonify({
            'response': response,
            'source': 'fallback'
        })

    except Exception as e:
        logger.error(f"❌ خطا در چت‌بات: {e}")
        return jsonify({
            'response': 'متأسفم، یه مشکل فنی پیش اومد. لطفاً دوباره تلاش کن. 🙏',
            'source': 'error'
        }), 500


# ============================================================
# Fallback (اگه LLM کار نکرد)
# ============================================================

def get_fallback_response(message):
    """پاسخ پیش‌فرض اگه LLM کار نکنه"""
    msg = message.lower()

    # ===== سلام =====
    if any(w in msg for w in ['سلام', 'درود', 'صبح بخیر', 'عصر بخیر']):
        return random.choice(FALLBACK_RESPONSES['greeting'])

    # ===== خداحافظ =====
    if any(w in msg for w in ['خداحافظ', 'بای', 'فعلا']):
        return "خداحافظ عزیزم 🌙 مواظب خودت باش. هر وقت نیاز داشتی من اینجام."

    # ===== تشکر =====
    if any(w in msg for w in ['مرسی', 'ممنون', 'سپاس']):
        return "خواهش می‌کنم 🌸 خوشحالم که تونستم کمکت کنم."
        # ===== پیش‌فرض =====
    return random.choice(FALLBACK_RESPONSES['default'])