from datetime import datetime
from app import db

class Check(db.Model):
    __tablename__ = 'checks'  # expliziter Tabellenname

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    tld = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'available' or 'taken' or 'error'
    ip = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
