# 📊 EaseLi Portfolio Advisor

A comprehensive portfolio management and investment advisory platform that combines real-time market data, AI-powered analysis, and social benchmarking features.

## 🚀 Features

### Portfolio Management
- **Real-time Portfolio Tracking**: Live market data for 80+ stocks/crypto
- **Asset Allocation**: Visual pie charts showing equity, bonds, crypto, cash distribution
- **Performance Metrics**: Net worth, gains/losses, annualized returns
- **Historical Data**: 6-month performance tracking with monthly snapshots
- **Portfolio Health Score**: AI-powered analysis with drift detection

### S&P 500 Analysis
- **Market Overview**: Real-time S&P 500 data with sector breakdown
- **Technical Indicators**: RSI, MACD, Bollinger Bands analysis
- **Heatmap Visualization**: Sector performance with color-coded returns
- **Top Gainers/Losers**: Daily market movers
- **Sector Analysis**: Detailed breakdown by industry

### Community Benchmarking
- **Social Comparison**: Compare performance with 15,420+ community members
- **Strategy Discovery**: Popular investment approaches (DCA, Value, Growth, etc.)
- **Risk Profiling**: Conservative, Moderate, Aggressive user distribution
- **Market Trends**: Most bought/sold stocks in the community
- **Performance Benchmarks**: Median returns, volatility, Sharpe ratios

### Advanced Features
- **Bot Management**: AI trading bots with different strategies
- **Alerts System**: Real-time notifications for portfolio changes
- **Onboarding**: Guided setup for new users
- **Dark Mode**: Complete theme switching capability
- **Drag-and-Drop Dashboard**: Customizable widget layout
- **Loading States**: Skeleton loaders for better UX

## 🏗️ Tech Stack

### Frontend
- **Framework**: Next.js 15.5.2 with React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **State Management**: React Context + Hooks

### Backend
- **Framework**: FastAPI with Python 3.12
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT tokens with bcrypt
- **APIs**: Alpaca Markets (stocks), Twelve Data (crypto)

## 📁 Project Structure

```
EaseLi/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App router pages
│   │   ├── components/      # React components
│   │   └── contexts/        # React contexts
│   ├── public/              # Static assets
│   └── package.json
├── backend/                 # FastAPI application
│   └── api.py              # Main API file
├── analysis/               # Analysis modules
├── data/                   # Data management
├── config/                 # Configuration files
├── news/                   # News sentiment analysis
├── portfolio/              # Portfolio data
└── requirements.txt        # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/EaseLi.git
cd EaseLi
```

2. **Setup Backend**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
```

3. **Setup Frontend**
```bash
cd frontend
npm install
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Demo Login
- Email: `demo@easeli.com`
- Password: `password123`

## 🔧 Configuration

### Environment Variables

Create `.env` files in both frontend and backend directories:

**Backend (.env)**
```env
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
TWELVE_DATA_API_KEY=your_twelve_data_key
DATABASE_URL=sqlite:///./enhanced_users.db
JWT_SECRET_KEY=your_jwt_secret
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 API Endpoints

### Core APIs
- `GET /portfolio` - Portfolio data with real-time values
- `GET /sp500` - S&P 500 market data
- `GET /portfolio-health` - AI-powered portfolio analysis
- `GET /community/comparison` - Social benchmarking data
- `GET /alerts` - User notifications
- `GET /bots` - Trading bot management

### Authentication
- `POST /auth/login` - User authentication
- `POST /auth/logout` - Session termination
- `GET /onboarding/status` - Onboarding progress

## 🗄️ Database Schema

### Core Tables
- **Users**: Authentication and user preferences
- **Portfolios**: User portfolio holdings
- **Holdings**: Individual stock/crypto positions
- **Bots**: AI trading bot configurations
- **Alerts**: Notification system
- **Historical Data**: Market data snapshots

## 🎨 UI Components

### Key Components
- **Dashboard**: Main application interface
- **Portfolio Summary**: Net worth and performance metrics
- **S&P 500 Analysis**: Market overview and sector breakdown
- **Community Benchmark**: Social comparison features
- **Theme System**: Dark/light mode toggle
- **Loading States**: Skeleton loaders for better UX

## 🔒 Security

- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Secure token-based authentication
- **Input Validation**: Sanitized user inputs
- **CORS**: Configured for frontend domain
- **Rate Limiting**: API abuse prevention

## 📈 Performance

- **Frontend**: Code splitting, lazy loading, memoization
- **Backend**: Async operations, database indexing
- **API**: Response compression, pagination, caching
- **Real-time Updates**: Sub-second data refresh

## 🧪 Testing

### Frontend Testing
- Unit tests with Jest
- Integration tests
- E2E tests with Playwright
- Visual regression testing

### Backend Testing
- Unit tests with pytest
- API tests with FastAPI TestClient
- Database operation testing
- Integration tests

## 🚀 Deployment

### Development
- Frontend: Next.js dev server (port 3000)
- Backend: FastAPI with uvicorn (port 8000)
- Database: SQLite

### Production
- Frontend: Vercel/Netlify deployment
- Backend: Docker containerization
- Database: PostgreSQL with connection pooling
- CDN: CloudFront for static assets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Alpaca Markets for real-time stock data
- Twelve Data for cryptocurrency data
- Recharts for data visualization
- Next.js and FastAPI communities

## 📞 Support

For support, email support@easeli.com or create an issue in this repository.

---

**Built with ❤️ by the EaseLi Team**
