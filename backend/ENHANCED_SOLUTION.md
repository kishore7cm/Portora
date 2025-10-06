# Enhanced Portfolio Management System

## 🎯 Complete Asset Type Handling Solution

This enhanced solution provides comprehensive handling for different asset types in a portfolio management system, with proper price updates, cash management, and daily calculations.

## 📊 Asset Type Categories

### 1. **Stocks** 📈
- **Price Source**: Alpaca API
- **Update Frequency**: Daily
- **Calculation**: `units × close_price`
- **Examples**: AAPL, MSFT, GOOGL, TSLA

### 2. **Bond ETFs** 🏦
- **Price Source**: Alpaca API (trade like stocks)
- **Update Frequency**: Daily
- **Calculation**: `units × close_price`
- **Examples**: BND, AGG, TLT, IEF, SHY

### 3. **Crypto** ₿
- **Price Source**: Twelve Data API
- **Update Frequency**: Daily
- **Calculation**: `units × close_price`
- **Examples**: BTC-USD, ETH-USD, ADA-USD

### 4. **Bonds (Non-ETF)** 💰
- **Ticker Format**: `BOND_CASH_{name}`
- **Price Source**: None (constant value)
- **Update Frequency**: Manual user updates only
- **Calculation**: Carry forward from portfolio table
- **Examples**: BOND_CASH_TREASURY_10Y, BOND_CASH_CORPORATE_5Y

### 5. **Cash Positions** 💵
- **Ticker Format**: `CASH_{currency}` or `Cash_{type}`
- **Price Source**: None (constant value)
- **Update Frequency**: Manual user updates only
- **Calculation**: Carry forward from portfolio table
- **Examples**: CASH_USD, Cash_Savings

### 6. **Transaction Cash** 💳
- **Storage**: `cash_transactions` table
- **Update Frequency**: Per transaction
- **Calculation**: Cumulative balance from deposits/withdrawals
- **Carry Forward**: Latest balance if no new transactions

## 🔧 Core Functions

### `update_daily_prices(stock_tickers, bond_etf_tickers, crypto_tickers)`

**Enhanced price updater with asset type handling:**

```python
# Example usage
stock_tickers = ["AAPL", "MSFT", "GOOGL"]
bond_etf_tickers = ["BND", "AGG", "TLT"]
crypto_tickers = ["BTC-USD", "ETH-USD"]

results = update_daily_prices(stock_tickers, bond_etf_tickers, crypto_tickers)
```

**Features:**
- ✅ Separate API handling for stocks/bond ETFs (Alpaca) vs crypto (Twelve Data)
- ✅ Automatic missing date detection and incremental updates
- ✅ Bulk insertion for efficiency
- ✅ Rate limiting and error handling
- ✅ Skips bonds-as-cash and cash positions (no price updates needed)

### `calculate_enhanced_daily_portfolio_job(target_date)`

**Enhanced daily calculator with asset type categorization:**

```python
# Example usage
from datetime import date
result = calculate_enhanced_daily_portfolio_job(date(2025, 10, 2))
```

**Process:**
1. **Categorize** portfolio positions by asset type
2. **Market Assets** (stocks, bond ETFs, crypto): Join with `daily_prices`, calculate `units × close_price`
3. **Bond Cash**: Carry forward value from `portfolio` table (no price lookup)
4. **Cash Positions**: Carry forward value from `portfolio` table
5. **Transaction Cash**: Calculate cumulative balance from `cash_transactions`
6. **Aggregate** all values for `portfolio_summary`

## 🗄️ Database Schema

### Enhanced Tables

```sql
-- Existing tables with enhancements
portfolio (
    portfolio_id, user_id, ticker, units, avg_price, buy_date
)

daily_prices (
    price_id, ticker, price_date, close_price, open_price, high_price, low_price, volume
)

portfolio_daily_value (
    value_id, portfolio_id, date, units, price, position_val
)

portfolio_summary (
    summary_id, user_id, date, total_value, total_cost_basis, 
    total_gain_loss, total_gain_loss_percent, num_positions, cash_balance
)

cash_transactions (
    id, user_id, amount, transaction_date, type, description, created_at
)
```

## 📋 Example Portfolio Calculation

### Sample Portfolio:
```json
{
  "stocks": [
    {"ticker": "AAPL", "units": 10, "avg_price": 175}
  ],
  "bond_etfs": [
    {"ticker": "BND", "units": 20, "avg_price": 80}
  ],
  "crypto": [
    {"ticker": "BTC-USD", "units": 0.5, "avg_price": 50000}
  ],
  "bond_cash": [
    {"ticker": "BOND_CASH_TREASURY_10Y", "units": 1, "avg_price": 10000}
  ],
  "cash_positions": [
    {"ticker": "CASH_USD", "units": 1, "avg_price": 5000}
  ],
  "cash_transactions": [
    {"type": "deposit", "amount": 3000, "date": "2025-09-01"},
    {"type": "withdrawal", "amount": 500, "date": "2025-09-15"}
  ]
}
```

### Daily Calculation (2025-10-02):
```python
# Market prices on 2025-10-02
prices = {
    "AAPL": 180.0,      # +$5 from avg_price
    "BND": 82.0,        # +$2 from avg_price  
    "BTC-USD": 55000.0  # +$5000 from avg_price
}

# Calculations
stock_value = 10 * 180.0 = 1800.0
bond_etf_value = 20 * 82.0 = 1640.0
crypto_value = 0.5 * 55000.0 = 27500.0
bond_cash_value = 1 * 10000.0 = 10000.0  # Constant
cash_position_value = 1 * 5000.0 = 5000.0  # Constant
transaction_cash = 3000.0 - 500.0 = 2500.0  # From transactions

total_value = 1800 + 1640 + 27500 + 10000 + 5000 + 2500 = 48440.0
```

## 🚀 API Endpoints

### Enhanced Portfolio Endpoint

**GET** `/portfolio/{user_id}/{date}`

**Response Format:**
```json
{
  "user_id": 101,
  "date": "2025-10-02",
  "total_value": 48440.0,
  "cash": 2500.0,
  "positions": [
    {"ticker": "AAPL", "units": 10, "price": 180.0, "position_val": 1800.0},
    {"ticker": "BND", "units": 20, "price": 82.0, "position_val": 1640.0},
    {"ticker": "BTC-USD", "units": 0.5, "price": 55000.0, "position_val": 27500.0},
    {"ticker": "BOND_CASH_TREASURY_10Y", "units": 1, "price": 10000.0, "position_val": 10000.0},
    {"ticker": "CASH_USD", "units": 1, "price": 5000.0, "position_val": 5000.0}
  ]
}
```

### Cash Transaction Endpoints

- **POST** `/cash-transactions/` - Add deposit/withdrawal
- **GET** `/cash-transactions/{user_id}` - List user transactions
- **GET** `/cash-balance/{user_id}/{date}` - Get cash balance

## 🔄 Scheduled Job Usage

### Daily Price Updates
```bash
# Auto-categorize and update all portfolio tickers
python services/enhanced_price_updater.py --auto

# Manual ticker specification
python services/enhanced_price_updater.py \
  --stocks AAPL MSFT GOOGL \
  --bond-etfs BND AGG TLT \
  --crypto BTC-USD ETH-USD
```

### Daily Portfolio Calculations
```bash
# Calculate for today
python jobs/enhanced_daily_calculator.py

# Calculate for specific date
python jobs/enhanced_daily_calculator.py --date 2025-10-02

# Backfill date range
python jobs/enhanced_daily_calculator.py \
  --backfill --start-date 2025-09-01 --end-date 2025-10-02
```

### Add Bond Cash Position
```bash
# Add a $10,000 Treasury bond as cash
python jobs/enhanced_daily_calculator.py \
  --add-bond 1 "Treasury_10Y" 10000
```

## 🎯 Key Benefits

### 1. **Proper Asset Categorization**
- Automatic detection of asset types
- Appropriate price source selection
- Correct handling of non-market assets

### 2. **Efficient Price Updates**
- Incremental updates (only missing dates)
- Bulk insertion for performance
- API rate limiting compliance

### 3. **Accurate Cash Handling**
- Separate transaction cash vs position cash
- Proper carry-forward logic
- Historical balance tracking

### 4. **Scalable Architecture**
- Clean separation of concerns
- Extensible asset type system
- Production-ready error handling

### 5. **Complete Audit Trail**
- All transactions recorded
- Historical price data preserved
- Daily portfolio snapshots

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_enhanced_system.py
```

This tests:
- ✅ All asset type handling
- ✅ Price updates and categorization
- ✅ Cash transaction management
- ✅ Daily portfolio calculations
- ✅ API endpoint responses
- ✅ Bond cash position creation

## 📈 Production Deployment

### 1. **Environment Variables**
```bash
export ALPACA_API_KEY="your_alpaca_key"
export ALPACA_SECRET_KEY="your_alpaca_secret"
export TWELVE_DATA_API_KEY="your_twelve_data_key"
```

### 2. **Cron Jobs**
```bash
# Daily price updates at 6 PM EST (after markets close)
0 18 * * 1-5 cd /path/to/backend && python services/enhanced_price_updater.py --auto

# Daily portfolio calculations at 7 PM EST
0 19 * * 1-5 cd /path/to/backend && python jobs/enhanced_daily_calculator.py
```

### 3. **API Deployment**
```bash
# Start the enhanced API server
uvicorn api_normalized:app --host 0.0.0.0 --port 8002 --workers 4
```

## 🎉 Summary

This enhanced solution provides:

- ✅ **Complete asset type handling** (stocks, bond ETFs, crypto, bonds-as-cash, cash)
- ✅ **Intelligent price updates** with proper API source selection
- ✅ **Accurate cash management** with transaction tracking
- ✅ **Efficient daily calculations** with asset categorization
- ✅ **Production-ready architecture** with error handling and logging
- ✅ **Comprehensive testing** and documentation

The system is ready for production use with proper handling of all portfolio asset types and cash management requirements.
