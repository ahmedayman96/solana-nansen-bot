from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Token:
    address: str
    symbol: str
    decimals: int

@dataclass
class WalletLabel:
    address: str
    label: str # e.g., "Smart Money", "Influencer", "Fund"
    is_smart_money: bool

@dataclass
class Transaction:
    tx_hash: str
    from_address: str
    to_address: str
    token_address: str
    amount: float
    timestamp: datetime
    block_number: int

@dataclass
class WalletScore:
    address: str
    win_rate: float
    avg_roi: float
    median_holding_time_minutes: float
    grade: str # "A", "B", "C" based on performance
