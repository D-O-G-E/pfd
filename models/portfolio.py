from db import db

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(10), nullable=False)
    average_buy_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
