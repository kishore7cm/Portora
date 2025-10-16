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
    
    // Return comprehensive test data that matches the dashboard format
    const testData = [
      {
        Ticker: 'AAPL',
        Category: 'Stock',
        Qty: 100,
        Current_Price: 150.00,
        Total_Value: 15000.00,
        Gain_Loss: 1000.00,
        Gain_Loss_Percent: 7.14,
        Brokerage: 'Fidelity',
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
        Brokerage: 'Vanguard',
        last_updated: new Date().toISOString()
      },
      {
        Ticker: 'BTC',
        Category: 'Crypto',
        Qty: 0.5,
        Current_Price: 45000.00,
        Total_Value: 22500.00,
        Gain_Loss: 2500.00,
        Gain_Loss_Percent: 12.5,
        Brokerage: 'Coinbase',
        last_updated: new Date().toISOString()
      },
      {
        Ticker: 'TSLA',
        Category: 'Stock',
        Qty: 25,
        Current_Price: 250.00,
        Total_Value: 6250.00,
        Gain_Loss: -500.00,
        Gain_Loss_Percent: -7.41,
        Brokerage: 'Robinhood',
        last_updated: new Date().toISOString()
      },
      {
        Ticker: 'SPY',
        Category: 'ETF',
        Qty: 30,
        Current_Price: 400.00,
        Total_Value: 12000.00,
        Gain_Loss: 800.00,
        Gain_Loss_Percent: 7.14,
        Brokerage: 'Schwab',
        last_updated: new Date().toISOString()
      }
    ];
    
    console.log('✅ Portfolio API working - returning test data for user:', userId);
    
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
