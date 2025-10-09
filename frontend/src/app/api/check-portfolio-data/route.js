import { db } from '@/lib/firebaseAdmin';

export async function GET(request) {
  try {
    console.log('🔍 Checking all portfolio_data in Firebase...');
    
    // Get ALL portfolio data (no filters)
    const allPortfolioSnapshot = await db.collection('portfolio_data').get();
    const allPortfolioData = allPortfolioSnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));
    
    console.log('📊 Total portfolio items found:', allPortfolioData.length);
    
    // Check different user_id formats
    const user1String = allPortfolioData.filter(item => item.user_id === '1');
    const user1Number = allPortfolioData.filter(item => item.user_id === 1);
    const user1Any = allPortfolioData.filter(item => 
      item.user_id === '1' || item.user_id === 1 || item.user_id === 'user_1'
    );
    
    // Check for any user_id patterns
    const uniqueUserIds = [...new Set(allPortfolioData.map(item => item.user_id))];
    
    const debugInfo = {
      total_items: allPortfolioData.length,
      all_user_ids: uniqueUserIds,
      user_id_1_string: user1String.length,
      user_id_1_number: user1Number.length,
      user_id_1_any: user1Any.length,
      sample_items: allPortfolioData.slice(0, 3).map(item => ({
        id: item.id,
        user_id: item.user_id,
        ticker: item.ticker || item.Ticker,
        quantity: item.quantity || item.Qty,
        total_value: item.total_value || item.Total_Value
      })),
      timestamp: new Date().toISOString()
    };
    
    console.log('🔍 Portfolio data check completed:', debugInfo);
    
    return Response.json(debugInfo);
    
  } catch (error) {
    console.error('❌ Portfolio data check error:', error);
    return Response.json({ 
      error: 'Failed to check portfolio data',
      details: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
