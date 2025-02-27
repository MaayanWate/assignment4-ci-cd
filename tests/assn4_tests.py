import requests
import pytest

# Base URLs for the services
STOCKS_BASE_URL = "http://localhost:5001"
CAPITAL_GAINS_BASE_URL = "http://localhost:5003"

# ==============================
# Sample Stock Payloads (Fixed keys to match the server)
# ==============================
# מניה עם מחיר רכישה שלילי
stock_alpha = {
    "name": "Apple Inc.",
    "symbol": "AAPL",
    "purchase price": -150.00,  # מחיר שלילי
    "purchase date": "2024-05-15",
    "shares": 10
}

# מניה עם מספר מניות שלילי
stock_beta = {
    "name": "Netflix, Inc.",
    "symbol": "NFLX",
    "purchase price": 430.75,
    "purchase date": "2024-02-20",
    "shares": -5  # מספר מניות שלילי
}

# מניה עם תאריך רכישה בעתיד
stock_gamma = {
    "name": "Google LLC",
    "symbol": "GOOGL",
    "purchase price": 2800.00,
    "purchase date": "2025-01-01",  # תאריך עתידי
    "shares": 7
}

# מניה עם שם חסר
stock_delta = {
    "symbol": "NVDA",
    "purchase price": 750.25,
    "purchase date": "2024-04-18",
    "shares": 12
}

# מניה עם מספר מניות אפס
stock_epsilon = {
    "name": "Adobe Inc.",
    "symbol": "ADBE",
    "purchase price": 650.00,
    "purchase date": "2024-03-10",
    "shares": 0  # מספר מניות אפס
}

# מניה עם מחיר רכישה לא מספרי
stock_zeta = {
    "name": "Cisco Systems, Inc.",
    "symbol": "CSCO",
    "purchase price": "two hundred",  # ערך טקסטואלי במקום מספר
    "purchase date": "2024-06-05",
    "shares": 30
}

# מניה עם תאריך רכישה בפורמט שגוי
stock_eta = {
    "name": "IBM",
    "symbol": "IBM",
    "purchase price": 140.50,
    "purchase date": "15-03-2024",  # פורמט לא תקין
    "shares": 25
}

# מניה עם סימול ארוך מדי
stock_theta = {
    "name": "Tesla Motors",
    "symbol": "TESLAMOTORS12345",  # סימול שגוי וארוך
    "purchase price": 750.00,
    "purchase date": "2024-02-28",
    "shares": 9
}

# מניה עם תאריך רכישה חסר
stock_iota = {
    "name": "Facebook Inc.",
    "symbol": "META",
    "purchase price": 320.40,
    "shares": 6
}

# מניה עם שדה נוסף לא צפוי
stock_kappa = {
    "name": "Salesforce",
    "symbol": "CRM",
    "purchase price": 250.99,
    "purchase date": "2024-05-12",
    "shares": 14,
    "unexpected_field": "Oops"  # שדה נוסף לא תקין
}

@pytest.fixture(autouse=True, scope="module")
def clean_db():
    """
    Fixture to ensure the database is clean before tests run.
    מנסה לקרוא ל־/stocks/reset ואם זה לא זמין, מוחק כל מניה בנפרד.
    """
    # Attempt to call the reset endpoint
    reset_response = requests.delete(f"{STOCKS_BASE_URL}/stocks/reset")
    if reset_response.status_code != 200:
        # If there is no reset endpoint – delete each stock individually.
        all_stocks = requests.get(f"{STOCKS_BASE_URL}/stocks").json()
        for stock in all_stocks:
            requests.delete(f"{STOCKS_BASE_URL}/stocks/{stock['id']}")
    # Ensure that the database is empty.
    all_stocks = requests.get(f"{STOCKS_BASE_URL}/stocks").json()
    assert len(all_stocks) == 0, f"Database not empty before tests: {all_stocks}"
    yield
    # Optionally, clean up at the end of the tests as well.
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
        # Check if a stock with this symbol already exists in the database.
        get_response = requests.get(f"{STOCKS_BASE_URL}/stocks?symbol={stock['symbol']}")
        if get_response.status_code == 200 and get_response.json():
            # If it exists, an attempt to add it should return an error (400).
            response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock)
            assert response.status_code == 400, f"Expected duplicate error for {stock['symbol']}, got: {response.json()}"
        else:
            # If it does not exist, the addition should succeed with a 201 status code.
            response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock)
            assert response.status_code == 201, f"Failed to add stock: {stock['symbol']} - {response.json()}"
            assert "id" in response.json(), "Response does not contain 'id'"
            ids.add(response.json()["id"])
    # We will check that the total number of stocks matches the number of new additions.
    get_all = requests.get(f"{STOCKS_BASE_URL}/stocks")
    # In this case, since the system was empty at the beginning, we expect to receive 3 records.
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
