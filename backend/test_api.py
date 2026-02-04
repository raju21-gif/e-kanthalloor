import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    # 1. Register/Login to get Token
    email = "test@example.com"
    password = "password123"
    
    # Try login first
    print("Attempting Login...")
    login_data = {"username": email, "password": password}
    res = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    
    if res.status_code != 200:
        print("Login failed, trying registration...")
        reg_data = {
            "full_name": "Test User",
            "email": email,
            "password": password,
            "role": "citizen"
        }
        res = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
        if res.status_code != 200:
            print(f"Registration failed: {res.text}")
            return
        
        # Login again
        res = requests.post(f"{BASE_URL}/auth/token", data=login_data)
        if res.status_code != 200:
            print(f"Login failed after registration: {res.text}")
            return

    token = res.json()["access_token"]
    print("Got Token.")

    # 2. Submit Info
    headers = {"Authorization": f"Bearer {token}"}
    info_data = {
        "full_name": "Test User",
        "age": 30,
        "bank_account_no": "1234567890",
        "aadhaar_no": "123412341234",
        "phone_number": "9876543210",
        "annual_income": 500000.0
    }
    
    print("Submitting Info...")
    res = requests.post(f"{BASE_URL}/info/submit", json=info_data, headers=headers)
    
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print(f"Test Exception: {e}")
