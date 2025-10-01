#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Module - SQLite Database for Trade Management
Replaces CSV files with proper database storage
"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import threading
import json


class TradingDatabase:
    """
    SQLite database manager for trading system
    Thread-safe with connection pooling
    """

    def __init__(self, db_path):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.lock = threading.Lock()
        self._ensure_directory()
        self._initialize_tables()

    def _ensure_directory(self):
        """Ensure database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def _initialize_tables(self):
        """Create database tables if they don't exist"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE NOT NULL,
                    tradingsymbol TEXT NOT NULL,
                    symboltoken TEXT NOT NULL,

                    -- Order details
                    order_date TEXT NOT NULL,
                    order_quantity INTEGER NOT NULL,
                    order_price REAL NOT NULL,
                    order_status TEXT NOT NULL,
                    order_strategy TEXT,

                    -- Buy details
                    buy_date TEXT,
                    buy_quantity INTEGER,
                    buy_price REAL,
                    buy_status TEXT,
                    unique_buy_order_id TEXT,

                    -- Sell details
                    sell_date TEXT,
                    sell_quantity INTEGER,
                    sell_price REAL,
                    sell_status TEXT,
                    sell_strategy TEXT,
                    unique_sell_order_id TEXT,

                    -- Status tracking
                    shyam_status TEXT NOT NULL DEFAULT 'ordered',

                    -- P&L
                    buy_total REAL,
                    sell_total REAL,
                    profit_loss REAL,

                    -- Trailing stop loss tracking
                    max_profit_seen REAL DEFAULT 0,

                    -- Metadata
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            # Daily P&L summary table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_pnl (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_date TEXT UNIQUE NOT NULL,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    total_profit_loss REAL DEFAULT 0,
                    max_profit REAL DEFAULT 0,
                    max_loss REAL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            # System metrics table (for circuit breakers)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_date TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(metric_date, metric_name)
                )
            ''')

            # Create indices for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_trades_symbol
                ON trades(tradingsymbol)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_trades_status
                ON trades(shyam_status)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_trades_date
                ON trades(order_date)
            ''')

            conn.commit()
            conn.close()

    def insert_trade(self, trade_data):
        """
        Insert a new trade record

        Args:
            trade_data: Dictionary with trade details

        Returns:
            str: order_id of inserted trade
        """
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order_id = datetime.now().strftime("%d%H%M%S")

            cursor.execute('''
                INSERT INTO trades (
                    order_id, tradingsymbol, symboltoken,
                    order_date, order_quantity, order_price,
                    order_status, order_strategy, unique_buy_order_id,
                    shyam_status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id,
                trade_data['tradingsymbol'],
                trade_data['symboltoken'],
                trade_data['order_date'],
                trade_data['order_quantity'],
                trade_data['order_price'],
                trade_data['order_status'],
                trade_data['order_strategy'],
                trade_data['unique_buy_order_id'],
                trade_data['shyam_status'],
                now,
                now
            ))

            conn.commit()
            conn.close()
            return order_id

    def update_buy_trade(self, order_id, buy_data):
        """
        Update trade with buy execution details

        Args:
            order_id: Order ID to update
            buy_data: Dictionary with buy details
        """
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('''
                UPDATE trades
                SET buy_date = ?, buy_quantity = ?, buy_price = ?,
                    buy_status = ?, unique_buy_order_id = ?,
                    shyam_status = ?, buy_total = ?, updated_at = ?
                WHERE order_id = ?
            ''', (
                buy_data['buy_date'],
                buy_data['buy_quantity'],
                buy_data['buy_price'],
                buy_data.get('buy_status', 'complete'),
                buy_data['unique_buy_order_id'],
                buy_data['shyam_status'],
                buy_data['buy_quantity'] * buy_data['buy_price'],
                now,
                order_id
            ))

            conn.commit()
            conn.close()

    def update_sell_trade(self, order_id, sell_data):
        """
        Update trade with sell execution details

        Args:
            order_id: Order ID to update
            sell_data: Dictionary with sell details
        """
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Calculate P&L
            cursor.execute('SELECT buy_price, buy_quantity FROM trades WHERE order_id = ?', (order_id,))
            row = cursor.fetchone()

            if row:
                buy_price = row['buy_price'] or row[0]
                buy_quantity = row['buy_quantity'] or row[1]
                sell_total = sell_data['sell_quantity'] * sell_data['sell_price']
                buy_total = buy_quantity * buy_price
                profit_loss = sell_total - buy_total

                cursor.execute('''
                    UPDATE trades
                    SET sell_date = ?, sell_quantity = ?, sell_price = ?,
                        sell_status = ?, sell_strategy = ?, unique_sell_order_id = ?,
                        shyam_status = ?, sell_total = ?, profit_loss = ?, updated_at = ?
                    WHERE order_id = ?
                ''', (
                    sell_data['sell_date'],
                    sell_data['sell_quantity'],
                    sell_data['sell_price'],
                    sell_data['sell_status'],
                    sell_data['sell_strategy'],
                    sell_data['unique_sell_order_id'],
                    sell_data['shyam_status'],
                    sell_total,
                    profit_loss,
                    now,
                    order_id
                ))

                # Update daily P&L
                trade_date = datetime.now().strftime("%Y-%m-%d")
                self._update_daily_pnl(cursor, trade_date, profit_loss)

            conn.commit()
            conn.close()

    def update_max_profit_seen(self, order_id, max_profit_pct):
        """
        Update max profit seen for trailing stop loss

        Args:
            order_id: Order ID
            max_profit_pct: Maximum profit percentage seen
        """
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('''
                UPDATE trades
                SET max_profit_seen = ?, updated_at = ?
                WHERE order_id = ?
            ''', (max_profit_pct, now, order_id))

            conn.commit()
            conn.close()

    def _update_daily_pnl(self, cursor, trade_date, profit_loss):
        """Update daily P&L summary"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if record exists
        cursor.execute('SELECT * FROM daily_pnl WHERE trade_date = ?', (trade_date,))
        row = cursor.fetchone()

        if row:
            # Update existing
            cursor.execute('''
                UPDATE daily_pnl
                SET total_trades = total_trades + 1,
                    winning_trades = winning_trades + ?,
                    losing_trades = losing_trades + ?,
                    total_profit_loss = total_profit_loss + ?,
                    max_profit = MAX(max_profit, ?),
                    max_loss = MIN(max_loss, ?),
                    updated_at = ?
                WHERE trade_date = ?
            ''', (
                1 if profit_loss > 0 else 0,
                1 if profit_loss <= 0 else 0,
                profit_loss,
                profit_loss if profit_loss > 0 else 0,
                profit_loss if profit_loss < 0 else 0,
                now,
                trade_date
            ))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO daily_pnl (
                    trade_date, total_trades, winning_trades, losing_trades,
                    total_profit_loss, max_profit, max_loss, created_at, updated_at
                ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_date,
                1 if profit_loss > 0 else 0,
                1 if profit_loss <= 0 else 0,
                profit_loss,
                profit_loss if profit_loss > 0 else 0,
                profit_loss if profit_loss < 0 else 0,
                now,
                now
            ))

    def get_open_trades(self, tradingsymbol=None):
        """
        Get all open trades (buy_complete status)

        Args:
            tradingsymbol: Optional filter by symbol

        Returns:
            list: List of open trade dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if tradingsymbol:
            cursor.execute('''
                SELECT * FROM trades
                WHERE shyam_status = 'buy_complete' AND tradingsymbol = ?
                ORDER BY created_at DESC
            ''', (tradingsymbol,))
        else:
            cursor.execute('''
                SELECT * FROM trades
                WHERE shyam_status = 'buy_complete'
                ORDER BY created_at DESC
            ''')

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_today_pnl(self):
        """
        Get today's P&L summary

        Returns:
            dict: Today's P&L statistics
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('SELECT * FROM daily_pnl WHERE trade_date = ?', (today,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        else:
            return {
                'trade_date': today,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_profit_loss': 0,
                'max_profit': 0,
                'max_loss': 0
            }

    def get_trade_by_order_id(self, order_id):
        """Get trade details by order ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM trades WHERE order_id = ?', (order_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def export_to_csv(self, output_path, start_date=None, end_date=None):
        """
        Export trades to CSV file

        Args:
            output_path: Path to output CSV file
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
        """
        conn = self._get_connection()

        query = 'SELECT * FROM trades WHERE 1=1'
        params = []

        if start_date:
            query += ' AND order_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND order_date <= ?'
            params.append(end_date)

        query += ' ORDER BY created_at DESC'

        df = pd.read_sql_query(query, conn, params=params)
        df.to_csv(output_path, index=False)
        conn.close()

        return len(df)


# Singleton instance
_db_instance = None

def get_database(db_path=None):
    """Get database singleton instance"""
    global _db_instance
    if _db_instance is None:
        if db_path is None:
            from secure_config import get_secure_config
            db_path = get_secure_config().get_db_path()
        _db_instance = TradingDatabase(db_path)
    return _db_instance
