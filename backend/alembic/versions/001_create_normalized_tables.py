"""Create normalized portfolio tables

Revision ID: 001_create_normalized_tables
Revises: 
Create Date: 2025-10-02 07:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_create_normalized_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create normalized portfolio tables"""
    
    # Create users table
    op.create_table('users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create portfolio table
    op.create_table('portfolio',
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('units', sa.Float(), nullable=False),
        sa.Column('avg_price', sa.Float(), nullable=False),
        sa.Column('buy_date', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('portfolio_id')
    )
    op.create_index(op.f('ix_portfolio_portfolio_id'), 'portfolio', ['portfolio_id'], unique=False)
    op.create_index(op.f('ix_portfolio_user_id'), 'portfolio', ['user_id'], unique=False)
    op.create_index(op.f('ix_portfolio_ticker'), 'portfolio', ['ticker'], unique=False)
    op.create_index('idx_portfolio_user_ticker', 'portfolio', ['user_id', 'ticker'], unique=False)
    op.create_index('idx_portfolio_ticker_date', 'portfolio', ['ticker', 'buy_date'], unique=False)
    
    # Create daily_prices table
    op.create_table('daily_prices',
        sa.Column('price_id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('price_date', sa.Date(), nullable=False),
        sa.Column('close_price', sa.Float(), nullable=False),
        sa.Column('open_price', sa.Float(), nullable=True),
        sa.Column('high_price', sa.Float(), nullable=True),
        sa.Column('low_price', sa.Float(), nullable=True),
        sa.Column('volume', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('price_id')
    )
    op.create_index(op.f('ix_daily_prices_price_id'), 'daily_prices', ['price_id'], unique=False)
    op.create_index(op.f('ix_daily_prices_ticker'), 'daily_prices', ['ticker'], unique=False)
    op.create_index(op.f('ix_daily_prices_price_date'), 'daily_prices', ['price_date'], unique=False)
    op.create_index('idx_daily_prices_ticker_date', 'daily_prices', ['ticker', 'price_date'], unique=True)
    op.create_index('idx_daily_prices_date', 'daily_prices', ['price_date'], unique=False)
    
    # Create portfolio_daily_value table
    op.create_table('portfolio_daily_value',
        sa.Column('value_id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('units', sa.Float(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('position_val', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolio.portfolio_id'], ),
        sa.PrimaryKeyConstraint('value_id')
    )
    op.create_index(op.f('ix_portfolio_daily_value_value_id'), 'portfolio_daily_value', ['value_id'], unique=False)
    op.create_index(op.f('ix_portfolio_daily_value_portfolio_id'), 'portfolio_daily_value', ['portfolio_id'], unique=False)
    op.create_index(op.f('ix_portfolio_daily_value_date'), 'portfolio_daily_value', ['date'], unique=False)
    op.create_index('idx_portfolio_daily_portfolio_date', 'portfolio_daily_value', ['portfolio_id', 'date'], unique=True)
    op.create_index('idx_portfolio_daily_date', 'portfolio_daily_value', ['date'], unique=False)
    
    # Create portfolio_summary table
    op.create_table('portfolio_summary',
        sa.Column('summary_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_value', sa.Float(), nullable=False),
        sa.Column('total_cost_basis', sa.Float(), nullable=True),
        sa.Column('total_gain_loss', sa.Float(), nullable=True),
        sa.Column('total_gain_loss_percent', sa.Float(), nullable=True),
        sa.Column('num_positions', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('summary_id')
    )
    op.create_index(op.f('ix_portfolio_summary_summary_id'), 'portfolio_summary', ['summary_id'], unique=False)
    op.create_index(op.f('ix_portfolio_summary_user_id'), 'portfolio_summary', ['user_id'], unique=False)
    op.create_index(op.f('ix_portfolio_summary_date'), 'portfolio_summary', ['date'], unique=False)
    op.create_index('idx_portfolio_summary_user_date', 'portfolio_summary', ['user_id', 'date'], unique=True)
    op.create_index('idx_portfolio_summary_date', 'portfolio_summary', ['date'], unique=False)
    
    # Create asset_categories table
    op.create_table('asset_categories',
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('category_id')
    )
    op.create_index(op.f('ix_asset_categories_category_id'), 'asset_categories', ['category_id'], unique=False)
    op.create_index(op.f('ix_asset_categories_ticker'), 'asset_categories', ['ticker'], unique=True)
    
    # Create portfolio_transactions table
    op.create_table('portfolio_transactions',
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('transaction_type', sa.String(length=10), nullable=False),
        sa.Column('units', sa.Float(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('transaction_id')
    )
    op.create_index(op.f('ix_portfolio_transactions_transaction_id'), 'portfolio_transactions', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_portfolio_transactions_user_id'), 'portfolio_transactions', ['user_id'], unique=False)
    op.create_index(op.f('ix_portfolio_transactions_ticker'), 'portfolio_transactions', ['ticker'], unique=False)
    op.create_index(op.f('ix_portfolio_transactions_transaction_date'), 'portfolio_transactions', ['transaction_date'], unique=False)
    op.create_index('idx_transactions_user_date', 'portfolio_transactions', ['user_id', 'transaction_date'], unique=False)
    op.create_index('idx_transactions_ticker_date', 'portfolio_transactions', ['ticker', 'transaction_date'], unique=False)


def downgrade() -> None:
    """Drop all normalized portfolio tables"""
    
    # Drop tables in reverse order to handle foreign key constraints
    op.drop_table('portfolio_transactions')
    op.drop_table('asset_categories')
    op.drop_table('portfolio_summary')
    op.drop_table('portfolio_daily_value')
    op.drop_table('daily_prices')
    op.drop_table('portfolio')
    op.drop_table('users')
