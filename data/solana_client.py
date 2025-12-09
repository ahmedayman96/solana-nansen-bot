from solana.rpc.api import Client
from solders.pubkey import Pubkey # type: ignore
from config import Config

class SolanaClient:
    def __init__(self):
        self.client = Client(Config.SOLANA_RPC_URL)

    def get_token_balance(self, wallet_address: str, token_address: str) -> float:
        """
        Get token balance for a specific wallet.
        """
        # Implementation stub
        # In reality, needs to parse token account info
        pass

    def get_sol_balance(self, wallet_address: str) -> float:
        """
        Get SOL balance.
        """
        try:
            pubkey = Pubkey.from_string(wallet_address)
            resp = self.client.get_balance(pubkey)
            return resp.value / 1e9
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return 0.0
