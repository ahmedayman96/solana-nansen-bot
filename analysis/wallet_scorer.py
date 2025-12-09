from typing import List, Dict
from data.models import WalletScore, Transaction

class WalletScorer:
    def __init__(self):
        self.wallet_scores: Dict[str, WalletScore] = {}

    def score_wallet(self, address: str, historical_txs: List[Transaction]) -> WalletScore:
        """
        Analyzes historical transactions to assign a score/grade.
        """
        # Placeholder logic for grading
        # In a real app, calculate Win Rate, PnL% per trade
        
        # Stub values for now
        total_trades = len(historical_txs) // 2
        win_rate = 0.65 if total_trades > 5 else 0.5
        avg_roi = 20.0
        
        score = WalletScore(
            address=address,
            win_rate=win_rate,
            avg_roi=avg_roi,
            median_holding_time_minutes=120.0, # Default mock
            grade="B"
        )
        
        # Grading logic
        if win_rate > 0.6 and avg_roi > 30:
            score.grade = "S" # S-tier (Smartest Money)
        elif win_rate > 0.5:
            score.grade = "A"
        
        self.wallet_scores[address] = score
        return score

    def get_wallet_grade(self, address: str) -> str:
        if address in self.wallet_scores:
            return self.wallet_scores[address].grade
        return "C" # Default unknown
