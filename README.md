# OM 1M Trading System

Professional algorithmic trading system for Indian options markets with advanced risk management and trailing stop loss.

## ⚠️ Disclaimer

**This is a personal trading system. Use at your own risk.**

- This software is provided "as is" without warranty of any kind
- Trading involves substantial risk of loss
- Past performance is not indicative of future results
- Always test thoroughly before live trading
- Start with paper trading and small positions

## 🎯 Features

### Trading Strategy
- **Entry Logic**: Multi-condition RSI + ADX based strategy
  - RSI above moving average
  - Rising RSI SMA
  - Minimum RSI-SMA gap
  - Trend strength confirmation via ADX

- **Exit Logic**: Smart exit with multiple triggers
  - RSI reversal detection
  - Fixed profit targets
  - Stop loss protection
  - **Trailing Stop Loss** that locks in profits

### Risk Management
- Daily loss limits with automatic halt
- Maximum position count enforcement
- Position size validation
- Duplicate position prevention
- Real-time risk dashboard

### Infrastructure
- SQLite database for trade tracking
- Professional logging framework
- Error handling with retry logic
- Order confirmation system
- Circuit breaker protection

## 📋 Prerequisites

- Python 3.8+
- Angel One trading account
- API credentials from Angel One

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/shyamdk/om_1m.git
cd om_1m
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your credentials
nano .env
```

**Required in `.env`:**
```env
ANGEL_API_KEY=your_api_key
ANGEL_CLIENT_ID=your_client_id
ANGEL_USERNAME=your_username
ANGEL_PASSWORD=your_password
ANGEL_TOTP_SECRET=your_totp_secret

LIVE_FLAG=LIVE_TEST
```

### 4. Run the System

```bash
python main_trading_app.py
```

## 📖 Documentation

- **[START_HERE.md](START_HERE.md)** - Quick navigation guide
- **[QUICK_START.md](QUICK_START.md)** - 5-minute setup guide
- **[README_IMPROVEMENTS.md](README_IMPROVEMENTS.md)** - Complete documentation
- **[SYSTEM_FLOW.md](SYSTEM_FLOW.md)** - Visual flow diagrams
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical details

## ⚙️ Configuration

Edit `config.py` to adjust:

**Entry Strategy:**
```python
ENTRY_RSI_SMA_GAP_MIN = 3  # Minimum RSI-SMA gap
ENTRY_ADX_MIN = 14         # Minimum ADX value
```

**Exit Strategy:**
```python
TARGET_PROFIT_PERCENT = 1  # Fixed profit target
STOP_LOSS = -4             # Fixed stop loss

# Trailing Stop Loss
TRAILING_STOP_LOSS_ENABLED = True
TRAILING_STOP_LOSS_TRIGGER_PERCENT = 1.5
TRAILING_STOP_LOSS_TRAIL_PERCENT = 1.0
```

**Risk Management:**
```python
POSITION_SIZE = 50000       # Position size in ₹
MAX_DAILY_LOSS = -10000     # Max daily loss
MAX_POSITION_COUNT = 3      # Max concurrent positions
```

## 🛡️ Safety Features

- **Environment Variables**: Credentials never in code
- **Daily Loss Limit**: Auto-halt when limit reached
- **Circuit Breaker**: Stops after repeated API failures
- **Order Confirmation**: Verifies every trade execution
- **Position Verification**: Checks against broker
- **Comprehensive Logging**: Full audit trail

## 🧪 Testing Modes

### Backtest Mode (Safest)
```python
LIVE_FLAG = 'BACKTEST'
```
No real orders, logic testing only

### Live Test Mode (Paper Trading)
```python
LIVE_FLAG = 'LIVE_TEST'
```
Simulated orders, full system test

### Live Mode (Real Trading)
```python
LIVE_FLAG = 'LIVE'
```
Real money - use after thorough testing!

## 📊 How It Works

### Entry Process
1. Fetch candle data with technical indicators
2. Check RSI > RSI_SMA conditions
3. Validate trend strength (ADX)
4. Run risk management checks
5. Place order if all conditions pass
6. Confirm order execution

### Exit Process
1. Monitor all open positions
2. Calculate current P&L and max profit
3. Check exit conditions:
   - RSI reversal
   - Profit target reached
   - Stop loss hit
   - Trailing SL triggered
4. Place sell order
5. Update P&L tracking

### Trailing Stop Loss
```
Entry: ₹100
→ Price reaches ₹101.50 (+1.5%): TSL activates
→ Price peaks at ₹105 (+5%): Exit threshold = 4%
→ Price drops to ₹103 (+3%): Still above 4% ✓
→ Price drops to ₹102 (+2%): Below 4% → EXIT
→ Profit locked: +2%
```

## 📁 Project Structure

```
om_1m/
├── main_trading_app.py      # Main application
├── entry_logic.py            # Entry strategy
├── exit_logic.py             # Exit + Trailing SL
├── risk_manager.py           # Risk management
├── order_manager.py          # Order handling
├── database.py               # SQLite database
├── error_handler.py          # Error handling
├── logger_config.py          # Logging system
├── technical_functions.py    # Technical indicators
├── config.py                 # Configuration
├── secure_config.py          # Credential management
├── utils.py                  # Utilities
└── requirements.txt          # Dependencies
```

## 🔒 Security

**NEVER commit sensitive data:**
- `.env` file (credentials)
- `keys/` directory
- `data/` directory (database)
- `logs/` directory
- Trade CSV files

All sensitive files are protected by `.gitignore`

## 📝 Logging

Logs are stored in `logs/` directory:
- `YYYY-MM-DD_trading.log` - All activity
- `YYYY-MM-DD_errors.log` - Errors only
- `YYYY-MM-DD_trades.log` - Trade execution

View live logs:
```bash
tail -f logs/$(date +%Y-%m-%d)_trading.log
```

## 💾 Database

Trade data stored in SQLite:
- Location: `data/trading.db`
- Tables: trades, daily_pnl, system_metrics
- Query: `sqlite3 data/trading.db`

Export trades:
```python
from database import get_database
db = get_database()
db.export_to_csv('trades.csv', start_date='2025-01-01')
```

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing environment variables | Check `.env` file exists |
| Circuit breaker OPEN | Wait 60s or reset manually |
| Trading halted | Check P&L, resume if OK |
| Order failed | Check logs for details |

## 📈 Performance Monitoring

The system provides:
- Real-time P&L tracking
- Win/loss statistics
- Risk metrics dashboard
- Daily performance summaries

## 🔄 Updates

To update dependencies:
```bash
pip install -r requirements.txt --upgrade
```

## 🤝 Contributing

This is a personal project. Feel free to fork for your own use.

## 📄 License

MIT License - See LICENSE file for details

## ⚠️ Risk Warning

**Trading Risks:**
- Options trading is highly speculative
- You can lose more than your initial investment
- Market conditions can change rapidly
- Past performance does not guarantee future results

**System Risks:**
- Software bugs may occur
- API failures can happen
- Internet connectivity issues
- Exchange downtime

**Always:**
- Test thoroughly in paper trading mode
- Start with minimum position sizes
- Monitor the system actively
- Have stop losses in place
- Only risk capital you can afford to lose

## 📞 Support

For issues:
1. Check the documentation in `docs/`
2. Review logs in `logs/`
3. Check database for trade status
4. Verify environment variables

## 🎓 Learn More

- **Angel One API**: [Official Documentation](https://smartapi.angelbroking.com/)
- **Technical Analysis**: Study RSI, ADX, and moving averages
- **Risk Management**: Understanding position sizing and stop losses
- **Python Trading**: Learn pandas, numpy for data analysis

---

**Built with:** Python, pandas, numpy, SmartAPI

**Author:** Shyam DK

**Last Updated:** 2025-10-01

---

⭐ If you find this useful, please star the repository!

**Remember: Trade responsibly and never risk more than you can afford to lose.**
