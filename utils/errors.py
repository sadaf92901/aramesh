# ============================================================
# مدیریت خطاها
# ============================================================

from flask import jsonify, request, render_template


# ============================================================
# کلاس‌های خطا
# ============================================================

class AppError(Exception):
    """خطای پایه‌ی اپ"""
    status_code = 500
    message = 'خطای داخلی سرور'

    def __init__(self, message=None, status_code=None):
        super().__init__()
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code

    def to_dict(self):
        return {
            'error': self.message,
            'status': 'error'
        }


class ValidationError(AppError):
    """خطای اعتبارسنجی"""
    status_code = 400
    message = 'اطلاعات ارسالی نامعتبر است'


class AuthError(AppError):
    """خطای احراز هویت"""
    status_code = 401
    message = 'لطفاً وارد شوید'


class ForbiddenError(AppError):
    """خطای دسترسی"""
    status_code = 403
    message = 'دسترسی غیرمجاز'


class NotFoundError(AppError):
    """خطای پیدا نشدن"""
    status_code = 404
    message = 'موردی یافت نشد'


class ServerError(AppError):
    """خطای سرور"""
    status_code = 500
    message = 'خطای داخلی سرور'


# ============================================================
# ثبت error handlerها
# ============================================================

def register_error_handlers(app):
    """ثبت همه‌ی error handlerها"""

    @app.errorhandler(AppError)
    def handle_app_error(error):
        response = error.to_dict()
        if hasattr(app, 'logger'):
            app.logger.warning(f'⚠️ {error.__class__.__name__}: {error.message}')
        return jsonify(response), error.status_code

    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'درخواست نامعتبر',
                'status': 'error'
            }), 400
        return render_template('404.html'), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'لطفاً وارد شوید',
            'status': 'error'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'دسترسی غیرمجاز',
            'status': 'error'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'صفحه مورد نظر یافت نشد',
                'status': 'error'
            }), 404
        return render_template('404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'متد غیرمجاز',
            'status': 'error'
        }), 405

    @app.errorhandler(500)
    def server_error(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'خطای داخلی سرور. لطفاً دوباره تلاش کنید.',
                'status': 'error'
            }), 500
        return render_template('500.html'), 500