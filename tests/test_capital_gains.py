import requests

BASE_URL = "http://localhost:5003"

def test_capital_gains_endpoint():
    response = requests.get(f"{BASE_URL}/capital-gains")
    print("Response from /capital-gains:", response.json())  # Debugging
    assert response.status_code == 200
    assert "total_gains" in response.json(), "Missing 'total_gains' in response"

def test_capital_gains_with_filter():
    response = requests.get(f"{BASE_URL}/capital-gains?numsharesgt=5")
    print("Response from /capital-gains?numsharesgt=5:", response.json())  # Debugging
    assert response.status_code == 200
    assert "details" in response.json(), "Missing 'details' in response"
