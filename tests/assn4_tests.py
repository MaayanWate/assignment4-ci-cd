import requests
import pytest
import os

# Base URLs for the services
STOCKS_BASE_URL = "http://localhost:5001"
CAPITAL_GAINS_BASE_URL = "http://localhost:5003"

# ==============================
# Sample Stock Payloads
# ==============================
stock_alpha = {
    "name": "Tesla, Inc.",
    "symbol": "TSLA",
    "purchase price": 650.00,
    "purchase date": "2024-05-20",
    "shares": 12
}

stock_beta = {
    "name": "Microsoft Corporation",
    "symbol": "MSFT",
    "purchase price": 210.50,
    "purchase date": "2024-03-15",
    "shares": 15
}

stock_gamma = {
    "name": "Amazon.com, Inc.",
    "symbol": "AMZN",
    "purchase price": 3200.99,
    "purchase date": "2024-04-10",
    "shares": 5
}

# For testing missing required field "symbol"
stock_delta = {
    "name": "Meta Platforms, Inc.",
    "purchase price": 280.50,
    "purchase date": "2024-06-01",
    "shares": 8
}

# For testing invalid purchase date format
stock_epsilon = {
    "name": "Intel Corporation",
    "symbol": "INTC",
    "purchase price": 54.75,
    "purchase date": "06/01/2024",  # Incorrect format
    "shares": 20
}

@pytest.fixture(scope="module")
def test_data():
    """
    Fixture to store shared data between tests.
    """
    return {}

# ==============================
# Capital Gains Service Tests
# ==============================
def test_capital_gains_endpoint():
    response = requests.get(f"{CAPITAL_GAINS_BASE_URL}/capital-gains")
    assert response.status_code == 200
    assert "total_gains" in response.json()

def test_home():
    response = requests.get(f"{STOCKS_BASE_URL}/")
    assert response.status_code == 200
    assert "Welcome to the stocks" in response.text

def test_add_stocks():
    stocks = [stock_alpha, stock_beta, stock_gamma]
    ids = set()
    for stock in stocks:
        response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock)
        assert response.status_code == 201, f"Failed to add stock: {stock['symbol']}, got {response.status_code}"
        assert "id" in response.json()
        ids.add(response.json()["id"])
    assert len(ids) == 3

def test_get_stock_by_id():
    response = requests.get(f"{STOCKS_BASE_URL}/stocks")
    assert response.status_code == 200
    stocks = response.json()
    assert len(stocks) > 0
    stock_id = stocks[0]["id"]

    response = requests.get(f"{STOCKS_BASE_URL}/stocks/{stock_id}")
    assert response.status_code == 200
    returned_stock = response.json()
    assert "symbol" in returned_stock, "Stock data does not contain 'symbol' key"

def test_get_all_stocks():
    response = requests.get(f"{STOCKS_BASE_URL}/stocks")
    assert response.status_code == 200
    assert len(response.json()) >= 3, "Expected at least 3 stocks, found different amount"

def test_get_stock_values():
    response = requests.get(f"{STOCKS_BASE_URL}/stocks")
    assert response.status_code == 200
    stocks = response.json()
    for stock in stocks:
        resp = requests.get(f"{STOCKS_BASE_URL}/stock-value/{stock['id']}")
        assert resp.status_code == 200
        assert "symbol" in resp.json()

def test_get_portfolio_value():
    response = requests.get(f"{STOCKS_BASE_URL}/portfolio-value")
    assert response.status_code == 200
    data = response.json()
    assert "portfolio value" in data, "Response missing 'portfolio value'"

def test_add_stock_missing_symbol():
    response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock_delta)
    assert response.status_code == 400, "Adding stock without symbol should fail"

def test_add_stock_invalid_date():
    response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock_epsilon)
    assert response.status_code == 400, "Adding stock with invalid date should fail"

def test_delete_stock():
    response = requests.get(f"{STOCKS_BASE_URL}/stocks?symbol=MSFT")
    stocks = response.json()
    if stocks:
        stock_id = stocks[0]['id']
        delete_response = requests.delete(f"{STOCKS_BASE_URL}/stocks/{stock_id}")
        assert delete_response.status_code == 204

        response = requests.get(f"{STOCKS_BASE_URL}/stocks/{stock_id}")
        assert response.status_code == 404
