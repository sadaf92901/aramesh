from utils.logger import logger
from utils.helpers import is_persian
from extensions import limiter
from flask import Blueprint, request, jsonify, session
from utils.llm.service import get_llm_service
from database import db
from config import get_config
import random
import json
import os

chat_bp = Blueprint('chat', __name__)

# ============================================================
# پاسخ‌های fallback
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
# حافظه‌ی چت
# ============================================================

def get_chat_history():
    if 'chat_history' not in session:
        session['chat_history'] = []
    return session['chat_history']


def add_to_chat_history(role, content):
    """ذخیره پیام در دیتابیس و Session"""
    user_id = session.get('user_id')
    if user_id:
        try:
            from database.models import ChatMessage
            msg = ChatMessage(user_id=user_id, role=role, content=content)
            db.session.add(msg)
            db.session.commit()
        except Exception as e:
            logger.warning(f"⚠️ خطا در ذخیره تاریخچه چت: {e}")
            db.session.rollback()

    history = get_chat_history()
    history.append({"role": role, "content": content})
    if len(history) > 20:
        history = history[-20:]
    session['chat_history'] = history


# ============================================================
# ذخیره‌ی چت برای آموزش (با رضایت)
# ============================================================

def save_chat_for_training(user_message, bot_response):
    try:
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
# تشخیص احساس با کلمه کلیدی (کامل و جامع)
# ============================================================

def detect_emotion_by_keyword(message):
    msg = message.lower()
    keywords = {
        "خستگی": [
            "خسته", "بی حال", "انرژی ندارم", "انرژی نمیده", "خوابم میاد",
            "کسالت", "فرسوده", "نمی‌تونم", "نمی تونم", "دیگه نمی‌تونم",
            "خسته‌ام", "خسته ام", "موندگی", "بی رمق", "خستگی",
            "ذهنی", "جسمی", "خسته شدم", "کم آوردم", "کسل", "داغون",
            "خواب آلود", "افت", "افت کرده", "انرژی تموم",
            "تخلیه", "خالی", "خسته‌کنه", "خسته کننده", "درمانده", "وازده",
            "خسته‌ی", "خسته ی", "دیگه کشش ندارم", "مغزم کار نمی‌کنه", "خسته جونی"
        ],
        "غم": [
            "غم", "غمگین", "ناراحت", "دلگیر", "گریه", "افسرده", "دلم گرفته",
            "بد", "خیلی بد", "افتضاح", "داغون", "نابود", "پوچ", "بی معنی",
            "احساس بدی", "نمی‌خوام", "حالم بد", "زندگیم به هم ریخته",
            "دلگیرم", "دل شکسته", "ناامید", "افسردگی", "بی انگیزه",
            "بی حوصله", "دلتنگ", "غمگینم", "ناراحتم", "گریه ام گرفت",
            "بغض", "بغض کردم", "داغونم", "پوچم", "بی معنیه", "حالم خوب نیست",
            "نا امید", "امید ندارم", "امیدمو از دست دادم", "بی امید", "ناامیدم",
            "غمگین هستم", "دپرس", "دپرسی", "افسردگی دارم", "زندگیم سیاهه",
            "دلشکسته", "دل شکست", "احساس بی ارزشی", "خسته از زندگی"
        ],
        "اضطراب": [
            "اضطراب", "نگران", "استرس", "دلشوره", "ترس", "پنیک",
            "می‌ترسم", "نگرانی", "تنش", "دلهره", "حواسم پرت",
            "خوابم نمی‌بره", "قلبم تند", "نفس کم", "دستام می‌لرزه",
            "مضطرب", "نگرانم", "استرس دارم", "دلشوره دارم", "می‌ترسم",
            "وحشت", "وحشت زده", "ترسیده", "نفس تنگ", "خفگی",
            "تپش قلب", "عرق", "لرزش", "بی قرار", "بی قراری", "ناآروم",
            "استرس شدید", "اضطراب شدید", "حمله پنیک", "استرس داره منو میخوره",
            "نگران آینده", "نگران فردا", "دلشوره شدید", "تنش عصبی"
        ],
        "خشم": [
            "عصبانی", "خشم", "داد", "حرص", "دلخور", "کلافه", "دعوا",
            "بحث", "ناراحتی", "متنفر", "نفرت", "کینه", "عصبانیت", "مغزمو خورد",
            "عصبانی ام", "عصبانی هستم", "عصبی", "داد زدم", "داد می‌زنم",
            "حرصم گرفت", "کلافه ام", "کلافه شدم", "دعوا کردم", "بحث کردم",
            "متنفرم", "نفرت دارم", "کینه دارم", "خشمگین", "قاطی کردم",
            "منفجر", "منفجر شدم", "دیوونه شدم", "عصبانی شدم", "خشمگین شدم",
            "حرص خوردم", "دلم می‌خواد داد بزنم", "از کوره در رفتم", "پکر شدم"
        ],
        "تنهایی": [
            "تنها", "بی کس", "کسی رو ندارم", "انزوا", "دلتنگ", "بلاتکلیف",
            "کسی نیست", "هیچ‌کس", "تنهایی", "فقط من", "کسی حالم رو نمی‌فهمه",
            "تنهام", "تنها هستم", "تنهایی می‌کنم", "احساس تنهایی",
            "بی کسم", "گوشه گیر", "منزوی",
            "بلاتکلیفم", "دلتنگم", "دلم تنگه", "هیچ‌کس نیست",
            "هیچ‌کس منو نمی‌فهمه", "کسی درکم نمی‌کنه", "همه رفتن", "رها شدم",
            "احساس می‌کنم تنهام", "دوست ندارم", "کسی رو ندارم که", "درک نشدم",
            "بی‌کس و کار", "دلگیرم از همه"
        ],
        "خودارزیابی منفی": [
            "بی ارزش", "کافی نیستم", "خودم رو سرزنش", "شکست", "اعتماد ندارم",
            "بی مصرف", "بدرد نخور", "هیچی نیستم", "شرمنده", "گناهکار", "فایده ندارم",
            "بی ارزشم", "خودمو سرزنش می‌کنم", "شکست خوردم",
            "به خودم اعتماد ندارم", "بی مصرفم", "بدرد نمی‌خورم",
            "شرمنده ام", "گناهکارم", "بی کفایت", "حقیر",
            "خودمو دوست ندارم", "از خودم بدم میاد", "بی عرضه",
            "احساس بی ارزشی می‌کنم", "هیچی نیستم", "خودمو قبول ندارم", "ضعیفم"
        ],
    }

    for emotion, words in keywords.items():
        if any(word in msg for word in words):
            return emotion
    return None


# ============================================================
# تولید پاسخ با سوال و هدایت به بخش‌ها
# ============================================================

def get_empathy_response(emotion, user_message):
    """تولید پاسخ هوشمند با سوالات (بدون تکرار سوال)"""

    emotion_data = {
        "غم": {
            "empathy": [
                "می‌شنوم که این روزها حالت خوب نیست و غم سنگینی داری.",
                "درکت می‌کنم، احساس غم می‌تونه خیلی خسته‌کننده باشه.",
                "دلم برای این حال و هوات می‌سوزه. این حس کاملاً طبیعیه."
            ],
            "questions": [
                "چه چیزی بیشتر از همه ناراحتت کرده؟",
                "دلت می‌خواد در موردش بیشتر بگی؟",
                "چند وقته این حس رو داری؟",
                "چه چیزی معمولاً حالت رو بهتر می‌کنه؟"
            ],
            "suggestions": [
                ("می‌خوای یه مدیتیشن ۵ دقیقه‌ای انجام بدیم؟", "/meditation"),
                ("دوست داری یه یادداشت از احساست بنویسی؟", "/journal")
            ]
        },
        "اضطراب": {
            "empathy": [
                "به نظر می‌رسه این روزها نگرانی‌های زیادی داری.",
                "نفس عمیق بکش، این حس می‌گذره.",
                "می‌فهمم چقدر این اضطراب و دلشوره می‌تونه آزاردهنده باشه."
            ],
            "questions": [
                "چه چیزی بیشتر از همه نگرانت کرده؟",
                "این نگرانی روی بدنت هم اثر گذاشته؟ (مثلاً قلبت تند می‌زنه؟)",
                "چند وقته این احساس رو داری؟",
                "می‌خوای با هم یه تمرین تنفس ساده انجام بدیم؟"
            ],
            "suggestions": [
                ("می‌خوای با هم یه تمرین تنفس عمیق انجام بدیم؟", "/breathing"),
                ("دوست داری یه مدیتیشن آرام‌بخش امتحان کنی؟", "/meditation")
            ]
        },
        "خشم": {
            "empathy": [
                "کاملاً حق داری که عصبانی باشی، این حس خیلی قدرتمنده.",
                "ممنون که این خشم رو با من در میون گذاشتی. نگه داشتنش سخت‌تره.",
                "می‌فهمم چیزی خیلی اذیتت کرده که این‌طوری عصبانیت."
            ],
            "questions": [
                "چه چیزی باعث شد این‌قدر عصبانی بشی؟",
                "دوست داری با هم آروم بشیم و در موردش حرف بزنیم؟",
                "قبلاً هم این‌طوری شدی؟",
                "چطور می‌تونیم این خشم رو مدیریت کنیم؟"
            ],
            "suggestions": [
                ("بیا یه تمرین تنفس ۴-۴-۴ انجام بدیم تا آروم بشی.", "/breathing"),
                ("دوست داری احساست رو توی روزنگار تخلیه کنی؟", "/journal")
            ]
        },
        "تنهایی": {
            "empathy": [
                "حس تنهایی خیلی سنگینه و درکت می‌کنم.",
                "ولی بدون که همین الان یکی هست که بهت گوش می‌ده، من اینجام.",
                "این حس که کسی درکت نمی‌کنه واقعاً سخته."
            ],
            "questions": [
                "چند وقته احساس تنهایی می‌کنی؟",
                "آیا کسی هست که بتونی باهاش حرف بزنی؟",
                "چه چیزی می‌تونه این حس رو کمتر کنه؟",
                "دوست داری با یه نفر صحبت کنی؟"
            ],
            "suggestions": [
                ("دوست داری توی روزنگار از احساست بنویسی؟", "/journal"),
                ("می‌خوای یه مدیتیشن برای آرامش انجام بدیم؟", "/meditation")
            ]
        },
        "خودارزیابی منفی": {
            "empathy": [
                "به نظر می‌رسه داری خودت رو سرزنش می‌کنی.",
                "یادت باشه که تو به اندازه‌ی کافی خوب هستی و هیچ‌کس بی‌نقص نیست.",
                "ما گاهی خودمون رو بیشتر از حد قضاوت می‌کنیم."
            ],
            "questions": [
                "چرا فکر می‌کنی کافی نیستی؟",
                "چه چیزی باعث شد این فکر به سرت بیاد؟",
                "دوست داری با هم ببینیم این فکر از کجا اومده؟",
                "چطور می‌تونیم این حس رو تغییر بدیم؟"
            ],
            "suggestions": [
                ("دوست داری یه تمرین شکرگزاری انجام بدیم؟", "/meditation"),
                ("بیا یه یادداشت از چیزهای خوب زندگی‌ات بنویسیم.", "/journal")
            ]
        },
        "خستگی": {
            "empathy": [
                "به نظر می‌رسه انرژی‌ت کاملاً تموم شده و خیلی خسته‌ای.",
                "این خستگی جسمی و ذهنی می‌تونه طاقت‌فرسا باشه.",
                "بیا یه نفس عمیق بکشیم و یه لحظه به خودت استراحت بده."
            ],
            "questions": [
                "خستگی جسمیه یا ذهنی؟",
                "چند وقته این‌طوری هستی؟",
                "خواب کافی داری؟",
                "چه کاری می‌تونه بهت انرژی بده؟"
            ],
            "suggestions": [
                ("می‌خوای یه مدیتیشن قبل از خواب انجام بدیم؟", "/meditation"),
                ("دوست داری یه تمرین تنفس کوتاه انجام بدیم؟", "/breathing")
            ]
        },
        "استرس": {
            "empathy": [
                "به نظر می‌رسه فشار و استرس زیادی تحمل می‌کنی.",
                "استرس وقتی زیاد می‌شه، همه‌چیز رو سخت می‌کنه.",
                "بیا با هم ببینیم چه چیزی بیشتر نگرانت کرده."
            ],
            "questions": [
                "چه چیزی بیشتر تحت فشارت گذاشته؟",
                "این استرس روی خوابت اثر گذاشته؟",
                "می‌خوای با هم چند تا تکنیک ساده برای مدیریت استرس یاد بگیریم؟",
                "چند وقته این حس رو داری؟"
            ],
            "suggestions": [
                ("بیا همین الان یه تمرین تنفس ۱ دقیقه‌ای انجام بدیم.", "/breathing"),
                ("دوست داری یه مدیتیشن برای کاهش استرس انجام بدیم؟", "/meditation")
            ]
        },
    }

    # دریافت داده‌های احساس
    data = emotion_data.get(emotion, {
        "empathy": ["من اینجام تا بهت گوش بدم."],
        "questions": ["می‌خوای بیشتر در موردش حرف بزنیم؟"],
        "suggestions": []
    })

    empathy = random.choice(data["empathy"])

    # انتخاب سوال (اولین سوالی که توی تاریخچه نپرسیده)
    question = data["questions"][0]  # پیش‌فرض
    history = get_chat_history()
    bot_messages = [msg['content'] for msg in history if msg['role'] == 'bot']

    # پیدا کردن اولین سوالی که هنوز پرسیده نشده
    for q in data["questions"]:
        if not any(q in bot_msg for bot_msg in bot_messages):
            question = q
            break

    # ساخت پاسخ
    response = f"{empathy} {question}"

    # پیشنهاد (فقط برای پیام‌های طولانی)
    if data["suggestions"] and len(user_message) > 15:
        suggestion_text, suggestion_link = random.choice(data["suggestions"])
        response += f"\n\n💡 <strong>{suggestion_text}</strong> <a href='{suggestion_link}' style='color: #8B5CF6; text-decoration: underline; font-weight: 700;'>اینجا کلیک کن</a>"

    return response


# ============================================================
# 🆕 تولید پاسخ چت با استفاده از دیتاست RAG
# ============================================================

def get_rag_chat_response(user_message):
    """جستجو در دیتاست برای پیدا کردن جواب همدلانه"""
    try:
        from utils.rag.service import get_rag_service
        rag = get_rag_service()

        if not rag.is_ready():
            return None

        # جستجوی نمونه‌های مشابه
        results = rag.retriever.retrieve(user_message, top_k=1)

        if not results:
            return None

        doc = results[0]['document']
        emotion = doc.get('emotion', 'نامشخص')
        similarity = results[0]['score']

        # اگر شباهت خیلی پایین بود، بی‌خیال شو (بذار کلمات کلیدی تصمیم بگیرن)
        if similarity < 0.2:
            return None

        logger.info(f"✅ RAG پاسخ پیدا کرد: احساس={emotion}, شباهت={similarity}")

        # تولید پاسخ همدلانه بر اساس احساس پیدا شده
        return get_empathy_response(emotion, user_message)

    except Exception as e:
        logger.warning(f"⚠️ خطا در RAG چت: {e}")
        return None


# ============================================================
# Fallback
# ============================================================

def get_fallback_response(message):
    msg = message.lower()

    if any(w in msg for w in ['سلام', 'درود', 'صبح بخیر', 'عصر بخیر']):
        return random.choice(FALLBACK_RESPONSES['greeting'])

    if any(w in msg for w in ['خداحافظ', 'بای', 'فعلا']):
        return "خداحافظ عزیزم 🌙 مواظب خودت باش. هر وقت نیاز داشتی من اینجام."

    if any(w in msg for w in ['مرسی', 'ممنون', 'سپاس']):
        return "خواهش می‌کنم 🌸 خوشحالم که تونستم کمکت کنم."

    return random.choice(FALLBACK_RESPONSES['default'])


# ============================================================
# API رضایت
# ============================================================

@chat_bp.route('/api/chat/consent', methods=['POST'])
def chat_consent():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    data = request.json or {}
    consent = data.get('consent', False)
    session['chat_consent'] = consent
    return jsonify({'success': True, 'consent': consent})


@chat_bp.route('/api/chat/consent/status', methods=['GET'])
def chat_consent_status():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    return jsonify({
        'has_decided': 'chat_consent' in session,
        'consent': session.get('chat_consent', False)
    })


# ============================================================
# API دریافت تاریخچه چت
# ============================================================

@chat_bp.route('/api/chat/history', methods=['GET'])
def get_chat_history_api():
    """دریافت چت‌های قبلی کاربر"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    from database.models import ChatMessage
    messages = ChatMessage.query.filter_by(user_id=user_id) \
        .order_by(ChatMessage.created_at.asc()).limit(50).all()

    return jsonify([{
        'role': m.role,
        'content': m.content,
        'created_at': m.created_at.isoformat()
    } for m in messages])


# ============================================================
# /api/chat (اصلی)
# ============================================================

@chat_bp.route('/api/chat', methods=['POST'])
@limiter.limit("50 per day")
def chat():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'برای چت باید وارد شوید'}), 401

    if 'chat_consent' not in session:
        return jsonify({
            'error': 'consent_required',
            'message': 'لطفاً ابتدا در مورد ذخیره‌سازی گفتگو تصمیم بگیرید.'
        }), 403

    try:
        user_message = request.json.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'پیامی ارسال نشده'}), 400

        if not is_persian(user_message):
            return jsonify({
                'error': 'لطفاً پیام خود را به زبان فارسی بنویسید.'
            }), 400

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
                return jsonify({'response': response, 'source': 'llm'})

        logger.info("🔄 LLM در دسترس نیست، تلاش برای RAG در چت...")

        # ۱. اول از RAG (دیتاست) استفاده کن
        response = get_rag_chat_response(user_message)
        if response:
            add_to_chat_history('bot', response)
            save_chat_for_training(user_message, response)
            return jsonify({
                'response': response,
                'source': 'rag'
            })

        # ۲. اگه RAG جواب نداد، از کلمات کلیدی استفاده کن
        logger.info("🔄 RAG جواب نداد، استفاده از کلمات کلیدی...")
        emotion = detect_emotion_by_keyword(user_message)

        # ۳. اگه پیدا نشد، از حافظه (پیام‌های قبلی) استفاده کن
        if not emotion:
            from database.models import ChatMessage
            last_msgs = ChatMessage.query.filter_by(user_id=user_id, role='user') \
                .order_by(ChatMessage.created_at.desc()).limit(3).all()

            for msg in last_msgs:
                prev_emotion = detect_emotion_by_keyword(msg.content)
                if prev_emotion:
                    emotion = prev_emotion
                    logger.info(f"🧠 استفاده از حافظه: احساس قبلی = {emotion}")
                    break

        # ۴. تولید پاسخ
        if emotion:
            response = get_empathy_response(emotion, user_message)
            add_to_chat_history('bot', response)
            save_chat_for_training(user_message, response)
            return jsonify({
                'response': response,
                'source': 'keyword',
                'emotion': emotion
            })

        # ۵. اگه هیچی پیدا نشد، از جواب‌های ساده استفاده کن
        response = get_fallback_response(user_message)
        add_to_chat_history('bot', response)
        save_chat_for_training(user_message, response)
        return jsonify({'response': response, 'source': 'fallback'})

    except Exception as e:
        logger.error(f"❌ خطا در چت‌بات: {e}")
        return jsonify({
            'response': 'متأسفم، یه مشکل فنی پیش اومد. لطفاً دوباره تلاش کن. 🙏',
            'source': 'error'
        }), 500
