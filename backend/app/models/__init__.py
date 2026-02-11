from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Statement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    bank_name = db.Column(db.String(64))
    transactions = db.relationship('Transaction', backref='statement', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'upload_date': self.upload_date.isoformat(),
            'bank_name': self.bank_name
        }

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    statement_id = db.Column(db.Integer, db.ForeignKey('statement.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(512), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), default='Uncategorized')
    is_anomaly = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'is_anomaly': self.is_anomaly
        }
