import requests
import sys

try:
    url = "http://127.0.0.1:8000/schemes/6967ad8a87c1e52bfc8da6ca"
    print(f"Requesting {url}...")
    resp = requests.get(url)
    print(f"Status Code: {resp.status_code}")
    print("Response Body:")
    print(resp.text)
except Exception as e:
    print(f"Error: {e}")
