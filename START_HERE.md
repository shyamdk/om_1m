# 👋 START HERE - Trading System Guide

## Welcome!

Your trading system has been completely upgraded and is ready to use. This guide will help you get started quickly.

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies (2 minutes)

```bash
pip install python-dotenv smartapi-python pandas numpy pyotp
```

### 2. Setup Credentials (2 minutes)

```bash
# Copy the template
cp .env.example .env

# Edit with your credentials
nano .env
```

Add your Angel One credentials:
```env
ANGEL_API_KEY=your_api_key_here
ANGEL_CLIENT_ID=your_client_id_here
ANGEL_USERNAME=your_username_here
ANGEL_PASSWORD=your_password_here
ANGEL_TOTP_SECRET=your_totp_secret_here

LIVE_FLAG=LIVE_TEST
```

### 3. Run the System (1 minute)

```bash
python main_trading_app.py
```

**Done! The system is running.** 🎉

---

## 📚 Documentation Map

Choose what you need:

### For First-Time Users
👉 **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes

### For Complete Understanding
👉 **[README_IMPROVEMENTS.md](README_IMPROVEMENTS.md)** - Full documentation with examples

### For Visual Learners
👉 **[SYSTEM_FLOW.md](SYSTEM_FLOW.md)** - Diagrams showing how everything works

### For Technical Details
👉 **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was built and how

### For Code Organization
👉 **[CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)** - How files were organized

### For Complete Overview
👉 **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Everything in one place

---

## 🎯 What You Have

### Trading Features
✅ **Entry Logic** - RSI > RSI_SMA, rising SMA, gap > 3, ADX > 14
✅ **Exit Logic** - RSI < RSI_SMA, fixed profit (1%), stop loss (-4%)
✅ **Trailing Stop Loss** - Activates at 1.5%, trails by 1%
✅ **Risk Management** - Daily loss limits, position limits
✅ **Order Confirmation** - Automatic verification
✅ **Error Handling** - Retry with exponential backoff

### Infrastructure
✅ **Database** - SQLite with thread safety
✅ **Logging** - Professional framework with multiple log files
✅ **Security** - Environment variables for credentials
✅ **Monitoring** - Real-time risk dashboard

### Code Quality
✅ **Clean Code** - 61 old files archived, no dead code
✅ **Professional** - Production-ready architecture
✅ **Documented** - 6 comprehensive guides
✅ **Tested** - Multiple safety checks

---

## 📖 Reading Order

### Beginners
1. This file (you're reading it!)
2. [QUICK_START.md](QUICK_START.md)
3. [SYSTEM_FLOW.md](SYSTEM_FLOW.md)
4. [README_IMPROVEMENTS.md](README_IMPROVEMENTS.md)

### Advanced Users
1. [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
2. [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)
3. [FINAL_SUMMARY.md](FINAL_SUMMARY.md)

### Everyone
👉 Start with [QUICK_START.md](QUICK_START.md) - it's really quick!

---

## 🗂️ Project Structure

```
om_ema5/
├── 📄 START_HERE.md             ⬅️ You are here!
│
├── 📚 Documentation/
│   ├── QUICK_START.md           → 5-minute setup guide
│   ├── README_IMPROVEMENTS.md   → Complete reference
│   ├── SYSTEM_FLOW.md           → Visual diagrams
│   ├── IMPLEMENTATION_SUMMARY.md → Technical details
│   ├── CLEANUP_SUMMARY.md       → Code organization
│   └── FINAL_SUMMARY.md         → Complete overview
│
├── 🎯 Core Application/
│   ├── main_trading_app.py      → Main application
│   ├── entry_logic.py           → Entry conditions
│   ├── exit_logic.py            → Exit + Trailing SL
│   ├── risk_manager.py          → Risk management
│   ├── order_manager.py         → Order handling
│   ├── database.py              → SQLite database
│   ├── error_handler.py         → Error handling
│   └── logger_config.py         → Logging system
│
├── ⚙️ Configuration/
│   ├── .env.example             → Template (copy to .env)
│   ├── .env                     → Your credentials (create this!)
│   ├── config.py                → System configuration
│   ├── secure_config.py         → Credential management
│   └── requirements.txt         → Python dependencies
│
└── 📁 Directories/
    ├── data/                    → Database (auto-created)
    ├── logs/                    → Log files (auto-created)
    └── old_files_after_ai/      → Archived files (61 files)
```

---

## ⚡ Quick Commands

### Start Trading
```bash
python main_trading_app.py
```

### View Logs
```bash
# Live trading log
tail -f logs/$(date +%Y-%m-%d)_trading.log

# Errors only
tail -f logs/$(date +%Y-%m-%d)_errors.log

# Trades only
tail -f logs/$(date +%Y-%m-%d)_trades.log
```

### Check Database
```bash
sqlite3 data/trading.db "SELECT * FROM trades WHERE date(order_date) = date('now');"
```

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

---

## 🎯 What's New

### From Old System
- ❌ CSV files → ✅ SQLite database
- ❌ Plaintext credentials → ✅ Environment variables
- ❌ Basic entry logic → ✅ Multi-condition RSI+ADX
- ❌ Simple exit → ✅ RSI + Fixed targets + Trailing SL
- ❌ No risk management → ✅ Automated limits
- ❌ Print statements → ✅ Professional logging
- ❌ 37 files → ✅ 20 clean files

### Major Improvements
✨ **Trailing Stop Loss** - Locks in profits automatically
✨ **Risk Management** - Daily loss limits, position limits
✨ **Order Confirmation** - Verifies every trade
✨ **Error Handling** - Automatic retry & circuit breakers
✨ **Professional Logging** - Track everything
✨ **Clean Code** - Production-ready quality

---

## 🛡️ Safety First

### Testing Modes

**1. BACKTEST** (Safest - No real orders)
```python
LIVE_FLAG = 'BACKTEST'
```
Use this first to test logic.

**2. LIVE_TEST** (Safe - Paper trading)
```python
LIVE_FLAG = 'LIVE_TEST'
```
Use this to test the full system.

**3. LIVE** (Real money!)
```python
LIVE_FLAG = 'LIVE'
```
Only use after thorough testing!

### Safety Features
- 🛡️ Daily loss limit (₹10,000 default)
- 🛡️ Position limit (3 max)
- 🛡️ Circuit breaker (halts after failures)
- 🛡️ Order confirmation (10s timeout)
- 🛡️ Position verification

---

## 📊 Entry & Exit Logic

### Entry (ALL conditions must be TRUE)
```
✓ RSI > RSI_SMA (e.g., 68 > 63)
✓ RSI_SMA rising (e.g., 63 > 62)
✓ Gap > 3 (e.g., 5 > 3)
✓ ADX > 14 (e.g., 18 > 14)
```

### Exit (ANY trigger exits)
```
1. RSI < RSI_SMA → EXIT
2. Profit >= 1% → EXIT
3. Loss <= -4% → EXIT
4. Trailing SL hit → EXIT
```

### Trailing Stop Loss
```
Entry: ₹100
→ At ₹101.50 (+1.5%): TSL activates
→ At ₹105 (+5%): Threshold = 4%
→ Drops to ₹103 (+3%): Exit (below 4%)
→ Profit locked: +3%
```

---

## ❓ Common Questions

### Q: Where are my trades stored?
**A:** In `data/trading.db` SQLite database. Old CSV files are in `files/`.

### Q: How do I see my P&L?
**A:** Check the risk dashboard (printed every 60 seconds) or query the database.

### Q: What if trading is halted?
**A:** Check daily P&L. Resume manually if OK:
```python
from risk_manager import get_risk_manager
get_risk_manager().resume_trading()
```

### Q: How do I adjust the entry/exit conditions?
**A:** Edit `config.py`:
```python
ENTRY_RSI_SMA_GAP_MIN = 3  # Gap threshold
ENTRY_ADX_MIN = 14         # Trend strength
TARGET_PROFIT_PERCENT = 1  # Profit target
STOP_LOSS = -4             # Stop loss
```

### Q: Can I backtest first?
**A:** Yes! Set `LIVE_FLAG = 'BACKTEST'` in `.env`

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Missing environment variables" | Create `.env` file from `.env.example` |
| "Circuit breaker OPEN" | Wait 60 seconds or reset manually |
| "Trading halted" | Check P&L, resume if within limits |
| "Order failed" | Check logs for details |
| "Database locked" | Close other DB connections |

---

## 📞 Next Steps

1. **Read** [QUICK_START.md](QUICK_START.md) (5 minutes)
2. **Setup** your `.env` file (2 minutes)
3. **Run** in BACKTEST mode (test)
4. **Monitor** logs and P&L (observe)
5. **Test** in LIVE_TEST mode (paper trading)
6. **Go Live** with small positions (real money)

---

## 🎓 Learn More

### Understanding the System
- **Entry Logic:** See `entry_logic.py`
- **Exit Logic:** See `exit_logic.py`
- **Trailing SL:** See `TrailingStopLoss` class in `exit_logic.py`
- **Risk Checks:** See `risk_manager.py`

### Customization
- **Parameters:** Edit `config.py`
- **Credentials:** Edit `.env`
- **Symbols:** Edit `INSTRUMENTS_*` in `config.py`

### Monitoring
- **Logs:** `logs/` directory
- **Database:** `data/trading.db`
- **Console:** Real-time output

---

## ✅ Checklist Before Going Live

- [ ] Read QUICK_START.md
- [ ] Created `.env` with credentials
- [ ] Installed dependencies
- [ ] Tested in BACKTEST mode
- [ ] Tested in LIVE_TEST mode
- [ ] Reviewed entry/exit logic
- [ ] Checked risk limits in config.py
- [ ] Understand trailing stop loss
- [ ] Know how to monitor logs
- [ ] Ready to start small

---

## 🎉 You're Ready!

Everything is set up and ready to go. Start with:

👉 **[QUICK_START.md](QUICK_START.md)**

Then explore the other documentation as needed.

**Happy Trading! 🚀📈**

---

*Last Updated: 2025-10-01*
*Status: Complete and Ready*
*Next Action: Read QUICK_START.md*
