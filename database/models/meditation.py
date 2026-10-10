from database import db
from datetime import datetime


class Meditation(db.Model):
    __tablename__ = 'meditations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # morning, breathing, night
    duration = db.Column(db.Integer, nullable=False)  # مدت به ثانیه
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date,
            'type': self.type,
            'duration': self.duration,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }