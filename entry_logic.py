#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved Entry Logic Module
Implements robust entry conditions with proper validation and error handling
"""

import pandas as pd
import numpy as np
from datetime import datetime
import traceback
import config


def validate_indicators(df_data, required_indicators):
    """
    Validate that all required indicators are present and not NaN

    Args:
        df_data: DataFrame with indicator data
        required_indicators: List of required indicator column names

    Returns:
        tuple: (is_valid, missing_indicators)
    """
    missing = []
    for indicator in required_indicators:
        if indicator not in df_data.columns:
            missing.append(indicator)
        elif pd.isna(df_data[indicator].iloc[-1]):
            missing.append(f"{indicator} (NaN)")

    return len(missing) == 0, missing


def calculate_entry_price(c_close, ema3, ema5):
    """
    Calculate optimal entry price based on current price and EMAs

    Strategy:
    - If price is below both EMAs: enter at current price (pullback)
    - Otherwise: enter at EMA3 (conservative)

    Args:
        c_close: Current close price
        ema3: EMA 3 value
        ema5: EMA 5 value

    Returns:
        float: Entry price
    """
    if c_close < ema3 and c_close < ema5:
        return c_close
    elif c_close < ema3 and c_close > ema5:
        return c_close
    else:
        return ema3


def round_to_5_paise(price):
    """
    Round price to nearest 5 paise (₹0.05) as per NSE tick size

    Args:
        price: Raw price

    Returns:
        float: Rounded price
    """
    return round(round(price * 20) / 20, 2)


def check_entry_conditions_v2(df_data, tradingsymbol):
    """
    Check entry conditions based on RSI, SMA, and ADX

    Entry Rules:
    1. RSI > RSI_SMA (RSI above its moving average)
    2. RSI_SMA > RSI_SMA_MINUS_ONE (RSI_SMA is rising)
    3. RSI_SMA_GAP > 3 (minimum gap between RSI and its SMA)
    4. ADX > 14 (sufficient trend strength)

    Args:
        df_data: DataFrame with technical indicators
        tradingsymbol: Trading symbol for logging

    Returns:
        dict: {
            'entry_signal': bool,
            'entry_price': float or None,
            'entry_reason': str,
            'indicators': dict with all indicator values
        }
    """

    # Required indicators for entry strategy
    required = ['RSI', 'SMA14_RSI', 'SMA14_RSI_MINUS_ONE', 'ADX',
                'EMA3', 'EMA5', 'close']

    # Validate indicators
    is_valid, missing = validate_indicators(df_data, required)
    if not is_valid:
        return {
            'entry_signal': False,
            'entry_price': None,
            'entry_reason': f'Missing indicators: {", ".join(missing)}',
            'indicators': {}
        }

    # Extract indicator values
    try:
        rsi = df_data["RSI"].iloc[-1]
        rsi_sma = df_data["SMA14_RSI"].iloc[-1]
        rsi_sma_minus_one = df_data["SMA14_RSI_MINUS_ONE"].iloc[-1]
        rsi_sma_gap = rsi - rsi_sma
        adx = df_data['ADX'].iloc[-1]
        ema3 = df_data["EMA3"].iloc[-1]
        ema5 = df_data["EMA5"].iloc[-1]
        c_close = df_data["close"].iloc[-1]

        # Store all indicator values for logging
        indicators = {
            'rsi': rsi,
            'rsi_sma': rsi_sma,
            'rsi_sma_minus_one': rsi_sma_minus_one,
            'rsi_sma_gap': rsi_sma_gap,
            'adx': adx,
            'ema3': ema3,
            'ema5': ema5,
            'close': c_close
        }

    except Exception as e:
        return {
            'entry_signal': False,
            'entry_price': None,
            'entry_reason': f'Error extracting indicators: {str(e)}',
            'indicators': {}
        }

    # Check each entry condition
    condition_1 = rsi > rsi_sma
    condition_2 = rsi_sma > rsi_sma_minus_one
    condition_3 = rsi_sma_gap > config.ENTRY_RSI_SMA_GAP_MIN
    condition_4 = adx > config.ENTRY_ADX_MIN

    # Combined entry condition
    entry_signal = condition_1 and condition_2 and condition_3 and condition_4

    # Build detailed reason string
    conditions_status = [
        f"RSI>{rsi_sma:.1f}: {condition_1}",
        f"RSI_SMA_Rising: {condition_2}",
        f"Gap>{config.ENTRY_RSI_SMA_GAP_MIN}: {condition_3} (gap={rsi_sma_gap:.1f})",
        f"ADX>{config.ENTRY_ADX_MIN}: {condition_4} (adx={adx:.1f})"
    ]

    if entry_signal:
        entry_reason = "ENTRY SIGNAL - " + ", ".join([c for c in conditions_status if "True" in c])
        entry_price = round_to_5_paise(calculate_entry_price(c_close, ema3, ema5))
    else:
        entry_reason = "NO ENTRY - " + ", ".join([c for c in conditions_status if "False" in c])
        entry_price = None

    # Detailed logging
    print(f"\n{'='*80}")
    print(f"ENTRY ANALYSIS: {tradingsymbol}")
    print(f"{'='*80}")
    print(f"RSI: {rsi:.2f} | RSI_SMA: {rsi_sma:.2f} | RSI_SMA_Prev: {rsi_sma_minus_one:.2f}")
    print(f"RSI-SMA Gap: {rsi_sma_gap:.2f} (Required: >{config.ENTRY_RSI_SMA_GAP_MIN})")
    print(f"ADX: {adx:.2f} (Required: >{config.ENTRY_ADX_MIN})")
    print(f"EMA3: {ema3:.2f} | EMA5: {ema5:.2f} | Close: {c_close:.2f}")
    print(f"\nConditions:")
    for i, status in enumerate(conditions_status, 1):
        print(f"  {i}. {status}")
    print(f"\nResult: {'✓ ENTRY SIGNAL' if entry_signal else '✗ NO ENTRY'}")
    if entry_signal:
        print(f"Entry Price: ₹{entry_price:.2f}")
    print(f"{'='*80}\n")

    return {
        'entry_signal': entry_signal,
        'entry_price': entry_price,
        'entry_reason': entry_reason,
        'indicators': indicators
    }


def process_buy_logic_improved(df_data, tradingsymbol, symboltoken, shares_or_contracts,
                                 utils_module, file_management_module):
    """
    Improved buy logic with better error handling and validation

    Args:
        df_data: DataFrame with technical indicators
        tradingsymbol: Trading symbol
        symboltoken: Symbol token for API
        shares_or_contracts: Quantity to trade
        utils_module: Reference to utils module for placing orders
        file_management_module: Reference to file_management_new module

    Returns:
        dict: Result of buy logic execution
    """

    # Check entry conditions
    entry_result = check_entry_conditions_v2(df_data, tradingsymbol)

    if not entry_result['entry_signal']:
        return {
            'success': False,
            'reason': entry_result['entry_reason']
        }

    # Entry signal confirmed
    entry_price = entry_result['entry_price']
    entry_reason = entry_result['entry_reason']

    # Prepare order details
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = config.get_file_path() + '/' + f"{tradingsymbol}_trade_log_{date_str}.csv"
    current_time = datetime.now().strftime("%d-%m-%y %H:%M:%S")

    try:
        # Place order based on LIVE_FLAG
        if config.LIVE_FLAG == 'LIVE':
            print(f"\n🔴 LIVE ORDER - Placing BUY order for {tradingsymbol}")
            print(f"   Price: ₹{entry_price} | Quantity: {shares_or_contracts}")

            response = utils_module.place_limit_order(
                tradingsymbol, symboltoken, "BUY", entry_price,
                shares_or_contracts, exchange="NFO"
            )

            unique_buy_order_id = utils_module.extract_uniqueorderid(response)

            if unique_buy_order_id:
                order_status = 'open'
                shyam_status = 'ordered'
                print(f"   ✓ Order placed successfully. ID: {unique_buy_order_id}")
            else:
                return {
                    'success': False,
                    'reason': 'Failed to extract order ID from response'
                }
        else:
            print(f"\n🟡 {config.LIVE_FLAG} MODE - Simulating BUY order")
            print(f"   Symbol: {tradingsymbol} | Price: ₹{entry_price} | Qty: {shares_or_contracts}")

            unique_buy_order_id = config.LIVE_FLAG
            order_status = 'complete'
            shyam_status = 'buy_complete'
            print(f"   ✓ Order logged successfully")

        # Log trade to file
        file_management_module.insert_trade_record(
            file_path, tradingsymbol, symboltoken, current_time,
            shares_or_contracts, entry_price, order_status,
            shyam_status, entry_reason, unique_buy_order_id
        )

        return {
            'success': True,
            'order_id': unique_buy_order_id,
            'entry_price': entry_price,
            'reason': entry_reason
        }

    except Exception as e:
        error_msg = f"Error during buy logic: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {
            'success': False,
            'reason': error_msg
        }
