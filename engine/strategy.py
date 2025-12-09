from typing import List
from datetime import datetime, timedelta
from engine.paper_trader import PaperTrader
from data.nansen_client import NansenClient
from analysis.holding_time import HoldingTimeAnalyzer
from config import Config

class Strategy:
    def __init__(self, trader: PaperTrader):
        self.trader = trader
        self.nansen = NansenClient(api_key=Config.NANSEN_API_KEY)
        # Scanning BONK for testing
        self.active_tokens = ["DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"]
    
    def _log(self, message: str, level: str = "INFO"):
        from data.store import Store
        store = Store()
        store.add_log(message, level)
        print(f"{level}: {message}")

    def run_cycle(self):
        """
        Main logic loop:
        1. Scan for Buy Waves
        2. Manage Open Positions
        """
        self._scan_for_entries()
        self._manage_positions()
        
    def _scan_for_entries(self):
        self._log("Scanning for buy waves...", "INFO")
        for token in self.active_tokens:
            # Check if we already have a position
            if token in self.trader.positions:
                continue
                
            self._log(f"Scanning token {token}...", "INFO")
            
            # 1. Get recent Smart Money activity
            txs = self.nansen.get_smart_money_transactions(token)
            
            if self._check_buy_wave(txs):
                self._log(f"BUY WAVE DETECTED for {token}!", "SUCCESS")
                # Calculate Median Holding Time
                # Using 80% of median time to front-run the dump
                median_hold_time = 240 # Mock median
                target_hold_mins = median_hold_time * 0.8
                target_exit_time = datetime.now() + timedelta(minutes=target_hold_mins)
                
                self.trader.buy(token, amount_sol=1.0, price_per_token=0.01, target_exit_time=target_exit_time)
            else:
                 self._log(f"No signal for {token}. Found {len(txs)} SM txs.", "INFO")
                
    def _check_buy_wave(self, transactions: List) -> bool:
        # Simplistic Buy Wave Logic:
        # If we see >= 3 Smart Money transactions in the result, we trigger.
        # In production this would be: "3 buys in 10 minutes"
        if len(transactions) >= 3:
            return True
        return False 

    def _manage_positions(self):
        # Check if we need to sell
        for token, pos in list(self.trader.positions.items()):
            # Time-based exit
            if datetime.now() >= pos.target_exit_time:
                print(f"Time Exit Triggered for {token}")
                # Mock current price (randomly up or down)
                current_price = pos.entry_price * 1.05 # Mock 5% gain
                self.trader.sell(token, current_price)
