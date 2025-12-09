import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import Config
from data.models import WalletLabel, Transaction

class NansenClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = Config.NANSEN_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_token_flows(self, token_address: str, start_date: str) -> List[Dict]:
        """
        Mock implementation of Token Flows API.
        In a real scenario, this would hit the Nansen API to see inflow/outflow.
        """
        # Placeholder logic
        # url = f"{self.base_url}/token_flows"
        # params = {"token_address": token_address, "start_date": start_date}
        # response = requests.get(url, headers=self.headers, params=params)
        # return response.json()
        print(f"Fetching token flows for {token_address} since {start_date}")
        return []

    def get_wallet_labels(self, addresses: List[str]) -> List[WalletLabel]:
        """
        Returns labels for a list of addresses.
        Uses Caching to save API credits.
        """
        from data.store import Store
        store = Store()
        
        results = []
        to_fetch = []
        
        # Check Cache first
        for addr in addresses:
            cached = store.get_cache_item(f"wallet_label:{addr}")
            if cached:
                results.append(WalletLabel(**cached))
            else:
                to_fetch.append(addr)
                
        if not to_fetch:
            return results

        print(f"Fetching labels for {len(to_fetch)} addresses from Real API...")
        for addr in to_fetch:
             # Real API Call
            try:
                url = f"{self.base_url}/profiler/address/labels"
                params = {"address": addr} # Assuming standard query param
                resp = requests.get(url, headers=self.headers, params=params)
                
                # Default values
                is_smart = False
                label = "Unknown"
                
                if resp.status_code == 200:
                    data = resp.json()
                    # Parse assuming data structure [ { "label": "...", "metadata": {...} } ]
                    # This is best effort without live API docs access
                    if data and isinstance(data, list) and len(data) > 0:
                        label = data[0].get('label', 'Unknown')
                        # Simple logic to detect smart money from label text if not explicit
                        if "Smart Money" in label or "Fund" in label or "Whale" in label:
                            is_smart = True
                
                wl = WalletLabel(address=addr, label=label, is_smart_money=is_smart)
                results.append(wl)
                
                # Save to Cache (Long TTL for labels: 24h)
                store.set_cache_item(f"wallet_label:{addr}", wl.__dict__, ttl_seconds=86400)
                
            except Exception as e:
                print(f"Error fetching label for {addr}: {e}")
                # Fallback
                results.append(WalletLabel(address=addr, label="Error", is_smart_money=False))
            
        return results

    def get_smart_money_transactions(self, token_address: str, lookback_hours: int = 24) -> List[Transaction]:
        """
        Finds recent transactions by Smart Money wallets for a specific token.
        Uses Nansen TGM endpoint.
        """
        print(f"Scanning for Smart Money txs in {token_address} (last {lookback_hours}h)...")
        
        try:
            # Correct Endpoint from Docs: POST https://api.nansen.ai/api/v1/tgm/transfers
            # Config.NANSEN_BASE_URL should be "https://api.nansen.ai/api/v1"
            url = f"{self.base_url}/tgm/transfers"
            
            # Calculate time range
            now = datetime.utcnow()
            start_date = now - timedelta(hours=lookback_hours)
            
            # Exact Payload from Docs
            payload = {
                "chain": "solana",
                "token_address": token_address,
                "date": {
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": now.strftime("%Y-%m-%d")
                },
                "filters": {
                    "only_smart_money": True
                },
                "pagination": {
                    "page": 1,
                    "per_page": 50
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "apiKey": self.api_key
            }
            
            resp = requests.post(url, headers=headers, json=payload)
            
            txs = []
            if resp.status_code == 200:
                data = resp.json()
                # Parse Nansen TGM response
                for item in data.get('data', []):
                    # Parse timestamp safely. API returns "block_timestamp"
                    ts_str = item.get('block_timestamp') or item.get('timestamp')
                    if ts_str:
                        # Handle "2025-12-07T19:17:59" format (no Z)
                        try:
                            if isinstance(ts_str, str): # Ensure it's a string
                                if 'Z' in ts_str:
                                    ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                                else:
                                    ts = datetime.fromisoformat(ts_str)
                            else:
                                ts = datetime.utcnow()
                        except ValueError:
                            ts = datetime.utcnow()
                    else:
                        ts = datetime.utcnow()

                    tx = Transaction(
                        tx_hash=item.get('tx_hash', 'unknown'),
                        from_address=item.get('from_address'),
                        to_address=item.get('to_address'),
                        token_address=token_address,
                        amount=float(item.get('quantity', 0) or item.get('transfer_amount', 0)),
                        timestamp=ts,
                        block_number=item.get('block_number', 0)
                    )
                    txs.append(tx)
            else:
                 print(f"Nansen API Error {resp.status_code}: {resp.text}")
                 
            return txs
            
        except Exception as e:
            print(f"Error fetching smart money txs: {e}")
            return []
