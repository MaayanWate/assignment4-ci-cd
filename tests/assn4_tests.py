import requests
import pytest

# Base URLs for the services
STOCKS_BASE_URL = "http://localhost:5001"
CAPITAL_GAINS_BASE_URL = "http://localhost:5003"

# ==============================
# Sample Stock Payloads (Fixed keys to match the server)
# ==============================
stock1 = {
    "name": "Nvidia Corporation",
    "symbol": "NVDA",
    "purchase price": 650.00,         # Fixed key format
    "purchase date": "2024-05-20",      # Fixed key format
    "shares": 12
}

stock2 = {
    "name": "Apple Inc.",
    "symbol": "AAPL",
    "purchase price": 210.50,
    "purchase date": "2024-03-15",
    "shares": 15
}

stock3 = {
    "name": "Alphabet Inc.",
    "symbol": "GOOG",
    "purchase price": 3200.99,
    "purchase date": "2024-04-10",
    "shares": 5
}

# For testing missing required field "symbol" (stock7)
stock7 = {
    "name": "Meta Platforms, Inc.",
    "purchase price": 280.50,
    "purchase date": "2024-06-01",
    "shares": 8
}

# For testing invalid purchase date format (stock8)
stock8 = {
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
    It attempts to call /stocks/reset, and if it's not available, it deletes each stock individually
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

def test_add_stocks(test_data):
    """
    Test 1
    """
    stocks = [stock1, stock2, stock3]
    ids = []
    for stock in stocks:
        response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock)
        assert response.status_code == 201, f"Failed to add stock: {stock['symbol']} - {response.json()}"
        assert "id" in response.json(), "Response does not contain 'id'"
        ids.append(response.json()["id"])
    assert len(set(ids)) == 3, "IDs are not unique"
    test_data["stock1_id"] = ids[0]
    test_data["stock2_id"] = ids[1]
    test_data["stock3_id"] = ids[2]
    get_all = requests.get(f"{STOCKS_BASE_URL}/stocks")
    assert len(get_all.json()) == 3, f"Expected 3 stocks, but found {len(get_all.json())}"

def test_get_stock_by_id(test_data):
    """
    Test 2:
    """
    stock1_id = test_data["stock1_id"]
    response = requests.get(f"{STOCKS_BASE_URL}/stocks/{stock1_id}")
    assert response.status_code == 200
    assert response.json().get("symbol") == "NVDA", f"Expected symbol NVDA, got {response.json().get('symbol')}"

def test_get_all_stocks():
    """
    Test 3:
    """
    response = requests.get(f"{STOCKS_BASE_URL}/stocks")
    assert response.status_code == 200
    assert len(response.json()) == 2, f"Expected exactly 3 stocks, found {len(response.json())}"

def test_get_stock_values(test_data):
    """
    Test 4:
    """
    # stock1
    response1 = requests.get(f"{STOCKS_BASE_URL}/stock-value/{test_data['stock1_id']}")
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1.get("symbol") == "NVDA", f"Expected symbol NVDA, got {data1.get('symbol')}"
    sv1 = data1.get("stock value")
    # stock2
    response2 = requests.get(f"{STOCKS_BASE_URL}/stock-value/{test_data['stock2_id']}")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2.get("symbol") == "AAPL", f"Expected symbol AAPL, got {data2.get('symbol')}"
    sv2 = data2.get("stock value")
    # stock3
    response3 = requests.get(f"{STOCKS_BASE_URL}/stock-value/{test_data['stock3_id']}")
    assert response3.status_code == 200
    data3 = response3.json()
    assert data3.get("symbol") == "GOOG", f"Expected symbol GOOG, got {data3.get('symbol')}"
    sv3 = data3.get("stock value")
    test_data["sv1"] = sv1
    test_data["sv2"] = sv2
    test_data["sv3"] = sv3

def test_get_portfolio_value(test_data):
    """
    Test 5:

    """
    response = requests.get(f"{STOCKS_BASE_URL}/portfolio-value")
    assert response.status_code == 200
    data = response.json()
    pv = data.get("portfolio value")
    assert pv is not None, "Missing 'portfolio value' in response"
    total_stock_value = test_data["sv1"] + test_data["sv2"] + test_data["sv3"]
    assert pv * 0.97 <= total_stock_value <= pv * 1.03, f"Total stock value {total_stock_value} not within 3% of portfolio value {pv}"

def test_add_stock_missing_symbol():
    """
    Test 6:

    """
    response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock7)
    assert response.status_code == 400, "Adding stock without symbol should fail"

def test_delete_stock(test_data):
    """
    Test 7 & 8:

    """
    stock2_id = test_data["stock2_id"]
    delete_response = requests.delete(f"{STOCKS_BASE_URL}/stocks/{stock2_id}")
    assert delete_response.status_code == 204, f"Unexpected status code on delete: {delete_response.status_code}"
    response = requests.get(f"{STOCKS_BASE_URL}/stocks/{stock2_id}")
    assert response.status_code == 404, "Deleted stock should not exist anymore"

def test_add_stock_invalid_date():
    """
    Test 9:

    """
    response = requests.post(f"{STOCKS_BASE_URL}/stocks", json=stock8)
    assert response.status_code == 400, f"Adding stock with invalid date should fail - {response.json()}"
