import requests

# Base URLs for the services
STOCKS_BASE_URL = "http://localhost:5001"
CAPITAL_GAINS_BASE_URL = "http://localhost:5003"

# ==============================
# Capital Gains Service Tests
# ==============================
def test_capital_gains_endpoint():
    response = requests.get(f"{CAPITAL_GAINS_BASE_URL}/capital-gains")
    assert response.status_code == 200
    assert "total_gains" in response.json(), "Missing 'total_gains' in response"

def test_capital_gains_with_filter():
    response = requests.get(f"{CAPITAL_GAINS_BASE_URL}/capital-gains?numsharesgt=5")
    assert response.status_code == 200
    assert "details" in response.json(), "Missing 'details' in response"

# ==============================
# Stocks Service Tests
# ==============================
def test_home():
    response = requests.get(f"{STOCKS_BASE_URL}/")
    assert response.status_code == 200
    assert "Welcome to the stocks" in response.text, "Unexpected homepage response"

def test_add_stocks():
    stocks = [
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "purchase_price": 134.66, "purchase_date": "2024-06-18", "shares": 7},
        {"symbol": "AAPL", "name": "Apple Inc.", "purchase_price": 183.63, "purchase_date": "2024-02-22", "shares": 19},
        {"symbol": "GOOG", "name": "Alphabet Inc.", "purchase_price": 140.12, "purchase_date": "2024-10-24", "shares": 14}
    ]

    ids = set()
    for stock in stocks:
        response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock)
        assert response.status_code == 201, f"Failed to add stock: {stock['symbol']}"
        assert "id" in response.json(), "Response does not contain 'id'"
        ids.add(response.json()["id"])

    assert len(ids) == 3, "IDs are not unique"

def test_get_stock_by_id():
    response = requests.get(f"{STOCKS_BASE_URL}/stocks")
    assert response.status_code == 200
    stocks = response.json()
    stock_id = stocks[0]["id"]

    response = requests.get(f"{STOCKS_BASE_URL}/stocks/{stock_id}")
    assert response.status_code == 200
    assert response.json()["symbol"] == "NVDA"

def test_get_all_stocks():
    response = requests.get(f"{STOCKS_BASE_URL}/stocks")
    assert response.status_code == 200
    assert len(response.json()) == 3, "Expected 3 stocks, found different amount"

def test_get_stock_values():
    response = requests.get(f"{STOCKS_BASE_URL}/stocks")
    assert response.status_code == 200
    stocks = response.json()

    for stock in stocks:
        response = requests.get(f"{STOCKS_BASE_URL}/stock-value/{stock['id']}")
        assert response.status_code == 200
        assert response.json()["symbol"] in ["NVDA", "AAPL", "GOOG"]

def test_get_portfolio_value():
    response = requests.get(f"{STOCKS_BASE_URL}/portfolio-value")
    assert response.status_code == 200
    portfolio_value = response.json()["portfolio_value"]

    response = requests.get(f"{STOCKS_BASE_URL}/stocks")
    stocks = response.json()
    stock_values = sum([requests.get(f"{STOCKS_BASE_URL}/stock-value/{s['id']}").json()["stock_value"] for s in stocks])

    assert portfolio_value * 0.97 <= stock_values <= portfolio_value * 1.03, "Portfolio value out of expected range"

def test_add_stock_missing_symbol():
    data = {"name": "Test Company", "purchase_price": 100.0, "purchase_date": "2024-01-01", "shares": 5}
    response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=data)
    assert response.status_code == 400, "Adding stock without symbol should fail"

def test_add_stock_invalid_date():
    data = {"symbol": "TEST", "name": "Test Company", "purchase_price": 100.0, "purchase_date": "InvalidDate", "shares": 5}
    response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=data)
    assert response.status_code == 400, "Adding stock with invalid date should fail"

def test_delete_stock():
    response = requests.get(f"{STOCKS_BASE_URL}/stocks?symbol=AAPL")
    stocks = response.json()
    assert len(stocks) > 0, "No stocks found to delete"

    stock_id = stocks[0]['id']
    delete_response = requests.delete(f"{STOCKS_BASE_URL}/stocks/{stock_id}")
    assert delete_response.status_code == 204, "Unexpected status code on delete"

    response = requests.get(f"{STOCKS_BASE_URL}/stocks/{stock_id}")
    assert response.status_code == 404, "Deleted stock should not exist anymore"