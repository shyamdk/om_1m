#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Error Handling Module
Provides robust error handling and retry logic for API calls
"""

import time
import traceback
from functools import wraps
from datetime import datetime


class TradingException(Exception):
    """Base exception for trading system"""
    pass


class APIException(TradingException):
    """Exception for API-related errors"""
    pass


class OrderException(TradingException):
    """Exception for order-related errors"""
    pass


class ValidationException(TradingException):
    """Exception for validation errors"""
    pass


def retry_on_failure(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    Decorator for retrying functions on failure with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch

    Usage:
        @retry_on_failure(max_retries=3, delay=2, backoff=2)
        def my_function():
            # code that might fail
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        print(f"\n⚠️  Attempt {attempt + 1}/{max_retries} failed for {func.__name__}")
                        print(f"   Error: {str(e)}")
                        print(f"   Retrying in {retry_delay}s...")

                        time.sleep(retry_delay)
                        retry_delay *= backoff
                    else:
                        print(f"\n❌ All {max_retries} retry attempts failed for {func.__name__}")
                        print(f"   Final error: {str(e)}")
                        traceback.print_exc()
                        raise last_exception

            # This should never be reached, but just in case
            raise last_exception if last_exception else Exception("Unknown error")

        return wrapper
    return decorator


class SafeAPIWrapper:
    """
    Wrapper for SmartAPI calls with error handling
    """

    def __init__(self, smartapi):
        """
        Initialize wrapper

        Args:
            smartapi: SmartAPI instance
        """
        self.smartapi = smartapi

    @retry_on_failure(max_retries=3, delay=2, backoff=2, exceptions=(Exception,))
    def get_candle_data(self, params):
        """
        Get candle data with retry logic

        Args:
            params: Parameters for getCandleData

        Returns:
            dict: Candle data response

        Raises:
            APIException: If API call fails after retries
        """
        try:
            response = self.smartapi.getCandleData(params)

            # Validate response
            if not response:
                raise APIException("Empty response from API")

            if 'data' not in response:
                raise APIException(f"Invalid response format: {response}")

            if not response['data']:
                raise APIException("No data in response")

            return response

        except Exception as e:
            raise APIException(f"Failed to get candle data: {str(e)}")

    @retry_on_failure(max_retries=3, delay=2, backoff=2, exceptions=(Exception,))
    def place_order(self, params):
        """
        Place order with retry logic

        Args:
            params: Order parameters

        Returns:
            dict: Order response

        Raises:
            OrderException: If order placement fails
        """
        try:
            # Validate order parameters
            required_params = ['tradingsymbol', 'symboltoken', 'transactiontype',
                              'exchange', 'ordertype', 'producttype', 'quantity']

            missing = [p for p in required_params if p not in params]
            if missing:
                raise ValidationException(f"Missing required parameters: {missing}")

            # Place order
            response = self.smartapi.placeOrder(params)

            # Validate response
            if not response:
                raise OrderException("Empty response from order placement")

            # Check for error in response
            if response.get('status') is False:
                error_msg = response.get('message', 'Unknown error')
                raise OrderException(f"Order placement failed: {error_msg}")

            return response

        except ValidationException:
            # Don't retry validation errors
            raise
        except Exception as e:
            raise OrderException(f"Failed to place order: {str(e)}")

    @retry_on_failure(max_retries=3, delay=1, backoff=2, exceptions=(Exception,))
    def get_order_details(self, unique_order_id):
        """
        Get order details with retry logic

        Args:
            unique_order_id: Unique order ID

        Returns:
            dict: Order details

        Raises:
            APIException: If API call fails
        """
        try:
            response = self.smartapi.individual_order_details(unique_order_id)

            if not response or 'data' not in response:
                raise APIException(f"Invalid response for order {unique_order_id}")

            return response

        except Exception as e:
            raise APIException(f"Failed to get order details: {str(e)}")

    @retry_on_failure(max_retries=2, delay=1, backoff=2, exceptions=(Exception,))
    def get_positions(self):
        """
        Get current positions with retry logic

        Returns:
            dict: Positions data

        Raises:
            APIException: If API call fails
        """
        try:
            response = self.smartapi.position()

            if not response or 'data' not in response:
                raise APIException("Invalid response from positions API")

            return response

        except Exception as e:
            raise APIException(f"Failed to get positions: {str(e)}")


class CircuitBreaker:
    """
    Circuit breaker pattern for API calls
    Prevents cascading failures by stopping calls after repeated failures
    """

    def __init__(self, failure_threshold=5, timeout=60):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args, **kwargs: Arguments for function

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == 'OPEN':
            # Check if timeout has elapsed
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
                print("🟡 Circuit breaker: HALF_OPEN - Attempting call")
            else:
                raise APIException("Circuit breaker is OPEN - too many failures")

        try:
            result = func(*args, **kwargs)

            # Success - reset or close circuit
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
                print("🟢 Circuit breaker: CLOSED - Recovered from failures")

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                print(f"🔴 Circuit breaker: OPEN - Too many failures ({self.failure_count})")

            raise e

    def reset(self):
        """Manually reset circuit breaker"""
        self.state = 'CLOSED'
        self.failure_count = 0
        self.last_failure_time = None
        print("🔄 Circuit breaker: RESET")


def validate_order_response(response):
    """
    Validate order response from API

    Args:
        response: API response

    Returns:
        tuple: (is_valid, error_message, order_id)
    """
    if not response:
        return False, "Empty response", None

    if not isinstance(response, dict):
        return False, f"Invalid response type: {type(response)}", None

    # Check status
    if response.get('status') is False:
        error_msg = response.get('message', 'Unknown error')
        return False, error_msg, None

    # Extract order ID
    order_id = None
    if 'data' in response and isinstance(response['data'], dict):
        order_id = response['data'].get('uniqueorderid')

    if not order_id:
        return False, "Order ID not found in response", None

    return True, "Success", order_id


def log_error(error, context=""):
    """
    Log error with context

    Args:
        error: Exception object
        context: Additional context string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*80}")
    print(f"ERROR LOG: {timestamp}")
    if context:
        print(f"Context: {context}")
    print(f"Error Type: {type(error).__name__}")
    print(f"Error Message: {str(error)}")
    print(f"Traceback:")
    traceback.print_exc()
    print(f"{'='*80}\n")


# Global circuit breaker instance
_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

def get_circuit_breaker():
    """Get global circuit breaker instance"""
    return _circuit_breaker
