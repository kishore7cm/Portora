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
    
    // Get portfolio data from Firebase
    let portfolioSnapshot = await db
      .collection('portfolio_data')
      .where('user_id', '==', userId)
      .get();
    
    if (portfolioSnapshot.empty) {
      return Response.json({ 
        data: [],
        message: 'No portfolio data found',
        user_id: userId 
      });
    }
    
    // Transform Firebase data to match your frontend interface
    const portfolioData = portfolioSnapshot.docs.map(doc => {
      const data = doc.data();
      
      // Calculate current price from total_value and shares if not provided
      const shares = data.shares || data.quantity || data.Qty || data.qty || 0;
      const totalValue = data.total_value || data.Total_Value || data.position_value || 0;
      const currentPrice = shares > 0 ? totalValue / shares : (data.purchase_price || data.current_price || data.Current_Price || data.price || 0);
      
      // Calculate gain/loss from cost basis and current value
      const costBasis = data.total_cost || data.cost_basis || data.Cost_Basis || totalValue;
      const gainLoss = totalValue - costBasis;
      const gainLossPercent = costBasis > 0 ? (gainLoss / costBasis) * 100 : 0;
      
      return {
        id: doc.id,
        Ticker: data.symbol || data.ticker || data.Ticker,
        Qty: shares,
        Current_Price: currentPrice,
        Total_Value: totalValue,
        Cost_Basis: costBasis,
        Gain_Loss: gainLoss,
        Gain_Loss_Percent: gainLossPercent,
        Category: data.asset_type || data.category || data.Category || 'Stock',
        Asset_Class: data.asset_class || data.Asset_Class || 'Equity',
        Sector: data.sector || data.Sector || 'Technology',
        Market_Value: totalValue,
        Unrealized_PnL: gainLoss,
        Unrealized_PnL_Percent: gainLossPercent,
        Last_Updated: data.last_updated || data.Last_Updated || new Date().toISOString()
      };
    });
    
    console.log('✅ Portfolio data fetched successfully:', portfolioData.length, 'items');
    
    return Response.json({ 
      data: portfolioData,
      user_id: userId,
      total_items: portfolioData.length,
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
