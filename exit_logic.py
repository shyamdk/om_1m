#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved Exit Logic Module
Implements robust exit conditions with trailing stop loss
"""

import pandas as pd
import numpy as np
from datetime import datetime
import traceback
import config


class TrailingStopLoss:
    """
    Trailing Stop Loss Manager

    Manages trailing stop loss for each position independently
    """

    def __init__(self, trigger_percent=None, trail_percent=None):
        """
        Initialize trailing stop loss

        Args:
            trigger_percent: Profit % at which trailing SL activates (default from config)
            trail_percent: Distance to trail from peak (default from config)
        """
        self.trigger_percent = trigger_percent or config.TRAILING_STOP_LOSS_TRIGGER_PERCENT
        self.trail_percent = trail_percent or config.TRAILING_STOP_LOSS_TRAIL_PERCENT
        self.enabled = config.TRAILING_STOP_LOSS_ENABLED

    def calculate_stop_loss(self, entry_price, current_price, max_profit_seen):
        """
        Calculate trailing stop loss level

        Args:
            entry_price: Original entry price
            current_price: Current market price
            max_profit_seen: Maximum profit % achieved so far

        Returns:
            dict: {
                'tsl_active': bool,
                'stop_loss_price': float,
                'trailing_threshold': float,
                'should_exit': bool
            }
        """
        if not self.enabled:
            return {
                'tsl_active': False,
                'stop_loss_price': None,
                'trailing_threshold': None,
                'should_exit': False
            }

        # Calculate current profit %
        current_profit_pct = ((current_price - entry_price) / entry_price) * 100

        # Update max profit if current is higher
        max_profit = max(max_profit_seen, current_profit_pct)

        # Check if TSL should be active
        tsl_active = max_profit >= self.trigger_percent

        if not tsl_active:
            return {
                'tsl_active': False,
                'stop_loss_price': None,
                'trailing_threshold': None,
                'should_exit': False,
                'max_profit': max_profit
            }

        # Calculate trailing threshold (profit level at which we exit)
        trailing_threshold = max_profit - self.trail_percent

        # Calculate stop loss price
        stop_loss_price = entry_price * (1 + trailing_threshold / 100)

        # Check if current price has fallen below trailing threshold
        should_exit = current_profit_pct < trailing_threshold

        return {
            'tsl_active': True,
            'stop_loss_price': stop_loss_price,
            'trailing_threshold': trailing_threshold,
            'should_exit': should_exit,
            'max_profit': max_profit
        }


def check_exit_conditions_v2(df_data, entry_price, max_profit_seen, tradingsymbol):
    """
    Check exit conditions based on RSI, fixed profit, stop loss, and trailing SL

    Exit Rules:
    1. RSI < RSI_SMA (RSI falls below its moving average)
    2. Fixed Profit Target reached (default: 1%)
    3. Fixed Stop Loss hit (default: -4%)
    4. Trailing Stop Loss triggered (if enabled)

    Args:
        df_data: DataFrame with technical indicators
        entry_price: Original entry price
        max_profit_seen: Maximum profit % seen for this trade
        tradingsymbol: Trading symbol for logging

    Returns:
        dict: {
            'exit_signal': bool,
            'exit_price': float or None,
            'exit_reason': str,
            'max_profit_updated': float,
            'indicators': dict
        }
    """

    # Required indicators
    required = ['RSI', 'SMA14_RSI', 'close', 'EMA3', 'EMA5']

    # Validate indicators
    missing = []
    for indicator in required:
        if indicator not in df_data.columns:
            missing.append(indicator)
        elif pd.isna(df_data[indicator].iloc[-1]):
            missing.append(f"{indicator} (NaN)")

    if missing:
        return {
            'exit_signal': False,
            'exit_price': None,
            'exit_reason': f'Missing indicators: {", ".join(missing)}',
            'max_profit_updated': max_profit_seen,
            'indicators': {}
        }

    try:
        # Extract indicator values
        rsi = df_data["RSI"].iloc[-1]
        rsi_sma = df_data["SMA14_RSI"].iloc[-1]
        c_close = df_data["close"].iloc[-1]
        ema3 = df_data["EMA3"].iloc[-1]
        ema5 = df_data["EMA5"].iloc[-1]

        # Calculate percentage profit
        percentage_profit = ((c_close - entry_price) / entry_price) * 100

        # Store indicators
        indicators = {
            'rsi': rsi,
            'rsi_sma': rsi_sma,
            'close': c_close,
            'ema3': ema3,
            'ema5': ema5,
            'percentage_profit': percentage_profit
        }

    except Exception as e:
        return {
            'exit_signal': False,
            'exit_price': None,
            'exit_reason': f'Error extracting indicators: {str(e)}',
            'max_profit_updated': max_profit_seen,
            'indicators': {}
        }

    # Initialize trailing stop loss manager
    tsl = TrailingStopLoss()
    tsl_result = tsl.calculate_stop_loss(entry_price, c_close, max_profit_seen)

    # Check each exit condition
    exit_reasons = []

    # Condition 1: RSI falls below RSI_SMA
    rsi_exit = rsi < rsi_sma
    if rsi_exit:
        exit_reasons.append(f"RSI<RSI_SMA ({rsi:.1f}<{rsi_sma:.1f})")

    # Condition 2: Fixed profit target
    profit_target = percentage_profit >= config.TARGET_PROFIT_PERCENT
    if profit_target:
        exit_reasons.append(f"Profit Target ({percentage_profit:.2f}%>={config.TARGET_PROFIT_PERCENT}%)")

    # Condition 3: Fixed stop loss
    stop_loss_hit = percentage_profit <= config.STOP_LOSS
    if stop_loss_hit:
        exit_reasons.append(f"Stop Loss ({percentage_profit:.2f}%<={config.STOP_LOSS}%)")

    # Condition 4: Trailing stop loss
    trailing_sl_hit = tsl_result['should_exit']
    if trailing_sl_hit:
        exit_reasons.append(
            f"Trailing SL (Max:{tsl_result['max_profit']:.2f}%, "
            f"Threshold:{tsl_result['trailing_threshold']:.2f}%, "
            f"Current:{percentage_profit:.2f}%)"
        )

    # Combined exit signal
    exit_signal = rsi_exit or profit_target or stop_loss_hit or trailing_sl_hit

    # Calculate exit price
    if exit_signal:
        # Use current close if it's above EMA3, otherwise use EMA3 as conservative exit
        exit_price = c_close if c_close > ema3 else ema3
        exit_reason = "EXIT SIGNAL - " + " | ".join(exit_reasons)
    else:
        exit_price = None
        exit_reason = "NO EXIT"

    # Detailed logging
    print(f"\n{'='*80}")
    print(f"EXIT ANALYSIS: {tradingsymbol}")
    print(f"{'='*80}")
    print(f"Entry Price: ₹{entry_price:.2f}")
    print(f"Current Price: ₹{c_close:.2f}")
    print(f"Profit/Loss: {percentage_profit:+.2f}%")
    print(f"\nIndicators:")
    print(f"  RSI: {rsi:.2f} | RSI_SMA: {rsi_sma:.2f} | RSI < RSI_SMA: {rsi_exit}")
    print(f"  EMA3: {ema3:.2f} | EMA5: {ema5:.2f}")
    print(f"\nExit Conditions:")
    print(f"  1. RSI Exit: {'✓' if rsi_exit else '✗'} (RSI < RSI_SMA)")
    print(f"  2. Profit Target: {'✓' if profit_target else '✗'} "
          f"({percentage_profit:.2f}% vs {config.TARGET_PROFIT_PERCENT}% target)")
    print(f"  3. Stop Loss: {'✓' if stop_loss_hit else '✗'} "
          f"({percentage_profit:.2f}% vs {config.STOP_LOSS}% limit)")

    if tsl.enabled:
        print(f"  4. Trailing SL: {'✓ ACTIVE' if tsl_result['tsl_active'] else '✗ Not Active'}")
        if tsl_result['tsl_active']:
            print(f"     Max Profit Seen: {tsl_result['max_profit']:.2f}%")
            print(f"     Trailing Threshold: {tsl_result['trailing_threshold']:.2f}%")
            print(f"     TSL Price: ₹{tsl_result['stop_loss_price']:.2f}")
            print(f"     Should Exit: {'✓ YES' if trailing_sl_hit else '✗ NO'}")
    else:
        print(f"  4. Trailing SL: ✗ DISABLED")

    print(f"\nResult: {'✓ EXIT SIGNAL' if exit_signal else '✗ HOLD POSITION'}")
    if exit_signal:
        print(f"Exit Price: ₹{exit_price:.2f}")
        print(f"Reason: {exit_reason}")
    print(f"{'='*80}\n")

    return {
        'exit_signal': exit_signal,
        'exit_price': exit_price,
        'exit_reason': exit_reason,
        'max_profit_updated': tsl_result.get('max_profit', max_profit_seen),
        'indicators': indicators
    }


def process_sell_logic_improved(df_data, trade_row, tradingsymbol, symboltoken,
                                  utils_module, file_management_module):
    """
    Improved sell logic with comprehensive exit conditions

    Args:
        df_data: DataFrame with technical indicators
        trade_row: Row from trade log containing position details
        tradingsymbol: Trading symbol
        symboltoken: Symbol token for API
        utils_module: Reference to utils module
        file_management_module: Reference to file_management_new module

    Returns:
        dict: Result of sell logic execution
    """

    # Extract trade details
    try:
        if config.LIVE_FLAG == 'LIVE':
            order_id = trade_row['order_id']
            entry_price = float(trade_row['buy_price'])
            buy_quantity = int(trade_row['buy_quantity'])
        else:
            order_id = trade_row['order_id']
            entry_price = float(trade_row['order_price'])
            buy_quantity = int(trade_row['order_quantity'])

        # Get max profit seen (initialize to 0 if not present)
        max_profit_seen = float(trade_row.get('max_profit_seen', 0))

    except Exception as e:
        return {
            'success': False,
            'reason': f'Error extracting trade details: {str(e)}'
        }

    # Check exit conditions
    exit_result = check_exit_conditions_v2(
        df_data, entry_price, max_profit_seen, tradingsymbol
    )

    if not exit_result['exit_signal']:
        # Update max profit seen even if not exiting
        return {
            'success': False,
            'reason': exit_result['exit_reason'],
            'max_profit_updated': exit_result['max_profit_updated'],
            'should_update_max_profit': True
        }

    # Exit signal confirmed
    exit_price = exit_result['exit_price']
    exit_reason = exit_result['exit_reason']

    # Prepare exit details
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = config.get_file_path() + '/' + f"{tradingsymbol}_trade_log_{date_str}.csv"
    sell_date = datetime.now().strftime("%d-%m-%y %H-%M-%S")

    try:
        # Place sell order
        if config.LIVE_FLAG == 'LIVE':
            print(f"\n🔴 LIVE ORDER - Placing SELL order for {tradingsymbol}")
            print(f"   Price: ~₹{exit_price} (Market Order) | Quantity: {buy_quantity}")

            response = utils_module.place_market_order(
                tradingsymbol, symboltoken, "SELL", buy_quantity, exchange="NFO"
            )

            unique_sell_order_id = utils_module.extract_uniqueorderid(response)

            if unique_sell_order_id:
                sell_status = 'open'
                shyam_status = 'sell_ordered'
                print(f"   ✓ Sell order placed successfully. ID: {unique_sell_order_id}")
            else:
                return {
                    'success': False,
                    'reason': 'Failed to extract sell order ID'
                }
        else:
            print(f"\n🟡 {config.LIVE_FLAG} MODE - Simulating SELL order")
            print(f"   Symbol: {tradingsymbol} | Price: ₹{exit_price:.2f} | Qty: {buy_quantity}")

            unique_sell_order_id = config.LIVE_FLAG
            sell_status = 'complete'
            shyam_status = 'sell_complete'
            print(f"   ✓ Sell order logged successfully")

        # Update trade log
        file_management_module.update_sell_trade(
            file_path, order_id, sell_date, buy_quantity, exit_price,
            sell_status, exit_reason, unique_sell_order_id, shyam_status, tradingsymbol
        )

        # Calculate P&L
        profit_loss = (exit_price - entry_price) * buy_quantity
        profit_pct = ((exit_price - entry_price) / entry_price) * 100

        print(f"\n{'='*60}")
        print(f"📊 TRADE CLOSED: {tradingsymbol}")
        print(f"{'='*60}")
        print(f"Entry: ₹{entry_price:.2f} | Exit: ₹{exit_price:.2f}")
        print(f"Quantity: {buy_quantity}")
        print(f"P&L: ₹{profit_loss:+.2f} ({profit_pct:+.2f}%)")
        print(f"Reason: {exit_reason}")
        print(f"{'='*60}\n")

        return {
            'success': True,
            'order_id': unique_sell_order_id,
            'exit_price': exit_price,
            'profit_loss': profit_loss,
            'profit_pct': profit_pct,
            'reason': exit_reason
        }

    except Exception as e:
        error_msg = f"Error during sell logic: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {
            'success': False,
            'reason': error_msg
        }
