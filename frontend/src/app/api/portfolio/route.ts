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
    
    console.log('🔥 Portfolio API called for user:', userId);
    
    // For now, return a test response to verify the API is working
    // TODO: Implement Firebase integration once API is confirmed working
    const testData = [
      {
        id: `${userId}_test_1`,
        Ticker: 'AAPL',
        Qty: 100,
        Current_Price: 150.00,
        Total_Value: 15000.00,
        Cost_Basis: 14000.00,
        Gain_Loss: 1000.00,
        Gain_Loss_Percent: 7.14,
        Category: 'Stock',
        Asset_Class: 'Equity',
        Sector: 'Technology',
        Market_Value: 15000.00,
        Unrealized_PnL: 1000.00,
        Unrealized_PnL_Percent: 7.14,
        Last_Updated: new Date().toISOString()
      },
      {
        id: `${userId}_test_2`,
        Ticker: 'VTI',
        Qty: 50,
        Current_Price: 200.00,
        Total_Value: 10000.00,
        Cost_Basis: 9500.00,
        Gain_Loss: 500.00,
        Gain_Loss_Percent: 5.26,
        Category: 'ETF',
        Asset_Class: 'Equity',
        Sector: 'Diversified',
        Market_Value: 10000.00,
        Unrealized_PnL: 500.00,
        Unrealized_PnL_Percent: 5.26,
        Last_Updated: new Date().toISOString()
      }
    ];
    
    console.log('✅ Portfolio API working - returning test data');
    
    return Response.json({ 
      data: testData,
      user_id: userId,
      total_items: testData.length,
      message: 'API is working - test data returned',
      timestamp: new Date().toISOString()
    });
    
  } catch (error: any) {
    console.error('❌ Portfolio API error:', error);
    return Response.json({ 
      error: 'Failed to fetch portfolio data',
      details: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
