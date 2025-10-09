import { db } from '@/lib/firebaseAdmin';

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('user_id') || '1';
    
    console.log('🔥 Fetching AI insights for user:', userId);
    
    // Get portfolio data for AI analysis
    const portfolioSnapshot = await db
      .collection('portfolio_data')
      .where('user_id', '==', userId)
      .get();
    
    if (portfolioSnapshot.empty) {
      return Response.json({ 
        insights: [],
        message: 'No portfolio data found for AI analysis',
        user_id: userId 
      });
    }
    
    const portfolioData = portfolioSnapshot.docs.map(doc => doc.data());
    
    // Calculate basic metrics for AI insights
    const totalValue = portfolioData.reduce((sum, item) => sum + (item.total_value || 0), 0);
    const totalGainLoss = portfolioData.reduce((sum, item) => sum + (item.gain_loss || 0), 0);
    const totalGainLossPercent = totalValue > 0 ? (totalGainLoss / totalValue) * 100 : 0;
    
    // Generate AI insights based on portfolio data
    const insights = [];
    
    // Diversification insight
    const categories = [...new Set(portfolioData.map(item => item.category || 'Stock'))];
    if (categories.length < 3) {
      insights.push({
        type: 'warning',
        title: 'Low Diversification',
        message: `Your portfolio has only ${categories.length} categories. Consider diversifying across more asset classes.`,
        priority: 'high',
        action: 'Consider adding bonds, REITs, or international stocks'
      });
    } else if (categories.length >= 5) {
      insights.push({
        type: 'success',
        title: 'Well Diversified',
        message: `Great! Your portfolio is well diversified across ${categories.length} categories.`,
        priority: 'low',
        action: 'Maintain current diversification strategy'
      });
    }
    
    // Performance insight
    if (totalGainLossPercent > 10) {
      insights.push({
        type: 'success',
        title: 'Strong Performance',
        message: `Your portfolio is up ${totalGainLossPercent.toFixed(2)}% overall. Excellent work!`,
        priority: 'medium',
        action: 'Consider taking some profits or rebalancing'
      });
    } else if (totalGainLossPercent < -10) {
      insights.push({
        type: 'warning',
        title: 'Portfolio Underperforming',
        message: `Your portfolio is down ${Math.abs(totalGainLossPercent).toFixed(2)}%. Consider reviewing your positions.`,
        priority: 'high',
        action: 'Review individual holdings and consider rebalancing'
      });
    }
    
    // Risk insight
    const highRiskPositions = portfolioData.filter(item => 
      (item.gain_loss_percent || 0) > 20 || (item.gain_loss_percent || 0) < -20
    );
    
    if (highRiskPositions.length > 0) {
      insights.push({
        type: 'info',
        title: 'High Volatility Positions',
        message: `You have ${highRiskPositions.length} positions with significant price movements.`,
        priority: 'medium',
        action: 'Monitor these positions closely and consider risk management'
      });
    }
    
    // Concentration insight
    const largestPosition = portfolioData.reduce((max, item) => 
      (item.total_value || 0) > (max.total_value || 0) ? item : max
    );
    const largestPositionPercent = totalValue > 0 ? (largestPosition.total_value / totalValue) * 100 : 0;
    
    if (largestPositionPercent > 30) {
      insights.push({
        type: 'warning',
        title: 'High Concentration Risk',
        message: `${largestPosition.ticker} represents ${largestPositionPercent.toFixed(1)}% of your portfolio.`,
        priority: 'high',
        action: 'Consider reducing position size to manage risk'
      });
    }
    
    const aiInsights = {
      insights: insights,
      portfolio_summary: {
        total_value: totalValue,
        total_gain_loss: totalGainLoss,
        total_gain_loss_percent: Math.round(totalGainLossPercent * 100) / 100,
        positions_count: portfolioData.length,
        categories_count: categories.length
      },
      user_id: userId,
      timestamp: new Date().toISOString()
    };
    
    console.log('✅ AI insights generated:', insights.length, 'insights');
    
    return Response.json(aiInsights);
    
  } catch (error) {
    console.error('❌ Firebase AI insights error:', error);
    return Response.json({ 
      error: 'Failed to generate AI insights',
      details: error.message,
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
