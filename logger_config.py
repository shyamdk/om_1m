#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging Configuration Module
Provides structured logging for the trading system
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        """Format log record with colors"""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logger(name='trading_system', log_dir=None, level=logging.INFO):
    """
    Setup comprehensive logging system

    Args:
        name: Logger name
        log_dir: Directory for log files (default: ./logs)
        level: Logging level

    Returns:
        logging.Logger: Configured logger instance
    """

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create log directory
    if log_dir is None:
        log_dir = Path(__file__).parent / 'logs'
    else:
        log_dir = Path(log_dir)

    log_dir.mkdir(parents=True, exist_ok=True)

    # Log file paths
    today = datetime.now().strftime('%Y-%m-%d')
    main_log_file = log_dir / f'{today}_trading.log'
    error_log_file = log_dir / f'{today}_errors.log'
    trade_log_file = log_dir / f'{today}_trades.log'

    # Formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )

    colored_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(colored_formatter)

    # Main log file handler (all logs)
    main_file_handler = RotatingFileHandler(
        main_log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    main_file_handler.setLevel(logging.DEBUG)
    main_file_handler.setFormatter(detailed_formatter)

    # Error log file handler (errors only)
    error_file_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=3
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_formatter)

    # Trade log file handler (custom level for trades)
    trade_file_handler = RotatingFileHandler(
        trade_log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=10
    )
    trade_file_handler.setLevel(logging.INFO)
    trade_file_handler.setFormatter(simple_formatter)

    # Add filter for trade logs
    trade_file_handler.addFilter(lambda record: 'TRADE' in record.getMessage())

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(main_file_handler)
    logger.addHandler(error_file_handler)
    logger.addHandler(trade_file_handler)

    return logger


class TradeLogger:
    """
    Specialized logger for trade events
    """

    def __init__(self, logger=None):
        """
        Initialize trade logger

        Args:
            logger: Base logger instance (optional)
        """
        self.logger = logger or setup_logger()

    def log_entry(self, tradingsymbol, entry_price, quantity, strategy, order_id):
        """Log trade entry"""
        self.logger.info(
            f"TRADE ENTRY | {tradingsymbol} | "
            f"Price: ₹{entry_price:.2f} | Qty: {quantity} | "
            f"Strategy: {strategy} | Order ID: {order_id}"
        )

    def log_exit(self, tradingsymbol, exit_price, quantity, pnl, pnl_pct, reason, order_id):
        """Log trade exit"""
        pnl_str = f"₹{pnl:+.2f} ({pnl_pct:+.2f}%)"
        self.logger.info(
            f"TRADE EXIT | {tradingsymbol} | "
            f"Price: ₹{exit_price:.2f} | Qty: {quantity} | "
            f"P&L: {pnl_str} | Reason: {reason} | Order ID: {order_id}"
        )

    def log_order_status(self, tradingsymbol, order_id, status, message=""):
        """Log order status change"""
        self.logger.info(
            f"TRADE ORDER | {tradingsymbol} | "
            f"Order ID: {order_id} | Status: {status} | {message}"
        )

    def log_risk_event(self, event_type, message):
        """Log risk management event"""
        self.logger.warning(
            f"TRADE RISK | {event_type} | {message}"
        )

    def log_daily_summary(self, summary):
        """Log daily trading summary"""
        self.logger.info(
            f"TRADE SUMMARY | "
            f"Trades: {summary['total_trades']} | "
            f"Win Rate: {summary.get('win_rate', 0):.1f}% | "
            f"P&L: ₹{summary['total_profit_loss']:+.2f}"
        )


def get_logger(name='trading_system'):
    """
    Get or create logger instance

    Args:
        name: Logger name

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


# Create default logger instance
_default_logger = None
_trade_logger = None

def get_default_logger():
    """Get default logger singleton"""
    global _default_logger
    if _default_logger is None:
        _default_logger = setup_logger()
    return _default_logger

def get_trade_logger():
    """Get trade logger singleton"""
    global _trade_logger
    if _trade_logger is None:
        _trade_logger = TradeLogger(get_default_logger())
    return _trade_logger


# Example usage functions
def log_system_start():
    """Log system startup"""
    logger = get_default_logger()
    logger.info("="*80)
    logger.info("TRADING SYSTEM STARTING")
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)

def log_system_stop():
    """Log system shutdown"""
    logger = get_default_logger()
    logger.info("="*80)
    logger.info("TRADING SYSTEM STOPPING")
    logger.info(f"Stop Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)
