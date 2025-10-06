"""Add cash transactions table

Revision ID: 002_add_cash_transactions
Revises: 001_create_normalized_tables
Create Date: 2025-10-02 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_cash_transactions'
down_revision: Union[str, None] = '001_create_normalized_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add cash_transactions table and update portfolio_summary"""
    
    # Create cash_transactions table
    op.create_table('cash_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cash_transactions_id'), 'cash_transactions', ['id'], unique=False)
    op.create_index(op.f('ix_cash_transactions_user_id'), 'cash_transactions', ['user_id'], unique=False)
    op.create_index(op.f('ix_cash_transactions_transaction_date'), 'cash_transactions', ['transaction_date'], unique=False)
    op.create_index('idx_cash_user_date', 'cash_transactions', ['user_id', 'transaction_date'], unique=False)
    op.create_index('idx_cash_date', 'cash_transactions', ['transaction_date'], unique=False)
    
    # Add cash_balance column to portfolio_summary
    op.add_column('portfolio_summary', sa.Column('cash_balance', sa.Float(), nullable=True, default=0.0))


def downgrade() -> None:
    """Remove cash transactions table and cash_balance column"""
    
    # Remove cash_balance column from portfolio_summary
    op.drop_column('portfolio_summary', 'cash_balance')
    
    # Drop cash_transactions table
    op.drop_table('cash_transactions')
