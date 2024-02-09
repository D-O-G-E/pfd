from db import db
from datetime import datetime

class HistoricalPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(10), nullable=False)
    price_date = db.Column(db.DateTime, nullable=False)
    closing_price = db.Column(db.Float, nullable=False)
