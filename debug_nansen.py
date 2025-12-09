import requests
from config import Config

def test_endpoints():
    print("--- Testing Nansen API Endpoints ---")
    api_key = Config.NANSEN_API_KEY
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 1. Test Standard Label Endpoint
    # Nansen V2 / Profiler is confusing, let's try a few base paths
    
    trials = [
        ("https://api.nansen.ai/v1", "/token_flows"),
        ("https://api.nansen.ai/v1", "/tgm/transfers"),
        ("https://pro.nansen.ai/api/v1", "/profiler/address/labels"),  
        ("https://api.nansen.ai/v1", "/labels"),
    ]
    
    # Try a known address (Foundation)
    test_addr = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263" # BONK
    
    for base, path in trials:
        url = f"{base}{path}"
        print(f"\nTesting: {url}")
        try:
            # Some are GET, some POST
            if "tgm" in path:
                 payload = {"token_address": test_addr} # minimal
                 resp = requests.post(url, headers=headers, json=payload)
            else:
                 params = {"address": test_addr}
                 resp = requests.get(url, headers=headers, params=params)
                 
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text[:200]}...")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    test_endpoints()
