import requests

BASE_URL = "http://localhost:5001"

def test_home():
    response = requests.get(f"{BASE_URL}/")
    print("Response from /:", response.text)  # Debugging
    assert response.status_code == 200
    assert "Welcome to the stocks" in response.text, "Unexpected homepage response"

def test_add_stock():
    data = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "purchase_price": 150.5,  # Fixed field name
        "purchase_date": "2024-01-01",  # Fixed field name
        "shares": 10
    }
    response = requests.post(f"{BASE_URL}/stocks", json=data)
    print("Response from POST /stocks:", response.json())  # Debugging
    assert response.status_code == 201, f"Unexpected status code: {response.status_code}"
    assert "id" in response.json(), "Response does not contain 'id'"

def test_get_stock():
    response = requests.get(f"{BASE_URL}/stocks?symbol=AAPL")
    print("Response from GET /stocks?symbol=AAPL:", response.json())  # Debugging
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    assert len(response.json()) > 0, "No stocks found for symbol AAPL"

def test_delete_stock():
    response = requests.get(f"{BASE_URL}/stocks?symbol=AAPL")
    stocks = response.json()
    print("Stocks found before delete:", stocks)  # Debugging

    assert len(stocks) > 0, "No stocks found to delete"
    
    stock_id = stocks[0]['id']
    delete_response = requests.delete(f"{BASE_URL}/stocks/{stock_id}")
    print("Response from DELETE /stocks/{stock_id}:", delete_response.status_code)  # Debugging
    assert delete_response.status_code == 204, f"Unexpected status code: {delete_response.status_code}"
