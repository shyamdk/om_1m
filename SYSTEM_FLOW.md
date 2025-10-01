# Trading System Flow Diagram

## 🎯 Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     MAIN TRADING APPLICATION                     │
│                    (main_trading_app.py)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │      INITIALIZATION PHASE             │
        ├──────────────────────────────────────┤
        │ 1. Load secure configuration (.env)  │
        │ 2. Connect to broker API             │
        │ 3. Initialize database               │
        │ 4. Setup risk manager                │
        │ 5. Create order manager              │
        │ 6. Setup logging                     │
        └──────────────┬───────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │         TRADING LOOP (60s)            │
        │  Runs from 9:15 AM to 3:30 PM         │
        └──────────────┬───────────────────────┘
                       │
                       ├─────────────────────────────────┐
                       │                                 │
                       ▼                                 ▼
        ┌──────────────────────┐            ┌──────────────────────┐
        │  ENTRY PROCESSING    │            │  EXIT PROCESSING     │
        │  (Every iteration)   │            │  (Every iteration)   │
        └──────────────────────┘            └──────────────────────┘
```

---

## 📥 Entry Processing Flow

```
START
  │
  ▼
┌─────────────────────────────────────┐
│ For each symbol in watchlist:       │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 1. RISK CHECK                       │
│    ├─ Daily loss limit OK?          │
│    ├─ Below max positions?          │
│    ├─ No existing position?         │
│    └─ Position size valid?          │
└───────────────┬─────────────────────┘
                │
                ├─ ❌ Failed ──→ Skip symbol
                │
                ▼ ✅ Passed
┌─────────────────────────────────────┐
│ 2. FETCH CANDLE DATA                │
│    ├─ Get historical candles         │
│    ├─ Calculate RSI                  │
│    ├─ Calculate RSI_SMA              │
│    ├─ Calculate ADX                  │
│    ├─ Calculate EMA3, EMA5           │
│    └─ Calculate CCI                  │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 3. CHECK ENTRY CONDITIONS            │
│    ┌─────────────────────────────┐  │
│    │ RSI > RSI_SMA?              │  │
│    │ RSI_SMA rising?             │  │
│    │ RSI-SMA gap > 3?            │  │
│    │ ADX > 14?                   │  │
│    └─────────────────────────────┘  │
└───────────────┬─────────────────────┘
                │
                ├─ ❌ No Signal ──→ Continue to next symbol
                │
                ▼ ✅ Entry Signal
┌─────────────────────────────────────┐
│ 4. CALCULATE ENTRY PRICE             │
│    If close < EMA3: Use close        │
│    Else: Use EMA3                    │
│    Round to 5 paise                  │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 5. PLACE ORDER                       │
│    ├─ Create order parameters        │
│    ├─ Place LIMIT order              │
│    ├─ Get order ID                   │
│    └─ Wait for confirmation (10s)    │
└───────────────┬─────────────────────┘
                │
                ├─ ❌ Failed ──→ Log error
                │
                ▼ ✅ Success
┌─────────────────────────────────────┐
│ 6. SAVE TO DATABASE                  │
│    ├─ Insert trade record            │
│    ├─ Set status: 'ordered'          │
│    └─ Log trade entry                │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 7. LOG TRADE                         │
│    ├─ Trade logger                   │
│    ├─ Console output                 │
│    └─ File logs                      │
└─────────────────────────────────────┘
                │
                ▼
            CONTINUE TO NEXT SYMBOL
```

---

## 📤 Exit Processing Flow

```
START
  │
  ▼
┌─────────────────────────────────────┐
│ Get all open positions from DB       │
│ (shyam_status = 'buy_complete')      │
└───────────────┬─────────────────────┘
                │
                ├─ No positions? ──→ END
                │
                ▼ Has positions
┌─────────────────────────────────────┐
│ For each open position:              │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 1. FETCH CURRENT DATA                │
│    ├─ Get latest candles             │
│    ├─ Calculate indicators           │
│    └─ Get current price              │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 2. CALCULATE CURRENT P&L             │
│    Current PnL% = (close - entry)    │
│                   / entry * 100      │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 3. UPDATE TRAILING STOP LOSS         │
│    ┌─────────────────────────────┐  │
│    │ If PnL% > 1.5%:             │  │
│    │   TSL Active = True         │  │
│    │   Update max_profit_seen    │  │
│    │   Threshold = max - 1%      │  │
│    └─────────────────────────────┘  │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 4. CHECK EXIT CONDITIONS             │
│    ┌─────────────────────────────┐  │
│    │ Condition 1: RSI < RSI_SMA  │  │
│    │ Condition 2: PnL >= +1%     │  │
│    │ Condition 3: PnL <= -4%     │  │
│    │ Condition 4: TSL triggered  │  │
│    └─────────────────────────────┘  │
└───────────────┬─────────────────────┘
                │
                ├─ ❌ No Exit ──→ Update max_profit → Continue
                │
                ▼ ✅ Exit Signal
┌─────────────────────────────────────┐
│ 5. CALCULATE EXIT PRICE              │
│    If close > EMA3: Use close        │
│    Else: Use EMA3                    │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 6. PLACE SELL ORDER                  │
│    ├─ Create sell parameters         │
│    ├─ Place MARKET order             │
│    ├─ Get order ID                   │
│    └─ Wait for confirmation          │
└───────────────┬─────────────────────┘
                │
                ├─ ❌ Failed ──→ Log error
                │
                ▼ ✅ Success
┌─────────────────────────────────────┐
│ 7. UPDATE DATABASE                   │
│    ├─ Update sell details            │
│    ├─ Calculate P&L                  │
│    ├─ Update daily_pnl               │
│    └─ Set status: 'sell_complete'    │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 8. LOG TRADE EXIT                    │
│    ├─ P&L amount                     │
│    ├─ P&L percentage                 │
│    ├─ Exit reason                    │
│    └─ Trade duration                 │
└─────────────────────────────────────┘
                │
                ▼
            CONTINUE TO NEXT POSITION
```

---

## 🎯 Entry Condition Logic

```
┌─────────────────────────────────────────────────┐
│           ENTRY CONDITION CHECK                  │
└─────────────────────────────────────────────────┘

    RSI vs RSI_SMA
    ─────────────
         RSI
          │
      70 ─┤        ●  ← RSI = 68
          │       ╱
      65 ─┤    ●─╯     RSI_SMA rising
          │   ╱
      60 ─┤  ● ← RSI_SMA = 63
          │
          └────────────────→ Time

    ✓ RSI > RSI_SMA (68 > 63)
    ✓ RSI_SMA rising (63 > 62)
    ✓ Gap = 5 (> 3 required)

    ADX
    ───
      30 ─┤
          │
      20 ─┤     ╱●  ← ADX = 18
          │   ╱
      10 ─┤ ╱
          │╱
       0 ─┴────────────────→ Time

    ✓ ADX > 14 (18 > 14)

    RESULT: ENTRY SIGNAL ✓
```

---

## 📊 Exit Condition Logic

```
┌─────────────────────────────────────────────────┐
│            EXIT CONDITION CHECK                  │
└─────────────────────────────────────────────────┘

    Price Movement with TSL
    ──────────────────────

    ₹105 ─┤                ●  Peak (5% profit)
          │               ╱ ╲
    ₹104 ─┤ TSL Threshold╱   ╲  ← 4% (peak - 1%)
          │ (moves up)  ╱     ╲
    ₹103 ─┤            ╱       ╲
          │           ╱         ╲
    ₹102 ─┤      ╱───●          ●  ← Exit here (2%)
          │     ╱  (3%)          │
    ₹101.50─┤─●─────────────────┴─ TSL activates
          │╱ Entry              Exit triggered
    ₹100 ─●─────────────────────────→ Time

    Timeline:
    1. Entry at ₹100
    2. Price → ₹101.50 (+1.5%): TSL activates
    3. Price → ₹103 (+3%): Peak = 3%, Threshold = 2%
    4. Price → ₹105 (+5%): Peak = 5%, Threshold = 4%
    5. Price drops to ₹102 (+2%): Below 4% threshold
    6. EXIT TRIGGERED by Trailing SL

    Exit Conditions Checked:
    □ RSI < RSI_SMA? No
    □ Profit >= 1%? Yes (2%)
    □ Loss <= -4%? No
    ☑ TSL Hit? YES

    RESULT: EXIT SIGNAL (Trailing SL) ✓
```

---

## 🛡️ Risk Management Flow

```
┌─────────────────────────────────────────────────┐
│          RISK MANAGEMENT CHECKS                  │
└─────────────────────────────────────────────────┘

ENTRY REQUEST
    │
    ▼
┌─────────────────────────────────────┐
│ 1. Daily Loss Check                 │
│    Current P&L: ₹-5,000             │
│    Limit: ₹-10,000                  │
│    Status: ✓ OK (within limit)      │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 2. Position Count Check             │
│    Open positions: 2                │
│    Max allowed: 3                   │
│    Status: ✓ OK (can open more)     │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 3. Existing Position Check          │
│    Symbol: NIFTY25000CE             │
│    Has open position? No            │
│    Status: ✓ OK (can open)          │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 4. Position Size Check              │
│    Proposed: ₹52,000                │
│    Range: ₹25,000 - ₹75,000         │
│    Status: ✓ OK (within range)      │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│        ALL CHECKS PASSED             │
│     ✓ ALLOW ENTRY                    │
└─────────────────────────────────────┘


SCENARIO: Daily Loss Limit Breach
─────────────────────────────────

Current P&L: ₹-10,500
    │
    ▼
┌─────────────────────────────────────┐
│ 🚨 DAILY LOSS LIMIT EXCEEDED        │
│    Current: ₹-10,500                │
│    Limit: ₹-10,000                  │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ ACTION: HALT TRADING                │
│    ├─ Set trading_enabled = False   │
│    ├─ Log halt reason                │
│    ├─ Block all new entries          │
│    └─ Allow exits only              │
└─────────────────────────────────────┘
```

---

## 🔄 Error Handling Flow

```
┌─────────────────────────────────────────────────┐
│            ERROR HANDLING FLOW                   │
└─────────────────────────────────────────────────┘

API CALL
    │
    ▼
┌─────────────────────────────────────┐
│ Attempt 1                           │
└───────────────┬─────────────────────┘
                │
                ├─ ✓ Success ──→ Return result
                │
                ▼ ✗ Failed
┌─────────────────────────────────────┐
│ Log error                           │
│ Wait 2 seconds                      │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ Attempt 2                           │
└───────────────┬─────────────────────┘
                │
                ├─ ✓ Success ──→ Return result
                │
                ▼ ✗ Failed
┌─────────────────────────────────────┐
│ Log error                           │
│ Wait 4 seconds (2 * 2)              │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ Attempt 3 (Final)                   │
└───────────────┬─────────────────────┘
                │
                ├─ ✓ Success ──→ Return result
                │
                ▼ ✗ Failed
┌─────────────────────────────────────┐
│ 🚨 ALL RETRIES FAILED               │
│    ├─ Log detailed error             │
│    ├─ Increment circuit breaker     │
│    └─ Raise exception                │
└─────────────────────────────────────┘


CIRCUIT BREAKER
───────────────

Failure count: 0
    │
    ▼ API call fails
Failure count: 1 ──→ Continue
    │
    ▼ API call fails
Failure count: 2 ──→ Continue
    │
    ▼ API call fails
Failure count: 5 ──→ OPEN CIRCUIT
    │
    ▼
┌─────────────────────────────────────┐
│ 🔴 CIRCUIT BREAKER OPEN             │
│    Block all API calls for 60s      │
└─────────────────────────────────────┘
    │
    │ Wait 60 seconds
    ▼
┌─────────────────────────────────────┐
│ 🟡 CIRCUIT BREAKER HALF-OPEN        │
│    Try one API call                 │
└───────────────┬─────────────────────┘
                │
                ├─ ✓ Success ──→ 🟢 CLOSE CIRCUIT
                │
                ▼ ✗ Failed
┌─────────────────────────────────────┐
│ 🔴 CIRCUIT BREAKER OPEN AGAIN       │
└─────────────────────────────────────┘
```

---

## 📝 Data Flow

```
┌─────────────────────────────────────────────────┐
│             DATA FLOW DIAGRAM                    │
└─────────────────────────────────────────────────┘

.env file
    │
    ▼
┌─────────────┐
│ Credentials │──→ secure_config.py
└─────────────┘          │
                         ▼
                ┌─────────────────┐
                │ SmartAPI        │
                │ Connection      │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Broker API      │
                └────────┬────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│Candle Data  │  │Order Status │  │ Positions   │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       ▼                ▼                ▼
┌──────────────────────────────────────────────┐
│        Technical Indicators Module            │
│  (RSI, ADX, EMA, SMA, CCI)                   │
└───────────────────┬──────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│Entry Logic  │ │Exit Logic   │ │Risk Manager │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Order Manager   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Database        │
              │ (SQLite)        │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Trade Log   │ │ Daily P&L   │ │  Metrics    │
└─────────────┘ └─────────────┘ └─────────────┘
```

---

## 🔔 System States

```
┌─────────────────────────────────────────────────┐
│           SYSTEM STATE DIAGRAM                   │
└─────────────────────────────────────────────────┘

         ┌──────────────┐
         │ INITIALIZED  │
         └──────┬───────┘
                │
                ▼
         ┌──────────────┐
         │   RUNNING    │──────┐
         └──────┬───────┘      │
                │              │
    ┌───────────┼───────────┐  │
    │           │           │  │
    ▼           ▼           ▼  │
┌─────────┐ ┌─────────┐ ┌──────────┐
│ SCANNING│ │ENTERING │ │ EXITING  │
│ SIGNALS │ │ TRADES  │ │  TRADES  │
└─────────┘ └─────────┘ └──────────┘
    │           │           │
    └───────────┼───────────┘
                │
                ▼
         ┌──────────────┐
         │   WAITING    │
         │   (60s)      │
         └──────┬───────┘
                │
                ▼
         Loop back to RUNNING


HALT STATE FLOW
───────────────

         ┌──────────────┐
         │   RUNNING    │
         └──────┬───────┘
                │
                ▼ Risk limit breached
         ┌──────────────┐
         │    HALTED    │
         └──────┬───────┘
                │
                │ Manual resume
                │ or Next day
                ▼
         ┌──────────────┐
         │   RUNNING    │
         └──────────────┘
```

---

This visual guide shows how all components work together!
