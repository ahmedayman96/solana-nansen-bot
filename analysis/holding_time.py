from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np
from data.models import Transaction

class HoldingTimeAnalyzer:
    @staticmethod
    def calculate_median_holding_time(entry_txs: List[Transaction], exit_txs: List[Transaction]) -> float:
        """
        Calculates the median holding time in minutes.
        Matches entries to exits using a FIFO (First-In-First-Out) method for simplicity in this MVP.
        """
        if not entry_txs or not exit_txs:
            return 0.0

        # Sort by time
        sorted_entries = sorted(entry_txs, key=lambda x: x.timestamp)
        sorted_exits = sorted(exit_txs, key=lambda x: x.timestamp)
        
        durations = []
        
        # Simplified matching logic: 
        # Assume 1 entry maps to 1 exit for the sake of metric calculation in this prototype.
        # In production, this needs robust accounting (partial fills).
        
        min_len = min(len(sorted_entries), len(sorted_exits))
        
        for i in range(min_len):
            entry_time = sorted_entries[i].timestamp
            exit_time = sorted_exits[i].timestamp
            
            if exit_time > entry_time:
                duration = (exit_time - entry_time).total_seconds() / 60
                durations.append(duration)
        
        if not durations:
            return 0.0
            
        return float(np.median(durations))

    @staticmethod
    def get_smart_money_median_hold_time(transactions: List[Transaction], smart_wallets: List[str]) -> float:
        """
        Filters transactions for smart wallets and calculates their collective median holding time.
        """
        # Group txs by wallet
        wallet_txs = {}
        for tx in transactions:
            if tx.from_address in smart_wallets or tx.to_address in smart_wallets:
                wallet = tx.from_address if tx.from_address in smart_wallets else tx.to_address
                if wallet not in wallet_txs:
                    wallet_txs[wallet] = {'entries': [], 'exits': []}
                
                # Simple heuristic: buying if 'to' is wallet, selling if 'from' is wallet
                # (Ignoring token transfers logic details for now)
                if tx.to_address == wallet:
                    wallet_txs[wallet]['entries'].append(tx)
                else:
                    wallet_txs[wallet]['exits'].append(tx)
        
        all_durations = []
        for wallet, txs in wallet_txs.items():
            # Calculate for each wallet
            # Reuse logic from calculate_median_holding_time but we can't call it directly continuously
            # Re-implement simple matching inside loop for aggregation
             entries = sorted(txs['entries'], key=lambda x: x.timestamp)
             exits = sorted(txs['exits'], key=lambda x: x.timestamp)
             min_l = min(len(entries), len(exits))
             for i in range(min_l):
                 if exits[i].timestamp > entries[i].timestamp:
                     all_durations.append((exits[i].timestamp - entries[i].timestamp).total_seconds() / 60)
        
        if not all_durations:
            return 240.0 # Default 4 hours if no data
            
        return float(np.median(all_durations))
