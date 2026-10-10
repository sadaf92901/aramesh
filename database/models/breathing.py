from database.db import db
from datetime import datetime


class BreathingExercise(db.Model):
    __tablename__ = 'breathing_exercises'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, default=1)
    duration = db.Column(db.Integer, default=30)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date,
            'count': self.count,
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }