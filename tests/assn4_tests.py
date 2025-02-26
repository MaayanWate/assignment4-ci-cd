import requests
import pytest

# Base URLs for the services
STOCKS_BASE_URL = "http://localhost:5001"
CAPITAL_GAINS_BASE_URL = "http://localhost:5003"

# ==============================
# Sample Stock Payloads (Fixed keys to match the server)
# ==============================
stock_alpha = {
    "name": "Tesla, Inc.",
    "symbol": "TSLA",
    "purchase price": 650.00,  # Fixed key format
    "purchase date": "2024-05-20",  # Fixed key format
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
    "purchase date": "06/01/2024",
    "shares": 20
}

@pytest.fixture(autouse=True, scope="module")
def clean_db():
    """
    Fixture to ensure the database is clean before tests run.
    מנסה לקרוא ל־/stocks/reset ואם זה לא זמין, מוחק כל מניה בנפרד.
    """
    # ניסיון לקרוא ל־endpoint reset
    reset_response = requests.delete(f"{STOCKS_BASE_URL}/stocks/reset")
    if reset_response.status_code != 200:
        # אם אין endpoint reset – מחק כל מניה בנפרד
        all_stocks = requests.get(f"{STOCKS_BASE_URL}/stocks").json()
        for stock in all_stocks:
            requests.delete(f"{STOCKS_BASE_URL}/stocks/{stock['id']}")
    # וודא שהמסד ריק
    all_stocks = requests.get(f"{STOCKS_BASE_URL}/stocks").json()
    assert len(all_stocks) == 0, f"Database not empty before tests: {all_stocks}"
    yield
    # Optionally, נקו גם בסיום הבדיקות
    requests.delete(f"{STOCKS_BASE_URL}/stocks/reset")

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
    stocks = [stock_alpha, stock_beta, stock_gamma]
    ids = set()
    for stock in stocks:
        # בודקים האם מניה עם הסימול הזה קיימת כבר במסד
        get_response = requests.get(f"{STOCKS_BASE_URL}/stocks?symbol={stock['symbol']}")
        if get_response.status_code == 200 and get_response.json():
            # אם קיימת, ניסיון הוספה צריך להחזיר שגיאה (400)
            response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock)
            assert response.status_code == 400, f"Expected duplicate error for {stock['symbol']}, got: {response.json()}"
        else:
            # אם אינה קיימת, ההוספה אמורה להצליח עם קוד 201
            response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock)
            assert response.status_code == 201, f"Failed to add stock: {stock['symbol']} - {response.json()}"
            assert "id" in response.json(), "Response does not contain 'id'"
            ids.add(response.json()["id"])
    # נבדוק שהמספר הכולל של המניות תואם למספר ההוספות החדשות
    get_all = requests.get(f"{STOCKS_BASE_URL}/stocks")
    # במקרה זה, כי המערכת הייתה ריקה בהתחלה, אנחנו מצפים לקבל 3 רשומות
    assert len(get_all.json()) == 3, f"Expected 3 stocks, but found {len(get_all.json())}"

def test_get_stock_by_id():
    response = requests.get(f"{STOCKS_BASE_URL}/stocks")
    assert response.status_code == 200
    stocks = response.json()
    assert stocks, "Stock list is empty"
    stock_id = stocks[0]["id"]

    response = requests.get(f"{STOCKS_BASE_URL}/stocks/{stock_id}")
    assert response.status_code == 200
    assert "symbol" in response.json(), "Response missing 'symbol'"

def test_get_all_stocks():
    response = requests.get(f"{STOCKS_BASE_URL}/stocks")
    assert response.status_code == 200
    assert len(response.json()) == 3, f"Expected exactly 3 stocks, found {len(response.json())}"

def test_get_stock_values():
    response = requests.get(f"{STOCKS_BASE_URL}/stocks")
    assert response.status_code == 200
    stocks = response.json()
    for stock in stocks:
        resp = requests.get(f"{STOCKS_BASE_URL}/stock-value/{stock['id']}")
        assert resp.status_code == 200
        assert "symbol" in resp.json(), "Response missing 'symbol'"

def test_get_portfolio_value():
    response = requests.get(f"{STOCKS_BASE_URL}/portfolio-value")
    assert response.status_code == 200
    assert "portfolio value" in response.json(), "Missing 'portfolio value' in response"

def test_add_stock_missing_symbol():
    response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock_delta)
    assert response.status_code == 400, "Adding stock without symbol should fail"

def test_add_stock_invalid_date():
    response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock_epsilon)
    assert response.status_code == 400, f"Adding stock with invalid date should fail - {response.json()}"

def test_delete_stock():
    response = requests.get(f"{STOCKS_BASE_URL}/stocks?symbol=MSFT")
    stocks = response.json()
    if stocks:
        stock_id = stocks[0]['id']
        delete_response = requests.delete(f"{STOCKS_BASE_URL}/stocks/{stock_id}")
        assert delete_response.status_code == 204, f"Unexpected status code on delete: {delete_response.status_code}"
        response = requests.get(f"{STOCKS_BASE_URL}/stocks/{stock_id}")
        assert response.status_code == 404, "Deleted stock should not exist anymore"
    else:
        pytest.skip("No stock found to delete")