import os
from flask import Blueprint, render_template, session, redirect, url_for, send_file, current_app

pages_bp = Blueprint('pages', __name__)


# ============================================================
# صفحات عمومی (برای همه)
# ============================================================

@pages_bp.route('/')
def index():
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)
    if user_id or is_guest:
        return render_template('index.html')
    return render_template('login.html')


@pages_bp.route('/login')
def login_page():
    session.clear()
    return render_template('login.html')


@pages_bp.route('/questionnaire')
def questionnaire():
    return render_template('questionnaire.html')


@pages_bp.route('/result')
def result():
    return render_template('result.html')


@pages_bp.route('/privacy')
def privacy_page():
    return render_template('privacy.html')


@pages_bp.route('/terms')
def terms_page():
    return render_template('terms.html')


@pages_bp.route('/about')
def about_page():
    return render_template('about.html')


@pages_bp.route('/onboarding')
def onboarding_page():
    return render_template('onboarding.html')


@pages_bp.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot_password.html')


@pages_bp.route('/reset-password')
def reset_password_page():
    return render_template('reset_password.html')


@pages_bp.route('/offline')
def offline_page():
    return render_template('offline.html')


# ============================================================
# صفحات نیازمند لاگین (مهمان نمیتونه)
# ============================================================

@pages_bp.route('/chat')
def chat_page():
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)
    if not user_id and not is_guest:
        return redirect(url_for('pages.index'))
    if is_guest:
        return redirect(url_for('pages.index') + '?guest_locked=1')
    return render_template('chat.html')


@pages_bp.route('/tools')
def tools_page():
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)
    if not user_id and not is_guest:
        return redirect(url_for('pages.index'))
    if is_guest:
        return redirect(url_for('pages.index') + '?guest_locked=1')
    return render_template('tools.html')


@pages_bp.route('/journal')
def journal_page():
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)
    if not user_id and not is_guest:
        return redirect(url_for('pages.index'))
    if is_guest:
        return redirect(url_for('pages.index') + '?guest_locked=1')
    return render_template('journal.html')


@pages_bp.route('/weekly-plan')
def weekly_plan_page():
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)
    if not user_id and not is_guest:
        return redirect(url_for('pages.index'))
    if is_guest:
        return redirect(url_for('pages.index') + '?guest_locked=1')
    return render_template('weekly_plan.html')


@pages_bp.route('/meditation')
def meditation_page():
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)
    if not user_id and not is_guest:
        return redirect(url_for('pages.index'))
    if is_guest:
        return redirect(url_for('pages.index') + '?guest_locked=1')
    return render_template('meditation.html')


@pages_bp.route('/breathing')
def breathing_page():
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)
    if not user_id and not is_guest:
        return redirect(url_for('pages.index'))
    if is_guest:
        return redirect(url_for('pages.index') + '?guest_locked=1')
    return render_template('breathing.html')


@pages_bp.route('/history')
def history_page():
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)
    if not user_id and not is_guest:
        return redirect(url_for('pages.index'))
    if is_guest:
        return redirect(url_for('pages.index') + '?guest_locked=1')
    return render_template('history.html')


@pages_bp.route('/profile')
def profile_page():
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)
    if not user_id and not is_guest:
        return redirect(url_for('pages.index'))
    if is_guest:
        return redirect(url_for('pages.index') + '?guest_locked=1')
    return render_template('profile.html')


@pages_bp.route('/progress')
def progress_page():
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)
    if not user_id and not is_guest:
        return redirect(url_for('pages.index'))
    if is_guest:
        return redirect(url_for('pages.index') + '?guest_locked=1')
    return render_template('progress.html')


# ============================================================
# PWA — سرو فایل‌های ریشه
# ============================================================

@pages_bp.route('/favicon.ico')
def favicon():
    return send_file(
        os.path.join(current_app.static_folder, 'images', 'favicon.ico'),
        mimetype='image/vnd.microsoft.icon'
    )

@pages_bp.route('/garden')
def garden_page():
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)
    if not user_id and not is_guest:
        return redirect(url_for('pages.index'))
    if is_guest:
        return redirect(url_for('pages.index') + '?guest_locked=1')
    return render_template('garden.html')


@pages_bp.route('/subscription')
def subscription_page():
    user_id = session.get('user_id')
    is_guest = session.get('is_guest', False)

    if not user_id and not is_guest:
        return redirect(url_for('pages.index'))
    if is_guest:
        return redirect(url_for('pages.index') + '?guest_locked=1')

    return render_template('subscription.html')