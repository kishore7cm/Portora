# EaseLi - Portfolio Management Dashboard

A modern, real-time portfolio management dashboard built with Next.js and FastAPI.

## 🚀 Features

- **Real-time Portfolio Tracking**: Live portfolio value and performance monitoring
- **Top Holdings & Movers**: Track your best performing assets
- **Performance Charts**: Interactive charts for 1W, 1M, 1Y, and YTD periods
- **Portfolio Health**: Comprehensive health metrics and risk analysis
- **S&P 500 Analysis**: Market comparison and benchmarking
- **Responsive Design**: Works on desktop and mobile devices

## 📁 Project Structure

```
EaseLi/
├── frontend/                 # Next.js React application
│   ├── src/
│   │   ├── app/             # App router pages
│   │   │   ├── dashboard/   # Main dashboard page
│   │   │   └── page.tsx     # Landing page
│   │   ├── components/      # React components
│   │   └── lib/            # Utilities and config
│   └── package.json
├── backend/                 # FastAPI Python backend
│   ├── api.py              # Main API endpoints
│   ├── models.py           # Database models
│   ├── database.py         # Database connection
│   └── seed_data.py        # Initial data setup
├── config/                 # Configuration files
│   └── api_keys.py         # API keys and settings
├── Portfolio CSV files/     # User portfolio data
└── requirements.txt        # Python dependencies
```

## 🛠️ Setup & Installation

### Prerequisites
- Node.js 18+ 
- Python 3.12+
- SQLite (included with Python)

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
cd backend
python api.py
```

### Frontend Setup
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

## 🌐 Usage

1. **Start Backend**: `cd backend && python api.py` (runs on http://localhost:8000)
2. **Start Frontend**: `cd frontend && npm run dev` (runs on http://localhost:3000)
3. **Open Dashboard**: Navigate to http://localhost:3000/dashboard

## 📊 Data Sources

- **Portfolio Data**: Imported from CSV files in `Portfolio CSV files/`
- **Historical Prices**: Fetched from Alpaca API
- **Market Data**: Real-time S&P 500 data

## 🔧 Configuration

Update API keys in `config/api_keys.py`:
```python
ALPACA_API_KEY = "your_alpaca_key"
ALPACA_SECRET_KEY = "your_alpaca_secret"
```

## 📈 Features Overview

### Dashboard Tabs
- **Overview**: Portfolio summary, net worth, allocation
- **Performance**: Interactive performance charts
- **S&P 500**: Market analysis and comparison
- **Portfolio Health**: Risk metrics and health scores

### Key Metrics
- Real-time portfolio valuation
- Performance tracking (1W, 1M, 1Y, YTD)
- Top 3 holdings and movers
- Diversification and risk analysis
- Cash flow and allocation tracking

## 🚀 Deployment

The application is ready for deployment on platforms like:
- Vercel (frontend)
- Railway/Render (backend)
- Docker (full stack)

## 📝 License

Private project - All rights reserved.
