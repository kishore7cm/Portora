import { db } from '../src/lib/firebaseAdmin';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const userId = req.query.user_id || '1';
    
    console.log('🔥 Fetching portfolio data for user:', userId);
    
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
    let portfolioSnapshot = await db
      .collection('portfolio_data')
      .where('user_id', '==', userId)
      .get();
    
    if (portfolioSnapshot.empty) {
      return res.status(200).json({ 
        data: [],
        message: 'No portfolio data found',
        user_id: userId 
      });
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
    
    res.status(200).json({ 
      data: portfolioData,
      user_id: userId,
      total_items: portfolioData.length,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Firebase portfolio error:', error);
    res.status(500).json({ 
      error: 'Failed to fetch portfolio data',
      details: error.message,
      timestamp: new Date().toISOString()
    });
  }
}
