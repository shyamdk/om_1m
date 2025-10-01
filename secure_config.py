#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Secure Configuration Module
Handles API credentials and sensitive configuration securely
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get the directory containing this file
BASE_DIR = Path(__file__).parent.absolute()

# Load environment variables from .env file
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)


class SecureConfig:
    """Secure configuration handler for API credentials and sensitive data"""

    def __init__(self):
        self.base_dir = BASE_DIR
        self._validate_env()

    def _validate_env(self):
        """Validate that all required environment variables are set"""
        required_vars = [
            'ANGEL_API_KEY',
            'ANGEL_CLIENT_ID',
            'ANGEL_USERNAME',
            'ANGEL_PASSWORD',
            'ANGEL_TOTP_SECRET'
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please create a .env file based on .env.example"
            )

    @property
    def api_key(self):
        """Get Angel One API key"""
        return os.getenv('ANGEL_API_KEY')

    @property
    def client_id(self):
        """Get Angel One client ID"""
        return os.getenv('ANGEL_CLIENT_ID')

    @property
    def username(self):
        """Get Angel One username"""
        return os.getenv('ANGEL_USERNAME')

    @property
    def password(self):
        """Get Angel One password"""
        return os.getenv('ANGEL_PASSWORD')

    @property
    def totp_secret(self):
        """Get Angel One TOTP secret"""
        return os.getenv('ANGEL_TOTP_SECRET')

    @property
    def live_flag(self):
        """Get live trading flag"""
        return os.getenv('LIVE_FLAG', 'LIVE_TEST')

    def get_api_credentials(self):
        """Get all API credentials as a dictionary"""
        return {
            'api_key': self.api_key,
            'client_id': self.client_id,
            'username': self.username,
            'password': self.password,
            'totp_secret': self.totp_secret
        }

    # Path helpers using relative paths
    def get_key_path(self):
        """Get keys directory path"""
        return str(self.base_dir / 'keys')

    def get_file_path(self):
        """Get files directory path"""
        return str(self.base_dir / 'files')

    def get_trade_file_path(self):
        """Get trade files directory path"""
        return str(self.base_dir / 'files' / 'trades')

    def get_log_file_path(self):
        """Get log files directory path"""
        return str(self.base_dir / 'files' / 'logs')

    def get_backtest_path(self):
        """Get backtest files directory path"""
        return str(self.base_dir / 'files' / 'backtest')

    def get_db_path(self):
        """Get database path"""
        db_path = os.getenv('DB_PATH', './data/trading.db')
        full_path = self.base_dir / db_path
        # Create data directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        return str(full_path)


# Create a singleton instance
_secure_config = None

def get_secure_config():
    """Get the secure config singleton instance"""
    global _secure_config
    if _secure_config is None:
        _secure_config = SecureConfig()
    return _secure_config


# Backward compatibility functions
def get_api_key():
    """Get API key (backward compatible)"""
    return get_secure_config().api_key

def get_key_path():
    """Get key path (backward compatible)"""
    return get_secure_config().get_key_path()

def get_file_path():
    """Get file path (backward compatible)"""
    return get_secure_config().get_file_path()
