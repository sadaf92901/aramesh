from database.db import db
from datetime import datetime

class DailyStatus(db.Model):
    __tablename__ = 'daily_status'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date = db.Column(db.String(20), nullable=False)
    mood = db.Column(db.String(20))
    energy = db.Column(db.String(20))
    sleep = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('daily_statuses', lazy=True))