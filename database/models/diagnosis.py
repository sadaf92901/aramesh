from database.db import db
from datetime import datetime

class Diagnosis(db.Model):
    __tablename__ = 'diagnosis'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date = db.Column(db.String(20), nullable=False)
    mcq_score = db.Column(db.Float, default=0)
    llm_score = db.Column(db.Float, default=0)
    final_score = db.Column(db.Float, nullable=False)
    prediction = db.Column(db.Integer, nullable=False)
    treatment = db.Column(db.Text, default='')
    mc_answers = db.Column(db.Text, default='[]')
    text_answers = db.Column(db.Text, default='[]')
    audio_files = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('diagnoses', lazy=True))