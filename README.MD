# Portfolio Tracker

(this project is WIP, readme incomplete)

Designed to help investors track their stock portfolio performance over time. It offers endpoints to add transactions, view portfolio balances, calculate portfolio composition percentages, and perform financial metrics analysis.

Focus on modular, service oriented design.
- `app.py` can be improved heavily by using flask [blueprints](https://flask.palletsprojects.com/en/2.3.x/blueprints/),  separting the routes into their own files

## Features

- **Transaction Management**: Add buy or sell stock transactions to your portfolio.
- **Portfolio Overview**: Get a detailed view of your current stock holdings, including average buy prices, quantities, and current market prices.
- **Portfolio Composition**: View your portfolio's composition by percentage, helping you understand your exposure to individual stocks.
- **Financial Metrics**: Calculate key financial metrics for your portfolio, such as performance against a benchmark (e.g., S&P 500 Index) over a specified period.
- **Account Management**: Track and predict future account balances based on income and expenses transactions.


### To do
- Create frontend
- Ensure calculations are accurate
- Add other portfolio metrics
- finish readme


### Get started
1. Clone the repository
2. python3 -m venv venv
3. activate environment:
- on mac/linux: source ./venv/bin/activate
- on windows: 
4. pip install requirements.txt
5. python3 app.py



## Usage

Here's how you can interact with the API:

### Home

- **Endpoint**: `/`
- **Method**: `GET`
- **Description**: Welcome message for the API.

### Add Transaction

- **Endpoint**: `/portfolio/transaction`
- **Method**: `POST`
- **Payload Example**:
```json
{
 "stock_symbol": "AAPL",
 "transaction_type": "buy",
 "price": 150.00,
 "quantity": 10
}

