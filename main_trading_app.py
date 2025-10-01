#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Trading Application - Improved Version
Integrates all improvements: secure config, database, risk management, etc.
"""

import sys
import time
import pandas as pd
import datetime as dt
from datetime import datetime
from pyotp import TOTP
import urllib
import json
from SmartApi import SmartConnect

# Import improved modules
from secure_config import get_secure_config
from database import get_database
from risk_manager import get_risk_manager
from order_manager import create_order_manager
from entry_logic import check_entry_conditions_v2, process_buy_logic_improved
from exit_logic import check_exit_conditions_v2, process_sell_logic_improved
from error_handler import SafeAPIWrapper, log_error
from logger_config import get_default_logger, get_trade_logger, log_system_start, log_system_stop
import technical_functions
import config


class TradingSystem:
    """
    Main trading system orchestrator
    """

    def __init__(self):
        """Initialize trading system"""
        self.logger = get_default_logger()
        self.trade_logger = get_trade_logger()
        self.config = get_secure_config()
        self.db = get_database()
        self.risk_manager = get_risk_manager()

        # Initialize API connection
        self.smartapi = None
        self.safe_api = None
        self.order_manager = None
        self.instrument_list = []

        self.logger.info("Trading System initialized")

    def connect_to_broker(self):
        """
        Establish connection to broker API

        Returns:
            bool: Success status
        """
        self.logger.info("Connecting to broker...")

        try:
            # Get credentials from secure config
            creds = self.config.get_api_credentials()

            # Initialize SmartAPI
            self.smartapi = SmartConnect(api_key=creds['api_key'])

            # Generate session
            session_data = self.smartapi.generateSession(
                creds['username'],
                creds['password'],
                TOTP(creds['totp_secret']).now()
            )

            self.logger.info("✅ Broker connection established")
            self.logger.info(f"Session: {session_data.get('data', {}).get('jwtToken', '')[:20]}...")

            # Initialize safe API wrapper
            self.safe_api = SafeAPIWrapper(self.smartapi)

            # Initialize order manager
            self.order_manager = create_order_manager(self.smartapi)

            # Fetch instrument list
            self.fetch_instrument_list()

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to connect to broker: {str(e)}")
            log_error(e, "Broker connection failed")
            return False

    def fetch_instrument_list(self):
        """Fetch and cache instrument list"""
        self.logger.info("Fetching instrument list...")

        try:
            instrument_url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
            response = urllib.request.urlopen(instrument_url)
            self.instrument_list = json.loads(response.read())

            self.logger.info(f"✅ Loaded {len(self.instrument_list)} instruments")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to fetch instrument list: {str(e)}")
            return False

    def get_symbol_token(self, tradingsymbol, exchange="NFO", instrumenttype="OPTIDX"):
        """
        Get symbol token from instrument list

        Args:
            tradingsymbol: Trading symbol
            exchange: Exchange
            instrumenttype: Instrument type

        Returns:
            str: Symbol token or None
        """
        for instrument in self.instrument_list:
            if (instrument["symbol"] == tradingsymbol and
                instrument["exch_seg"] == exchange and
                instrument["instrumenttype"] == instrumenttype):
                return instrument["token"]

        self.logger.error(f"Symbol token not found for {tradingsymbol}")
        return None

    def fetch_candle_data(self, tradingsymbol, symboltoken, interval, days_back, exchange="NFO"):
        """
        Fetch historical candle data

        Args:
            tradingsymbol: Trading symbol
            symboltoken: Symbol token
            interval: Candle interval
            days_back: Number of days to fetch
            exchange: Exchange

        Returns:
            pd.DataFrame: Candle data with technical indicators
        """
        self.logger.debug(f"Fetching candle data for {tradingsymbol}")

        try:
            params = {
                "exchange": exchange,
                "symboltoken": symboltoken,
                "interval": interval,
                "fromdate": (dt.date.today() - dt.timedelta(days_back)).strftime('%Y-%m-%d %H:%M'),
                "todate": dt.datetime.now().strftime('%Y-%m-%d %H:%M')
            }

            hist_data = self.safe_api.get_candle_data(params)

            # Convert to DataFrame
            df_data = pd.DataFrame(
                hist_data["data"],
                columns=["date", "open", "high", "low", "close", "volume"]
            )
            df_data.index = pd.to_datetime(df_data["date"])
            df_data.index = df_data.index.tz_localize(None)

            # Calculate technical indicators
            df_data = technical_functions.RSI_CORRECTED(df_data, n=14, sma_length=14)
            df_data = technical_functions.get_adx(df_data, lookback=14)
            df_data = technical_functions.SMA_ALL(df_data, n=20)
            df_data = technical_functions.EMA5(df_data, n=5)
            df_data = technical_functions.EMA3(df_data, n=3)
            df_data = technical_functions.CCI(df_data, n=20)

            self.logger.debug(f"Fetched {len(df_data)} candles for {tradingsymbol}")

            return df_data

        except Exception as e:
            self.logger.error(f"Failed to fetch candle data for {tradingsymbol}: {str(e)}")
            log_error(e, f"Candle data fetch failed for {tradingsymbol}")
            return None

    def process_entry_signals(self, symbol_list, interval):
        """
        Process entry signals for list of symbols

        Args:
            symbol_list: List of trading symbols
            interval: Candle interval
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"SCANNING FOR ENTRY SIGNALS")
        self.logger.info(f"Symbols: {len(symbol_list)} | Interval: {interval}")
        self.logger.info(f"{'='*80}")

        for tradingsymbol in symbol_list:
            try:
                self.logger.info(f"\n--- Processing {tradingsymbol} ---")

                # Get quantity for this symbol
                if tradingsymbol.startswith("NIFTY"):
                    shares_or_contracts = config.BUY_NIFTY_1
                elif tradingsymbol.startswith("BANKNIFTY"):
                    shares_or_contracts = config.BUY_BANKNIFTY_1
                else:
                    shares_or_contracts = config.BUY_EQUITY_1

                # Get symbol token
                symboltoken = self.get_symbol_token(tradingsymbol)
                if not symboltoken:
                    continue

                # Check risk management
                entry_price_estimate = 100  # Placeholder, will be calculated
                risk_check = self.risk_manager.can_enter_trade(
                    tradingsymbol, entry_price_estimate, shares_or_contracts
                )

                if not risk_check['allowed']:
                    self.logger.warning(f"⛔ Entry blocked: {risk_check['reason']}")
                    continue

                # Fetch candle data
                df_data = self.fetch_candle_data(tradingsymbol, symboltoken, interval, 108)

                if df_data is None or df_data.empty:
                    self.logger.warning(f"No data available for {tradingsymbol}")
                    continue

                # Check entry conditions
                entry_result = check_entry_conditions_v2(df_data, tradingsymbol)

                if entry_result['entry_signal']:
                    self.logger.info(f"✅ Entry signal detected for {tradingsymbol}")

                    # Final risk check with actual entry price
                    risk_check = self.risk_manager.can_enter_trade(
                        tradingsymbol,
                        entry_result['entry_price'],
                        shares_or_contracts
                    )

                    if not risk_check['allowed']:
                        self.logger.warning(f"⛔ Entry blocked: {risk_check['reason']}")
                        continue

                    # Execute entry
                    self.execute_entry(
                        df_data, tradingsymbol, symboltoken,
                        shares_or_contracts, entry_result
                    )

                time.sleep(1)  # Rate limiting

            except Exception as e:
                self.logger.error(f"Error processing {tradingsymbol}: {str(e)}")
                log_error(e, f"Entry processing failed for {tradingsymbol}")
                continue

    def execute_entry(self, df_data, tradingsymbol, symboltoken, quantity, entry_result):
        """Execute entry trade"""
        entry_price = entry_result['entry_price']
        entry_reason = entry_result['entry_reason']

        self.logger.info(f"\n🎯 EXECUTING ENTRY: {tradingsymbol}")
        self.logger.info(f"   Price: ₹{entry_price:.2f}")
        self.logger.info(f"   Quantity: {quantity}")
        self.logger.info(f"   Reason: {entry_reason}")

        # Place order
        order_result = self.order_manager.place_buy_order(
            tradingsymbol, symboltoken, entry_price, quantity
        )

        if order_result['success']:
            order_id = order_result['order_id']

            # Save to database
            trade_data = {
                'tradingsymbol': tradingsymbol,
                'symboltoken': symboltoken,
                'order_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'order_quantity': quantity,
                'order_price': entry_price,
                'order_status': 'open' if config.LIVE_FLAG == 'LIVE' else 'complete',
                'order_strategy': entry_reason,
                'unique_buy_order_id': order_id,
                'shyam_status': 'ordered' if config.LIVE_FLAG == 'LIVE' else 'buy_complete'
            }

            self.db.insert_trade(trade_data)

            # Log trade
            self.trade_logger.log_entry(
                tradingsymbol, entry_price, quantity, entry_reason, order_id
            )

            self.logger.info(f"✅ Entry executed successfully for {tradingsymbol}")
        else:
            self.logger.error(f"❌ Entry failed for {tradingsymbol}: {order_result['message']}")

    def process_exit_signals(self, interval):
        """
        Process exit signals for open positions

        Args:
            interval: Candle interval
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"SCANNING FOR EXIT SIGNALS")
        self.logger.info(f"{'='*80}")

        # Get open trades
        open_trades = self.db.get_open_trades()

        if not open_trades:
            self.logger.info("No open positions to monitor")
            return

        self.logger.info(f"Monitoring {len(open_trades)} open positions")

        for trade in open_trades:
            try:
                tradingsymbol = trade['tradingsymbol']
                symboltoken = trade['symboltoken']

                self.logger.info(f"\n--- Checking {tradingsymbol} ---")

                # Fetch current candle data
                df_data = self.fetch_candle_data(tradingsymbol, symboltoken, interval, 108)

                if df_data is None or df_data.empty:
                    continue

                # Check exit conditions
                entry_price = float(trade['order_price'])
                max_profit_seen = float(trade.get('max_profit_seen', 0))

                exit_result = check_exit_conditions_v2(
                    df_data, entry_price, max_profit_seen, tradingsymbol
                )

                # Update max profit if changed
                if exit_result['max_profit_updated'] != max_profit_seen:
                    self.db.update_max_profit_seen(
                        trade['order_id'],
                        exit_result['max_profit_updated']
                    )

                # Execute exit if signal detected
                if exit_result['exit_signal']:
                    self.logger.info(f"✅ Exit signal detected for {tradingsymbol}")
                    self.execute_exit(trade, exit_result)

                time.sleep(1)  # Rate limiting

            except Exception as e:
                self.logger.error(f"Error checking exit for {tradingsymbol}: {str(e)}")
                log_error(e, f"Exit processing failed for {tradingsymbol}")
                continue

    def execute_exit(self, trade, exit_result):
        """Execute exit trade"""
        tradingsymbol = trade['tradingsymbol']
        symboltoken = trade['symboltoken']
        quantity = int(trade['order_quantity'])
        exit_price = exit_result['exit_price']
        exit_reason = exit_result['exit_reason']
        entry_price = float(trade['order_price'])

        self.logger.info(f"\n🎯 EXECUTING EXIT: {tradingsymbol}")
        self.logger.info(f"   Price: ₹{exit_price:.2f}")
        self.logger.info(f"   Quantity: {quantity}")
        self.logger.info(f"   Reason: {exit_reason}")

        # Place sell order
        order_result = self.order_manager.place_sell_order(
            tradingsymbol, symboltoken, quantity, order_type="MARKET"
        )

        if order_result['success']:
            order_id = order_result['order_id']

            # Update database
            sell_data = {
                'sell_date': datetime.now().strftime("%d-%m-%y %H-%M-%S"),
                'sell_quantity': quantity,
                'sell_price': exit_price,
                'sell_status': 'open' if config.LIVE_FLAG == 'LIVE' else 'complete',
                'sell_strategy': exit_reason,
                'unique_sell_order_id': order_id,
                'shyam_status': 'sell_ordered' if config.LIVE_FLAG == 'LIVE' else 'sell_complete'
            }

            self.db.update_sell_trade(trade['order_id'], sell_data)

            # Calculate P&L
            pnl = (exit_price - entry_price) * quantity
            pnl_pct = ((exit_price - entry_price) / entry_price) * 100

            # Log trade
            self.trade_logger.log_exit(
                tradingsymbol, exit_price, quantity, pnl, pnl_pct, exit_reason, order_id
            )

            self.logger.info(f"✅ Exit executed for {tradingsymbol} | P&L: ₹{pnl:+.2f} ({pnl_pct:+.2f}%)")
        else:
            self.logger.error(f"❌ Exit failed for {tradingsymbol}: {order_result['message']}")

    def run(self, symbol_list, interval=config.DURATION_1M):
        """
        Main trading loop

        Args:
            symbol_list: List of symbols to trade
            interval: Candle interval
        """
        log_system_start()
        self.logger.info(f"Starting trading loop for {len(symbol_list)} symbols")
        self.logger.info(f"Interval: {interval} | Mode: {config.LIVE_FLAG}")

        # Trading hours
        start_time = dt.time(9, 15)
        end_time = dt.time(15, 30)

        try:
            while True:
                current_time = dt.datetime.now()

                # Check if within trading hours
                if current_time.time() >= end_time:
                    self.logger.info("Trading hours ended")
                    break

                if current_time.time() < start_time:
                    wait_seconds = (dt.datetime.combine(dt.date.today(), start_time) - current_time).total_seconds()
                    self.logger.info(f"Waiting until market open: {wait_seconds:.0f}s")
                    time.sleep(min(wait_seconds, 60))
                    continue

                # Print risk summary
                self.risk_manager.print_risk_summary()

                # Check if trading is enabled
                if not self.risk_manager.trading_enabled:
                    self.logger.warning("Trading is halted - skipping iteration")
                    time.sleep(60)
                    continue

                # Process entry signals
                self.process_entry_signals(symbol_list, interval)

                # Process exit signals
                self.process_exit_signals(interval)

                # Wait for next iteration (60 seconds)
                self.logger.info(f"\n{'='*80}")
                self.logger.info("Sleeping for 60 seconds...")
                self.logger.info(f"{'='*80}\n")
                time.sleep(60)

        except KeyboardInterrupt:
            self.logger.info("\n⚠️  Keyboard interrupt received")
        except Exception as e:
            self.logger.error(f"❌ Fatal error in main loop: {str(e)}")
            log_error(e, "Main loop failed")
        finally:
            log_system_stop()
            # Print final summary
            self.risk_manager.print_risk_summary()


def main():
    """Main entry point"""
    # Create trading system
    system = TradingSystem()

    # Connect to broker
    if not system.connect_to_broker():
        print("Failed to connect to broker. Exiting.")
        sys.exit(1)

    # Define symbols to trade
    symbol_list = config.INSTRUMENTS_NIFTY_O

    # Run trading system
    system.run(symbol_list)


if __name__ == "__main__":
    main()
