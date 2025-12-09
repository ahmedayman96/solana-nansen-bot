import { NextResponse } from 'next/server';
import sqlite3 from 'sqlite3';
import path from 'path';

// Database path - relative to dashboard folder, it's one level up
const DB_PATH = path.resolve(process.cwd(), '../bot_data.db');

export async function GET() {
    const db = new sqlite3.Database(DB_PATH, sqlite3.OPEN_READONLY);

    const getTrades = () => {
        return new Promise((resolve, reject) => {
            db.all("SELECT * FROM trades ORDER BY id DESC LIMIT 50", (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    };

    const getPortfolio = () => {
        return new Promise((resolve, reject) => {
            // Get latest portfolio snapshot
            db.get("SELECT * FROM portfolio ORDER BY id DESC LIMIT 1", (err, row) => {
                if (err) reject(err);
                else resolve(row);
            });
        });
    };

    const getHeartbeat = () => {
        return new Promise((resolve, reject) => {
            db.get("SELECT timestamp FROM system_status WHERE key = 'heartbeat'", (err, row) => {
                if (err) resolve(null); // Non-critical
                else resolve(row);
            });
        });
    };

    const getLogs = () => {
        return new Promise((resolve, reject) => {
            db.all("SELECT message, level, timestamp FROM logs ORDER BY id DESC LIMIT 50", (err, rows) => {
                if (err) resolve([]);
                else resolve(rows);
            });
        });
    };

    try {
        const [trades, portfolio, heartbeat, logs] = await Promise.all([
            getTrades(),
            getPortfolio(),
            getHeartbeat(),
            getLogs()
        ]);

        // Calculate Status Server-Side to avoid Clock Skew
        let is_online = false;
        let seconds_ago = 99999;

        if (heartbeat && heartbeat.timestamp) {
            const last = new Date(heartbeat.timestamp).getTime();
            const now = Date.now(); // Server UTC time (roughly)
            seconds_ago = (now - last) / 1000;
            is_online = seconds_ago < 120; // 2 mins threshold
        }

        db.close();

        return NextResponse.json({
            trades,
            portfolio: portfolio || null,
            heartbeat: heartbeat || null,
            logs: logs || [],
            status_data: {
                is_online,
                seconds_ago
            }
        });
    } catch (error) {
        db.close();
        return NextResponse.json({ error: 'Database error', details: error }, { status: 500 });
    }
}
