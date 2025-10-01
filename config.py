#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 14:42:35 2024

@author: shyamkrishnamurthy
"""
LIVE_FLAG = 'LIVE_TEST'
#LIVE_FLAG = 'BACKTEST'


#LIVE_FLAG = 'LIVE'
wait_time_interval = 3

STRETCHED = 'YES'

# Entry Strategy Parameters
ENTRY_RSI_SMA_GAP_MIN = 3  # Minimum gap between RSI and RSI_SMA for entry
ENTRY_ADX_MIN = 14  # Minimum ADX value for entry

# Exit Strategy Parameters
TARGET_PROFIT_PERCENT = 1  # Fixed profit target percentage
STOP_LOSS = -4  # Fixed stop loss percentage (negative value)

# Trailing Stop Loss Parameters
TRAILING_STOP_LOSS_ENABLED = True  # Enable/disable trailing stop loss
TRAILING_STOP_LOSS_TRIGGER_PERCENT = 1.5  # Profit % to activate trailing SL
TRAILING_STOP_LOSS_TRAIL_PERCENT = 1.0  # Trail distance from peak profit %

# Risk Management Parameters
POSITION_SIZE = 50000  # Position size in currency units
MAX_DAILY_LOSS = -10000  # Maximum daily loss limit (negative value)
MAX_POSITION_COUNT = 3  # Maximum number of concurrent positions


DURATION_1M = 'ONE_MINUTE'
DURATION_3M = 'THREE_MINUTE'
DURATION_5M = 'FIVE_MINUTE'
DURATION_10M = 'TEN_MINUTE'
DURATION_15M = 'FIFTEEN_MINUTE'	
DURATION_30M = 'THIRTY_MINUTE'	
DURATION_1H = 'ONE_HOUR'
DURATION_1D = 'ONE_DAY'



GAP_LIMIT_PURE = 3
GAP_LIMIT_SMALL = 2


NIFTY50_ENTRY_STRATEGY_MOMEMTUM_LOW = 'EMA3_SMA21_MOMEMT_LOW'
NIFTY50_ENTRY_STRATEGY_MOMEMTUM_HIGH = 'EMA3_SMA21_MOMEMT_LOW'
NIFTY50_EXIT_STRATEGY_2_PERCENT = 'TWO_PERCENT'
NIFTY50_EXIT_STRATEGY_EMA_CROSS_UNDER = 'EMA_CROSS_UNDER'
 

#ENTRY_STRATEGY = 'EMA3_SMA13_ADXI'
ENTRY_STRATEGY = 'EMA3_SMA13_ADXI'

TIMING_OFFSET = -1

#EXIT_STRATEGY = 'RSI_EMA_ADXD'
#EXIT_STRATEGY = 'RSI'
EXIT_STRATEGY = 'EMA3_SMA13_ADXI'


BUY_NIFTY_1 = 75
BUY_BANKNIFTY_1 = 30
BUY_EQUITY_1 = 1
BUY_MULTIPLIER = 1

INSTRUMENTS_NIFTY_ONLY = ['NIFTY']
INSTRUMENTS_BANK_NIFTY_ONLY = ['BANKNIFTY']
INSTRUMENTS_BANK_AND_NIFTY = ['NIFTY', 'BANKNIFTY']
INSTRUMENTS_NIFTY_50_HDFC = ['HDFCBANK']

INSTRUMENTS_NIFTY_50_ONLY_ALL = ["NIFTY","WIPRO","ULTRACEMCO","UPL","TITAN","TECHM","TATASTEEL","TATAMOTORS",
           "TATACONSUM","TCS","SUNPHARMA","SBIN","SBILIFE","RELIANCE","POWERGRID",
           "ONGC","NESTLEIND","NTPC","MARUTI","M&M","LT","KOTAKBANK","JSWSTEEL",
           "INFY","INDUSINDBK","ITC","ICICIBANK","HDFCBANK","HINDUNILVR","HINDALCO",
           "HEROMOTOCO","HDFCLIFE","HDFCBANK","HCLTECH","GRASIM","EICHERMOT",
           "DRREDDY","DIVISLAB","COALINDIA","CIPLA","BRITANNIA","BHARTIARTL",
           "BPCL","BAJAJFINSV","BAJFINANCE","BAJAJ-AUTO","AXISBANK","ASIANPAINT",
           "APOLLOHOSP","ADANIPORTS","ADANIENT"]


INSTRUMENTS_NIFTY_50_V_50_ONLY_ALL = ["RELIANCE","HDFCBANK","TCS","BHARTIARTL","ICICIBANK","SBIN","INFY","BAJFINANCE","HINDUNILVR",
                                      "ITC","LT","HCLTECH","KOTAKBANK","SUNPHARMA","MARUTI","M&M","AXISBANK","ULTRACEMCO","NTPC","BAJAJFINSV",
                                      "ADANIPORTS","TITAN","ONGC","ADANIENT","BEL","POWERGRID","TATAMOTORS","WIPRO","ETERNAL",
                                      "COALINDIA","JSWSTEEL","BAJAJ-AUTO","NESTLEIND","ASIANPAINT","TRENT","TATASTEEL",
                                      "JIOFIN","SBILIFE","GRASIM","HDFCLIFE","TECHM","EICHERMOT","HINDALCO","SHRIRAMFIN",
                                      "CIPLA","TATACONSUM","DRREDDY","APOLLOHOSP","HEROMOTOCO","INDUSINDBK","BAJAJHLDNG",
                                      "PIDILITIND","ICICIGI","HAVELLS","ICICIPRULI","DABUR","ICICIPRULI","MARICO","BERGEPAINT",
                                      "COLPAL","GLAXO","PAGEIND","NAM-INDIA","VOLTAS","CDSL","GILLETTE","PFIZER","BATAINDIA",
                                      "AAVAS","HDFCAMC","PGHH","SANOFI"]


INSTRUMENTS_NIFTY_50_LTD = ["TCS","RELIANCE","HDFCBANK", "AXISBANK", "SUNPHARMA", "TATACONSUM"]
INSTRUMENTS_NIFTY_IN_LIST_1H = ["TCS", "TATASTEEL", "ASIANPAINT"]

#INSTRUMENTS_NIFTY_50_ONLY = ['HDFCBANK', ]
#INSTRUMENTS_NIFTY_50_ONLY_ALL = ["WIPRO","ULTRACEMCO","UPL","TITAN","TECHM","TATASTEEL","TATAMOTORS"]

INSTRUMENTS_NIFTY_B = [ 'NIFTY26JUN2525000CE', 'BANKNIFTY26JUN2556600CE','NIFTY26JUN2525000PE', 'BANKNIFTY26JUN2556600PE']
INSTRUMENTS_NIFTY_O = [ 'NIFTY23SEP2525550PE']

#for in the money, take lower than ATM CE and higher than ATM PE
#if ATRM is 24000, then CE - 23800 and PE should be 24200


KEY_PATH_BT = r"/Users/shyamdk/developer/aone/trading/om_ema5/files/backtest"
TRADE_PATH = r"/Users/shyamdk/developer/aone/trading/om_ema5/files/trades"
BASE_FILE = "om_ema5"
KEY_PATH_S = r"/Users/shyamdk/developer/aone/trading/"+BASE_FILE+"/keys"
FILE_PATH_S = r"/Users/shyamdk/developer/aone/trading/"+BASE_FILE+"/files"
FILE_PATH_E_S = r"/Users/shyamdk/developer/aone/trading/"+BASE_FILE+"/files/e"
MODULE_PATH_S = r"/Users/shyamdk/developer/aone/trading/"+BASE_FILE
LOG_FILE_PATH_S = r"/Users/shyamdk/developer/aone/trading/"+BASE_FILE+"/files/logs"
FILE_PATH_SCREENER_S = r"/Users/shyamdk/developer/aone/trading/"+BASE_FILE+"/files/screener"
FLAG_FILE_PATH_S = r"/Users/shyamdk/developer/aone/trading/"+BASE_FILE+"/files/flags"
PE_ONLY = False
CE_ONLY = False


def get_trade_file_path():
    return "/Users/shyamdk/developer/aone/trading/om_ema5/files/trades"
    
def get_key_path():
    return KEY_PATH_S
    
def get_file_path():
    return FILE_PATH_S
    
def get_equity_file_path():
    return FILE_PATH_E_S
    
def get_module_path():
    return MODULE_PATH_S
    
def get_log_file_path():
    return LOG_FILE_PATH_S
