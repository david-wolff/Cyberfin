from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SurfData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    water_temperature = db.Column(db.Float, nullable=False)
    wave_direction = db.Column(db.Float, nullable=False)
    wave_height = db.Column(db.Float, nullable=False)
    wave_period = db.Column(db.Float, nullable=False)
    wind_direction = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)

    __table_args__ = (db.UniqueConstraint('date', 'time', name='_date_time_uc'),)
