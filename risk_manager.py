#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Risk Management Module
Implements circuit breakers, position limits, and daily loss limits
"""

from datetime import datetime
import config
from database import get_database


class RiskManager:
    """
    Comprehensive risk management system
    """

    def __init__(self, db=None):
        """
        Initialize risk manager

        Args:
            db: Database instance (optional, will create if not provided)
        """
        self.db = db or get_database()
        self.trading_enabled = True
        self.halt_reason = None

    def check_daily_loss_limit(self):
        """
        Check if daily loss limit has been exceeded

        Returns:
            dict: {
                'allowed': bool,
                'reason': str,
                'pnl': dict
            }
        """
        pnl = self.db.get_today_pnl()
        total_pnl = pnl.get('total_profit_loss', 0)

        # Check against max daily loss
        if total_pnl <= config.MAX_DAILY_LOSS:
            return {
                'allowed': False,
                'reason': f"Daily loss limit exceeded: ₹{total_pnl:+.2f} (Limit: ₹{config.MAX_DAILY_LOSS})",
                'pnl': pnl
            }

        return {
            'allowed': True,
            'reason': 'Within daily loss limit',
            'pnl': pnl
        }

    def check_max_positions(self):
        """
        Check if maximum position count has been reached

        Returns:
            dict: {
                'allowed': bool,
                'reason': str,
                'current_count': int
            }
        """
        open_trades = self.db.get_open_trades()
        current_count = len(open_trades)

        if current_count >= config.MAX_POSITION_COUNT:
            return {
                'allowed': False,
                'reason': f"Maximum positions reached: {current_count}/{config.MAX_POSITION_COUNT}",
                'current_count': current_count
            }

        return {
            'allowed': True,
            'reason': f'Position limit OK: {current_count}/{config.MAX_POSITION_COUNT}',
            'current_count': current_count
        }

    def check_existing_position(self, tradingsymbol):
        """
        Check if position already exists for this symbol

        Args:
            tradingsymbol: Trading symbol to check

        Returns:
            dict: {
                'allowed': bool,
                'reason': str,
                'existing_position': dict or None
            }
        """
        open_trades = self.db.get_open_trades(tradingsymbol=tradingsymbol)

        if open_trades:
            return {
                'allowed': False,
                'reason': f'Position already exists for {tradingsymbol}',
                'existing_position': open_trades[0]
            }

        return {
            'allowed': True,
            'reason': 'No existing position',
            'existing_position': None
        }

    def can_enter_trade(self, tradingsymbol, entry_price, quantity):
        """
        Comprehensive check if trade can be entered

        Args:
            tradingsymbol: Trading symbol
            entry_price: Proposed entry price
            quantity: Proposed quantity

        Returns:
            dict: {
                'allowed': bool,
                'reason': str,
                'checks': dict with individual check results
            }
        """
        # Check if trading is globally enabled
        if not self.trading_enabled:
            return {
                'allowed': False,
                'reason': f'Trading halted: {self.halt_reason}',
                'checks': {}
            }

        checks = {}

        # 1. Check daily loss limit
        daily_loss_check = self.check_daily_loss_limit()
        checks['daily_loss'] = daily_loss_check

        if not daily_loss_check['allowed']:
            self.halt_trading(daily_loss_check['reason'])
            return {
                'allowed': False,
                'reason': daily_loss_check['reason'],
                'checks': checks
            }

        # 2. Check max positions
        position_check = self.check_max_positions()
        checks['max_positions'] = position_check

        if not position_check['allowed']:
            return {
                'allowed': False,
                'reason': position_check['reason'],
                'checks': checks
            }

        # 3. Check existing position for symbol
        existing_check = self.check_existing_position(tradingsymbol)
        checks['existing_position'] = existing_check

        if not existing_check['allowed']:
            return {
                'allowed': False,
                'reason': existing_check['reason'],
                'checks': checks
            }

        # 4. Validate position size
        position_value = entry_price * quantity
        checks['position_value'] = {
            'value': position_value,
            'allowed_range': f'₹{config.POSITION_SIZE * 0.5:.2f} - ₹{config.POSITION_SIZE * 1.5:.2f}'
        }

        # Position should be roughly equal to configured size
        if position_value < config.POSITION_SIZE * 0.5 or position_value > config.POSITION_SIZE * 1.5:
            return {
                'allowed': False,
                'reason': f'Position size out of range: ₹{position_value:.2f} '
                         f'(Target: ₹{config.POSITION_SIZE:.2f})',
                'checks': checks
            }

        # All checks passed
        return {
            'allowed': True,
            'reason': 'All risk checks passed',
            'checks': checks
        }

    def halt_trading(self, reason):
        """
        Halt all trading activities

        Args:
            reason: Reason for halting
        """
        self.trading_enabled = False
        self.halt_reason = reason
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n{'#'*80}")
        print(f"{'🛑 TRADING HALTED':^80}")
        print(f"{'#'*80}")
        print(f"Time: {timestamp}")
        print(f"Reason: {reason}")
        print(f"{'#'*80}\n")

    def resume_trading(self):
        """Resume trading after halt"""
        self.trading_enabled = True
        self.halt_reason = None
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n{'='*80}")
        print(f"{'✅ TRADING RESUMED':^80}")
        print(f"{'='*80}")
        print(f"Time: {timestamp}")
        print(f"{'='*80}\n")

    def get_risk_summary(self):
        """
        Get current risk metrics summary

        Returns:
            dict: Risk metrics
        """
        pnl = self.db.get_today_pnl()
        open_trades = self.db.get_open_trades()

        total_pnl = pnl.get('total_profit_loss', 0)
        pnl_percent = (total_pnl / abs(config.MAX_DAILY_LOSS)) * 100 if config.MAX_DAILY_LOSS != 0 else 0

        return {
            'trading_enabled': self.trading_enabled,
            'halt_reason': self.halt_reason,
            'daily_pnl': total_pnl,
            'daily_pnl_percent': pnl_percent,
            'daily_limit': config.MAX_DAILY_LOSS,
            'open_positions': len(open_trades),
            'max_positions': config.MAX_POSITION_COUNT,
            'winning_trades': pnl.get('winning_trades', 0),
            'losing_trades': pnl.get('losing_trades', 0),
            'total_trades': pnl.get('total_trades', 0),
            'max_profit': pnl.get('max_profit', 0),
            'max_loss': pnl.get('max_loss', 0)
        }

    def print_risk_summary(self):
        """Print formatted risk summary"""
        summary = self.get_risk_summary()

        print(f"\n{'='*80}")
        print(f"{'RISK MANAGEMENT DASHBOARD':^80}")
        print(f"{'='*80}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Trading Status: {'🟢 ENABLED' if summary['trading_enabled'] else '🔴 HALTED'}")

        if not summary['trading_enabled']:
            print(f"Halt Reason: {summary['halt_reason']}")

        print(f"\n{'Daily P&L:'}")
        pnl_color = '🟢' if summary['daily_pnl'] >= 0 else '🔴'
        print(f"  {pnl_color} Total: ₹{summary['daily_pnl']:+.2f} "
              f"({summary['daily_pnl_percent']:+.1f}% of limit)")
        print(f"  Limit: ₹{summary['daily_limit']:.2f}")
        print(f"  Max Profit: ₹{summary['max_profit']:+.2f}")
        print(f"  Max Loss: ₹{summary['max_loss']:+.2f}")

        print(f"\n{'Positions:'}")
        print(f"  Current: {summary['open_positions']}/{summary['max_positions']}")

        print(f"\n{'Trade Statistics:'}")
        print(f"  Total Trades: {summary['total_trades']}")
        print(f"  Winning: {summary['winning_trades']}")
        print(f"  Losing: {summary['losing_trades']}")

        if summary['total_trades'] > 0:
            win_rate = (summary['winning_trades'] / summary['total_trades']) * 100
            print(f"  Win Rate: {win_rate:.1f}%")

        print(f"{'='*80}\n")


# Singleton instance
_risk_manager = None

def get_risk_manager():
    """Get risk manager singleton instance"""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = RiskManager()
    return _risk_manager
