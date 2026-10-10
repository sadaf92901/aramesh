# ============================================================
# مدل برنامه درمانی هفتگی
# ============================================================

from database import db
from datetime import datetime
import json


class WeeklyPlan(db.Model):
    __tablename__ = 'weekly_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    week_start = db.Column(db.String(20), nullable=False)  # تاریخ شروع هفته
    week_end = db.Column(db.String(20), nullable=False)  # تاریخ پایان هفته

    level = db.Column(db.Integer, nullable=False)  # سطح تشخیص (0-3)
    plan_data = db.Column(db.Text, nullable=False)  # داده‌های برنامه (JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('weekly_plans', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'week_start': self.week_start,
            'week_end': self.week_end,
            'level': self.level,
            'plan_data': json.loads(self.plan_data) if self.plan_data else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }