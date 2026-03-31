from __future__ import annotations

import os
import sqlite3
from pathlib import Path


_db_path_env = os.getenv("DATABASE_PATH")
DB_PATH = Path(_db_path_env) if _db_path_env else Path("data") / "app.db"
DATA_DIR = DB_PATH.parent


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS onboarding_profiles (
                user_id INTEGER PRIMARY KEY,
                goal_type TEXT NOT NULL,
                goal_amount REAL NOT NULL,
                investment_horizon_years INTEGER NOT NULL,
                age INTEGER NOT NULL,
                date_of_birth TEXT NOT NULL,
                marital_status TEXT NOT NULL,
                address TEXT NOT NULL,
                annual_income REAL NOT NULL,
                current_savings REAL NOT NULL,
                monthly_contribution REAL NOT NULL,
                savings_rate REAL NOT NULL,
                risk_preference TEXT NOT NULL,
                stress_response TEXT NOT NULL,
                strategy_preference TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
