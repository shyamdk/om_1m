# Trading System Improvements - Implementation Guide

## Overview

This document details all improvements made to the trading system to make it production-ready with robust error handling, security, and risk management.

## 🎯 What Was Improved

### 1. **Security Enhancements**
- ✅ Moved API credentials to environment variables (.env file)
- ✅ Created `.gitignore` to prevent committing secrets
- ✅ Implemented secure configuration module (`secure_config.py`)

### 2. **Entry Logic** (`entry_logic.py`)
Updated entry conditions as requested:
- ✅ RSI > RSI_SMA (RSI above its moving average)
- ✅ RSI_SMA > RSI_SMA_MINUS_ONE (RSI_SMA is rising)
- ✅ RSI_SMA_GAP > 3 (minimum gap of 3 points)
- ✅ ADX > 14 (sufficient trend strength)

### 3. **Exit Logic** (`exit_logic.py`)
Implemented comprehensive exit conditions:
- ✅ RSI < RSI_SMA (primary exit signal)
- ✅ Fixed profit target (1% by default)
- ✅ Fixed stop loss (-4% by default)
- ✅ **Trailing Stop Loss**:
  - Activates at 1.5% profit
  - Trails by 1% from peak
  - Automatically adjusts as profit increases

### 4. **Database** (`database.py`)
- ✅ Replaced CSV files with SQLite database
- ✅ Thread-safe operations with connection pooling
- ✅ Automatic daily P&L tracking
- ✅ Trade history with full audit trail
- ✅ Support for trailing stop loss tracking

### 5. **Error Handling** (`error_handler.py`)
- ✅ Retry decorator with exponential backoff
- ✅ Safe API wrapper for all broker calls
- ✅ Circuit breaker pattern to prevent cascading failures
- ✅ Detailed error logging with context

### 6. **Risk Management** (`risk_manager.py`)
- ✅ Daily loss limit enforcement
- ✅ Maximum position count limits
- ✅ Position size validation
- ✅ Automatic trading halt on limit breach
- ✅ Real-time risk dashboard

### 7. **Order Management** (`order_manager.py`)
- ✅ Order confirmation after placement
- ✅ Position verification against broker
- ✅ Trade book reconciliation
- ✅ Execution price tracking

### 8. **Logging** (`logger_config.py`)
- ✅ Structured logging with multiple levels
- ✅ Separate log files for errors and trades
- ✅ Colored console output
- ✅ Rotating log files to prevent disk fill
- ✅ Trade-specific logging

### 9. **Main Application** (`main_trading_app.py`)
- ✅ Integrated all improvements
- ✅ Clean architecture with separation of concerns
- ✅ Proper error handling at all levels
- ✅ Graceful shutdown handling

### 10. **Relative Paths** (`secure_config.py`)
- ✅ All paths now relative to project root
- ✅ Automatic directory creation
- ✅ Cross-platform compatibility

---

## 📦 Installation

### Step 1: Install Dependencies

```bash
cd /Users/shyamdk/developer/aone/trading/om_ema5

# Install required packages
pip install -r requirements.txt
```

### Step 2: Setup Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Your `.env` file should look like this:**
```env
ANGEL_API_KEY=your_actual_api_key
ANGEL_CLIENT_ID=your_actual_client_id
ANGEL_USERNAME=your_actual_username
ANGEL_PASSWORD=your_actual_password
ANGEL_TOTP_SECRET=your_actual_totp_secret

LIVE_FLAG=LIVE_TEST
```

⚠️ **NEVER commit the `.env` file to git!**

### Step 3: Initialize Database

The database will be automatically created on first run at:
`/Users/shyamdk/developer/aone/trading/om_ema5/data/trading.db`

---

## 🚀 Usage

### Running the Improved System

```bash
python main_trading_app.py
```

### Configuration

Edit [config.py](config.py) to adjust:

**Entry Strategy:**
```python
ENTRY_RSI_SMA_GAP_MIN = 3  # Minimum gap between RSI and RSI_SMA
ENTRY_ADX_MIN = 14         # Minimum ADX for entry
```

**Exit Strategy:**
```python
TARGET_PROFIT_PERCENT = 1        # Fixed profit target (1%)
STOP_LOSS = -4                   # Fixed stop loss (-4%)

TRAILING_STOP_LOSS_ENABLED = True
TRAILING_STOP_LOSS_TRIGGER_PERCENT = 1.5  # Activate at 1.5% profit
TRAILING_STOP_LOSS_TRAIL_PERCENT = 1.0    # Trail by 1% from peak
```

**Risk Management:**
```python
POSITION_SIZE = 50000         # Position size in ₹
MAX_DAILY_LOSS = -10000       # Maximum daily loss (₹)
MAX_POSITION_COUNT = 3        # Maximum concurrent positions
```

---

## 🔄 Migration from Old System

### Option 1: Fresh Start (Recommended)
1. Backup your existing system
2. Use the new modules directly
3. Start with clean database

### Option 2: Gradual Migration
You can use individual modules with your existing code:

```python
# In your existing code, add:
from entry_logic import check_entry_conditions_v2
from exit_logic import check_exit_conditions_v2
from risk_manager import get_risk_manager
from database import get_database

# Then use them in your logic
```

---

## 📊 Understanding the New Logic

### Entry Logic Flow

```
1. Fetch candle data with technical indicators
   ↓
2. Check entry conditions:
   - RSI > RSI_SMA? ✓
   - RSI_SMA rising? ✓
   - RSI-SMA gap > 3? ✓
   - ADX > 14? ✓
   ↓
3. Check risk management:
   - Within daily loss limit? ✓
   - Below max positions? ✓
   - No existing position for symbol? ✓
   - Position size valid? ✓
   ↓
4. Place order and confirm
   ↓
5. Save to database
```

### Exit Logic Flow

```
1. Monitor open positions
   ↓
2. Fetch current candle data
   ↓
3. Check exit conditions:
   - RSI < RSI_SMA? → EXIT
   - Profit >= 1%? → EXIT
   - Loss <= -4%? → EXIT
   - Trailing SL hit? → EXIT
   ↓
4. Place sell order
   ↓
5. Update database with P&L
   ↓
6. Update daily P&L metrics
```

### Trailing Stop Loss Example

```
Entry: ₹100
Trailing SL activates at: ₹101.50 (1.5% profit)

Price moves to ₹103:
- Peak profit: 3%
- Trailing threshold: 3% - 1% = 2%
- Will exit if profit drops below 2% (price below ₹102)

Price moves to ₹105:
- Peak profit: 5%
- Trailing threshold: 5% - 1% = 4%
- Will exit if profit drops below 4% (price below ₹104)
```

---

## 📁 New File Structure

```
om_ema5/
├── main_trading_app.py          # New main application
├── secure_config.py             # Secure configuration
├── database.py                  # SQLite database
├── entry_logic.py               # Entry conditions
├── exit_logic.py                # Exit conditions + TSL
├── risk_manager.py              # Risk management
├── order_manager.py             # Order handling
├── error_handler.py             # Error handling
├── logger_config.py             # Logging framework
├── .env                         # Your credentials (DO NOT COMMIT)
├── .env.example                 # Example env file
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── data/
│   └── trading.db              # SQLite database (auto-created)
└── logs/
    ├── YYYY-MM-DD_trading.log  # Main logs
    ├── YYYY-MM-DD_errors.log   # Error logs
    └── YYYY-MM-DD_trades.log   # Trade logs
```

---

## 🛡️ Safety Features

### 1. Daily Loss Limit
```python
# System automatically halts trading if loss exceeds limit
if daily_loss <= MAX_DAILY_LOSS:
    halt_trading("Daily loss limit exceeded")
```

### 2. Position Limits
```python
# Prevents opening too many positions
if open_positions >= MAX_POSITION_COUNT:
    reject_trade("Maximum positions reached")
```

### 3. Circuit Breaker
```python
# Stops API calls after repeated failures
if failure_count >= 5:
    open_circuit("Too many API failures")
```

### 4. Order Confirmation
```python
# Verifies order execution before proceeding
confirmation = confirm_order_placement(order_id, max_wait=10)
if not confirmation['confirmed']:
    handle_failed_order()
```

---

## 🔍 Monitoring & Debugging

### View Logs

```bash
# Main log
tail -f logs/$(date +%Y-%m-%d)_trading.log

# Errors only
tail -f logs/$(date +%Y-%m-%d)_errors.log

# Trades only
tail -f logs/$(date +%Y-%m-%d)_trades.log
```

### Query Database

```bash
sqlite3 data/trading.db

# View today's trades
SELECT * FROM trades WHERE date(order_date) = date('now');

# View daily P&L
SELECT * FROM daily_pnl ORDER BY trade_date DESC LIMIT 10;

# View open positions
SELECT * FROM trades WHERE shyam_status = 'buy_complete';
```

### Export to CSV

```python
from database import get_database

db = get_database()
db.export_to_csv('trades_export.csv', start_date='2025-01-01')
```

---

## 🧪 Testing

### Backtest Mode (Safe)
```python
# In config.py
LIVE_FLAG = 'BACKTEST'
```

### Live Test Mode (Paper Trading)
```python
# In config.py or .env
LIVE_FLAG = 'LIVE_TEST'
```

### Live Mode (Real Money)
```python
# In .env
LIVE_FLAG = 'LIVE'
```

⚠️ **Always test thoroughly in BACKTEST mode first!**

---

## ❗ Important Notes

1. **Trailing Stop Loss**
   - Only activates after profit reaches trigger level (1.5%)
   - Trails by configured percentage (1%) from peak
   - Cannot be disabled once activated for a trade

2. **Daily Loss Limit**
   - System automatically halts trading when limit is hit
   - Manual resume required: `risk_manager.resume_trading()`
   - Resets at market open next day

3. **Database vs CSV**
   - Old CSV files will not be automatically migrated
   - New system uses SQLite exclusively
   - Can export database to CSV for compatibility

4. **API Rate Limits**
   - Automatic retry with exponential backoff
   - Circuit breaker prevents excessive calls
   - 1-second delay between symbols

5. **Security**
   - `.env` file is in `.gitignore`
   - Never commit credentials to git
   - Use environment variables in production

---

## 🆘 Troubleshooting

### Issue: "Missing required environment variables"
**Solution:** Copy `.env.example` to `.env` and fill in your credentials

### Issue: "Circuit breaker is OPEN"
**Solution:** Wait 60 seconds or manually reset:
```python
from error_handler import get_circuit_breaker
get_circuit_breaker().reset()
```

### Issue: "Trading halted - daily loss limit"
**Solution:** Check P&L and manually resume if needed:
```python
from risk_manager import get_risk_manager
get_risk_manager().resume_trading()
```

### Issue: "Database locked"
**Solution:** Close all other connections to the database

---

## 📞 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review error messages in console output
3. Check database for trade status
4. Verify environment variables are set correctly

---

## ✅ Checklist Before Going Live

- [ ] Environment variables configured in `.env`
- [ ] Tested in BACKTEST mode
- [ ] Tested in LIVE_TEST mode
- [ ] Risk limits configured appropriately
- [ ] Daily loss limit set
- [ ] Position size configured
- [ ] Trailing stop loss parameters verified
- [ ] Logs directory writable
- [ ] Database directory writable
- [ ] API credentials verified
- [ ] Backup of original system created

---

## 📈 Next Steps

After successful testing:
1. Monitor system for a few days in LIVE_TEST mode
2. Verify all trades are logged correctly
3. Check risk management triggers work as expected
4. Review P&L calculations
5. Gradually transition to LIVE mode with small position sizes

---

**Happy Trading! 🚀**

Remember: Always test thoroughly and never risk more than you can afford to lose.
