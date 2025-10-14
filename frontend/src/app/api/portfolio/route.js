import { db } from '../../../lib/firebaseAdmin';

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('user_id');
    
    if (!userId) {
      return Response.json({ 
        error: 'User ID is required',
        message: 'Please provide a valid user_id parameter'
      }, { status: 400 });
    }
    
    console.log('🔥 Fetching portfolio data for user:', userId);
    
    // Get portfolio data from Firebase - single document per user
    const portfolioDoc = await db.collection('portfolio_data').doc(userId).get();
    
    if (!portfolioDoc.exists) {
      return Response.json({ 
        data: [],
        message: 'No portfolio data found',
        user_id: userId 
      });
    }
    
    const portfolioData = portfolioDoc.data();
    
    if (!portfolioData.holdings || !Array.isArray(portfolioData.holdings)) {
      return Response.json({ 
        data: [],
        message: 'No holdings found in portfolio',
        user_id: userId 
      });
    }
    
    // Transform holdings array to match frontend interface
    const transformedHoldings = portfolioData.holdings.map((holding, index) => {
      const shares = holding.shares || holding.quantity || holding.Qty || holding.qty || 0;
      const totalValue = holding.total_value || holding.Total_Value || holding.position_value || 0;
      const currentPrice = shares > 0 ? totalValue / shares : (holding.purchase_price || holding.current_price || holding.Current_Price || holding.price || 0);
      
      // Calculate gain/loss from cost basis and current value
      const costBasis = holding.total_cost || holding.cost_basis || holding.Cost_Basis || totalValue;
      const gainLoss = totalValue - costBasis;
      const gainLossPercent = costBasis > 0 ? (gainLoss / costBasis) * 100 : 0;
      
      return {
        id: `${userId}_${index}`,
        Ticker: holding.symbol || holding.ticker || holding.Ticker,
        Qty: shares,
        Current_Price: currentPrice,
        Total_Value: totalValue,
        Cost_Basis: costBasis,
        Gain_Loss: gainLoss,
        Gain_Loss_Percent: gainLossPercent,
        Category: holding.asset_type || holding.category || holding.Category || 'Stock',
        Asset_Class: holding.asset_class || holding.Asset_Class || 'Equity',
        Sector: holding.sector || holding.Sector || 'Technology',
        Market_Value: totalValue,
        Unrealized_PnL: gainLoss,
        Unrealized_PnL_Percent: gainLossPercent,
        Last_Updated: holding.last_updated || holding.Last_Updated || new Date().toISOString()
      };
    });
    
    console.log('✅ Portfolio data fetched successfully:', transformedHoldings.length, 'items');
    
    return Response.json({ 
      data: transformedHoldings,
      user_id: userId,
      total_items: transformedHoldings.length,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Firebase portfolio error:', error);
    return Response.json({ 
      error: 'Failed to fetch portfolio data',
      details: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
