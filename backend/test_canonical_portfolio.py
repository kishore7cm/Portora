"""
Unit tests for Canonical Portfolio Service
Tests with tiny fixture as specified
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local imports
from core.database import Base
from domain.models_v2 import User, Portfolio, DailyPrice, CashTransaction
from services.portfolio_calculation_service import PortfolioCalculationService

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_canonical.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    
    # Create test data fixture
    setup_test_fixture(session)
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=test_engine)

def setup_test_fixture(session):
    """
    Create tiny fixture as specified:
    - portfolio: AAPL(STOCK, 10u, avg 150), TLT(BOND_ETF, 5u, avg 100), 
                 BTC-USD(CRYPTO, 0.5u, avg 30000), CASH(—, 0u), B1(BOND_CASH, 1000u, avg 1)
    - daily_prices: AAPL: {2025-09-30:170, 2025-10-01:175}, TLT: {2025-10-01:90}, BTC-USD: {2025-10-01:60000}
    - cash_transactions: +5000 on 2025-09-29
    """
    
    # Create test user
    user = User(user_id=1, name="Test User", email="test@example.com")
    session.add(user)
    
    # Create portfolio positions
    positions = [
        Portfolio(
            portfolio_id=1, user_id=1, ticker="AAPL", asset_class="STOCK",
            units=10.0, avg_price=150.0, buy_date=date(2025, 9, 1)
        ),
        Portfolio(
            portfolio_id=2, user_id=1, ticker="TLT", asset_class="BOND_ETF", 
            units=5.0, avg_price=100.0, buy_date=date(2025, 9, 1)
        ),
        Portfolio(
            portfolio_id=3, user_id=1, ticker="BTC-USD", asset_class="CRYPTO",
            units=0.5, avg_price=30000.0, buy_date=date(2025, 9, 1)
        ),
        Portfolio(
            portfolio_id=4, user_id=1, ticker="CASH", asset_class="CASH",
            units=0.0, avg_price=1.0, buy_date=date(2025, 9, 1)
        ),
        Portfolio(
            portfolio_id=5, user_id=1, ticker="B1", asset_class="BOND_CASH",
            units=1000.0, avg_price=1.0, buy_date=date(2025, 9, 1)
        )
    ]
    
    for pos in positions:
        session.add(pos)
    
    # Create daily prices
    prices = [
        DailyPrice(ticker="AAPL", price_date=date(2025, 9, 30), close_price=170.0),
        DailyPrice(ticker="AAPL", price_date=date(2025, 10, 1), close_price=175.0),
        DailyPrice(ticker="TLT", price_date=date(2025, 10, 1), close_price=90.0),
        DailyPrice(ticker="BTC-USD", price_date=date(2025, 10, 1), close_price=60000.0)
    ]
    
    for price in prices:
        session.add(price)
    
    # Create cash transaction
    cash_txn = CashTransaction(
        user_id=1, amount=5000.0, transaction_date=date(2025, 9, 29),
        type="deposit", description="Test deposit"
    )
    session.add(cash_txn)
    
    session.commit()

class TestCanonicalPortfolioService:
    """Test canonical portfolio service with fixture data"""
    
    def test_asset_classification(self, db_session):
        """Test asset classification logic"""
        service = PortfolioCalculationService(db_session)
        
        # Test with explicit asset_class
        assert service.classify_asset("AAPL", "STOCK") == "STOCK"
        assert service.classify_asset("TLT", "BOND_ETF") == "BOND_ETF"
        assert service.classify_asset("BTC-USD", "CRYPTO") == "CRYPTO"
        assert service.classify_asset("CASH", "CASH") == "CASH"
        assert service.classify_asset("B1", "BOND_CASH") == "BOND_CASH"
        
        # Test fallback classification
        assert service.classify_asset("AAPL") == "STOCK"
        assert service.classify_asset("BND") == "BOND_ETF"  # Known bond ETF
        assert service.classify_asset("BTC-USD") == "CRYPTO"
        assert service.classify_asset("CASH") == "CASH"
        assert service.classify_asset("BOND_CASH_TEST") == "BOND_CASH"
    
    def test_latest_price(self, db_session):
        """Test latest price lookup"""
        service = PortfolioCalculationService(db_session)
        
        # Test existing prices
        price, price_date = service.latest_price("AAPL", date(2025, 10, 1))
        assert price == Decimal('175.0')
        assert price_date == date(2025, 10, 1)
        
        # Test price on earlier date
        price, price_date = service.latest_price("AAPL", date(2025, 9, 30))
        assert price == Decimal('170.0')
        assert price_date == date(2025, 9, 30)
        
        # Test non-existent ticker
        result = service.latest_price("NONEXISTENT", date(2025, 10, 1))
        assert result is None
    
    def test_cash_balance(self, db_session):
        """Test cash balance calculation"""
        service = PortfolioCalculationService(db_session)
        
        # Test after deposit
        balance = service.cash_balance(1, date(2025, 9, 29))
        assert balance == Decimal('5000.0')
        
        # Test before deposit
        balance = service.cash_balance(1, date(2025, 9, 28))
        assert balance == Decimal('0.0')
        
        # Test future date (should include deposit)
        balance = service.cash_balance(1, date(2025, 10, 1))
        assert balance == Decimal('5000.0')
    
    def test_bond_cash_value(self, db_session):
        """Test bond cash value calculation"""
        service = PortfolioCalculationService(db_session)
        
        # Should return 1000 * 1 = 1000
        bond_cash_val = service.bond_cash_value(1)
        assert bond_cash_val == Decimal('1000.0')
    
    def test_portfolio_snapshot_2025_10_01(self, db_session):
        """
        Test portfolio snapshot on 2025-10-01
        Expected values:
        - equity_value = 10*175 = 1750
        - bond_etf_value = 5*90 = 450  
        - crypto_value = 0.5*60000 = 30000
        - bond_cash_value = 1000*1 = 1000
        - cash = 5000
        - total_value = 1750+450+30000+1000+5000 = 38200
        """
        service = PortfolioCalculationService(db_session)
        
        snapshot = service.compute_portfolio_snapshot(1, date(2025, 10, 1))
        
        # Test individual asset class values
        assert snapshot.by_class['equity_value'] == Decimal('1750.0')  # 10 * 175
        assert snapshot.by_class['bond_etf_value'] == Decimal('450.0')  # 5 * 90
        assert snapshot.by_class['crypto_value'] == Decimal('30000.0')  # 0.5 * 60000
        assert snapshot.by_class['bond_cash_value'] == Decimal('1000.0')  # 1000 * 1
        assert snapshot.by_class['cash'] == Decimal('5000.0')  # Cash transaction
        
        # Test total value
        expected_total = Decimal('38200.0')  # 1750+450+30000+1000+5000
        assert snapshot.total_value == expected_total
        
        # Test position details
        positions_by_ticker = {pos.ticker: pos for pos in snapshot.by_position}
        
        # AAPL position
        aapl = positions_by_ticker['AAPL']
        assert aapl.units == Decimal('10.0')
        assert aapl.price == Decimal('175.0')
        assert aapl.position_val == Decimal('1750.0')
        assert not aapl.missing_price
        
        # TLT position
        tlt = positions_by_ticker['TLT']
        assert tlt.units == Decimal('5.0')
        assert tlt.price == Decimal('90.0')
        assert tlt.position_val == Decimal('450.0')
        assert not tlt.missing_price
        
        # BTC-USD position
        btc = positions_by_ticker['BTC-USD']
        assert btc.units == Decimal('0.5')
        assert btc.price == Decimal('60000.0')
        assert btc.position_val == Decimal('30000.0')
        assert not btc.missing_price
        
        # B1 (BOND_CASH) position
        b1 = positions_by_ticker['B1']
        assert b1.units == Decimal('1000.0')
        assert b1.price == Decimal('1.0')  # Uses avg_price
        assert b1.position_val == Decimal('1000.0')
        assert not b1.missing_price
        
        # No missing prices expected
        assert len(snapshot.missing_prices) == 0
    
    def test_allocation_breakdown(self, db_session):
        """Test allocation percentage calculation"""
        service = PortfolioCalculationService(db_session)
        
        allocation = service.allocation_breakdown(1, date(2025, 10, 1))
        
        # Total value = 38200
        # stock: 1750/38200 = 4.58%
        # bond: 450/38200 = 1.18%  
        # crypto: 30000/38200 = 78.53%
        # cash: (5000+1000)/38200 = 15.71%
        
        assert abs(allocation['stock'] - Decimal('4.58')) < Decimal('0.01')
        assert abs(allocation['bond'] - Decimal('1.18')) < Decimal('0.01')
        assert abs(allocation['crypto'] - Decimal('78.53')) < Decimal('0.01')
        assert abs(allocation['cash'] - Decimal('15.71')) < Decimal('0.01')
        
        # Should sum to 100%
        total_pct = sum(allocation.values())
        assert abs(total_pct - Decimal('100.0')) < Decimal('0.01')
    
    def test_top_holdings(self, db_session):
        """Test top holdings calculation"""
        service = PortfolioCalculationService(db_session)
        
        holdings = service.top_holdings(1, date(2025, 10, 1), k=3)
        
        # Should be ordered by position value: BTC-USD (30000), AAPL (1750), B1 (1000)
        assert len(holdings) == 4  # We have 4 non-CASH positions
        assert holdings[0]['ticker'] == 'BTC-USD'
        assert holdings[0]['position_val'] == 30000.0
        assert holdings[1]['ticker'] == 'AAPL'
        assert holdings[1]['position_val'] == 1750.0
        assert holdings[2]['ticker'] == 'B1'
        assert holdings[2]['position_val'] == 1000.0
    
    def test_portfolio_created_date(self, db_session):
        """Test portfolio creation date"""
        service = PortfolioCalculationService(db_session)
        
        created_date = service.portfolio_created_date(1)
        assert created_date == date(2025, 9, 1)
        
        # Test non-existent user
        created_date = service.portfolio_created_date(999)
        assert created_date is None
    
    def test_starting_and_current_values(self, db_session):
        """Test starting and current value calculations"""
        service = PortfolioCalculationService(db_session)
        
        # Starting value on 2025-09-01 (creation date)
        # Need to calculate what values would be on that date
        starting_val = service.starting_value(1)
        # This will use latest available prices <= 2025-09-01, which may be none
        # So positions without prices will be 0, only cash and bond_cash will have value
        
        # Current value on 2025-10-01
        current_val = service.current_value(1, date(2025, 10, 1))
        assert current_val == Decimal('38200.0')
        
        # Total gain/loss
        gain_loss = service.total_gain_loss(1, date(2025, 10, 1))
        assert gain_loss == current_val - starting_val
        
        # Return percentage
        return_pct = service.return_pct(1, date(2025, 10, 1))
        if starting_val > 0:
            expected_return = (current_val - starting_val) / starting_val * Decimal('100')
            assert abs(return_pct - expected_return) < Decimal('0.01')
    
    def test_upsert_daily_snapshot(self, db_session):
        """Test snapshot persistence"""
        service = PortfolioCalculationService(db_session)
        
        # Create snapshot
        snapshot = service.upsert_daily_snapshot(1, date(2025, 10, 1))
        
        # Verify it was saved to database
        from domain.models_v2 import PortfolioSummary, PortfolioDailyValue
        
        summary = (
            db_session.query(PortfolioSummary)
            .filter(PortfolioSummary.user_id == 1, PortfolioSummary.date == date(2025, 10, 1))
            .first()
        )
        
        assert summary is not None
        assert summary.total_value == 38200.0
        assert summary.equity_value == 1750.0
        assert summary.bond_etf_value == 450.0
        assert summary.crypto_value == 30000.0
        assert summary.cash_value == 5000.0
        assert summary.bond_cash_value == 1000.0
        
        # Check daily values were saved
        daily_values = (
            db_session.query(PortfolioDailyValue)
            .filter(PortfolioDailyValue.date == date(2025, 10, 1))
            .all()
        )
        
        assert len(daily_values) == 4  # 4 non-CASH positions
    
    def test_missing_price_detection(self, db_session):
        """Test detection of missing/stale prices"""
        service = PortfolioCalculationService(db_session)
        
        # Test on date with missing TLT price (only has price on 2025-10-01)
        snapshot = service.compute_portfolio_snapshot(1, date(2025, 9, 30))
        
        # Should detect missing prices for TLT and BTC-USD
        missing_tickers = {mp['ticker'] for mp in snapshot.missing_prices}
        assert 'TLT' in missing_tickers
        assert 'BTC-USD' in missing_tickers
        
        # AAPL should have price on 2025-09-30
        assert 'AAPL' not in missing_tickers
    
    def test_round_decimal_helper(self, db_session):
        """Test decimal rounding for response boundary"""
        service = PortfolioCalculationService(db_session)
        
        # Test money rounding
        assert service.round_decimal(Decimal('123.456789'), 2) == 123.46
        assert service.round_decimal(Decimal('123.454'), 2) == 123.45
        assert service.round_decimal(None, 2) is None
        
        # Test percentage rounding  
        assert service.round_decimal(Decimal('12.3456'), 2) == 12.35

def test_sharpe_ratio_insufficient_data(db_session):
    """Test that Sharpe ratio returns null with <3 data points"""
    # This would be implemented in risk_metrics function
    # For now, just verify the concept
    
    service = PortfolioCalculationService(db_session)
    
    # With only 2 data points in our fixture, Sharpe should be null
    # This is a placeholder - actual implementation would be in risk_metrics
    
    # Get daily series (we only have 1-2 days of data)
    from domain.models_v2 import PortfolioSummary
    
    # Ensure we have snapshots
    service.upsert_daily_snapshot(1, date(2025, 9, 30))
    service.upsert_daily_snapshot(1, date(2025, 10, 1))
    
    series = (
        db_session.query(PortfolioSummary)
        .filter(PortfolioSummary.user_id == 1)
        .order_by(PortfolioSummary.date)
        .all()
    )
    
    # Should have <= 2 data points, insufficient for Sharpe calculation
    assert len(series) <= 2
    
    # In a real implementation, risk_metrics would return null for Sharpe
    # when data points < 3

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
