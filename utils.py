#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 13:59:30 2024

@author: shyamkrishnamurthy
"""

import csv
import time
from SmartApi import SmartConnect
import os
import urllib
import json
import pandas as pd
import datetime as dt
from pyotp import TOTP

import traceback
import config
import technical_functions
from datetime import datetime
import sys

#import logging


#key_path = config.KEY_PATH_S
key_path = config.get_key_path()
#key_path = r"/Users/shyamdk/Developer/aone/Integrated/files"
os.chdir(key_path)

key_secret = open("key.txt", "r").read().split()

smartapi = SmartConnect(api_key=key_secret[0])
data = smartapi.generateSession(
    key_secret[2], key_secret[3], TOTP(key_secret[4]).now())

instrument_url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response = urllib.request.urlopen(instrument_url)
instrument_list = json.loads(response.read())




def get_ema_crossover_file_path(tradingsymbol):
    file_path = config.get_file_path()
    return os.path.join(file_path, f"{tradingsymbol}_ema_crossover_state.json")

def read_ema_crossover_state(tradingsymbol):
    path = get_ema_crossover_file_path(tradingsymbol)
    if os.path.exists(path):
        with open(path, "r") as file:
            return json.load(file)
    else:
        return {
            "ema_crossover_flag": False,
            "trades_after_crossover": 0
        }

def write_ema_crossover_state(tradingsymbol, state):
    path = get_ema_crossover_file_path(tradingsymbol)
    with open(path, "w") as file:
        json.dump(state, file)


def token_lookup(ticker, instrument_list, exchange="NSE"):
    for instrument in instrument_list:
        if instrument["name"] == ticker and instrument["exch_seg"] == exchange and instrument["symbol"].split('-')[
                -1] == "EQ":
            return instrument["token"]

def token_lookup_der_option(ticker, instrument_list, strike, expiry, ce_pe, instrumenttype="OPTIDX", exchange="NFO"):
    for instrument in instrument_list:
        if instrument["name"] == ticker and instrument["symbol"].endswith(ce_pe) and instrument["exch_seg"] == exchange and instrument["instrumenttype"] == instrumenttype and instrument["expiry"] == expiry and instrument["strike"] == strike:
            return instrument["token"]

def symbol_lookup_der_option(ticker, instrument_list, strike, expiry, ce_pe, instrumenttype="OPTIDX", exchange="NFO"):
    for instrument in instrument_list:
        if instrument["name"] == ticker and instrument["symbol"].endswith(ce_pe) and instrument["exch_seg"] == exchange and instrument["instrumenttype"] == instrumenttype and instrument["expiry"] == expiry and instrument["strike"] == strike:
            print('I am in symbol look up and we are looking at symbol',instrument["symbol"])
            return instrument["symbol"]

def token_lookup_der_option_given_tradingsymbol(tradingsymbol, instrument_list, instrumenttype="OPTIDX", exchange="NFO"):
    for instrument in instrument_list:
        if instrument["symbol"] == tradingsymbol and instrument["exch_seg"] == exchange and instrument["instrumenttype"] == instrumenttype:
            return instrument["token"]


def getfilename(filetype, btest_live, ticker):
    global current_symbol
    #directory_path = r"/Users/shyamkrishnamurthy/Oracle Content - Accounts/Oracle Content/Developer/pythonProject/aone/Integrated/files/df"
    
    # Generate filename with only the current date
    filename = filetype + "_" + ticker + "_" + btest_live  + "_" + datetime.now().strftime("%Y-%m-%d") + ".csv"
    
    # Combine the file path (location) and filename
    #full_path = os.path.join(directory_path, filename)
    
    return filename
    


def extract_uniqueorderid(response):
    # Check if 'data' key exists and 'uniqueorderid' exists within 'data'
    if 'data' in response and 'uniqueorderid' in response['data']:
        return response['data']['uniqueorderid']
    else:
        return None  # Return None if uniqueorderid is not found


# Initialize the trade_executed_flag globally or as part of the function's state
trade_executed_flag = False

        
def check_shyam_status(df):
    # Define the target status to trigger a return of the respective records
    target_status = 'buy_complete'
    
    # Filter rows where Shyam_Status matches the target status
    filtered_df = df[df['Shyam_Status'].str.lower() == target_status.lower()]
    
    # Check if there are any matching rows
    if not filtered_df.empty:
        print("There are open unconfirmed orders")
        
        # Convert each column to a single string
        order_ids = filtered_df['Order_ID'].to_string(index=False)
        symbols = filtered_df['Symbol'].to_string(index=False)
        order_quantities = filtered_df['Order_Quantity'].to_string(index=False)
        order_prices = filtered_df['Order_Price'].to_string(index=False)
        order_statuses = filtered_df['Order_Status'].to_string(index=False)
        unique_buy_order_ids = filtered_df['Unique_Buy_Order_ID'].to_string(index=False)
        buy_execution_time = filtered_df['Buy_Execution_Time'].to_string(index=False)          	
        buy_price = filtered_df['Buy_Price'].to_string(index=False)          	
        buy_quantity = filtered_df['Buy_Quantity'].to_string(index=False)       
        shyam_status = filtered_df['Shyam_Status'].to_string(index=False) 
        buy_strategy = filtered_df['Buy_Strategy'].to_string(index=False) 
        # Print values for verification
        print(order_ids, symbols, order_quantities, order_prices, order_statuses, unique_buy_order_ids, buy_execution_time, buy_price, buy_quantity, shyam_status, buy_strategy)
        
        # Return the string values
        return order_ids, symbols, order_quantities, order_prices, order_statuses, unique_buy_order_ids, buy_execution_time, buy_price, buy_quantity, shyam_status, buy_strategy
    else:
        print("No Orders placed")
        return 'Continue', None, None, None, None, None, None, None, None, None, None

def write_trade_to_file(file_path, entry_date, tradingsymbol, entry_ema8, entry_sma13, entry_price, shares_or_contracts, uniqueorderid, status):
    file_exists = os.path.isfile(file_path)
    
    # Open the file in append mode, and create a CSV writer
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # If file does not exist, write the header
        if not file_exists:
            writer.writerow(['Entry Date', 'Symbol', 'EMA', 'SMA', 'Entry Price', 'Quantity', 'Unique Order ID', 'Status'])
        
        # Write the trade data to the file
        writer.writerow([entry_date, tradingsymbol, entry_ema8, entry_sma13, entry_price, shares_or_contracts, uniqueorderid, status])
    
    print(f"Trade details written to {file_path}, Unique ID: {uniqueorderid}")


def round_to_nearest_5_paise(price):
    """Rounds the price to the nearest multiple of 0.05."""
    return round(price * 20) / 20


def place_limit_order(tradingsymbol, symboltoken, buy_sell, price, quantity, exchange="NFO"):
    #quantity = 1
    global uniqueorderid
    #new_price = float(price) * 0.99
    new_price = round_to_nearest_5_paise(price)  # Round to nearest 5 paise

    try:
        params = {
            "variety": "NORMAL",
            "tradingsymbol": tradingsymbol,
            "symboltoken": str(symboltoken),
            "transactiontype": buy_sell,
            "exchange": exchange,
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": str(new_price),
            "quantity": quantity
        }
        
        response = smartapi.placeOrder(params)
        print(response)
        return response
    except Exception as e:
        print(f"Error during placing: {e}")
        traceback.print_exc()  # Print the traceback
        time.sleep(5)  # Retry after delay in case of error
        

# Function to get and update status in the CSV file
def get_current_status():
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    file_path = f'trade_log_{current_date}.csv'  # Dynamic file name

    try:
        # Load the CSV file into a DataFrame
        trade_log_df = pd.read_csv(file_path)
    except FileNotFoundError:
        return 'No Trade Yet' , None # Return if the file does not exist
    except pd.errors.EmptyDataError:
        return 'No Trade Yet' , None  # Return if the file is empty
    except Exception as e:
        print(f"Error reading the file: {e}")
        return 'No Trade Yet' , None  # Return for any other read errors

    # Check if the required columns are present
    required_columns = ['Symbol', 'Unique Order ID', 'Status']
    for column in required_columns:
        if column not in trade_log_df.columns:
            return 'No Trade Yet' , None # Return if any required column is missing

    # Iterate over the ordered trades
    for index, ordered_trade in trade_log_df.iterrows():
        if ordered_trade['tradingsymbol'] == tradingsymbol:
            # Fetch the unique order ID
            u_id = ordered_trade['Unique Order ID']
            # Get the current status from the CSV
            current_status = ordered_trade['Status']
            print('Current status from file:', current_status)
            return current_status, u_id

    return 'No Trade Yet', None  # Return if no matching trades found


# Function to get and update status in the CSV file
def get_sell_current_status(tradingsymbol):
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    file_path = f'sell_trade_log_{current_date}.csv'  # Dynamic file name

    try:
        # Load the CSV file into a DataFrame
        trade_log_df = pd.read_csv(file_path)
    except FileNotFoundError:
        return 'No Trade Yet' , None # Return if the file does not exist
    except pd.errors.EmptyDataError:
        return 'No Trade Yet' , None  # Return if the file is empty
    except Exception as e:
        print(f"Error reading the file: {e}")
        return 'No Trade Yet' , None  # Return for any other read errors

    # Check if the required columns are present
    required_columns = ['Symbol', 'Unique Order ID', 'Status']
    for column in required_columns:
        if column not in trade_log_df.columns:
            return 'No Trade Yet' , None # Return if any required column is missing

    # Iterate over the ordered trades
    for index, ordered_trade in trade_log_df.iterrows():
        if ordered_trade['Symbol'] == tradingsymbol:
            # Fetch the unique order ID
            u_id = ordered_trade['Unique Order ID']
            # Get the current status from the CSV
            current_status = ordered_trade['Status']
            print('Current status from file:', current_status)
            return current_status, u_id

    return 'No Trade Yet', None  # Return if no matching trades found



def is_market_open():
    """Check if current time is within market hours."""
    now = dt.datetime.now()
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return now.weekday() < 5 and market_open <= now <= market_close


def get_buy_price(tradingsymbol,uniqueorderid):
    response = smartapi.orderBook()
    for order in response['data']:
        if order['orderstatus'] == 'complete' and order['tradingsymbol'] == tradingsymbol and order['uniqueorderid'] == uniqueorderid:
            #print(f"Order ID: {order['orderid']}")
            #print(f"Symbol: {order['tradingsymbol']}")
            buy_price = order['price']
            #print(f"Price: {buy_price}")
            #print(f"uniqueorderid : {order['uniqueorderid']}")
            return buy_price

def get_position(symbolname, uniqueorderid):
    response = smartapi.position()
    # Filter for open positions (where netqty is not 0)
    open_positions = [position for position in response['data'] if int(position['netqty']) != 0]
    # Extract trading symbols of open positions
    #open_position_symbols = [position['tradingsymbol'] for position in open_positions]
    for position in open_positions:
        if position['symbolname'] == symbolname:
            symbolname = position['symbolname']
            #print('symbolname:', symbolname) #NIFTY, BANKNIFTY, SENSEX]
            tradingsymbol = position['tradingsymbol']
            #print('tradingsymbol:', tradingsymbol )
            #get_open_order_tradingsymbol(tradingsymbol)
            CE_PE = position['optiontype']
            #print('optiontype:',CE_PE )
            quantity = position['netqty']
            #print('netqty:', quantity)
            buy_price = get_buy_price(position['tradingsymbol'], uniqueorderid)
            #print('buy_price:', buy_price)
            return symbolname, tradingsymbol, CE_PE, quantity, buy_price
        else:
            print('No Open Positions')
            
def are_there_current_positions():
    time.sleep(2)
    response = smartapi.position()
    
    # Check if response and data are not None
    if response is not None and 'data' in response and response['data'] is not None:
        # Filter for open positions (where netqty is not 0)
        open_positions = [position for position in response['data'] if int(position['netqty']) != 0]
        print(open_positions)
        
        # Check if there are any open positions
        if not open_positions:
            print("No open positions found.")
            return False
       #return True
    else:
        print("There are no information on current Orders or invalid response from smartapi.")
        return False
    return True

            




def hist_data_extended(ticker, duration, interval, instrument_list, CE_PE, tradingsymbol, symboltoken,  instrument_type="OPTIDX", exchange="NFO"):


    print('symboltoken: ', symboltoken)
    print('symbol: ', tradingsymbol)
    st_date = dt.date.today() - dt.timedelta(duration)
    end_date = dt.date.today()
    st_date = dt.datetime(st_date.year, st_date.month, st_date.day, 9, 15)
    end_date = dt.datetime(end_date.year, end_date.month, end_date.day)
    df_data = pd.DataFrame(
        columns=["date", "open", "high", "low", "close", "volume"])
    time.sleep(2)
    while st_date < end_date:
        time.sleep(1)  # Avoiding throttling rate limit
        params = {
            "exchange": exchange,
            "symboltoken": symboltoken,
            "interval": interval,
            "fromdate": st_date.strftime('%Y-%m-%d %H:%M'),
            "todate": end_date.strftime('%Y-%m-%d %H:%M')
        }
        hist_data = smartapi.getCandleData(params)
        #print(hist_data)
        temp = pd.DataFrame(hist_data["data"], columns=[
                            "date", "open", "high", "low", "close", "volume"])
        df_data = pd.concat([temp, df_data], ignore_index=True)
        end_date = dt.datetime.strptime(
            temp['date'].iloc[0][:16], "%Y-%m-%dT%H:%M")
        if len(temp) <= 1:  # Handle edge case where start date and end date become the same
            break

    df_data.set_index("date", inplace=True)
    df_data.index = pd.to_datetime(df_data.index)
    df_data.index = df_data.index.tz_localize(None)
    df_data.drop_duplicates(keep="first", inplace=True)

    # Calculate and add Heikin-Ashi candles, RSI, MACD, and ADX
    df_data = technical_functions.RSI(df_data, n=14, sma_length=14)
    df_data = technical_functions.get_adx(df_data, lookback=14)
    #df_data = SMA(df_data, n=50)
    df_data = technical_functions.SMA_ALL(df_data, n=13)
    df_data = technical_functions.ATR(df_data, n=14)
    df_data = technical_functions.EMA_ALL(df_data, n=8)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df_data['DateTime'] = current_time
    df_data['Symbol'] = ticker
    #print(df_data)
    file_path = config.get_file_path()
    #print(file_path)
    #key_path = r"/Users/shyamdk/Developer/aone/Integrated/files"
    os.chdir(file_path)
    df_data.to_csv(getfilename('historical_data', 'backtest', ticker), index=True)
    return symboltoken, tradingsymbol, df_data


def get_order_details_from_trade_book(uniqueorderid):
    response = smartapi.individual_order_details(uniqueorderid)
    angel_order_id = response['data']['orderid']
    print(f"get_order_details_from_trade_book -- For uniqueorderid:{uniqueorderid}, angel one orderid : {angel_order_id}")
    trade_book_response =  smartapi.tradeBook()
    #print(f'trade_book_response:{trade_book_response}')
    
    # Check if the response is successful
    if trade_book_response.get("status") and trade_book_response.get("data"):
        # Iterate through the data to find the matching order
        for trade in trade_book_response["data"]:
            if trade.get("orderid") == angel_order_id:
                fillprice = trade.get("fillprice")
                filltime = trade.get("filltime")
                fillsize = trade.get("fillsize")
                print(f'fillprice:{fillprice}, filltime:{filltime}, fillsize:{fillsize}')
                return fillprice, filltime
    
    # If order not found or response unsuccessful, return None values
    return None, None


def get_individual_order_details(uniqueorderid):

    response = smartapi.individual_order_details(uniqueorderid)
    print(f'get_individual_order_details response: {response}')
    new_status = response['data']['status']

    if new_status == 'complete':
        #response = {'status': True, 'message': 'SUCCESS', 'errorcode': '', 'data': {'variety': 'NORMAL', 'ordertype': 'LIMIT', 'producttype': 'INTRADAY', 'duration': 'DAY', 'price': 234.0, 'triggerprice': 0.0, 'quantity': '25', 'disclosedquantity': '0', 'squareoff': 0.0, 'stoploss': 0.0, 'trailingstoploss': 0.0, 'tradingsymbol': 'NIFTY31OCT2424600PE', 'transactiontype': 'BUY', 'exchange': 'NFO', 'symboltoken': '54759', 'instrumenttype': 'OPTIDX', 'strikeprice': 24600.0, 'optiontype': 'PE', 'expirydate': '31OCT2024', 'lotsize': '25', 'cancelsize': '0', 'averageprice': 234.0, 'filledshares': '25', 'unfilledshares': '0', 'orderid': '241023100051327', 'text': '', 'status': 'complete', 'orderstatus': 'complete', 'updatetime': '23-Oct-2024 09:17:34', 'exchtime': '23-Oct-2024 09:16:39', 'exchorderupdatetime': '23-Oct-2024 09:17:34', 'fillid': '', 'filltime': '', 'parentorderid': '', 'ordertag': '', 'uniqueorderid': '51ec9f15-fa22-4db0-b0a1-77f9782b160f'}}
        # Extract relevant fields from the response
        #unique_id = response['data']['uniqueorderid']
        fill_price, fill_time = get_order_details_from_trade_book(uniqueorderid)
        fill_quantity = response['data']['filledshares']
        print(f'The status is {new_status} ')
        return new_status, fill_price, fill_quantity, fill_time
    elif new_status == 'cancelled' :
        print(f'The status is {new_status} ')
        return new_status, None, None, None
    elif new_status == 'rejected':
        print(f'The status is {new_status} ')
        return new_status, None, None, None
    else:
        print(f'The status is {new_status} ')
        return None, None, None, None
    


def place_market_order(tradingsymbol, symboltoken, buy_sell, quantity, exchange="NFO"):
    #quantity = 1
    global uniqueorderid
    #new_price = float(price) * 0.99
    #new_price = round_to_nearest_5_paise(price)  # Round to nearest 5 paise

    try:
        params = {
            "variety": "NORMAL",
            "tradingsymbol": tradingsymbol,
            "symboltoken": str(symboltoken),
            "transactiontype": buy_sell,
            "exchange": exchange,
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "quantity": str(quantity)
        }
        
        response = smartapi.placeOrder(params)
        print(response)
        return response
    except Exception as e:
        print(f"Error during placing: {e}")
        traceback.print_exc()  # Print the traceback
        time.sleep(5)  # Retry after delay in case of error
        


def log_trade(CSV_FILE, trade, interval):
    """
    Logs trade details into a CSV file with an interval column at the beginning.
    """
    fieldnames = ["Interval", "Buy Date", "Buy Price", "Buy Quantity", 
                  "Sell Date", "Sell Price", "Sell Quantity", "Profit/Loss"]

    # Add the interval at the beginning of the trade dictionary
    trade_with_interval = {"Interval": interval, **trade}  

    try:
        with open(CSV_FILE, 'r') as f:
            pass
    except FileNotFoundError:
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(trade_with_interval)
'''

def log_trade(CSV_FILE, trade, interval):
    """
    Logs trade details into CSV file.
    """
    fieldnames = ["Interval","Buy Date", "Buy Price", "Buy Quantity", 
                  "Sell Date", "Sell Price", "Sell Quantity", 
                  "Profit/Loss"]

    try:
        with open(CSV_FILE, 'r') as f:
            pass
    except FileNotFoundError:
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(trade)
'''
def update_summary(tradingsymbol, strategy_name, df_trades, interval, STOP_LOSS,  PROFIT_PERCENT, SL_Trail):
    """ Updates the backtest summary CSV file with additional trade statistics, including brokerage costs. """

    # Save trade logs
    current_date = datetime.now().strftime("%d-%m-%y")
    file_path = config.KEY_PATH_BT + f"/{current_date}_backtest_summary.csv"

    total_trades = len(df_trades)
    
    # Apply brokerage cost of ₹50 per trade (assuming round-trip)
    brokerage_per_trade = 50
    total_brokerage = total_trades * brokerage_per_trade
    total_profit = df_trades["Profit/Loss"].sum() - total_brokerage
    avg_profit = (df_trades["Profit/Loss"].mean() - brokerage_per_trade) if total_trades else 0
    win_rate = (df_trades["Profit/Loss"] > 0).sum() / total_trades if total_trades else 0
    buy_logic = df_trades["buy_logic"]
    sell_logic = df_trades["sell_logic"]
    # Count positive and negative trades
    positive_trades = (df_trades["Profit/Loss"] > 0).sum()
    negative_trades = (df_trades["Profit/Loss"] <= 0).sum()

    summary = pd.DataFrame([{
        "Interval": interval,
        "SL_Trail": SL_Trail,
        "STOP_LOSS": STOP_LOSS,
        "PROFIT_PERCENT": PROFIT_PERCENT,
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Symbol": tradingsymbol,
        "Strategy": strategy_name,
        "Total Trades": total_trades,
        "Total Profit (after brokerage)": total_profit,
        "Avg Profit per Trade (after brokerage)": avg_profit,
        "Win Rate (%)": round(win_rate * 100, 2),
        "Positive Trades": positive_trades,
        "Negative Trades": negative_trades,
        "Total Brokerage Paid": total_brokerage,
        "Buy Logic": buy_logic,
        "Sell Logic": sell_logic
    }])

    # Append to CSV, keeping latest first
    if pd.io.common.file_exists(file_path):
        existing_df = pd.read_csv(file_path)
        summary = pd.concat([summary, existing_df])

    summary.to_csv(file_path, index=False)

def check_symbol_formation(list_of_symbols):
    for tradingsymbol in list_of_symbols:
        symboltoken = token_lookup_der_option_given_tradingsymbol(
            tradingsymbol, instrument_list, instrumenttype="OPTIDX", exchange="NFO"
        )
        print(f"The Symbol:{tradingsymbol} --- The Token: {symboltoken}")
        if symboltoken == None:
            print(f"Problem with Symbol:{tradingsymbol}")
            sys.exit()
'''

print('in execute method')
candle_duration = config.DURATION_3M
interval = 1
tickers = config.INSTRUMENTS_NIFTY_ONLY
strategy = config.STRATEGY_ONE
print('got info from config')

ticker = 'NIFTY'
duration = 'THREE_MINUTE'
interval = '1'
CE_PE ='CE'
tradingsymbol = get_current_atm_symbol.symbol_lookup_der_option(ticker, instrument_list, get_current_atm_symbol.find_atm_strike(ticker, get_current_atm_symbol.get_price(ticker))+"00.000000", get_current_atm_symbol.next_expiration(ticker), CE_PE, instrumenttype="OPTIDX", exchange='NFO')
time.sleep(2)
symboltoken = get_current_atm_symbol.token_lookup_der_option(ticker, instrument_list, get_current_atm_symbol.find_atm_strike(ticker, get_current_atm_symbol.get_price(ticker))+"00.000000", get_current_atm_symbol.next_expiration(ticker), CE_PE, instrumenttype="OPTIDX", exchange='NFO')
print('tradingsymbol', tradingsymbol)
print('symboltoken', symboltoken)
#hist_data_extended(ticker, candle_duration, interval, instrument_list, CE_PE, tradingsymbol, symboltoken,  instrument_type="OPTIDX", exchange="NFO")

#hist_data_extended(ticker, 30, 'THREE_MINUTE', instrument_list, "CE", tradingsymbol, symboltoken,  instrument_type="OPTIDX", exchange="NFO")

'''
