import { db } from '@/lib/firebaseAdmin';

export async function POST(request) {
  try {
    console.log('🌱 Starting Firebase data seeding...');
    
    // Sample user data
    const userData = {
      user_id: '1',
      name: 'Test User',
      email: 'test@example.com',
      created_at: new Date().toISOString(),
      last_login: new Date().toISOString()
    };
    
    // Sample portfolio data
    const portfolioData = [
      {
        user_id: '1',
        ticker: 'AAPL',
        quantity: 10,
        current_price: 150.00,
        total_value: 1500.00,
        cost_basis: 1400.00,
        gain_loss: 100.00,
        gain_loss_percent: 7.14,
        category: 'Stock',
        asset_class: 'Equity',
        sector: 'Technology',
        last_updated: new Date().toISOString()
      },
      {
        user_id: '1',
        ticker: 'GOOGL',
        quantity: 5,
        current_price: 2800.00,
        total_value: 14000.00,
        cost_basis: 13000.00,
        gain_loss: 1000.00,
        gain_loss_percent: 7.69,
        category: 'Stock',
        asset_class: 'Equity',
        sector: 'Technology',
        last_updated: new Date().toISOString()
      },
      {
        user_id: '1',
        ticker: 'TSLA',
        quantity: 3,
        current_price: 800.00,
        total_value: 2400.00,
        cost_basis: 2700.00,
        gain_loss: -300.00,
        gain_loss_percent: -11.11,
        category: 'Stock',
        asset_class: 'Equity',
        sector: 'Automotive',
        last_updated: new Date().toISOString()
      }
    ];
    
    // Add user data
    console.log('👤 Adding user data...');
    const userRef = db.collection('users').doc('user_1');
    await userRef.set(userData);
    console.log('✅ User data added');
    
    // Add portfolio data
    console.log('📊 Adding portfolio data...');
    const batch = db.batch();
    
    portfolioData.forEach((item, index) => {
      const docRef = db.collection('portfolio_data').doc(`portfolio_${index + 1}`);
      batch.set(docRef, {
        ...item,
        created_at: new Date().toISOString()
      });
    });
    
    await batch.commit();
    console.log('✅ Portfolio data added');
    
    // Verify data was added
    const usersSnapshot = await db.collection('users').get();
    const portfolioSnapshot = await db.collection('portfolio_data').get();
    
    const seedResult = {
      success: true,
      message: 'Firebase data seeded successfully',
      data_added: {
        users: usersSnapshot.size,
        portfolio: portfolioSnapshot.size
      },
      sample_data: {
        user: userData,
        portfolio_items: portfolioData.length
      },
      timestamp: new Date().toISOString()
    };
    
    console.log('✅ Firebase seeding completed:', seedResult);
    
    return Response.json(seedResult);
    
  } catch (error) {
    console.error('❌ Firebase seeding error:', error);
    return Response.json({ 
      success: false,
      error: 'Firebase seeding failed',
      details: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
