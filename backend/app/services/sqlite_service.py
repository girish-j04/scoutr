"""
SQLite Financial Data Service.

Ported from Dev 1's scoutr-backend. Provides player financial data
(contract expiry, market value) from a local SQLite database.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data_pipeline/data/db/players.db')


def init_db():
    """Initialize the database and create tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_financials (
            player_id TEXT PRIMARY KEY,
            contract_expiry TEXT,
            market_value REAL
        )
    ''')
    conn.commit()
    conn.close()


def get_player_financials(player_id: str):
    """Get contract expiry and market value for a player."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT contract_expiry, market_value FROM player_financials WHERE player_id = ?', (player_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"contract_expiry": row[0], "market_value": row[1]}
    return {"contract_expiry": None, "market_value": None}


def save_financials(player_id: str, contract_expiry: str, market_value: float):
    """Save or update player financial data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO player_financials (player_id, contract_expiry, market_value)
        VALUES (?, ?, ?)
    ''', (player_id, contract_expiry, market_value))
    conn.commit()
    conn.close()


init_db()
