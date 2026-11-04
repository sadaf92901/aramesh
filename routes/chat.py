from utils.logger import logger
from utils.helpers import is_persian
from extensions import limiter
from flask import Blueprint, request, jsonify, session
from utils.llm.service import get_llm_service
from config import get_config
import random
import json
import os

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
تو ارزشمند هستی و کمک در دسترسه. 💚"""


# ============================================================
# 🆕 حافظه‌ی چت (ذخیره‌ی تاریخچه در Session)
# ============================================================

def get_chat_history():
    """دریافت تاریخچه‌ی چت از Session"""
    if 'chat_history' not in session:
        session['chat_history'] = []
    return session['chat_history']


def add_to_chat_history(role, content):
    """اضافه کردن پیام به تاریخچه (حداکثر ۲۰ پیام آخر)"""
    history = get_chat_history()
    history.append({"role": role, "content": content})

    # نگه داشتن ۲۰ پیام آخر (۱۰ رفت و برگشت)
    if len(history) > 20:
        history = history[-20:]
    session['chat_history'] = history


def get_last_user_emotion():
    """تشخیص احساس از پیام‌های قبلی کاربر (اگه پیام فعلی مبهم بود)"""
    history = get_chat_history()
    for msg in reversed(history):
        if msg['role'] == 'user':
            return detect_emotion_by_keyword(msg['content'])
    return None


# ============================================================
# 🆕 ذخیره‌ی چت برای آموزش (با رضایت کاربر)
# ============================================================

def save_chat_for_training(user_message, bot_response):
    """ذخیره‌ی چت ناشناس برای آموزش مدل در آینده"""
    try:
        # فقط اگر کاربر رضایت داده باشه
        if not session.get('chat_consent'):
            return

        data_dir = os.path.join(get_config().BASE_DIR, 'data')
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, 'chat_training_samples.jsonl')

        sample = {
            "messages": [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": bot_response}
            ]
        }

        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')

    except Exception as e:
        logger.warning(f"⚠️ خطا در ذخیره چت: {e}")


# ============================================================
# تشخیص احساس با کلمه کلیدی
# ============================================================

def detect_emotion_by_keyword(message):
    """تشخیص احساس بر اساس کلمات کلیدی"""
    msg = message.lower()
    keywords = {
        "خستگی": ["خسته", "بی حال", "انرژی ندارم", "خوابم میاد", "کسالت", "فرسوده"],
        "غم": ["غم", "غمگین", "ناراحت", "دلگیر", "گریه", "افسرده", "دلم گرفته"],
        "اضطراب": ["اضطراب", "نگران", "استرس", "دلشوره", "ترس", "پنیک", "می‌ترسم"],
        "خشم": ["عصبانی", "خشم", "داد", "حرص", "دلخور", "کلافه"],
        "تنهایی": ["تنها", "بی کس", "کسی رو ندارم", "انزوا", "دلتنگ"],
        "خودارزیابی منفی": ["بی ارزش", "کافی نیستم", "خودم رو سرزنش", "شکست", "اعتماد ندارم"],
    }

    for emotion, words in keywords.items():
        if any(word in msg for word in words):
            return emotion
    return None


# ============================================================
# 🆕 تولید پاسخ همدلانه (با تنوع بالا)
# ============================================================

def get_empathy_response(emotion, user_message):
    """تولید پاسخ با تنوع بسیار بالا (بدون LLM)"""
    user_snippet = user_message[:25] + "..." if len(user_message) > 25 else user_message

    # ===== بخش اول: بازتاب (Reflective Listening) =====
    reflections = [
        f"می‌شنوم که می‌گی «{user_snippet}».",
        f"متوجه شدم گفتی «{user_snippet}».",
        f"از حرفات اینطور برداشت کردم که «{user_snippet}».",
        f"خب، پس «{user_snippet}».",
        f"دقیقاً متوجه شدم چی گفتی: «{user_snippet}»."
    ]

    # ===== بخش دوم: همدلی بر اساس احساس =====
    empathy_map = {
        "غم": ["خیلی سخته که غم رو تجربه کنی.", "احساس غم کاملاً طبیعیه و تو تنها نیستی.",
               "دلم برای این حال و هوات می‌سوزه.", "به نظر می‌رسه این روزها خیلی تحت فشار احساسی هستی."],
        "اضطراب": ["نفس عمیق بکش، این حس می‌گذره.", "اضطراب خیلی خسته‌کننده‌ست.",
                   "می‌فهمم چقدر این نگرانی‌ها می‌تونه آزاردهنده باشه.", "وقتی ذهن آروم نیست، همه‌چیز سخت‌تر می‌شه."],
        "خشم": ["کاملاً حق داری که عصبانی باشی.", "خشم یه احساس قدرتمنده و درکت می‌کنم.",
                "ممنون که این حس رو با من در میون گذاشتی.", "خوب شد گفتی، نگه داشتن خشم سخت‌تره."],
        "تنهایی": ["حس تنهایی خیلی سنگینه.", "ولی بدون که همین الان یکی هست که بهت گوش می‌ده.",
                   "من اینجام تا این حس رو با هم در میون بذاریم.", "هیچ‌کس نباید حس کنه کاملاً تنهام."],
        "خودارزیابی منفی": ["یادت باشه که تو به اندازه‌ی کافی خوب هستی.",
                            "ما گاهی خودمون رو بیشتر از حد قضاوت می‌کنیم.", "هیچ‌کس بی‌نقص نیست.",
                            "به جای سرزنش خودت، بیا با مهربونی به خودت نگاه کنیم."],
        "خستگی": ["خستگی جسمی و ذهنی می‌تونه طاقت‌فرسا باشه.", "انرژی تموم شده، این کاملاً طبیعیه.",
                  "آیا به خودت استراحت کافی می‌دی؟", "بیا یه نفس عمیق بکشیم و یه لحظه به خودت استراحت بده."],
        "استرس": ["استرس وقتی زیاد می‌شه، همه‌چیز رو سخت می‌کنه.", "احساس فشار زیاد، خیلی خسته‌کننده‌ست.",
                  "بیا با هم ببینیم چه چیزی بیشتر نگرانت کرده.", "یه قدم کوچیک می‌تونه از فشار کم کنه."],
        "خوشحالی": ["چه عالی که حالت خوبه! 🌸", "این انرژی مثبت خیلی ارزشمنده.", "خوشحالم که این حس خوب رو داری.",
                    "این لحظه‌های شاد رو قدر بدون."],
        "امید": ["این حس امیدواری خیلی ارزشمنده.", "داشتن امید یعنی داری به آینده باور داری.",
                 "بهت افتخار می‌کنم که داری تلاش می‌کنی.", "این مسیر درستیه."],
        "حمایت": ["داشتن حمایت اجتماعی یه نعمت بزرگه.", "خیلی خوبه که آدم‌هایی رو داری که حمایتت می‌کنن.",
                  "وقتی کسی هست که حمایتمون کنه، سختی‌ها آسون‌تر می‌شن.", "این ارتباط رو حفظ کن."],
    }

    # ===== بخش سوم: سوال برای ادامه مکالمه =====
    questions = [
        "می‌خوای بیشتر در موردش حرف بزنیم؟",
        "چه چیزی بیشتر از همه اذیتت می‌کنه؟",
        "دوست داری در موردش بیشتر توضیح بدی؟",
        "فکر می‌کنی چه چیزی می‌تونه کمکت کنه؟",
        "چطور می‌تونم بهتر کمکت کنم؟",
        "می‌خوای با هم یه راه‌حل پیدا کنیم؟",
        "این حس از کِی شروع شد؟"
    ]

    # ===== ترکیب تصادفی =====
    reflection = random.choice(reflections)
    empathy = random.choice(empathy_map.get(emotion, ["من اینجام تا بهت گوش بدم."]))
    question = random.choice(questions)

    # ===== ساختاردهی به جواب نهایی =====
    if random.random() > 0.5:
        response = f"{reflection} {empathy} {question}"
    else:
        response = f"{empathy} {question}"

    return response


# ============================================================
# Fallback (اگه LLM و RAG کار نکردن)
# ============================================================

def get_fallback_response(message):
    """پاسخ پیش‌فرض اگه LLM کار نکنه"""
    msg = message.lower()

    if any(w in msg for w in ['سلام', 'درود', 'صبح بخیر', 'عصر بخیر']):
        return random.choice(FALLBACK_RESPONSES['greeting'])

    if any(w in msg for w in ['خداحافظ', 'بای', 'فعلا']):
        return "خداحافظ عزیزم 🌙 مواظب خودت باش. هر وقت نیاز داشتی من اینجام."

    if any(w in msg for w in ['مرسی', 'ممنون', 'سپاس']):
        return "خواهش می‌کنم 🌸 خوشحالم که تونستم کمکت کنم."

    return random.choice(FALLBACK_RESPONSES['default'])


# ============================================================
# API: ثبت رضایت
# ============================================================

@chat_bp.route('/api/chat/consent', methods=['POST'])
def chat_consent():
    """ثبت رضایت کاربر برای ذخیره‌ی چت"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    data = request.json or {}
    consent = data.get('consent', False)

    session['chat_consent'] = consent
    return jsonify({'success': True, 'consent': consent})


@chat_bp.route('/api/chat/consent/status', methods=['GET'])
def chat_consent_status():
    """چک کردن اینکه آیا کاربر رضایت داده یا نه"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    has_decided = 'chat_consent' in session
    consent = session.get('chat_consent', False)

    return jsonify({
        'has_decided': has_decided,
        'consent': consent
    })


# ============================================================
# /api/chat (اصلی)
# ============================================================

@chat_bp.route('/api/chat', methods=['POST'])
@limiter.limit("50 per day")
def chat():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'برای چت باید وارد شوید'}), 401

    # 🆕 چک رضایت
    if 'chat_consent' not in session:
        return jsonify({
            'error': 'consent_required',
            'message': 'لطفاً ابتدا در مورد ذخیره‌سازی گفتگو تصمیم بگیرید.'
        }), 403

    try:
        user_message = request.json.get('message', '').strip()

        if not user_message:
            if not user_message:
                return jsonify({'error': 'پیامی ارسال نشده'}), 400

            # 🆕 چک زبان فارسی
            if not is_persian(user_message):
                return jsonify({
                    'error': 'لطفاً پیام خود را به زبان فارسی بنویسید.'
                }), 400
            return jsonify({'error': 'پیامی ارسال نشده'}), 400

        add_to_chat_history('user', user_message)

        if any(kw in user_message for kw in CRISIS_KEYWORDS):
            logger.warning(f"🆘 پیام بحرانی شناسایی شد")
            add_to_chat_history('bot', CRISIS_RESPONSE)
            save_chat_for_training(user_message, CRISIS_RESPONSE)
            return jsonify({
                'response': CRISIS_RESPONSE,
                'source': 'crisis',
                'is_crisis': True
            })

        llm_service = get_llm_service()

        if llm_service.is_available():
            response = llm_service.chat(user_message)

            if response:
                add_to_chat_history('bot', response)
                save_chat_for_training(user_message, response)
                return jsonify({
                    'response': response,
                    'source': 'llm'
                })

        logger.info("🔄 LLM در دسترس نیست، تلاش برای RAG در چت...")

        emotion = detect_emotion_by_keyword(user_message)

        if not emotion:
            try:
                from utils.rag.service import get_rag_service
                rag = get_rag_service()
                if rag.is_ready():
                    results = rag.retriever.retrieve(user_message, top_k=1)
                    if results:
                        emotion = results[0]['document'].get('emotion')
            except Exception as e:
                logger.warning(f"⚠️ خطا در RAG: {e}")

        if not emotion:
            emotion = get_last_user_emotion()

        if emotion:
            response = get_empathy_response(emotion, user_message)
            add_to_chat_history('bot', response)
            save_chat_for_training(user_message, response)
            return jsonify({
                'response': response,
                'source': 'rag_fallback',
                'emotion': emotion
            })

        response = get_fallback_response(user_message)
        add_to_chat_history('bot', response)
        save_chat_for_training(user_message, response)
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
