import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class Store:
    def __init__(self, db_path="bot_data.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 1. Trades Table
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token_address TEXT,
            type TEXT, -- BUY / SELL
            amount REAL,
            price REAL,
            timestamp DATETIME,
            pnl REAL,
            pnl_percent REAL,
            reasoning TEXT -- Short explanation
        )''')

        # 2. Portfolio Table (Snapshots)
        c.execute('''CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            total_value_sol REAL,
            active_positions TEXT -- JSON dump
        )''')
        
        # 3. Cache Table (Simple Key-Value for API responses)
        c.execute('''CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT,
            expiry DATETIME
        )''')

        # 4. System Status Table
        c.execute('''CREATE TABLE IF NOT EXISTS system_status (
            key TEXT PRIMARY KEY,
            value TEXT,
            timestamp DATETIME
        )''')

        # 5. Activity Logs Table
        c.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            level TEXT,
            timestamp DATETIME
        )''')
        
        conn.commit()
        conn.close()

    def add_log(self, message: str, level: str = "INFO"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO logs (message, level, timestamp) VALUES (?, ?, ?)",
                  (message, level, datetime.utcnow().isoformat() + "Z"))
        # Keep only last 100 logs
        c.execute("DELETE FROM logs WHERE id NOT IN (SELECT id FROM logs ORDER BY id DESC LIMIT 100)")
        conn.commit()
        conn.close()

    def get_recent_logs(self, limit: int = 20) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT message, level, timestamp FROM logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_heartbeat(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO system_status (key, value, timestamp) VALUES (?, ?, ?)",
                  ("heartbeat", "alive", datetime.utcnow().isoformat() + "Z"))
        conn.commit()
        conn.close()

    def get_heartbeat(self) -> Optional[datetime]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT timestamp FROM system_status WHERE key = 'heartbeat'")
        row = c.fetchone()
        conn.close()
        if row:
            return datetime.fromisoformat(row[0])
        return None

    def add_trade(self, trade_data: Dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO trades 
            (token_address, type, amount, price, timestamp, pnl, pnl_percent, reasoning) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                trade_data['token'],
                trade_data['type'],
                trade_data['amount_sol'],
                trade_data['price'],
                trade_data['time'].isoformat(),
                trade_data.get('pnl', 0.0),
                trade_data.get('pnl_percent', 0.0),
                trade_data.get('reasoning', "")
            )
        )
        conn.commit()
        conn.close()

    def log_portfolio(self, total_value: float, positions: Dict):
        # Convert positions to JSON-friendly format
        pos_list = []
        for token, pos in positions.items():
            pos_list.append({
                "token": token,
                "amount": pos.amount,
                "entry_price": pos.entry_price,
                "current_val": pos.amount * pos.entry_price, # simplified
                "target_exit": pos.target_exit_time.isoformat()
            })
            
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO portfolio (timestamp, total_value_sol, active_positions) VALUES (?, ?, ?)",
                  (datetime.utcnow().isoformat() + "Z", total_value, json.dumps(pos_list)))
        conn.commit()
        conn.close()

    def get_trades(self, limit=50) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM trades ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
        
    def get_portfolio_history(self, limit=100) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM portfolio ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # --- Caching Methods ---
    def get_cache_item(self, key: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT value, expiry FROM cache WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        
        if row:
            value_json, expiry_str = row
            expiry = datetime.fromisoformat(expiry_str)
            if datetime.now() < expiry:
                return json.loads(value_json)
            else:
                # Expired
                return None
        return None

    def set_cache_item(self, key: str, value: Dict, ttl_seconds: int = 3600):
        # Default TTL 1 hour
        expiry = datetime.now().timestamp() + ttl_seconds
        expiry_dt = datetime.fromtimestamp(expiry)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO cache (key, value, expiry) VALUES (?, ?, ?)",
                  (key, json.dumps(value), expiry_dt.isoformat()))
        conn.commit()
        conn.close()
