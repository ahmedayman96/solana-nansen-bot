from typing import Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Position:
    token_address: str
    amount: float
    entry_price: float
    entry_time: datetime
    target_exit_time: datetime

class PaperTrader:
    def __init__(self, initial_balance: float = 10.0):
        self.balance_sol = initial_balance
        self.positions: Dict[str, Position] = {}
        self.trade_history = []
        
        # Initial Log
        from data.store import Store
        store = Store()
        store.log_portfolio(self.balance_sol, self.positions)
        
    def get_portfolio_value(self) -> float:
        # In a real system, we'd need current prices of all held tokens
        # For simplicity, returning SOL balance
        return self.balance_sol

    def buy(self, token_address: str, amount_sol: float, price_per_token: float, target_exit_time: datetime):
        if amount_sol > self.balance_sol:
            print(f"FAILED BUY: Insufficient funds. Balance: {self.balance_sol}, Required: {amount_sol}")
            return
            
        token_amount = amount_sol / price_per_token
        self.balance_sol -= amount_sol
        
        position = Position(
            token_address=token_address,
            amount=token_amount,
            entry_price=price_per_token,
            entry_time=datetime.now(),
            target_exit_time=target_exit_time
        )
        self.positions[token_address] = position
        
        trade_data = {
            "type": "BUY",
            "token": token_address,
            "amount_sol": amount_sol,
            "price": price_per_token,
            "time": datetime.now(),
            "reasoning": "Buy Wave Detected" # Placeholder, can be passed in
        }
        self.trade_history.append(trade_data)
        
        # Persistent Log
        from data.store import Store
        store = Store()
        store.add_trade(trade_data)
        
        # Log Portfolio State
        store.log_portfolio(self.balance_sol, self.positions)
        
        print(f"PAPER TRADE: BOUGHT {token_amount:.4f} of {token_address} @ {price_per_token} SOL")

    def sell(self, token_address: str, price_per_token: float):
        if token_address not in self.positions:
            return
            
        pos = self.positions[token_address]
        sol_value = pos.amount * price_per_token
        self.balance_sol += sol_value
        
        # Calculate PnL
        pnl = sol_value - (pos.amount * pos.entry_price)
        pnl_percent = (pnl / (pos.amount * pos.entry_price)) * 100
        
        trade_data = {
            "type": "SELL",
            "token": token_address,
            "amount_sol": sol_value,
            "price": price_per_token,
            "pnl": pnl,
            "pnl_percent": pnl_percent,
            "time": datetime.now(),
            "reasoning": "Target Exit Time Reached" # Default
        }
        self.trade_history.append(trade_data)
        
        # Persistent Log
        from data.store import Store
        store = Store()
        store.add_trade(trade_data)
        
        # Log Portfolio State
        store.log_portfolio(self.balance_sol, self.positions)
        
        del self.positions[token_address]
        print(f"PAPER TRADE: SOLD {pos.amount:.4f} of {token_address} @ {price_per_token} SOL. PnL: {pnl_percent:.2f}%")
