"""
SQLite Financial Data Service.

Ported from Dev 1's scoutr-backend. Provides player financial data
(contract expiry, market value) and historical match statistics from StatsBomb.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data_pipeline/data/db/players.db')


def init_db():
    """Initialize the database and create tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Player Financials (Mocked from FBRef data)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_financials (
            player_id TEXT PRIMARY KEY,
            contract_expiry TEXT,
            market_value REAL
        )
    ''')

    # 2. Match-by-match statistics (Extracted from StatsBomb)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player_match_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT,
            match_id TEXT,
            match_date TEXT,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            tackles INTEGER DEFAULT 0,
            passes_accuracy REAL DEFAULT 0,
            rating REAL DEFAULT 6.5,
            minutes_played INTEGER DEFAULT 0,
            UNIQUE(player_id, match_id)
        )
    ''')

    # 3. Form Cache (For rapid-api backward compatibility/offline use)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS form_cache (
            player_id TEXT PRIMARY KEY,
            form_score REAL,
            style_fit TEXT,
            last_updated TEXT
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


def save_match_stat(player_id: str, match_id: str, match_date: str, goals: int, assists: int, tackles: int, passes_acc: float, rating: float, mins: int):
    """Save a single match performance record."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO player_match_stats 
        (player_id, match_id, match_date, goals, assists, tackles, passes_accuracy, rating, minutes_played)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (player_id, match_id, match_date, goals, assists, tackles, passes_acc, rating, mins))
    conn.commit()
    conn.close()


def get_recent_matches(player_id: str, limit: int = 5) -> list[dict]:
    """Get the N most recent match stats for a player."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM player_match_stats 
        WHERE player_id = ? 
        ORDER BY match_date DESC 
        LIMIT ?
    ''', (player_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_form_cache(player_id: str):
    """Retrieve cached form score and style fit."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT form_score, style_fit FROM form_cache WHERE player_id = ?', (player_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"form_score": row[0], "style_fit": row[1]}
    return None


def save_form_cache(player_id: str, form_score: float, style_fit: str):
    """Save or update form cache."""
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO form_cache (player_id, form_score, style_fit, last_updated)
        VALUES (?, ?, ?, ?)
    ''', (player_id, form_score, style_fit, datetime.now().isoformat()))
    conn.commit()
    conn.close()


init_db()
