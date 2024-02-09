from db import db

class CurrentAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # for future user authentication
    balance = db.Column(db.Float, nullable=False)
