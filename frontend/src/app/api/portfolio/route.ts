import { NextRequest } from 'next/server';
// @ts-ignore - Firebase admin types
import { db } from '../../../lib/firebaseAdmin';

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
    // @ts-ignore
    console.log('🔥 Firebase admin available:', !!db);
    
    // Try to get real data from Firebase first
    // @ts-ignore
    if (db) {
      try {
        console.log('📊 Attempting to fetch from Firebase...');
        console.log('📊 Looking for user ID:', userId);
        
        // Try to get portfolio data by user_id field first
        // @ts-ignore
        let portfolioDoc = await db.collection('portfolio_data').doc(userId).get();
        
        if (!portfolioDoc.exists) {
          console.log('📊 No document found with user_id, trying uid field...');
          // Try to find by uid field in users collection
          // @ts-ignore
          const userDoc = await db.collection('users').doc(userId).get();
          if (userDoc.exists) {
            console.log('📊 Found user document, checking for portfolio data...');
            // Check if portfolio data exists in the same document or separate collection
            const userData = userDoc.data();
            if (userData?.portfolio_data) {
              // Create a mock document snapshot for portfolio_data
              const mockDoc = {
                exists: true,
                data: () => userData.portfolio_data,
                id: userId,
                ref: null,
                readTime: null,
                get: () => null,
                isEqual: () => false
              };
              portfolioDoc = mockDoc as any;
            }
          }
        }
        
        if (portfolioDoc.exists) {
          const portfolioData = portfolioDoc.data();
          console.log('📊 Firebase data found:', portfolioData);
          
          if (portfolioData?.holdings && Array.isArray(portfolioData.holdings)) {
            // Transform Firebase data to match frontend format
            const transformedHoldings = portfolioData.holdings.map((holding: any, index: number) => {
              const shares = holding.shares || holding.quantity || holding.Qty || holding.qty || 0;
              const totalValue = holding.total_value || holding.Total_Value || holding.position_value || 0;
              const currentPrice = shares > 0 ? totalValue / shares : (holding.purchase_price || holding.current_price || holding.Current_Price || holding.price || 0);
              
              const costBasis = holding.total_cost || holding.cost_basis || holding.Cost_Basis || totalValue;
              const gainLoss = totalValue - costBasis;
              const gainLossPercent = costBasis > 0 ? (gainLoss / costBasis) * 100 : 0;
              
              return {
                Ticker: holding.symbol || holding.ticker || holding.Ticker,
                Category: holding.asset_type || holding.category || holding.Category || 'Stock',
                Qty: shares,
                Current_Price: currentPrice,
                Total_Value: totalValue,
                Gain_Loss: gainLoss,
                Gain_Loss_Percent: gainLossPercent,
                Brokerage: holding.brokerage || holding.Brokerage || 'Unknown',
                last_updated: holding.last_updated || holding.Last_Updated || new Date().toISOString()
              };
            });
            
            console.log('✅ Firebase data transformed successfully:', transformedHoldings.length, 'holdings');
            
            return Response.json({ 
              data: transformedHoldings,
              user_id: userId,
              total_items: transformedHoldings.length,
              message: 'Real portfolio data from Firebase',
              timestamp: new Date().toISOString()
            });
          }
        }
        
        console.log('⚠️ No Firebase data found, using fallback test data');
      } catch (firebaseError) {
        console.error('❌ Firebase error:', firebaseError);
        console.log('🔄 Falling back to test data due to Firebase error');
      }
    } else {
      console.log('⚠️ Firebase admin not available, using test data');
    }
    
    // Try client-side Firebase as fallback
    try {
      console.log('🔄 Trying client-side Firebase connection...');
      const { db: clientDb } = await import('../../../lib/firebaseClient');
      const { doc, getDoc } = await import('firebase/firestore');
      
      const portfolioDocRef = doc(clientDb, 'portfolio_data', userId);
      const portfolioDoc = await getDoc(portfolioDocRef);
      
      if (portfolioDoc.exists()) {
        const portfolioData = portfolioDoc.data();
        console.log('📊 Client-side Firebase data found:', portfolioData);
        console.log('📊 Holdings array:', portfolioData?.holdings);
        console.log('📊 Holdings type:', typeof portfolioData?.holdings);
        console.log('📊 Is array:', Array.isArray(portfolioData?.holdings));
        
        if (portfolioData?.holdings && Array.isArray(portfolioData.holdings)) {
          const transformedHoldings = portfolioData.holdings.map((holding: any) => {
            console.log('🔄 Transforming holding:', holding);
            
            // Calculate total value from shares and current price
            const shares = holding.shares || holding.Qty || holding.qty || holding.quantity || 0;
            const currentPrice = holding.current_price || holding.Current_Price || holding.price || 0;
            const totalValue = shares * currentPrice || holding.total_value || holding.Total_Value || holding.value || 0;
            
            // Calculate gain/loss percentage
            const gainLoss = holding.gain_loss || holding.Gain_Loss || 0;
            const gainLossPercent = totalValue > 0 ? (gainLoss / (totalValue - gainLoss)) * 100 : 0;
            
            const transformed = {
              Ticker: holding.symbol || holding.Ticker || holding.ticker,
              Category: holding.category || holding.Category || holding.asset_type || 'Stock',
              Qty: shares,
              Current_Price: currentPrice,
              Total_Value: totalValue,
              Gain_Loss: gainLoss,
              Gain_Loss_Percent: gainLossPercent,
              Brokerage: holding.brokerage || holding.Brokerage || 'Unknown',
              last_updated: holding.last_updated || new Date().toISOString()
            };
            
            console.log('✅ Transformed holding:', transformed);
            return transformed;
          });
          
          console.log('✅ Client-side Firebase data transformed successfully:', transformedHoldings.length, 'holdings');
          
          return Response.json({ 
            data: transformedHoldings,
            user_id: userId,
            total_items: transformedHoldings.length,
            message: 'Real portfolio data from client-side Firebase',
            timestamp: new Date().toISOString()
          });
        }
      }
      
      console.log('⚠️ No client-side Firebase data found');
    } catch (clientError) {
      console.error('❌ Client-side Firebase error:', clientError);
    }
    
    // Final fallback: Return test data if no Firebase data is available
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
      }
    ];
    
    console.log('✅ Portfolio API working - returning fallback test data for user:', userId);
    
    return Response.json({ 
      data: testData,
      user_id: userId,
      total_items: testData.length,
      message: 'Fallback test data (Firebase not available or no data found)',
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
