from db import db
from datetime import datetime

class AccountTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('current_account.id'), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'income' / 'expense'
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(100))
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
