# ============================================================
# routes/diagnosis.py — تشخیص هوشمند
# ============================================================

from utils.garden_helper import give_seed
from utils.logger import logger
from extensions import limiter
from flask import Blueprint, request, jsonify, session
from database import db
from database.models import Diagnosis
from datetime import datetime
import json
import uuid
import os
from utils.helpers import sanitize_input, is_allowed_file
from config import get_config

diagnosis_bp = Blueprint('diagnosis', __name__)

UPLOAD_FOLDER = get_config().UPLOAD_FOLDER
ALLOWED_EXTENSIONS = get_config().ALLOWED_EXTENSIONS
LLM_ENABLED = get_config().LLM_ENABLED


# ============================================================
# سوالات چندگزینه‌ای (برای محاسبه‌ی MCQ)
# ============================================================

MCQ_TYPES = [
    'positive', 'negative', 'negative', 'positive', 'positive',
    'negative', 'negative', 'negative', 'negative',
    'negative', 'negative', 'negative', 'negative', 'negative', 'positive',
    'positive', 'positive', 'positive', 'positive', 'positive',
]

MCQ_WEIGHTS = [
    3, 3, 2, 1, 1,
    2, 3, 2, 3,
    3, 2, 2, 2, 3, 2,
    2, 3, 3, 2, 2,
]

MCQ_OPTIONS = {
    'اصلاً': 0.5, 'کمی': 1.5, 'تا حدی': 2.5, 'خیلی زیاد': 3.5,
    'هرگز': 0.5, 'چند روز': 1.5, 'بیش از نیمی از روزها': 2.5, 'تقریباً هر روز': 3.5,
    'خیلی بد': 0.5, 'بد': 1.5, 'متوسط': 2.5, 'خوب': 3.5,
    'خیلی کم‌تر': 0.5, 'کم‌تر': 1.5, 'مثل قبل': 2.5, 'بیشتر': 3.5,
    'به‌ندرت': 1.0, 'گاهی': 2.0, 'اغلب': 3.0,
}


# ============================================================
# محاسبه‌ی امتیاز MCQ
# ============================================================

def calculate_mcq_score(mc_answers):
    if len(mc_answers) < 20:
        return 0.0

    total_score = 0.0
    max_possible = 0.0

    for i, answer in enumerate(mc_answers[:20]):
        option_value = MCQ_OPTIONS.get(answer, 1.5)
        weight = MCQ_WEIGHTS[i] if i < len(MCQ_WEIGHTS) else 1

        if MCQ_TYPES[i] == 'negative':
            option_value = 4 - option_value

        total_score += option_value * weight
        max_possible += 3.5 * weight

    if max_possible == 0:
        return 0.0

    score = (total_score / max_possible) * 100
    return round(min(100, max(0, score)), 1)


# ============================================================
# تحلیل با LLM
# ============================================================

def analyze_with_llm(text_answers):
    """
    تحلیل با LLM

    Returns:
        dict یا None (اگه LLM در دسترس نبود)
    """
    if not LLM_ENABLED:
        return None

    valid_texts = [t for t in text_answers if t and len(t.strip()) >= 10]

    if not valid_texts:
        return None

    try:
        from utils.llm.service import get_llm_service
        llm_service = get_llm_service()

        if not llm_service.is_available():
            logger.warning("⚠️ LLMService در دسترس نیست")
            return None

        result = llm_service.analyze_text(text_answers)

        # ===== اگه result None بود، یعنی LLM کار نکرده =====
        if not result:
            logger.warning("⚠️ LLM نتیجه‌ی معتبر برنگرداند")
            return None

        return {
            'score': result.get('final_score', 0),
            'status': result.get('status', 'نامشخص'),
            'treatment': result.get('treatment', ''),
            'emotion': result.get('dominant_emotion', ''),
            'key_concerns': result.get('key_concerns', [])
        }

    except Exception as e:
        logger.error(f"❌ خطا در LLM: {e}")
        return None


# ============================================================
# تعیین سطح و درمان
# ============================================================

def get_prediction(score):
    """
    تعیین سطح بر اساس «نمره‌ی سلامت روان»

    نمره‌ی بالاتر = سلامت روانی بهتر
    - ۰ = سالم
    - ۱ = خفیف
    - ۲ = متوسط
    - ۳ = شدید
    """
    if score >= 65:
        return 0  # سالم
    elif score >= 45:
        return 1  # خفیف
    elif score >= 25:
        return 2  # متوسط
    else:
        return 3  # شدید


def get_treatment(prediction):
    treatments = [
        'وضعیت شما خوب است. به حفظ سلامت روان خود ادامه دهید.',
        'توصیه می‌شود روزانه ۱۰ دقیقه مدیتیشن انجام دهید و با دوستان خود صحبت کنید.',
        'توصیه می‌شود با یک روانشناس مشورت کنید و تمرینات تنفسی را روزانه انجام دهید.',
        'توصیه می‌شود در اسرع وقت با یک روانشناس متخصص مشورت کنید.'
    ]
    return treatments[prediction] if 0 <= prediction <= 3 else treatments[0]


# ============================================================
# تحلیل کامل
# ============================================================

def analyze_answers(mc_answers, text_answers):
    """
    تحلیل کامل پاسخ‌های کاربر

    ترکیب دو نمره:
    - mcq_score: نمره‌ی پرسشنامه چندگزینه‌ای
    - llm_score: نمره‌ی تحلیل متن باز توسط LLM

    نمره‌ی نهایی (final_score) = «نمره‌ی سلامت روان»
    """
    # ===== ۱. محاسبه‌ی نمره‌ی MCQ =====
    mcq_score = calculate_mcq_score(mc_answers)

    # ===== ۲. تحلیل متن باز با LLM =====
    valid_texts = [t for t in text_answers if t and len(t.strip()) >= 10]
    has_valid_text = len(valid_texts) > 0

    llm_result = None
    llm_score = 0
    llm_status = 'در دسترس نیست'
    llm_treatment = ''

    if LLM_ENABLED and has_valid_text:
        llm_result = analyze_with_llm(text_answers)

        if llm_result:
            llm_score = llm_result.get('score', 0)
            llm_status = llm_result.get('status', 'نامشخص')
            llm_treatment = llm_result.get('treatment', '')
        else:
            llm_status = 'LLM در دسترس نیست'
    else:
        if not LLM_ENABLED:
            llm_status = 'غیرفعال'
        else:
            llm_status = 'متنی نیست'

    # ===== ۳. محاسبه‌ی نمره‌ی نهایی =====
    # اگه LLM نمره‌ی معتبر داد، ترکیب کن
    # وگرنه فقط MCQ
    if llm_result and llm_score > 0:
        final_score = (mcq_score * 0.5) + (llm_score * 0.5)
    else:
        final_score = mcq_score

    final_score = round(final_score, 1)

    # ===== ۴. تعیین سطح =====
    prediction = get_prediction(final_score)

    # ===== ۵. توصیه‌ی درمانی =====
    if llm_treatment:
        treatment = llm_treatment
    else:
        treatment = get_treatment(prediction)

    # ===== ۶. خروجی =====
    return {
        'prediction': prediction,
        'score': final_score,
        'mcqScore': mcq_score,
        'llmScore': llm_score,
        'llmStatus': llm_status,
        'treatment': treatment
    }


# ============================================================
# ذخیره‌ی نمونه‌ی ناشناس برای بهبود مدل
# ============================================================

def save_anonymized_sample(mc_answers, text_answers, result):
    """
    ذخیره‌ی نمونه‌ی ناشناس (بدون اطلاعات کاربر)

    این داده برای بهبود مدل استفاده می‌شه، ولی:
    - هیچ user_id ذخیره نمی‌شه
    - هیچ فایل صوتی ذخیره نمی‌شه
    - فقط متن + نمره‌ها + تشخیص
    """
    try:
        # ===== مسیر فایل =====
        data_dir = os.path.join(get_config().BASE_DIR, 'data')
        os.makedirs(data_dir, exist_ok=True)
        samples_file = os.path.join(data_dir, 'training_samples.jsonl')

        # ===== نمونه‌ی ناشناس =====
        sample = {
            'timestamp': datetime.now().isoformat(),
            'mcq_answers': mc_answers,
            'text_answers': [t for t in text_answers if t and t.strip()],
            'mcq_score': result.get('mcqScore', 0),
            'llm_score': result.get('llmScore', 0),
            'final_score': result.get('score', 0),
            'prediction': result.get('prediction', 0),
            'llm_status': result.get('llmStatus', ''),
        }

        # ===== نوشتن (JSONL — هر خط یه نمونه) =====
        with open(samples_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')

        logger.info(f"📊 نمونه‌ی ناشناس ذخیره شد")

    except Exception as e:
        logger.warning(f"⚠️ خطا در ذخیره‌ی نمونه‌ی ناشناس: {e}")


# ============================================================
# /api/predict
# ============================================================

@diagnosis_bp.route('/api/predict', methods=['POST'])
@limiter.limit("3 per day")
def predict():
    audio_paths = []  # ← بیرون از try تا توی finally در دسترس باشه

    try:
        mc_answers = request.form.getlist('mc_answers[]')
        text_answers = request.form.getlist('text_answers[]')
        audio_files = request.files.getlist('audio_files[]')

        if len(mc_answers) < 20:
            return jsonify({'error': 'لطفاً به همه سوالات پاسخ دهید'}), 400

        if len(text_answers) < 3:
            return jsonify({'error': 'لطفاً به همه سوالات باز پاسخ دهید'}), 400

        text_answers = [sanitize_input(t) for t in text_answers]

        # ===== ذخیره‌ی موقت فایل‌های صوتی =====
        saved_audio = []

        for i, audio_file in enumerate(audio_files):
            if audio_file and audio_file.filename:
                if is_allowed_file(audio_file.filename, ALLOWED_EXTENSIONS):
                    filename = f"audio_{uuid.uuid4().hex[:8]}_{i}.wav"
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    audio_file.save(filepath)
                    saved_audio.append(filename)
                    audio_paths.append(filepath)

        # ===== تبدیل صوت به متن =====
        if audio_paths and text_answers:
            try:
                from utils.speech.service import get_speech_service
                speech_service = get_speech_service()

                if speech_service.is_available():
                    logger.info(f"🔄 در حال تبدیل {len(audio_paths)} فایل صوتی به متن...")

                    for i, audio_path in enumerate(audio_paths):
                        if i < len(text_answers) and not text_answers[i].strip():
                            transcribed = speech_service.transcribe(audio_path)
                            if transcribed:
                                text_answers[i] = transcribed
                                logger.info(f"✅ سوال {i+1} تبدیل شد ({len(transcribed)} کاراکتر)")

            except Exception as e:
                logger.warning(f"⚠️ خطا در تبدیل صوت: {e}")

        # ===== تحلیل =====
        result = analyze_answers(mc_answers, text_answers)

        # ===== ذخیره در دیتابیس (با user_id — برای خود کاربر) =====
        user_id = session.get('user_id')
        today = datetime.now().isoformat().split('T')[0]

        diagnosis = Diagnosis(
            user_id=user_id,
            date=today,
            mcq_score=result['mcqScore'],
            llm_score=result['llmScore'],
            final_score=result['score'],
            prediction=result['prediction'],
            treatment=result['treatment'],
            mc_answers=json.dumps(mc_answers),
            text_answers=json.dumps(text_answers),
            audio_files=json.dumps(saved_audio)
        )
        db.session.add(diagnosis)
        db.session.commit()
        give_seed(user_id, 'diagnosis')

        # ===== 📊 ذخیره‌ی نمونه‌ی ناشناس (بدون user_id) =====
        save_anonymized_sample(mc_answers, text_answers, result)

        return jsonify({
            'success': True,
            'diagnosis_id': diagnosis.id,
            'prediction': result['prediction'],
            'score': result['score'],
            'mcqScore': result['mcqScore'],
            'llmScore': result['llmScore'],
            'llmStatus': result['llmStatus'],
            'treatment': result['treatment'],
            'llmEnabled': LLM_ENABLED
        })

    except Exception as e:
        logger.error(f"❌ خطا در تحلیل: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        # ===== 🔒 پاک کردن فایل‌های صوتی (حریم خصوصی) =====
        for path in audio_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    logger.info(f"🗑️ فایل صوتی پاک شد: {os.path.basename(path)}")
            except Exception as e:
                logger.warning(f"⚠️ خطا در پاک کردن {path}: {e}")


# ============================================================
# /api/history
# ============================================================

@diagnosis_bp.route('/api/history', methods=['GET', 'DELETE'])
def history():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لاگین نیستید'}), 401

    if request.method == 'GET':
        diagnoses = Diagnosis.query.filter_by(user_id=user_id)\
            .order_by(Diagnosis.created_at.desc()).all()

        return jsonify([
            {
                'id': d.id,
                'date': d.date,
                'prediction': d.prediction,
                'final_score': d.final_score,
                'mcq_score': d.mcq_score,
                'llm_score': d.llm_score
            }
            for d in diagnoses
        ])

    elif request.method == 'DELETE':
        Diagnosis.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({'success': True})


# ============================================================
# /api/upload-audio
# ============================================================

@diagnosis_bp.route('/api/upload-audio', methods=['POST'])
@limiter.limit('9 per day')
def upload_audio():
    """آپلود فایل صوتی"""
    if 'audio' not in request.files:
        return jsonify({'error': 'فایلی ارسال نشده'}), 400

    audio_file = request.files['audio']

    if audio_file.filename == '':
        return jsonify({'error': 'نام فایل خالی است'}), 400

    if not is_allowed_file(audio_file.filename, ALLOWED_EXTENSIONS):
        return jsonify({'error': 'فرمت فایل مجاز نیست'}), 400

    filename = f"audio_{uuid.uuid4().hex[:8]}.wav"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    audio_file.save(filepath)

    return jsonify({
        'success': True,
        'filename': filename,
        'url': f'/uploads/{filename}'
    })


# ============================================================
# /uploads/<filename>
# ============================================================

@diagnosis_bp.route('/uploads/<filename>')
def serve_upload(filename):
    """سرو کردن فایل صوتی"""
    from flask import send_file
    return send_file(
        os.path.join(UPLOAD_FOLDER, filename),
        as_attachment=False
    )


# ============================================================
# /api/predict/status — چک وضعیت تشخیص
# ============================================================

@diagnosis_bp.route('/api/predict/status', methods=['GET'])
def predict_status():
    """چک کن کاربر چقدر تشخیص دیگه می‌تونه بده"""
    from flask import session
    from extensions import limiter

    # ===== پیش‌فرض =====
    limit = 3
    remaining = limit

    # ===== تلاش برای محاسبه =====
    try:
        today = datetime.now().isoformat().split('T')[0]
        user_id = session.get('user_id')

        if user_id:
            count_today = Diagnosis.query.filter_by(
                user_id=user_id,
                date=today
            ).count()
            remaining = max(0, limit - count_today)
        else:
            # کاربر لاگین نیست، نمی‌تونیم دقیق بگیم
            remaining = limit

    except Exception as e:
        logger.warning(f"⚠️ خطا در predict_status: {e}")

    return jsonify({
        'limit': limit,
        'remaining': remaining,
        'can_predict': remaining > 0
    })
