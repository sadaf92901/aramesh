from utils.logger import logger
from utils.garden_helper import give_seed
from utils.helpers import sanitize_input,is_allowed_file
from flask import Blueprint, request, jsonify, session
from database import db
from database.models import DailyNote
from datetime import datetime, timedelta, timezone
import os
import uuid
from config import get_config

notes_bp = Blueprint('notes', __name__)
# ============================================================
# تنظیمات ضبط صدا
# ============================================================

UPLOAD_FOLDER = get_config().UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm', 'm4a'}
MAX_AUDIO_SIZE = 5 * 1024 * 1024  # ۵ مگابایت


@notes_bp.route('/api/notes', methods=['GET', 'POST'])
def handle_notes():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لطفاً وارد شوید'}), 401

    # ============================================================
    # GET — لیست یاداشت‌ها
    # ============================================================
    if request.method == 'GET':
        notes = DailyNote.query.filter_by(user_id=user_id).order_by(DailyNote.date.desc()).all()
        return jsonify([note.to_dict() for note in notes])

    # ============================================================
    # POST — ساخت یاداشت جدید
    # ============================================================
    elif request.method == 'POST':
        data = request.json

        content = sanitize_input(data.get('content', '').strip())
        title = sanitize_input(data.get('title', '').strip())

        if not content:
            return jsonify({'error': 'متن یاداشت را وارد کنید'}), 400

        today = datetime.now().isoformat().split('T')[0]

        note = DailyNote(
            user_id=user_id,
            date=today,
            title=title,
            content=content,
            mood=data.get('mood', ''),
            tags=','.join(data.get('tags', [])) if data.get('tags') else ''
        )

        db.session.add(note)
        db.session.commit()

        # ===== یه دانه به کاربر بده =====
        give_seed(user_id, 'note')

        return jsonify({'success': True, 'id': note.id})


@notes_bp.route('/api/notes/<int:note_id>', methods=['PUT', 'DELETE'])
def handle_note(note_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لطفاً وارد شوید'}), 401

    note = db.session.get(DailyNote, note_id)
    if not note:
        return jsonify({'error': 'یاداشت یافت نشد'}), 404
    if note.user_id != user_id:
        return jsonify({'error': 'دسترسی غیرمجاز'}), 403

    if request.method == 'PUT':
        data = request.json
        if 'title' in data:
            note.title = sanitize_input(data['title'].strip())
        if 'content' in data:
            note.content = sanitize_input(data['content'].strip())
        if 'mood' in data:
            note.mood = data['mood']
        if 'tags' in data:
            note.tags = ','.join(data['tags']) if data['tags'] else ''
        note.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        # ⚠️ توی PUT دانه نمی‌دیم (چون یاداشت جدید نیست)
        return jsonify({'success': True, 'id': note.id})

    elif request.method == 'DELETE':
        db.session.delete(note)
        db.session.commit()
        return jsonify({'success': True})


@notes_bp.route('/api/notes/stats', methods=['GET'])
def get_note_stats():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لطفاً وارد شوید'}), 401

    notes = DailyNote.query.filter_by(user_id=user_id).all()
    total = len(notes)

    mood_count = {}
    for note in notes:
        if note.mood:
            mood_count[note.mood] = mood_count.get(note.mood, 0) + 1
    most_common_mood = max(mood_count.items(), key=lambda x: x[1])[0] if mood_count else None

    dates = sorted(set([note.date for note in notes]))
    streak = 0
    if dates:
        today = datetime.now().isoformat().split('T')[0]
        if dates[-1] == today:
            streak = 1
            for i in range(len(dates) - 2, -1, -1):
                prev = datetime.strptime(dates[i], '%Y-%m-%d')
                curr = datetime.strptime(dates[i + 1], '%Y-%m-%d')
                if (curr - prev).days == 1:
                    streak += 1
                else:
                    break

    week_ago = (datetime.now() - timedelta(days=7)).isoformat().split('T')[0]
    this_week = len([n for n in notes if n.date >= week_ago])
    return jsonify({
        'total': total,
        'mood_count': mood_count,
        'most_common_mood': most_common_mood,
        'streak': streak,
        'this_week': this_week
    })


# ============================================================
# /api/notes/transcribe — تبدیل صدا به متن
# ============================================================

@notes_bp.route('/api/notes/transcribe', methods=['POST'])
def transcribe_note():
    """
    تبدیل صدای یاداشت به متن

    - فایل صوتی دریافت می‌شه
    - به متن تبدیل می‌شه (Whisper)
    - فایل صوتی پاک می‌شه
    - فقط متن برگردونده می‌شه
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'لطفاً وارد شوید'}), 401

    # ===== چک فایل =====
    if 'audio' not in request.files:
        return jsonify({'error': 'فایلی ارسال نشده'}), 400

    audio_file = request.files['audio']

    if not audio_file.filename:
        return jsonify({'error': 'نام فایل خالی است'}), 400

    # ===== چک فرمت =====
    if not is_allowed_file(audio_file.filename, ALLOWED_EXTENSIONS):
        return jsonify({'error': 'فرمت فایل مجاز نیست'}), 400

    # ===== چک حجم =====
    audio_file.seek(0, 2)  # برو به آخر
    size = audio_file.tell()
    audio_file.seek(0)  # برگرد به اول

    if size > MAX_AUDIO_SIZE:
        return jsonify({'error': 'حجم فایل بیشتر از ۵ مگابایته'}), 400

    # ===== ذخیره‌ی موقت =====
    ext = audio_file.filename.rsplit('.', 1)[1].lower()
    filename = f"note_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        audio_file.save(filepath)

        # ===== تبدیل به متن =====
        from utils.speech.service import get_speech_service
        speech_service = get_speech_service()

        if not speech_service.is_available():
            return jsonify({
                'error': 'سرویس تبدیل صوت در دسترس نیست. لطفاً بعداً تلاش کن.'
            }), 503

        logger.info(f"🎤 در حال تبدیل صوت یاداشت... ({size} bytes)")

        text = speech_service.transcribe(filepath)

        if not text or not text.strip():
            return jsonify({'error': 'تبدیل صوت ناموفق بود. دوباره تلاش کن.'}), 500

        # ===== Sanitize =====
        text = sanitize_input(text.strip())

        if not text:
            return jsonify({'error': 'متن استخراج‌شده خالیه'}), 400

        logger.info(f"✅ صوت به متن تبدیل شد ({len(text)} کاراکتر)")

        return jsonify({
            'success': True,
            'text': text
        })

    except Exception as e:
        logger.error(f"❌ خطا در transcribe یاداشت: {e}")
        return jsonify({'error': 'خطا در تبدیل صوت'}), 500

    finally:
        # ===== 🔒 پاک کردن صدا (حریم خصوصی) =====
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info(f"🗑️ فایل صوتی پاک شد: {filename}")
            except Exception as e:
                logger.warning(f"⚠️ خطا در پاک کردن {filepath}: {e}")
