# Quick Start Guide - Improved Trading System

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (1 minute)

```bash
cd /Users/shyamdk/developer/aone/trading/om_ema5
pip install python-dotenv smartapi-python pandas numpy pyotp
```

### Step 2: Setup Credentials (2 minutes)

```bash
# Copy the example file
cp .env.example .env

# Edit with your Angel One credentials
nano .env
```

Fill in your credentials:
```env
ANGEL_API_KEY=your_api_key_here
ANGEL_CLIENT_ID=your_client_id_here
ANGEL_USERNAME=your_username_here
ANGEL_PASSWORD=your_password_here
ANGEL_TOTP_SECRET=your_totp_secret_here

LIVE_FLAG=LIVE_TEST
```

### Step 3: Run the System (2 minutes)

```bash
python main_trading_app.py
```

**That's it! The system is now running.**

---

## 📋 What You'll See

### Console Output

```
================================================================================
TRADING SYSTEM STARTING
Start Time: 2025-10-01 09:15:00
================================================================================
Connecting to broker...
✅ Broker connection established
✅ Loaded 50000 instruments

================================================================================
                        RISK MANAGEMENT DASHBOARD
================================================================================
Time: 2025-10-01 09:15:30
Trading Status: 🟢 ENABLED

Daily P&L:
  🟢 Total: ₹0.00 (0.0% of limit)
  Limit: ₹-10000.00

Positions:
  Current: 0/3

Trade Statistics:
  Total Trades: 0
================================================================================

================================================================================
SCANNING FOR ENTRY SIGNALS
Symbols: 1 | Interval: ONE_MINUTE
================================================================================

--- Processing NIFTY23SEP2525550PE ---

================================================================================
ENTRY ANALYSIS: NIFTY23SEP2525550PE
================================================================================
RSI: 67.50 | RSI_SMA: 62.30 | RSI_SMA_Prev: 61.80
RSI-SMA Gap: 5.20 (Required: >3)
ADX: 18.50 (Required: >14)

Conditions:
  1. RSI>62.3: True
  2. RSI_SMA_Rising: True
  3. Gap>3: True (gap=5.2)
  4. ADX>14: True (adx=18.5)

Result: ✓ ENTRY SIGNAL
Entry Price: ₹125.00
================================================================================
```

---

## ⚙️ Configuration Quick Reference

### Entry Conditions (config.py)

```python
ENTRY_RSI_SMA_GAP_MIN = 3    # Gap between RSI and RSI_SMA
ENTRY_ADX_MIN = 14           # Minimum ADX for trend
```

**Logic:**
- RSI must be above RSI_SMA ✓
- RSI_SMA must be rising ✓
- Gap between RSI and RSI_SMA must be > 3 ✓
- ADX must be > 14 ✓

### Exit Conditions (config.py)

```python
TARGET_PROFIT_PERCENT = 1    # Take profit at 1%
STOP_LOSS = -4               # Stop loss at -4%

# Trailing Stop Loss
TRAILING_STOP_LOSS_ENABLED = True
TRAILING_STOP_LOSS_TRIGGER_PERCENT = 1.5  # Activate at 1.5%
TRAILING_STOP_LOSS_TRAIL_PERCENT = 1.0    # Trail by 1%
```

**Exit Triggers:**
1. RSI falls below RSI_SMA → EXIT
2. Profit reaches 1% → EXIT
3. Loss reaches -4% → EXIT
4. Trailing SL hit → EXIT (if enabled)

### Risk Management (config.py)

```python
POSITION_SIZE = 50000           # ₹50,000 per position
MAX_DAILY_LOSS = -10000         # Max loss: ₹10,000
MAX_POSITION_COUNT = 3          # Max 3 positions
```

---

## 🎯 Trading Example

### Entry Example

```
Entry Conditions Met:
- RSI: 68.5 > RSI_SMA: 63.2 ✓
- RSI_SMA Rising: 63.2 > 62.8 ✓
- Gap: 5.3 > 3 ✓
- ADX: 17.5 > 14 ✓

Action: BUY
Symbol: NIFTY23SEP2525550PE
Price: ₹125.00
Quantity: 75 lots
```

### Exit Example (Trailing SL)

```
Entry: ₹125.00

Price moves to ₹126.90 (+1.52%)
→ Trailing SL ACTIVATES
→ Threshold: 0.52% (1.52% - 1%)

Price moves to ₹129.00 (+3.2%)
→ Peak: 3.2%
→ New Threshold: 2.2% (3.2% - 1%)

Price drops to ₹127.50 (+2.0%)
→ Below threshold of 2.2%
→ TRAILING SL TRIGGERED
→ EXIT at ₹127.50

Profit: ₹2.50 per lot = ₹187.50 (2.0%)
```

---

## 🛡️ Safety Features Active

1. **Circuit Breaker** - Stops trading after 5 consecutive API failures
2. **Daily Loss Limit** - Halts trading if loss > ₹10,000
3. **Position Limit** - Max 3 concurrent positions
4. **Order Confirmation** - Verifies every order execution
5. **Error Retry** - Automatic retry with exponential backoff

---

## 📊 Monitor Your Trading

### Real-time Dashboard

System prints risk dashboard every 60 seconds:

```
Daily P&L: ₹+1,250.00 (12.5% of limit)
Positions: 2/3
Win Rate: 75.0%
```

### Check Database

```bash
# Open database
sqlite3 data/trading.db

# View today's trades
SELECT tradingsymbol, order_price, sell_price, profit_loss
FROM trades
WHERE date(order_date) = date('now');
```

### View Logs

```bash
# Watch live logs
tail -f logs/$(date +%Y-%m-%d)_trading.log

# Watch trade execution
tail -f logs/$(date +%Y-%m-%d)_trades.log

# Watch errors
tail -f logs/$(date +%Y-%m-%d)_errors.log
```

---

## ⚠️ Before Going Live

### Testing Modes

**1. Backtest Mode (Safe)**
```python
# In config.py
LIVE_FLAG = 'BACKTEST'
```
- No real orders placed
- Tests logic only
- Uses historical data

**2. Live Test Mode (Paper Trading)**
```python
# In .env
LIVE_FLAG=LIVE_TEST
```
- Logs orders but doesn't place them
- Full system test
- No real money

**3. Live Mode (Real Trading)**
```python
# In .env
LIVE_FLAG=LIVE
```
- Places real orders
- Uses real money
- **Test thoroughly first!**

---

## 🔧 Common Commands

### Start Trading
```bash
python main_trading_app.py
```

### Stop Trading
```
Ctrl+C (graceful shutdown)
```

### Check System Status
```python
from risk_manager import get_risk_manager
risk_manager = get_risk_manager()
risk_manager.print_risk_summary()
```

### Reset Circuit Breaker
```python
from error_handler import get_circuit_breaker
get_circuit_breaker().reset()
```

### Resume Trading (after halt)
```python
from risk_manager import get_risk_manager
get_risk_manager().resume_trading()
```

---

## 📞 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Missing environment variables" | Check `.env` file exists and has all credentials |
| "Circuit breaker OPEN" | Wait 60 seconds or reset manually |
| "Trading halted" | Check daily P&L and resume if needed |
| "Order failed" | Check logs for details, verify API credentials |
| "Database locked" | Close other database connections |

---

## 🎓 Understanding the Output

### Entry Signal
```
✓ ENTRY SIGNAL
Entry Price: ₹125.00
```
**Means:** All entry conditions met, order will be placed

### Exit Signal
```
EXIT SIGNAL - RSI<RSI_SMA | Profit Target (1.2%>=1%)
```
**Means:** Exit condition triggered, position will be closed

### Risk Block
```
⛔ Entry blocked: Daily loss limit exceeded
```
**Means:** Risk limit reached, entry prevented

---

## 📈 Performance Metrics

System tracks:
- Total trades
- Win rate
- P&L (absolute and percentage)
- Max profit/loss per day
- Average profit per trade

Access via:
```python
from database import get_database
db = get_database()
pnl = db.get_today_pnl()
print(pnl)
```

---

## ✅ First Day Checklist

- [ ] Installed dependencies
- [ ] Created `.env` with credentials
- [ ] Set `LIVE_FLAG=LIVE_TEST`
- [ ] Started system
- [ ] Verified broker connection
- [ ] Checked logs directory created
- [ ] Confirmed database created
- [ ] Watched for entry/exit signals
- [ ] Reviewed P&L tracking

---

## 🎯 Next Steps

1. **Day 1-3:** Run in `LIVE_TEST` mode, monitor behavior
2. **Day 4-7:** Verify all conditions working correctly
3. **Week 2:** Test with small position sizes in `LIVE` mode
4. **Week 3+:** Scale up after confirming system works

---

## 💡 Pro Tips

1. **Always monitor logs** - They tell you exactly what's happening
2. **Check risk dashboard** - Printed every 60 seconds
3. **Test RSI conditions** - Make sure gap and ADX thresholds work for your market
4. **Adjust trailing SL** - Default 1.5%/1% may need tuning
5. **Start small** - Use minimum position sizes initially

---

## 🚨 Emergency Stop

If something goes wrong:

```bash
# Stop the system
Ctrl+C

# Check open positions
python -c "
from order_manager import create_order_manager
from SmartApi import SmartConnect
from secure_config import get_secure_config
from pyotp import TOTP

config = get_secure_config()
creds = config.get_api_credentials()
api = SmartConnect(api_key=creds['api_key'])
api.generateSession(creds['username'], creds['password'], TOTP(creds['totp_secret']).now())
positions = api.position()
print(positions)
"
```

---

**You're now ready to trade! 🎉**

Remember: The system has multiple safety features, but always monitor it, especially in the beginning.

For detailed information, see [README_IMPROVEMENTS.md](README_IMPROVEMENTS.md)
