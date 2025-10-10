import { db } from '@/lib/firebaseAdmin';

export async function GET(request) {
  try {
    console.log('🔥 Starting Firebase data ingestion test...');
    
    // Test 1: Check Firebase connection
    console.log('📡 Testing Firebase connection...');
    const testCollection = await db.collection('test').limit(1).get();
    console.log('✅ Firebase connection successful');
    
    // Test 2: Check users collection
    console.log('👥 Checking users collection...');
    const usersSnapshot = await db.collection('users').limit(5).get();
    const usersData = usersSnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));
    console.log('👥 Users found:', usersData.length);
    
    // Test 3: Check portfolio_data collection
    console.log('📊 Checking portfolio_data collection...');
    const portfolioSnapshot = await db.collection('portfolio_data').limit(10).get();
    const portfolioData = portfolioSnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));
    console.log('📊 Portfolio items found:', portfolioData.length);
    
    // Test 4: Check specific user portfolio using uid from users collection
    let userIdToTest = '1'; // Default
    if (usersData.length > 0 && usersData[0].uid) {
      userIdToTest = usersData[0].uid; // Use actual uid from users collection
    }
    
    console.log(`🔍 Checking portfolio_data for user_id: ${userIdToTest} (from users.uid)...`);
    const userPortfolioSnapshot = await db
      .collection('portfolio_data')
      .where('user_id', '==', userIdToTest)
      .get();
    const userPortfolioData = userPortfolioSnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));
    console.log(`🔍 User ${userIdToTest} portfolio items:`, userPortfolioData.length);
    
    // Test 5: Check data structure
    const samplePortfolio = portfolioData[0];
    const sampleUser = usersData[0];
    
    const debugInfo = {
      firebase_connection: 'success',
      collections: {
        users: {
          count: usersData.length,
          sample: sampleUser ? {
            id: sampleUser.id,
            fields: Object.keys(sampleUser)
          } : null
        },
        portfolio_data: {
          count: portfolioData.length,
          sample: samplePortfolio ? {
            id: samplePortfolio.id,
            fields: Object.keys(samplePortfolio)
          } : null
        }
      },
      user_portfolio: {
        user_id_tested: userIdToTest,
        user_id_source: 'users.uid',
        count: userPortfolioData.length,
        items: userPortfolioData.map(item => ({
          id: item.id,
          user_id: item.user_id,
          ticker: item.ticker || item.Ticker,
          quantity: item.quantity || item.Qty,
          total_value: item.total_value || item.Total_Value
        }))
      },
      uid_mapping: {
        users_uid: usersData.length > 0 ? usersData[0].uid : null,
        portfolio_user_ids: [...new Set(portfolioData.map(item => item.user_id))],
        match_found: userPortfolioData.length > 0
      },
      environment_check: {
        firebase_admin_configured: !!process.env.FIREBASE_ADMIN_SA_JSON,
        project_id: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || 'wealtheon-1d939'
      },
      timestamp: new Date().toISOString()
    };
    
    console.log('✅ Firebase debug completed successfully');
    console.log('📊 Debug info:', JSON.stringify(debugInfo, null, 2));
    
    return Response.json(debugInfo);
    
  } catch (error) {
    console.error('❌ Firebase debug error:', error);
    return Response.json({ 
      error: 'Firebase debug failed',
      details: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
