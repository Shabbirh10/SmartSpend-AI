from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

db = SQLAlchemy()

# Global async sessionmaker
async_session = None

def init_async_db(app):
    global async_session
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_async_engine(db_uri)
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Statement(db.Model):
    __tablename__ = 'statement'
    id = sa.Column(sa.Integer, primary_key=True)
    filename = sa.Column(sa.String(256), nullable=False)
    upload_date = sa.Column(sa.DateTime, default=datetime.utcnow)
    bank_name = sa.Column(sa.String(64))
    transactions = relationship('Transaction', back_populates='statement', lazy='selectin', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'upload_date': self.upload_date.isoformat(),
            'bank_name': self.bank_name
        }

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = sa.Column(sa.Integer, primary_key=True)
    statement_id = sa.Column(sa.Integer, sa.ForeignKey('statement.id'), nullable=False)
    date = sa.Column(sa.Date, nullable=False)
    description = sa.Column(sa.String(512), nullable=False)
    amount = sa.Column(sa.Float, nullable=False)
    category = sa.Column(sa.String(64), default='Uncategorized')
    is_anomaly = sa.Column(sa.Boolean, default=False)
    statement = relationship('Statement', back_populates='transactions', lazy='selectin')

    def to_dict(self):
        import re
        date_str = self.date.isoformat() if hasattr(self.date, 'isoformat') else str(self.date)

        # Clean up transaction description noise
        desc = self.description or ''
        # Strip leading UPI * / NEFT * / IMPS * prefix
        desc = re.sub(r'^(UPI|NEFT|IMPS|RTGS)\s*\*\s*', '', desc, flags=re.IGNORECASE).strip()
        # Strip trailing * UPIxxxxxx, * REFxxxxx junk
        desc = re.sub(r'\s*\*\s*(UPI|REF|N)\w+.*$', '', desc, flags=re.IGNORECASE).strip()
        # Strip trailing standalone REF/UPI reference tokens
        desc = re.sub(r'\s+(REF|UPI|N)\w+', '', desc, flags=re.IGNORECASE).strip()
        # Strip trailing lone numbers (e.g. "BigBasket 1")
        desc = re.sub(r'\s+\d+$', '', desc).strip()
        # Handle "MERCHANT *ACTION" patterns like "UBER *RIDE" -> "Uber", "PAYPAL *EBAY" -> "PayPal - eBay"
        desc = re.sub(r'\s*\*\s*RIDE\b.*', '', desc, flags=re.IGNORECASE).strip()
        desc = re.sub(r'\s*\*\s*TRIP\b.*', '', desc, flags=re.IGNORECASE).strip()
        desc = re.sub(r'(PAYPAL)\s*\*\s*(\w+)', r'PayPal - \2', desc, flags=re.IGNORECASE).strip()
        # For NEFT salary lines keep it readable
        desc = re.sub(r'\s*\*\s*SALARY\s*\*.*', ' - Salary', desc, flags=re.IGNORECASE).strip()
        # Title-case if all uppercase
        if desc == desc.upper() and len(desc) > 2:
            desc = desc.title()

        return {
            'id': self.id,
            'statement_id': self.statement_id,
            'date': date_str,
            'description': desc if desc else self.description,
            'amount': self.amount,
            'category': self.category,
            'is_anomaly': self.is_anomaly
        }

class Investment(db.Model):
    __tablename__ = 'investment'
    id = sa.Column(sa.Integer, primary_key=True)
    ticker = sa.Column(sa.String(16), nullable=False, unique=True)
    shares = sa.Column(sa.Float, nullable=False, default=0.0)
    average_price = sa.Column(sa.Float, nullable=False, default=0.0)

    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'shares': self.shares,
            'average_price': self.average_price
        }
