import { db } from '@/lib/firebaseAdmin';

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('user_id') || '1';
    
    console.log('🔥 Fetching portfolio data for user:', userId);
    
    // Get portfolio data from Firebase
    const portfolioSnapshot = await db
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
      return {
        id: doc.id,
        Ticker: data.ticker || data.Ticker,
        Qty: data.quantity || data.Qty || data.qty,
        Current_Price: data.current_price || data.Current_Price || data.price,
        Total_Value: data.total_value || data.Total_Value || data.position_value,
        Cost_Basis: data.cost_basis || data.Cost_Basis || data.total_value,
        Gain_Loss: data.gain_loss || data.Gain_Loss || 0,
        Gain_Loss_Percent: data.gain_loss_percent || data.Gain_Loss_Percent || 0,
        Category: data.category || data.Category || 'Stock',
        Asset_Class: data.asset_class || data.Asset_Class || 'Equity',
        Sector: data.sector || data.Sector || 'Technology',
        Market_Value: data.market_value || data.Market_Value || data.total_value,
        Unrealized_PnL: data.unrealized_pnl || data.Unrealized_PnL || 0,
        Unrealized_PnL_Percent: data.unrealized_pnl_percent || data.Unrealized_PnL_Percent || 0,
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

export async function POST(request) {
  try {
    const body = await request.json();
    const { user_id, portfolio_data } = body;
    
    console.log('🔥 Adding portfolio data for user:', user_id);
    
    // Add portfolio data to Firebase
    const batch = db.batch();
    
    portfolio_data.forEach(item => {
      const docRef = db.collection('portfolio_data').doc();
      batch.set(docRef, {
        user_id: user_id,
        ticker: item.Ticker,
        quantity: item.Qty,
        current_price: item.Current_Price,
        total_value: item.Total_Value,
        cost_basis: item.Cost_Basis || item.Total_Value,
        gain_loss: item.Gain_Loss || 0,
        gain_loss_percent: item.Gain_Loss_Percent || 0,
        category: item.Category || 'Stock',
        asset_class: item.Asset_Class || 'Equity',
        sector: item.Sector || 'Technology',
        market_value: item.Market_Value || item.Total_Value,
        unrealized_pnl: item.Unrealized_PnL || 0,
        unrealized_pnl_percent: item.Unrealized_PnL_Percent || 0,
        last_updated: new Date().toISOString(),
        created_at: new Date().toISOString()
      });
    });
    
    await batch.commit();
    
    console.log('✅ Portfolio data added successfully');
    
    return Response.json({ 
      message: 'Portfolio data added successfully',
      user_id: user_id,
      items_added: portfolio_data.length,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Firebase portfolio POST error:', error);
    return Response.json({ 
      error: 'Failed to add portfolio data',
      details: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
