from utils.garden_helper import give_seed
from utils.helpers import sanitize_input
from flask import Blueprint, request, jsonify, session
from database import db
from database.models import DailyNote
from datetime import datetime, timedelta, timezone

notes_bp = Blueprint('notes', __name__)


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
            note.title = data['title'].strip()
        if 'content' in data:
            note.content = data['content'].strip()
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