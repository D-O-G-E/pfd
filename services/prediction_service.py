import numpy as np
from datetime import datetime, timedelta

def predict_future_balance(current_balance, transactions, days_ahead):
    """
    Predict future balance based on past transactions.
    transactions: list of dicts with keys 'amount' and 'transaction_date'
    days_ahead: number of days to predict into the future
    """
    ref_date = datetime.now() - timedelta(days=365)  # one year ago
    days_since_ref = np.array([(datetime.strptime(t['transaction_date'], '%Y-%m-%d') - ref_date).days for t in transactions])
    amounts = np.array([t['amount'] for t in transactions])

    # basic linear regression to predict future balance
    A = np.vstack([days_since_ref, np.ones(len(days_since_ref))]).T
    m, c = np.linalg.lstsq(A, amounts, rcond=None)[0]

    future_day = (datetime.now() - ref_date + timedelta(days=days_ahead)).days
    predicted_change = m * future_day + c
    return current_balance + predicted_change
