import { db } from '../../../lib/firebaseAdmin';

export async function POST(request) {
  try {
    const { userId, holdings } = await request.json();
    
    if (!userId || !holdings || !Array.isArray(holdings)) {
      return Response.json({ 
        error: 'Invalid data',
        message: 'Please provide userId and holdings array'
      }, { status: 400 });
    }
    
    console.log(`🔄 Migrating portfolio for user: ${userId}`);
    console.log(`📊 Holdings count: ${holdings.length}`);
    
    // Transform holdings to match the new structure
    const transformedHoldings = holdings.map(holding => ({
      symbol: holding.symbol,
      ticker: holding.symbol,
      asset_type: holding.asset_type,
      category: holding.asset_type,
      sector: holding.asset_type,
      brokerage: holding.account_name,
      shares: holding.shares,
      purchase_price: holding.purchase_price,
      current_price: holding.purchase_price, // Assuming current = purchase for now
      total_cost: holding.total_cost,
      total_value: holding.total_value,
      gain_loss: holding.total_value - holding.total_cost,
      gain_loss_percent: holding.total_cost > 0 ? 
        ((holding.total_value - holding.total_cost) / holding.total_cost) * 100 : 0,
      last_updated: new Date()
    }));
    
    // Calculate total portfolio value
    const totalPortfolioValue = transformedHoldings.reduce((sum, holding) => 
      sum + holding.total_value, 0
    );
    
    // Create single document for user
    await db.collection('portfolio_data').doc(userId).set({
      user_id: userId,
      holdings: transformedHoldings,
      totalPortfolioValue: totalPortfolioValue,
      lastUpdated: new Date()
    });
    
    console.log(`✅ Portfolio migrated successfully for user: ${userId}`);
    console.log(`💰 Total portfolio value: $${totalPortfolioValue.toFixed(2)}`);
    
    return Response.json({ 
      success: true,
      message: 'Portfolio migrated successfully',
      user_id: userId,
      total_holdings: transformedHoldings.length,
      total_portfolio_value: totalPortfolioValue,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Migration error:', error);
    return Response.json({ 
      error: 'Failed to migrate portfolio',
      details: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
