from flask import Flask
from db import db
from models.portfolio import Portfolio
from flask import request, jsonify
from services.stock_service import get_current_stock_price
from services.stock_service import calculate_portfolio_metrics
from datetime import datetime
import pandas as pd

from models.transaction import Transaction
from models.historical_price import HistoricalPrice
from models.currentaccount import CurrentAccount
from models.accounttransaction import AccountTransaction

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
    db.init_app(app)
    return app

app = create_app()

@app.route('/')
def home():
    return "Welcome to the Portfolio Tracker API!"

@app.route('/portfolio/transaction', methods=['POST'])
def add_transaction():
    data = request.json
    transaction = Transaction(
        stock_symbol=data['stock_symbol'],
        transaction_type=data['transaction_type'],  # 'buy' / 'sell'
        price=data['price'],
        quantity=data['quantity'],
    )
    db.session.add(transaction)
    
    stock = Portfolio.query.filter_by(stock_symbol=data['stock_symbol']).first()
    if stock:
        if data['transaction_type'] == 'buy':
            total_cost = stock.average_buy_price * stock.quantity
            additional_cost = data['price'] * data['quantity']
            stock.quantity += data['quantity']
            stock.average_buy_price = (total_cost + additional_cost) / stock.quantity
        elif data['transaction_type'] == 'sell' and stock.quantity >= data['quantity']:
            stock.quantity -= data['quantity']
            if stock.quantity == 0:
                db.session.delete(stock)
        else:
            return jsonify({"error": "Cannot sell more shares than you own"}), 400
    else:
        if data['transaction_type'] == 'buy':
            new_stock = Portfolio(
                stock_symbol=data['stock_symbol'],
                average_buy_price=data['price'],
                quantity=data['quantity']
            )
            db.session.add(new_stock)
        else:
            return jsonify({"error": "Cannot sell stock that is not in portfolio"}), 400

    db.session.commit()
    return jsonify({"message": f"Transaction recorded."}), 201


@app.route('/portfolio', methods=['GET'])
def get_portfolio():
    all_stocks = Portfolio.query.all()
    portfolio_data = []

    for stock in all_stocks:
        current_price = get_current_stock_price(stock.stock_symbol)
        transactions = Transaction.query.filter_by(stock_symbol=stock.stock_symbol).all()
        transaction_data = [{'type': t.transaction_type, 'price': t.price, 'quantity': t.quantity, 'date': t.transaction_date} for t in transactions]

        stock_data = {
            'stock_symbol': stock.stock_symbol,
            'average_buy_price': stock.average_buy_price,
            'quantity': stock.quantity,
            'current_price': current_price,
            'total_value': current_price * stock.quantity,
            'transactions': transaction_data
        }
        portfolio_data.append(stock_data)

    return jsonify(portfolio_data)

@app.route('/portfolio/composition', methods=['GET'])
def get_portfolio_composition():
    all_stocks = Portfolio.query.all()
    total_portfolio_value = sum(stock.quantity * get_current_stock_price(stock.stock_symbol) for stock in all_stocks)
    
    portfolio_composition = []
    for stock in all_stocks:
        current_price = get_current_stock_price(stock.stock_symbol)
        stock_value = current_price * stock.quantity
        composition_percentage = (stock_value / total_portfolio_value) * 100 if total_portfolio_value else 0
        portfolio_composition.append({
            'stock_symbol': stock.stock_symbol,
            'percentage_of_portfolio': composition_percentage
        })

    return jsonify(portfolio_composition)

@app.route('/portfolio/metrics', methods=['GET'])
def portfolio_metrics():
    risk_free_rate = 5.22 / 100  # convert percentage to decimal
    benchmark_symbol = '^GSPC'  # e.g. s&p index
    start_date = '2015-01-01'  # choose start date
    end_date = datetime.now().strftime('%Y-%m-%d')  # starting from today
    all_stocks = Portfolio.query.all()

    metrics = calculate_portfolio_metrics(all_stocks, benchmark_symbol, start_date, end_date, risk_free_rate)
    return jsonify(metrics)


@app.route('/current_account/balance', methods=['POST'])
def update_balance():
    data = request.json
    user_id = data['user_id'] 
    new_balance = data['balance']

    account = CurrentAccount.query.filter_by(user_id=user_id).first()
    if account:
        account.balance = new_balance
    else:
        account = CurrentAccount(user_id=user_id, balance=new_balance)
        db.session.add(account)

    db.session.commit()
    return jsonify({"message": "Account balance updated."}), 200


@app.route('/current_account/transaction', methods=['POST'])
def add_ca_transaction():
    data = request.json
    account_id = data['account_id']
    transaction = AccountTransaction(
        account_id=account_id,
        transaction_type=data['transaction_type'],  # 'income' / 'expense'
        amount=data['amount'],
        description=data['description']
    )
    db.session.add(transaction)

    account = CurrentAccount.query.get(account_id)
    if account:
        if transaction.transaction_type == 'income':
            account.balance += transaction.amount
        elif transaction.transaction_type == 'expense':
            account.balance -= transaction.amount

    db.session.commit()
    return jsonify({"message": f"{transaction.transaction_type.title()} transaction recorded."}), 200

@app.route('/current_account/balance/<int:user_id>', methods=['GET'])
def get_balance(user_id):
    account = CurrentAccount.query.filter_by(user_id=user_id).first()
    if account:
        return jsonify({"balance": account.balance}), 200
    else:
        return jsonify({"error": "Account not found"}), 404

from services.prediction_service import predict_future_balance
from models.currentaccount import CurrentAccount
from models.accounttransaction import AccountTransaction

@app.route('/current_account/predict_balance/<int:user_id>/<int:days_ahead>', methods=['GET'])
def predict_balance(user_id, days_ahead):
    account = CurrentAccount.query.filter_by(user_id=user_id).first()
    if not account:
        return jsonify({"error": "Account not found"}), 404

    transactions = AccountTransaction.query.filter_by(account_id=account.id).all()
    transaction_data = [{
        'amount': t.amount,
        'transaction_date': t.transaction_date.strftime('%Y-%m-%d')
    } for t in transactions]

    predicted_balance = predict_future_balance(account.balance, transaction_data, days_ahead)

    return jsonify({
        "current_balance": account.balance,
        "predicted_balance": predicted_balance,
        "days_ahead": days_ahead
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
