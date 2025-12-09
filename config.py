import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NANSEN_API_KEY = os.getenv("NANSEN_API_KEY")
    SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    PAPER_TRADING_BALANCE_SOL = float(os.getenv("PAPER_TRADING_BALANCE", "50.0")) # Start with 50 SOL paper money
    
    # Strategy Settings
    MIN_BUY_WAVE_SCORE = float(os.getenv("MIN_BUY_WAVE_SCORE", "7.5"))
    DEFAULT_STOP_LOSS = float(os.getenv("DEFAULT_STOP_LOSS", "0.10")) # 10%
    
    # Nansen endpoints
    NANSEN_BASE_URL = "https://api.nansen.ai/api/v1"
