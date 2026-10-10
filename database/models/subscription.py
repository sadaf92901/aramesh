from database.db import db
from datetime import datetime

from utils.helpers import utcnow
class Subscription(db.Model):
    """اشتراک کاربر"""
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # ===== پلن =====
    plan = db.Column(db.String(20), nullable=False)  # free, premium, pro
    status = db.Column(db.String(20), default='active')  # active, expired, cancelled

    # ===== زمان =====
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    # ===== پرداخت =====
    payment_id = db.Column(db.String(100), nullable=True)
    payment_amount = db.Column(db.Integer, nullable=True)
    payment_gateway = db.Column(db.String(20), nullable=True)  # zarinpal, idpay
    payment_status = db.Column(db.String(20), nullable=True)  # pending, success, failed

    # ===== متادیتا =====
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('subscriptions', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan': self.plan,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'payment_amount': self.payment_amount,
            'payment_gateway': self.payment_gateway,
            'payment_status': self.payment_status,
            'is_active': self.is_active(),
        }

    def is_active(self):
        """آیا اشتراک فعاله؟"""
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < utcnow():
            return False
        return True