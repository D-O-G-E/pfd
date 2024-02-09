import yfinance as yf
import pandas as pd
import numpy as np

def get_current_stock_price(stock_symbol):
    stock = yf.Ticker(stock_symbol)
    todays_data = stock.history(period='1d')
    return todays_data['Close'][0] if not todays_data.empty else None

def get_historical_prices(stock_symbol, start_date, end_date):
    stock = yf.Ticker(stock_symbol)
    historical_data = stock.history(start=start_date, end=end_date)
    return historical_data['Close']

def calculate_daily_returns(prices):
    return prices.pct_change().dropna()

def calculate_sharpe_ratio(daily_returns, risk_free_rate):
    excess_returns = daily_returns - risk_free_rate
    return excess_returns.mean() / excess_returns.std()


def calculate_sortino_ratio(daily_returns, risk_free_rate):
    negative_returns = daily_returns[daily_returns < risk_free_rate]
    downside_std = negative_returns.std()
    return (daily_returns.mean() - risk_free_rate) / downside_std

def calculate_beta(portfolio_returns, market_returns):
    covariance = np.cov(portfolio_returns, market_returns)[0][1]
    market_variance = market_returns.var()
    return covariance / market_variance

def calculate_alpha(portfolio_returns, market_returns, risk_free_rate, portfolio_beta):
    expected_portfolio_return = risk_free_rate + portfolio_beta * (market_returns.mean() - risk_free_rate)
    return portfolio_returns.mean() - expected_portfolio_return

def calculate_volatility(portfolio_returns):
    return portfolio_returns.std()

def calculate_portfolio_metrics(all_stocks, benchmark_symbol, start_date, end_date, risk_free_rate):
    total_investment = sum(stock.average_buy_price * stock.quantity for stock in all_stocks)
    portfolio_returns = pd.Series(dtype=float)

    for stock in all_stocks:
        weight = (stock.average_buy_price * stock.quantity) / total_investment
        stock_prices = get_historical_prices(stock.stock_symbol, start_date, end_date)
        stock_returns = calculate_daily_returns(stock_prices) * weight
        portfolio_returns = portfolio_returns.add(stock_returns, fill_value=0)

    benchmark_prices = get_historical_prices(benchmark_symbol, start_date, end_date)
    benchmark_returns = calculate_daily_returns(benchmark_prices)

    return {
        "sharpe_ratio": calculate_sharpe_ratio(portfolio_returns, risk_free_rate),
        "sortino_ratio": calculate_sortino_ratio(portfolio_returns, risk_free_rate),
        "beta": calculate_beta(portfolio_returns, benchmark_returns),
        "alpha": calculate_alpha(portfolio_returns, benchmark_returns, risk_free_rate, calculate_beta(portfolio_returns, benchmark_returns)),
        "volatility": calculate_volatility(portfolio_returns)
    }
