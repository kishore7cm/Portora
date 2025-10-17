import { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('user_id');
    
    if (!userId) {
      return Response.json({ 
        error: 'User ID is required',
        message: 'Please provide a valid user_id parameter'
      }, { status: 400 });
    }
    
    console.log('🔥 Simple Portfolio API called for user:', userId);
    
    // Return simple test data without Firebase dependency
    const testData = [
      {
        Ticker: 'AAPL',
        Category: 'Stock',
        Qty: 100,
        Current_Price: 150.00,
        Total_Value: 15000.00,
        Gain_Loss: 1000.00,
        Gain_Loss_Percent: 7.14,
        Brokerage: 'Test Brokerage',
        last_updated: new Date().toISOString()
      },
      {
        Ticker: 'VTI',
        Category: 'ETF',
        Qty: 50,
        Current_Price: 200.00,
        Total_Value: 10000.00,
        Gain_Loss: 500.00,
        Gain_Loss_Percent: 5.26,
        Brokerage: 'Test Brokerage',
        last_updated: new Date().toISOString()
      }
    ];
    
    console.log('✅ Simple Portfolio API working - returning test data');
    
    return Response.json({ 
      data: testData,
      user_id: userId,
      total_items: testData.length,
      message: 'Simple API working - test data returned',
      timestamp: new Date().toISOString()
    });
    
  } catch (error: any) {
    console.error('❌ Simple Portfolio API error:', error);
    return Response.json({ 
      error: 'Failed to fetch portfolio data',
      details: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
