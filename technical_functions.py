#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Technical Functions Module
Provides technical indicator calculations for trading strategies

Author: shyamkrishnamurthy
Updated: 2025-10-01
"""

import pandas as pd
import numpy as np


def convert_to_heikin_ashi(df_dict):
    """
    Convert regular OHLC candles to Heikin Ashi candles and update df_dict in place.

    Parameters:
        df_dict (pd.DataFrame): DataFrame with columns ['open', 'high', 'low', 'close']

    Returns:
        pd.DataFrame: Updated DataFrame with Heikin Ashi columns ['ha_open', 'ha_high', 'ha_low', 'ha_close']
    """

    # Heikin Ashi Close = (Open + High + Low + Close) / 4
    ha_close = (df_dict['open'] + df_dict['high'] + df_dict['low'] + df_dict['close']) / 4

    # Initialize ha_open as an array with NaNs
    ha_open = np.full(len(df_dict), np.nan)
    if len(df_dict) > 0:
        ha_open[0] = (df_dict['open'].iloc[0] + df_dict['close'].iloc[0]) / 2

        # Iteratively calculate the rest
        for i in range(1, len(df_dict)):
            ha_open[i] = (ha_open[i - 1] + ha_close.iloc[i - 1]) / 2

    # Heikin Ashi High = max(high, ha_open, ha_close)
    ha_high = np.maximum.reduce([df_dict['high'].values, ha_open, ha_close.values])

    # Heikin Ashi Low = min(low, ha_open, ha_close)
    ha_low = np.minimum.reduce([df_dict['low'].values, ha_open, ha_close.values])

    # Update df_dict in place
    df_dict['ha_open'] = ha_open
    df_dict['ha_high'] = ha_high
    df_dict['ha_low'] = ha_low
    df_dict['ha_close'] = ha_close

    return df_dict



def SMA_ALL(df_dict, n=8):

    sma8 = df_dict['close'].rolling(8).mean()
    df_dict['SMA8'] = sma8
    df_dict["SMA8_MINUS_ONE"] = df_dict["SMA8"].shift(1)
    df_dict["SMA8_MINUS_TWO"] = df_dict["SMA8"].shift(2)
    df_dict["SMA8_PERCENT"] = ((df_dict['SMA8'] - df_dict["SMA8_MINUS_ONE"])/df_dict["SMA8_MINUS_ONE"])*100
    
    sma5 = df_dict['close'].rolling(5).mean()
    df_dict['SMA5'] = sma5
    df_dict["SMA5_MINUS_ONE"] = df_dict["SMA5"].shift(1)
    df_dict["SMA5_MINUS_TWO"] = df_dict["SMA5"].shift(2)
    df_dict["SMA5_PERCENT"] = ((df_dict['SMA5'] - df_dict["SMA5_MINUS_ONE"])/df_dict["SMA5_MINUS_ONE"])*100
    
    sma3 = df_dict['close'].rolling(3).mean()
    df_dict['SMA3'] = sma3
    df_dict["SMA3_MINUS_ONE"] = df_dict["SMA3"].shift(1)
    df_dict["SMA3_MINUS_TWO"] = df_dict["SMA3"].shift(2)
    df_dict["SMA3_PERCENT"] = ((df_dict['SMA3'] - df_dict["SMA3_MINUS_ONE"])/df_dict["SMA3_MINUS_ONE"])*100
    
    sma13 = df_dict['close'].rolling(13).mean()
    df_dict['SMA13'] = sma13
    df_dict["SMA13_MINUS_ONE"] = df_dict["SMA13"].shift(1)
    df_dict["SMA13_MINUS_TWO"] = df_dict["SMA13"].shift(2)
    df_dict["SMA13_PERCENT"] = ((df_dict['SMA13'] - df_dict["SMA13_MINUS_ONE"])/df_dict["SMA13_MINUS_ONE"])*100
    
    sma21 = df_dict['close'].rolling(21).mean()
    df_dict['SMA21'] = sma21
    df_dict["SMA21_MINUS_ONE"] = df_dict["SMA21"].shift(1)
    df_dict["SMA21_MINUS_TWO"] = df_dict["SMA21"].shift(2)
    df_dict["SMA21_PERCENT"] = ((df_dict['SMA21'] - df_dict["SMA21_MINUS_ONE"])/df_dict["SMA21_MINUS_ONE"])*100
    
    sma34 = df_dict['close'].rolling(34).mean()
    df_dict['SMA34'] = sma34
    df_dict['SMA34_MINUS_ONE'] = df_dict['SMA34'].shift(1)
    df_dict['SMA34_MINUS_TWO'] = df_dict['SMA34'].shift(2)
    df_dict["SMA34_PERCENT"] = ((df_dict['SMA34'] - df_dict["SMA34_MINUS_ONE"])/df_dict["SMA34_MINUS_ONE"])*100
    
    
    sma51 = df_dict['close'].rolling(51).mean()
    df_dict['SMA51'] = sma51
    df_dict['SMA51_MINUS_ONE'] = df_dict['SMA51'].shift(1)
    df_dict['SMA51_MINUS_TWO'] = df_dict['SMA51'].shift(2)
    df_dict["SMA51_PERCENT"] = ((df_dict['SMA51'] - df_dict["SMA51_MINUS_ONE"])/df_dict["SMA51_MINUS_ONE"])*100


    sma101 = df_dict['close'].rolling(101).mean()
    df_dict['SMA101'] = sma101
    df_dict['SMA101_MINUS_ONE'] = df_dict['SMA101'].shift(1)
    df_dict['SMA101_MINUS_TWO'] = df_dict['SMA101'].shift(2)
    df_dict["SMA101_PERCENT"] = ((df_dict['SMA101'] - df_dict["SMA101_MINUS_ONE"])/df_dict["SMA101_MINUS_ONE"])*100
    
    sma201 = df_dict['close'].rolling(201).mean()
    df_dict['SMA201'] = sma201
    df_dict['SMA201_MINUS_ONE'] = df_dict['SMA201'].shift(1)
    df_dict['SMA201_MINUS_TWO'] = df_dict['SMA201'].shift(2)
    df_dict["SMA201_PERCENT"] = ((df_dict['SMA201'] - df_dict["SMA201_MINUS_ONE"])/df_dict["SMA201_MINUS_ONE"])*100
    return df_dict

def EMA8(df_dict, n=8):
    multiplier = 2 / (n + 1)
    sma = df_dict['close'].rolling(n).mean()
    ema = np.full(len(df_dict['close']), np.nan)
    # Set the first EMA value to the first non-NaN SMA value
    first_valid_idx = len(sma) - len(sma.dropna())
    ema[first_valid_idx] = sma.dropna().iloc[0]
    
    for i in range(first_valid_idx + 1, len(df_dict['close'])):
        if not np.isnan(ema[i - 1]):
            ema[i] = ((df_dict['close'].iloc[i] - ema[i - 1]) * multiplier) + ema[i - 1]
    
    # Reset the first EMA value to NaN
    ema[first_valid_idx] = np.nan
    df_dict['EMA8'] = ema
    df_dict["EMA8_MINUS_ONE"] = df_dict["EMA8"].shift(1)
    
    return df_dict

def EMA21(df_dict, n=21):
    multiplier = 2 / (n + 1)
    sma = df_dict['close'].rolling(n).mean()
    ema = np.full(len(df_dict['close']), np.nan)
    # Set the first EMA value to the first non-NaN SMA value
    first_valid_idx = len(sma) - len(sma.dropna())
    ema[first_valid_idx] = sma.dropna().iloc[0]
    
    for i in range(first_valid_idx + 1, len(df_dict['close'])):
        if not np.isnan(ema[i - 1]):
            ema[i] = ((df_dict['close'].iloc[i] - ema[i - 1]) * multiplier) + ema[i - 1]
    
    # Reset the first EMA value to NaN
    ema[first_valid_idx] = np.nan
    df_dict['EMA21'] = ema
    df_dict["EMA21_MINUS_ONE"] = df_dict["EMA21"].shift(1)
    
    return df_dict


def EMA5(df_dict, n=5):
    multiplier = 2 / (n + 1)
    sma = df_dict['close'].rolling(n).mean()
    ema = np.full(len(df_dict['close']), np.nan)
    # Set the first EMA value to the first non-NaN SMA value
    first_valid_idx = len(sma) - len(sma.dropna())
    ema[first_valid_idx] = sma.dropna().iloc[0]
    
    for i in range(first_valid_idx + 1, len(df_dict['close'])):
        if not np.isnan(ema[i - 1]):
            ema[i] = ((df_dict['close'].iloc[i] - ema[i - 1]) * multiplier) + ema[i - 1]
    
    # Reset the first EMA value to NaN
    ema[first_valid_idx] = np.nan
    df_dict['EMA5'] = ema
    df_dict["EMA5_MINUS_ONE"] = df_dict["EMA5"].shift(1)
    
    return df_dict

def EMA3(df_dict, n=3):
    multiplier = 2 / (n + 1)
    sma = df_dict['close'].rolling(n).mean()
    ema = np.full(len(df_dict['close']), np.nan)
    # Set the first EMA value to the first non-NaN SMA value
    first_valid_idx = len(sma) - len(sma.dropna())
    ema[first_valid_idx] = sma.dropna().iloc[0]
    
    for i in range(first_valid_idx + 1, len(df_dict['close'])):
        if not np.isnan(ema[i - 1]):
            ema[i] = ((df_dict['close'].iloc[i] - ema[i - 1]) * multiplier) + ema[i - 1]
    
    # Reset the first EMA value to NaN
    ema[first_valid_idx] = np.nan
    df_dict['EMA3'] = ema
    df_dict["EMA3_MINUS_ONE"] = df_dict["EMA3"].shift(1)
    
    return df_dict


def RMA(ser, n=9):
    multiplier = 1 / n
    sma = ser.rolling(n).mean()
    ema = np.full(len(ser), np.nan)

    # Check if sma.dropna() has any values before accessing the first element
    sma_dropna = sma.dropna()
    if len(sma_dropna) > 0:
        # Initialize the EMA with the first available SMA value
        ema[len(sma) - len(sma_dropna)] = sma_dropna.iloc[0]

        for i in range(len(ser)):
            if i > 0 and not np.isnan(ema[i - 1]):
                ema[i] = ((ser.iloc[i] - ema[i - 1]) * multiplier) + ema[i - 1]
        
        # Reset the initial value to NaN as per your original code
        ema[len(sma) - len(sma_dropna)] = np.nan
    
    return ema

def ATR(df_dict, n=14):
    "function to calculate True Range and Average True Range"
    df_dict["H-L"] = df_dict["high"] - df_dict["low"]
    df_dict["H-PC"] = abs(df_dict["high"] - df_dict["close"].shift(1))
    df_dict["L-PC"] = abs(df_dict["low"] - df_dict["close"].shift(1))
    df_dict["TR"] = df_dict[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    # df_dict[df]["TR"].ewm(span=n, min_periods=n).mean()
    df_dict["ATR"] = RMA(df_dict["TR"], n)
    df_dict.drop(["H-L", "H-PC", "L-PC", "TR"], axis=1, inplace=True)
    return df_dict




def CCI(df_dict, n=20, cci_sma_len=20):
    """
    Calculate the Commodity Channel Index (CCI) and its SMA, and add them to the DataFrame.

    Parameters:
    df_dict (dict): A dictionary containing 'open', 'close', 'high', 'low' as lists or pandas Series.
    n (int): The period for calculating the CCI. Default is 20.
    cci_sma_len (int): The period for calculating the SMA of the CCI. Default is 20.

    Returns:
    pd.DataFrame: The original DataFrame with added 'CCI', 'CCI_MINUS_ONE', and 'CCI_SMA' columns.
    """
    # Convert the dictionary into a DataFrame
    df = pd.DataFrame(df_dict)
    
    # Ensure required columns are present
    if not all(col in df.columns for col in ['high', 'low', 'close']):
        raise ValueError("The dictionary must contain 'high', 'low', and 'close' keys.")

    # Calculate Typical Price
    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
    
    # Calculate the SMA of the Typical Price
    df['sma_typical'] = df['typical_price'].rolling(window=n).mean()
    
    # Calculate the Mean Deviation
    df['mean_deviation'] = df['typical_price'].rolling(window=n).apply(
        lambda x: abs(x - x.mean()).mean(), raw=True
    )
    
    # Calculate CCI
    df['CCI'] = (df['typical_price'] - df['sma_typical']) / (0.015 * df['mean_deviation'])
    df['CCI_MINUS_ONE'] = df['CCI'].shift(1)

    # Calculate CCI SMA
    df['CCI_SMA'] = df['CCI'].rolling(window=cci_sma_len).mean()
    df['CCI_SMA_MINUS_ONE'] = df['CCI_SMA'].shift(1)
    df['CCI_SMA_MINUS_TWO'] = df['CCI_SMA'].shift(2)
    
    # Drop intermediate columns (optional)
    df.drop(columns=['typical_price', 'sma_typical', 'mean_deviation'], inplace=True)
    
    return df





def get_adx(df_dict, lookback):
    high = df_dict["high"]
    low = df_dict["low"]
    close = df_dict["close"]
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
    # atr = tr.rolling(lookback).mean()
    atr = RMA(tr, lookback)
    plus_di = 100 * (plus_dm.ewm(alpha=1/lookback).mean() / atr)
    minus_di = abs(100 * (minus_dm.ewm(alpha=1/lookback).mean() / atr))
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    adx = ((dx.shift(1) * (lookback - 1)) + dx) / lookback
    # adx_smooth = adx.ewm(alpha = 1/lookback).mean()
    adx_smooth = RMA(adx, lookback)
    df_dict['PLUS_DI'] = plus_di
    df_dict['MINUS_DI'] = minus_di
    df_dict['ADX'] = adx_smooth
    df_dict["ADX_MINUS_ONE"] = df_dict["ADX"].shift(1)

    return df_dict



def RSI(df_dict, n=14, sma_length=14):
    "function to calculate RSI"
    df_dict["change"] = df_dict["close"] - df_dict["close"].shift(1)
    df_dict["gain"] = np.where(df_dict["change"] >= 0, df_dict["change"], 0)
    df_dict["loss"] = np.where(df_dict["change"] < 0, -1*df_dict["change"], 0)
    df_dict["avgGain"] = RMA_NEW(df_dict["gain"], n)
    df_dict["avgLoss"] = RMA_NEW(df_dict["loss"], n)
    df_dict["rs"] = df_dict["avgGain"]/df_dict["avgLoss"]
    df_dict["RSI"] = 100 - (100 / (1 + df_dict["rs"]))
    df_dict["SMA14_RSI"] = df_dict["RSI"].rolling(window=sma_length).mean()
    # Add previous RSI and previous RSI_SMA values
    df_dict["RSI_MINUS_ONE"] = df_dict["RSI"].shift(1)
    df_dict["SMA14_RSI_MINUS_ONE"] = df_dict["SMA14_RSI"].shift(1)
    df_dict.drop(["change", "gain", "loss", "avgGain",
                 "avgLoss", "rs"], axis=1, inplace=True)
    return df_dict

def RMA_NEW(ser, n=14):
    """
    Wilder's Smoothing (RMA) - used in traditional RSI calculation
    """
    multiplier = 1 / n
    sma = ser.rolling(n).mean()
    ema = np.full(len(ser), np.nan)
    
    # Get the first non-NaN index where SMA starts
    sma_dropna = sma.dropna()
    if len(sma_dropna) > 0:
        start_idx = len(sma) - len(sma_dropna)
        ema[start_idx] = sma_dropna.iloc[0]
        # Start loop from next index after initialization
        for i in range(start_idx + 1, len(ser)):
            ema[i] = ((ser.iloc[i] - ema[i - 1]) * multiplier) + ema[i - 1]
    
    return ema

def RSI_CORRECTED(df_dict, n=14, sma_length=14):
    """
    Corrected RSI function with proper handling of edge cases
    """
    # Create a copy to avoid modifying original
    df = df_dict.copy()
    
    # Calculate price changes
    df["change"] = df["close"] - df["close"].shift(1)
    df["gain"] = np.where(df["change"] >= 0, df["change"], 0)
    df["loss"] = np.where(df["change"] < 0, -1*df["change"], 0)
    
    # Calculate RMA (Wilder's smoothing)
    df["avgGain"] = RMA_NEW(df["gain"], n)
    df["avgLoss"] = RMA_NEW(df["loss"], n)
    
    # Calculate RS and RSI with proper handling of division by zero
    df["rs"] = np.where(df["avgLoss"] != 0, df["avgGain"]/df["avgLoss"], np.inf)
    df["RSI_TEST"] = np.where(df["avgLoss"] != 0, 100 - (100 / (1 + df["rs"])), 100)
    df["RSI"] = df["RSI_TEST"].shift(0)
    
    # Calculate SMA of RSI
    df["SMA14_RSI"] = df["RSI"].rolling(window=sma_length).mean()
    
    # Add previous period values
    df["RSI_MINUS_ONE"] = df["RSI"].shift(1)
    df["SMA14_RSI_MINUS_ONE"] = df["SMA14_RSI"].shift(1)
    
    # Clean up intermediate columns
    df.drop(["change", "gain", "loss", "avgGain", "avgLoss", "rs"], axis=1, inplace=True)
    
    return df


def EMA_MACD(series, period):
    return series.ewm(span=period, adjust=False).mean()

def MACD(df_dict, fast=12, slow=26, signal_length=9):
    #print(df_dict.columns)

    """Function to calculate MACD line, Signal line, and previous values"""
    df_dict["EMA_fast"] = EMA_MACD(df_dict["close"], fast)
    df_dict["EMA_slow"] = EMA_MACD(df_dict["close"], slow)

    df_dict["MACD"] = df_dict["EMA_fast"] - df_dict["EMA_slow"]
    df_dict["MACD_Signal"] = EMA_MACD(df_dict["MACD"], signal_length)

    # Previous values for crossover logic
    df_dict["MACD_MINUS_ONE"] = df_dict["MACD"].shift(1)
    df_dict["MACD_Signal_MINUS_ONE"] = df_dict["MACD_Signal"].shift(1)

    # Drop intermediate EMAs if not needed
    df_dict.drop(["EMA_fast", "EMA_slow"], axis=1, inplace=True)

    return df_dict

def sma_volume(df_dict, n=20):
    """
    Function to calculate the n-period SMA of volume
    and its previous value for comparison.
    """
    sma_vol = df_dict['volume'].rolling(n).mean()
    df_dict[f'SMA{n}_VOLUME'] = sma_vol
    df_dict[f'SMA{n}_VOLUME_MINUS_ONE'] = df_dict[f'SMA{n}_VOLUME'].shift(1)
    return df_dict

def is_bullish_candle(df_dict):
    """
    Adds a boolean column 'bullish_candle' that is True if:
    - Close > Open (green candle)
    - Optional filter: small wicks (like a Marubozu)
    """
    body = abs(df_dict["close"] - df_dict["open"])
    upper_wick = df_dict["high"] - df_dict[["close", "open"]].max(axis=1)
    lower_wick = df_dict[["close", "open"]].min(axis=1) - df_dict["low"]

    # Bullish candle with small wicks (adjust 0.2 as tolerance)
    df_dict["bullish_candle"] = (
        (df_dict["close"] > df_dict["open"]) &
        (upper_wick <= body * 0.2) &
        (lower_wick <= body * 0.2)
    )
    
    return df_dict


def Envelope(df_dict, period=20, percentage=2.5):
    """
    Function to calculate Envelope bands.
    Envelope = SMA ± (SMA * percentage / 100)

    Args:
        df_dict: DataFrame with 'close' column
        period: Period for SMA calculation (default: 20)
        percentage: Percentage for envelope bands (default: 2.5)

    Returns:
        DataFrame with added Envelope columns
    """
    if 'close' not in df_dict.columns:
        raise ValueError("DataFrame must contain 'close' column")

    if len(df_dict) < period:
        raise ValueError(f"Not enough data. Need at least {period} rows, got {len(df_dict)}")

    # Calculate SMA
    df_dict["Envelope_SMA"] = df_dict["close"].rolling(window=period).mean()

    # Calculate upper and lower envelopes
    df_dict["Envelope_Upper"] = df_dict["Envelope_SMA"] * (1 + percentage / 100)
    df_dict["Envelope_Lower"] = df_dict["Envelope_SMA"] * (1 - percentage / 100)

    return df_dict



def Knoxville_Divergence(df_dict, rsi_period=14, momentum_period=20, bars_back=200):
    """
    Calculate Knoxville Divergence using RSI and Momentum.
    Detects bullish/bearish divergences for the last `bars_back` candles.

    Args:
        df_dict: DataFrame with a 'close' column
        rsi_period: Period for RSI calculation (default: 14)
        momentum_period: Period for Momentum comparison (default: 20)
        bars_back: Number of candles to evaluate (default: 200)

    Returns:
        DataFrame with added KD_Type and KD_Value columns
    """
    if 'close' not in df_dict.columns:
        raise ValueError("DataFrame must contain 'close' column")

    if len(df_dict) < max(rsi_period, momentum_period):
        raise ValueError(f"Not enough data. Need at least {max(rsi_period, momentum_period)} rows")

    # Calculate RSI
    delta = df_dict['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period).mean()
    rs = avg_gain / avg_loss
    df_dict['RSI'] = 100 - (100 / (1 + rs))

    # Calculate Momentum
    df_dict['Momentum'] = df_dict['close'] - df_dict['close'].shift(momentum_period)

    # Initialize result columns
    df_dict['KD_Type'] = None
    df_dict['KD_Value'] = None

    # Limit processing to last `bars_back` candles
    start_index = max(momentum_period, len(df_dict) - bars_back)

    for i in range(start_index, len(df_dict)):
        # Bullish Divergence
        if (
            df_dict['close'].iloc[i] < df_dict['close'].iloc[i - momentum_period] and
            df_dict['RSI'].iloc[i] > df_dict['RSI'].iloc[i - momentum_period] and
            df_dict['Momentum'].iloc[i] > df_dict['Momentum'].iloc[i - momentum_period]
        ):
            df_dict.at[df_dict.index[i], 'KD_Type'] = 'bullish'
            df_dict.at[df_dict.index[i], 'KD_Value'] = df_dict['close'].iloc[i]

        # Bearish Divergence
        elif (
            df_dict['close'].iloc[i] > df_dict['close'].iloc[i - momentum_period] and
            df_dict['RSI'].iloc[i] < df_dict['RSI'].iloc[i - momentum_period] and
            df_dict['Momentum'].iloc[i] < df_dict['Momentum'].iloc[i - momentum_period]
        ):
            df_dict.at[df_dict.index[i], 'KD_Type'] = 'bearish'
            df_dict.at[df_dict.index[i], 'KD_Value'] = df_dict['close'].iloc[i]

    return df_dict




