import requests
from config import Config
from datetime import datetime, timedelta

def probe_endpoints():
    api_key = Config.NANSEN_API_KEY
    token_address = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
    
    # Common Headers
    headers = {
        "Content-Type": "application/json",
        "apiKey": api_key
    }
    
    # Variations to test
    variations = [
        ("https://api.nansen.ai/api/v1/tgm/transfers", "solana"),
        ("https://api.nansen.ai/v1/tgm/transfers", "solana"),
        ("https://api.nansen.ai/tgm/transfers", "solana"),
        ("https://pro.nansen.ai/api/v1/tgm/transfers", "solana"),
        # Try without 'solana' just in case
        ("https://api.nansen.ai/api/v1/tgm/transfers", "ethereum"), 
    ]
    
    now = datetime.utcnow()
    payload_template = {
        "token_address": token_address,
        "date": {
            "from": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
            "to": now.strftime("%Y-%m-%d")
        },
        "filters": {"only_smart_money": True},
        "pagination": {"page": 1, "per_page": 10}
    }

    print(f"--- Probing Nansen API with Key: {api_key[:5]}... ---")

    for url, chain in variations:
        print(f"\n[PROBE] URL: {url} | Chain: {chain}")
        
        current_payload = payload_template.copy()
        current_payload["chain"] = chain
        if chain == "ethereum": 
             # Use a random ETH address for safety if testing ETH support
             current_payload["token_address"] = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

        try:
            resp = requests.post(url, headers=headers, json=current_payload)
            print(f"Result: {resp.status_code}")
            if resp.status_code != 404:
                print(f"SUCCESS/INTERESTING RESPONSE: {resp.text[:500]}")
            else:
                 print(f"Error ({resp.status_code}): {resp.json().get('message')}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    probe_endpoints()
