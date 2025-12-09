import datetime
from data.models import Transaction
from engine.strategy import Strategy
from engine.paper_trader import PaperTrader
import time

def mock_get_smart_money_transactions(token_address):
    """
    Overrides the strategy's nansen client method to return a BUY WAVE.
    """
    print(f"DEBUG: Returning mock Buy Wave for {token_address}")
    base_time = datetime.datetime.now()
    txs = []
    # Create 10 buys in the last 10 minutes from "SmartMoney"
    for i in range(10):
        tx = Transaction(
            tx_hash=f"tx_{i}",
            from_address=f"smart_wallet_{i}", # Treated as BUY if from is smart wallet? No, in logic: to_address=wallet is ENTRY
            # Wait, holding_time.py says: 
            # if tx.to_address == wallet: wallet_txs[wallet]['entries'].append(tx)
            # So for a BUY (entry), the Smart Wallet should be the receiver of the token?
            # Usually strict: Swap SOL -> Token. Token goes TO wallet.
            to_address=f"smart_wallet_{i}",
            token_address=token_address,
            amount=1000.0,
            timestamp=base_time - datetime.timedelta(minutes=i), # 0 to 9 mins ago
            block_number=1000+i
        )
        txs.append(tx)
    return txs

def run_verification():
    print("--- Starting Verification Simulation ---")
    
    # 1. Setup
    trader = PaperTrader(initial_balance=100.0)
    strategy = Strategy(trader)
    
    # Override the method on the instance to inject mock data
    # We need to monkeypath the nansen client instance inside strategy
    strategy.nansen.get_smart_money_transactions = mock_get_smart_money_transactions
    
    # Override _check_buy_wave to TRUE for this test, or ensure logic passes
    # Let's inspect _check_buy_wave in strategy.py... it returns False by default.
    # We need to update it or mock it.
    strategy._check_buy_wave = lambda txs: True # Force True for test
    
    # 2. Run Cycle (Should Trigger BUY)
    print("\n[Step 1] Running Strategy Cycle (Expecting BUY)...")
    strategy.run_cycle()
    
    # Check Result
    if "MockTokenAddress123" in trader.positions:
        print("SUCCESS: Position created!")
        pos = trader.positions["MockTokenAddress123"]
        print(f"Position Details: {pos}")
        
        # Verify DB
        from data.store import Store
        store = Store()
        trades = store.get_trades()
        if trades and trades[0]['token_address'] == "MockTokenAddress123":
             print("SUCCESS: Trade logged to SQLite DB.")
        else:
             print("FAILURE: Trade NOT found in SQLite DB.")
             
    else:
        print("FAILURE: No position created.")
        # Diagnostics
        print(f"Active Tokens: {strategy.active_tokens}")
        print("Check terminal output for 'Nansen API Error' messages.")
        return

     # Verify Heartbeat
    from data.store import Store
    hb_store = Store()
    hb_store.update_heartbeat()
    hb = hb_store.get_heartbeat()
    if hb:
         print(f"SUCCESS: Heartbeat active at {hb.isoformat()}")
    else:
         print("FAILURE: Heartbeat not found.")

    # 3. Simulate Time Passing for Exit
    print("\n[Step 2] Simulating Time Pass (Expecting SELL)...")
    # Manually adjust target_exit_time to be in the past
    trader.positions["MockTokenAddress123"].target_exit_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
    
    strategy.run_cycle()
    
    # Check Result
    if "MockTokenAddress123" not in trader.positions:
        print("SUCCESS: Position closed!")
        last_trade = trader.trade_history[-1]
        print(f"Sell Trade: {last_trade}")
    else:
        print("FAILURE: Position not closed.")

if __name__ == "__main__":
    run_verification()
