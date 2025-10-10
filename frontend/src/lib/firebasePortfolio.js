import { db } from './firebaseAdmin';

export async function getPortfolioData(userId = '1') {
  try {
    console.log('🔥 Fetching portfolio data directly from Firebase for user:', userId);
    
    // First, try to get the actual uid from users collection if userId is '1'
    if (userId === '1') {
      try {
        const usersSnapshot = await db.collection('users').limit(1).get();
        if (!usersSnapshot.empty) {
          const userData = usersSnapshot.docs[0].data();
          if (userData.uid) {
            userId = userData.uid;
            console.log('🔄 Using actual uid from users collection:', userId);
          }
        }
      } catch (error) {
        console.log('⚠️ Could not fetch uid from users, using default:', userId);
      }
    }
    
    // Get portfolio data from Firebase
    const portfolioSnapshot = await db
      .collection('portfolio_data')
      .where('user_id', '==', userId)
      .get();
    
    if (portfolioSnapshot.empty) {
      return { 
        data: [],
        message: 'No portfolio data found',
        user_id: userId 
      };
    }
    
    // Transform Firebase data to match your frontend interface
    const portfolioData = portfolioSnapshot.docs.map(doc => {
      const data = doc.data();
      return {
        id: doc.id,
        Ticker: data.symbol || data.ticker || data.Ticker,
        Qty: data.shares || data.quantity || data.Qty || data.qty,
        Current_Price: data.purchase_price || data.current_price || data.Current_Price || data.price,
        Total_Value: data.total_value || data.Total_Value || data.position_value,
        Cost_Basis: data.total_cost || data.cost_basis || data.Cost_Basis || data.total_value,
        Gain_Loss: data.gain_loss || data.Gain_Loss || 0,
        Gain_Loss_Percent: data.gain_loss_percent || data.Gain_Loss_Percent || 0,
        Category: data.asset_type || data.category || data.Category || 'Stock',
        Asset_Class: data.asset_class || data.Asset_Class || 'Equity',
        Sector: data.sector || data.Sector || 'Technology',
        Market_Value: data.market_value || data.Market_Value || data.total_value,
        Unrealized_PnL: data.unrealized_pnl || data.Unrealized_PnL || 0,
        Unrealized_PnL_Percent: data.unrealized_pnl_percent || data.Unrealized_PnL_Percent || 0,
        Last_Updated: data.last_updated || data.Last_Updated || new Date().toISOString()
      };
    });
    
    console.log('✅ Portfolio data fetched successfully:', portfolioData.length, 'items');
    
    return { 
      data: portfolioData,
      user_id: userId,
      total_items: portfolioData.length,
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    console.error('❌ Firebase portfolio error:', error);
    throw new Error(`Failed to fetch portfolio data: ${error.message}`);
  }
}

export async function getPortfolioHealth(userId = '1') {
  try {
    console.log('🔥 Fetching portfolio health directly from Firebase for user:', userId);
    
    // Get portfolio data to calculate health metrics
    const portfolioSnapshot = await db
      .collection('portfolio_data')
      .where('user_id', '==', userId)
      .get();
    
    if (portfolioSnapshot.empty) {
      return { 
        health_score: 0,
        message: 'No portfolio data found',
        user_id: userId 
      };
    }
    
    const portfolioData = portfolioSnapshot.docs.map(doc => doc.data());
    
    // Calculate health metrics
    const totalValue = portfolioData.reduce((sum, item) => sum + (item.total_value || 0), 0);
    const totalGainLoss = portfolioData.reduce((sum, item) => sum + (item.gain_loss || 0), 0);
    const totalGainLossPercent = totalValue > 0 ? (totalGainLoss / totalValue) * 100 : 0;
    
    // Calculate diversification score
    const categories = [...new Set(portfolioData.map(item => item.asset_type || item.category || 'Stock'))];
    const diversificationScore = Math.min(categories.length * 20, 100); // Max 100
    
    // Calculate risk score (simplified)
    const riskScore = Math.max(0, 100 - diversificationScore);
    
    // Calculate overall health score
    const healthScore = Math.max(0, Math.min(100, 
      (diversificationScore * 0.4) + 
      (Math.max(0, 100 + totalGainLossPercent) * 0.3) + 
      (Math.max(0, 100 - riskScore) * 0.3)
    ));
    
    return {
      health_score: Math.round(healthScore),
      total_value: totalValue,
      total_gain_loss: totalGainLoss,
      total_gain_loss_percent: Math.round(totalGainLossPercent * 100) / 100,
      diversification_score: diversificationScore,
      risk_score: riskScore,
      categories_count: categories.length,
      positions_count: portfolioData.length,
      categories: categories,
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    console.error('❌ Firebase portfolio health error:', error);
    throw new Error(`Failed to calculate portfolio health: ${error.message}`);
  }
}
