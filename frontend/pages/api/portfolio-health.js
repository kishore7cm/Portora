import { db } from '../../src/lib/firebaseAdmin';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    let userId = req.query.user_id || '1';
    
    console.log('🔥 Fetching portfolio health for user:', userId);
    
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
    
    // Get portfolio data to calculate health metrics
    const portfolioSnapshot = await db
      .collection('portfolio_data')
      .where('user_id', '==', userId)
      .get();
    
    if (portfolioSnapshot.empty) {
      return res.status(200).json({ 
        health_score: 0,
        message: 'No portfolio data found',
        user_id: userId 
      });
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
    
    const healthData = {
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
    
    console.log('✅ Portfolio health calculated:', healthData);
    
    res.status(200).json(healthData);
    
  } catch (error) {
    console.error('❌ Firebase portfolio health error:', error);
    res.status(500).json({ 
      error: 'Failed to calculate portfolio health',
      details: error.message,
      timestamp: new Date().toISOString()
    });
  }
}
