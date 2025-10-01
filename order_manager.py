#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Order Management Module
Handles order placement, confirmation, and status tracking
"""

import time
from datetime import datetime
from error_handler import SafeAPIWrapper, validate_order_response, log_error


class OrderManager:
    """
    Manages order lifecycle with proper confirmation and tracking
    """

    def __init__(self, smartapi):
        """
        Initialize order manager

        Args:
            smartapi: SmartAPI instance
        """
        self.api = SafeAPIWrapper(smartapi)
        self.smartapi = smartapi

    def place_buy_order(self, tradingsymbol, symboltoken, entry_price, quantity, exchange="NFO"):
        """
        Place buy order with confirmation

        Args:
            tradingsymbol: Trading symbol
            symboltoken: Symbol token
            entry_price: Entry price
            quantity: Quantity
            exchange: Exchange (default: NFO)

        Returns:
            dict: {
                'success': bool,
                'order_id': str or None,
                'message': str,
                'response': dict
            }
        """
        print(f"\n📋 Preparing BUY order...")
        print(f"   Symbol: {tradingsymbol}")
        print(f"   Price: ₹{entry_price:.2f}")
        print(f"   Quantity: {quantity}")
        print(f"   Exchange: {exchange}")

        # Prepare order parameters
        params = {
            "variety": "NORMAL",
            "tradingsymbol": tradingsymbol,
            "symboltoken": str(symboltoken),
            "transactiontype": "BUY",
            "exchange": exchange,
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": str(round(entry_price, 2)),
            "quantity": str(quantity)
        }

        try:
            # Place order
            response = self.api.place_order(params)

            # Validate response
            is_valid, message, order_id = validate_order_response(response)

            if not is_valid:
                return {
                    'success': False,
                    'order_id': None,
                    'message': message,
                    'response': response
                }

            print(f"✅ BUY order placed successfully")
            print(f"   Order ID: {order_id}")

            # Wait and confirm order
            confirmation = self.confirm_order_placement(order_id, max_wait=5)

            return {
                'success': True,
                'order_id': order_id,
                'message': 'Order placed and confirmed',
                'response': response,
                'confirmation': confirmation
            }

        except Exception as e:
            log_error(e, f"Failed to place BUY order for {tradingsymbol}")
            return {
                'success': False,
                'order_id': None,
                'message': str(e),
                'response': None
            }

    def place_sell_order(self, tradingsymbol, symboltoken, quantity, exchange="NFO",
                         order_type="MARKET", exit_price=None):
        """
        Place sell order with confirmation

        Args:
            tradingsymbol: Trading symbol
            symboltoken: Symbol token
            quantity: Quantity
            exchange: Exchange
            order_type: MARKET or LIMIT
            exit_price: Exit price (required for LIMIT orders)

        Returns:
            dict: Order placement result
        """
        print(f"\n📋 Preparing SELL order...")
        print(f"   Symbol: {tradingsymbol}")
        print(f"   Type: {order_type}")
        print(f"   Quantity: {quantity}")
        print(f"   Exchange: {exchange}")

        # Prepare order parameters
        params = {
            "variety": "NORMAL",
            "tradingsymbol": tradingsymbol,
            "symboltoken": str(symboltoken),
            "transactiontype": "SELL",
            "exchange": exchange,
            "ordertype": order_type,
            "producttype": "INTRADAY",
            "duration": "DAY",
            "quantity": str(quantity)
        }

        # Add price for limit orders
        if order_type == "LIMIT":
            if exit_price is None:
                return {
                    'success': False,
                    'order_id': None,
                    'message': 'Exit price required for LIMIT orders',
                    'response': None
                }
            params["price"] = str(round(exit_price, 2))
            print(f"   Price: ₹{exit_price:.2f}")

        try:
            # Place order
            response = self.api.place_order(params)

            # Validate response
            is_valid, message, order_id = validate_order_response(response)

            if not is_valid:
                return {
                    'success': False,
                    'order_id': None,
                    'message': message,
                    'response': response
                }

            print(f"✅ SELL order placed successfully")
            print(f"   Order ID: {order_id}")

            # Wait and confirm order
            confirmation = self.confirm_order_placement(order_id, max_wait=5)

            return {
                'success': True,
                'order_id': order_id,
                'message': 'Order placed and confirmed',
                'response': response,
                'confirmation': confirmation
            }

        except Exception as e:
            log_error(e, f"Failed to place SELL order for {tradingsymbol}")
            return {
                'success': False,
                'order_id': None,
                'message': str(e),
                'response': None
            }

    def confirm_order_placement(self, order_id, max_wait=10):
        """
        Confirm order placement by checking order status

        Args:
            order_id: Order ID to confirm
            max_wait: Maximum seconds to wait for confirmation

        Returns:
            dict: {
                'confirmed': bool,
                'status': str,
                'fill_price': float or None,
                'fill_quantity': int or None,
                'fill_time': str or None
            }
        """
        print(f"\n⏳ Confirming order {order_id}...")

        start_time = time.time()
        check_interval = 1  # Check every second

        while time.time() - start_time < max_wait:
            try:
                response = self.api.get_order_details(order_id)

                if response and 'data' in response:
                    order_data = response['data']
                    status = order_data.get('status', '').lower()

                    print(f"   Status: {status}")

                    if status == 'complete':
                        # Get execution details from trade book
                        fill_price, fill_time = self.get_trade_book_details(order_id)

                        return {
                            'confirmed': True,
                            'status': 'complete',
                            'fill_price': fill_price,
                            'fill_quantity': int(order_data.get('filledshares', 0)),
                            'fill_time': fill_time
                        }

                    elif status in ['rejected', 'cancelled']:
                        return {
                            'confirmed': False,
                            'status': status,
                            'fill_price': None,
                            'fill_quantity': None,
                            'fill_time': None
                        }

                    # Order still pending, wait and check again
                    time.sleep(check_interval)

            except Exception as e:
                log_error(e, f"Error checking order status for {order_id}")
                time.sleep(check_interval)

        # Timeout reached
        print(f"⚠️  Order confirmation timeout for {order_id}")
        return {
            'confirmed': False,
            'status': 'timeout',
            'fill_price': None,
            'fill_quantity': None,
            'fill_time': None
        }

    def get_trade_book_details(self, order_id):
        """
        Get execution details from trade book

        Args:
            order_id: Unique order ID

        Returns:
            tuple: (fill_price, fill_time)
        """
        try:
            # First get order details to find Angel order ID
            order_response = self.api.get_order_details(order_id)

            if not order_response or 'data' not in order_response:
                return None, None

            angel_order_id = order_response['data'].get('orderid')

            if not angel_order_id:
                return None, None

            # Get trade book
            trade_book_response = self.smartapi.tradeBook()

            if not trade_book_response or 'data' not in trade_book_response:
                return None, None

            # Find matching trade
            for trade in trade_book_response['data']:
                if trade.get('orderid') == angel_order_id:
                    fill_price = float(trade.get('fillprice', 0))
                    fill_time = trade.get('filltime', '')
                    return fill_price, fill_time

            return None, None

        except Exception as e:
            log_error(e, f"Error getting trade book details for {order_id}")
            return None, None

    def get_open_positions(self):
        """
        Get current open positions

        Returns:
            list: List of open positions
        """
        try:
            response = self.api.get_positions()

            if not response or 'data' not in response:
                return []

            # Filter for positions with non-zero quantity
            open_positions = [
                pos for pos in response['data']
                if int(pos.get('netqty', 0)) != 0
            ]

            return open_positions

        except Exception as e:
            log_error(e, "Error getting open positions")
            return []

    def verify_position(self, tradingsymbol, expected_quantity):
        """
        Verify that position exists with expected quantity

        Args:
            tradingsymbol: Trading symbol to verify
            expected_quantity: Expected position quantity

        Returns:
            dict: {
                'verified': bool,
                'actual_quantity': int,
                'message': str
            }
        """
        positions = self.get_open_positions()

        for pos in positions:
            if pos.get('tradingsymbol') == tradingsymbol:
                actual_qty = int(pos.get('netqty', 0))

                if actual_qty == expected_quantity:
                    return {
                        'verified': True,
                        'actual_quantity': actual_qty,
                        'message': 'Position verified successfully'
                    }
                else:
                    return {
                        'verified': False,
                        'actual_quantity': actual_qty,
                        'message': f'Quantity mismatch: Expected {expected_quantity}, Got {actual_qty}'
                    }

        return {
            'verified': False,
            'actual_quantity': 0,
            'message': f'Position not found for {tradingsymbol}'
        }


def create_order_manager(smartapi):
    """
    Factory function to create order manager

    Args:
        smartapi: SmartAPI instance

    Returns:
        OrderManager instance
    """
    return OrderManager(smartapi)
