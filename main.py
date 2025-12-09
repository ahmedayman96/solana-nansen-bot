import time
from config import Config
from engine.strategy import Strategy
from engine.paper_trader import PaperTrader
from data.nansen_client import NansenClient

def main():
    print("Starting Solana Nansen Bot...")
    print(f"Mode: {'PAPER TRADING'}")
    
    # Initialize components
    nansen = NansenClient(api_key=Config.NANSEN_API_KEY)
    trader = PaperTrader(initial_balance=Config.PAPER_TRADING_BALANCE_SOL)
    strategy = Strategy(trader=trader) # Note: Strategy creates its own NansenClient internally in current code, let's fix that.
    
    print(f"Initial Portfolio Value: {trader.get_portfolio_value()} SOL")
    
    # Main Loop
    try:
        from data.store import Store
        store = Store()
        
        while True:
            print("Scanning for signals...")
            store.update_heartbeat() # Pulse
            
            # Mock loop for now
            strategy.run_cycle()
            time.sleep(60) # Run every minute
            
    except KeyboardInterrupt:
        print("Bot stopped by user.")
        print(f"Final Portfolio Value: {trader.get_portfolio_value()} SOL")

if __name__ == "__main__":
    main()
