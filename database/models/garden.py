from database.db import db
from datetime import datetime


class Garden(db.Model):
    """باغ کاربر — دانه‌ها و گل‌های کاشته‌شده"""
    __tablename__ = 'garden'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    activity_type = db.Column(db.String(20), nullable=False, index=True)
    flower_type = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    is_planted = db.Column(db.Boolean, default=False)
    planted_at = db.Column(db.DateTime, nullable=True)
    position_x = db.Column(db.Integer, nullable=True)  # ← موقعیت افقی
    position_y = db.Column(db.Integer, nullable=True)  # ← موقعیت عمودی
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('garden', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'flower_type': self.flower_type,
            'date': self.date,
            'is_planted': self.is_planted,
            'planted_at': self.planted_at.isoformat() if self.planted_at else None,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }