'use client'

import React, { useState } from 'react'
import { 
  ChevronDown, 
  ChevronUp,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info
} from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from 'recharts'

interface CollapsibleCardProps {
  title: string
  children: React.ReactNode
  defaultExpanded?: boolean
  icon?: React.ReactNode
}

const CollapsibleCard: React.FC<CollapsibleCardProps> = ({ 
  title, 
  children, 
  defaultExpanded = true,
  icon 
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
      <div 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-3">
          {icon}
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-500" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-500" />
        )}
      </div>
      {isExpanded && (
        <div className="px-4 pb-4">
          {children}
        </div>
      )}
    </div>
  )
}

const StatCard: React.FC<{
  title: string
  value: string
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  subtitle?: string
}> = ({ title, value, change, changeType = 'neutral', subtitle }) => {
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive': return 'text-green-600'
      case 'negative': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getChangeIcon = () => {
    switch (changeType) {
      case 'positive': return <TrendingUp className="h-4 w-4" />
      case 'negative': return <TrendingDown className="h-4 w-4" />
      default: return null
    }
  }

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="text-sm font-medium text-gray-500 mb-1">{title}</div>
      <div className="text-2xl font-bold text-gray-900 mb-1">{value}</div>
      {change && (
        <div className={`flex items-center space-x-1 text-sm ${getChangeColor()}`}>
          {getChangeIcon()}
          <span>{change}</span>
        </div>
      )}
      {subtitle && (
        <div className="text-xs text-gray-500 mt-1">{subtitle}</div>
      )}
    </div>
  )
}

const InsightsTab: React.FC = () => {
  // Mock data for Portfolio Health Snapshot
  const portfolioTrendData = [
    { date: 'Oct 1', value: 325000 },
    { date: 'Oct 3', value: 327500 },
    { date: 'Oct 5', value: 329200 },
    { date: 'Oct 7', value: 326800 },
    { date: 'Oct 9', value: 330100 },
    { date: 'Oct 11', value: 332400 },
    { date: 'Oct 13', value: 328900 },
    { date: 'Oct 15', value: 331200 },
    { date: 'Oct 17', value: 334500 },
    { date: 'Oct 19', value: 336800 },
    { date: 'Oct 21', value: 335200 },
    { date: 'Oct 23', value: 338100 },
    { date: 'Oct 25', value: 340500 },
    { date: 'Oct 27', value: 339200 },
    { date: 'Oct 29', value: 342000 },
    { date: 'Oct 31', value: 344800 }
  ]

  const topPerformers = [
    { symbol: 'NVDA', name: 'NVIDIA Corp', change: '+12.5%', value: '$28,450' },
    { symbol: 'TSLA', name: 'Tesla Inc', change: '+8.7%', value: '$24,200' },
    { symbol: 'AMZN', name: 'Amazon.com', change: '+6.2%', value: '$31,800' }
  ]

  const worstPerformers = [
    { symbol: 'META', name: 'Meta Platforms', change: '-4.2%', value: '$18,900' },
    { symbol: 'NFLX', name: 'Netflix Inc', change: '-3.8%', value: '$12,400' },
    { symbol: 'RIVN', name: 'Rivian Automotive', change: '-7.1%', value: '$5,200' }
  ]

  // Mock data for Risk & Diversification
  const sectorAllocation = [
    { name: 'Technology', value: 45, color: '#3B82F6' },
    { name: 'Healthcare', value: 15, color: '#10B981' },
    { name: 'Finance', value: 12, color: '#F59E0B' },
    { name: 'Consumer', value: 18, color: '#EF4444' },
    { name: 'Energy', value: 6, color: '#8B5CF6' },
    { name: 'Other', value: 4, color: '#6B7280' }
  ]

  const topHoldings = [
    { symbol: 'AAPL', name: 'Apple Inc', percentage: '8.5%', value: '$29,200' },
    { symbol: 'MSFT', name: 'Microsoft Corp', percentage: '7.2%', value: '$24,800' },
    { symbol: 'GOOGL', name: 'Alphabet Inc', percentage: '6.8%', value: '$23,400' }
  ]

  // Mock data for Market Signals
  const rsiData = [
    { symbol: 'AAPL', rsi: 68, status: 'Neutral' },
    { symbol: 'TSLA', rsi: 82, status: 'Overbought' },
    { symbol: 'MSFT', rsi: 45, status: 'Oversold' }
  ]

  const getRsiColor = (rsi: number) => {
    if (rsi > 70) return 'text-red-600 bg-red-100'
    if (rsi < 30) return 'text-green-600 bg-green-100'
    return 'text-yellow-600 bg-yellow-100'
  }

  // Mock data for Forecast
  const forecastData = [
    { month: 'Nov', conservative: 348000, moderate: 352000, aggressive: 358000 },
    { month: 'Dec', conservative: 351000, moderate: 357000, aggressive: 365000 },
    { month: 'Jan', conservative: 354000, moderate: 362000, aggressive: 372000 },
    { month: 'Feb', conservative: 357000, moderate: 367000, aggressive: 379000 },
    { month: 'Mar', conservative: 360000, moderate: 372000, aggressive: 386000 },
    { month: 'Apr', conservative: 363000, moderate: 377000, aggressive: 393000 }
  ]

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Portfolio Insights</h1>
        <p className="text-gray-600">Comprehensive analysis of your investment portfolio</p>
      </div>

      {/* Portfolio Health Snapshot */}
      <CollapsibleCard 
        title="Portfolio Health Snapshot" 
        icon={<TrendingUp className="h-6 w-6 text-blue-600" />}
      >
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
          <StatCard
            title="Total Portfolio Value"
            value="$344,800"
            change="+$19,800 (6.1%)"
            changeType="positive"
            subtitle="Last 30 days"
          />
          <StatCard
            title="Weekly Change"
            value="+$2,625"
            change="+0.77%"
            changeType="positive"
            subtitle="Last 7 days"
          />
          <StatCard
            title="Monthly Change"
            value="+$19,800"
            change="+6.1%"
            changeType="positive"
            subtitle="Last 30 days"
          />
          <StatCard
            title="Cash Position"
            value="4.3%"
            subtitle="$15,000 cash"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Portfolio Trend Chart */}
          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">30-Day Portfolio Trend</h4>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={portfolioTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Portfolio Value']} />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Top Gainers/Losers */}
          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Top Performers (30 Days)</h4>
            
            <div className="mb-4">
              <h5 className="text-sm font-medium text-green-600 mb-2">Top Gainers</h5>
              <div className="space-y-2">
                {topPerformers.map((stock, index) => (
                  <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0">
                    <div>
                      <div className="font-medium text-gray-900">{stock.symbol}</div>
                      <div className="text-sm text-gray-500">{stock.name}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-green-600 font-medium">{stock.change}</div>
                      <div className="text-sm text-gray-500">{stock.value}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h5 className="text-sm font-medium text-red-600 mb-2">Top Losers</h5>
              <div className="space-y-2">
                {worstPerformers.map((stock, index) => (
                  <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0">
                    <div>
                      <div className="font-medium text-gray-900">{stock.symbol}</div>
                      <div className="text-sm text-gray-500">{stock.name}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-red-600 font-medium">{stock.change}</div>
                      <div className="text-sm text-gray-500">{stock.value}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Cash Progress Bar */}
        <div className="mt-6 bg-white rounded-lg p-4 border">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Cash Allocation</span>
            <span className="text-sm text-gray-500">4.3% of portfolio</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-blue-600 h-2 rounded-full" style={{ width: '4.3%' }}></div>
          </div>
          <div className="text-xs text-gray-500 mt-1">Target: 5-10% cash position</div>
        </div>
      </CollapsibleCard>

      {/* Risk & Diversification */}
      <CollapsibleCard 
        title="Risk & Diversification" 
        icon={<AlertTriangle className="h-6 w-6 text-yellow-600" />}
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Sector Allocation Pie Chart */}
          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Sector Allocation</h4>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sectorAllocation}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sectorAllocation.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            
            {/* Overweight Warning */}
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
                <span className="text-sm font-medium text-yellow-800">
                  Your portfolio is overweight in Technology sector (45%)
                </span>
              </div>
              <p className="text-xs text-yellow-700 mt-1">
                Consider reducing tech exposure below 30% for better diversification
              </p>
            </div>
          </div>

          {/* Top Holdings */}
          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Top 3 Holdings</h4>
            <div className="space-y-4">
              {topHoldings.map((holding, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">{holding.symbol}</div>
                    <div className="text-sm text-gray-500">{holding.name}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium text-gray-900">{holding.percentage}</div>
                    <div className="text-sm text-gray-500">{holding.value}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="text-sm font-medium text-green-800">
                  Good diversification - No single holding exceeds 10%
                </span>
              </div>
            </div>
          </div>
        </div>
      </CollapsibleCard>

      {/* Performance Insights */}
      <CollapsibleCard 
        title="Performance Insights" 
        icon={<TrendingUp className="h-6 w-6 text-green-600" />}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <StatCard
            title="YTD Return"
            value="18.2%"
            change="vs S&P 500: +2.1%"
            changeType="positive"
          />
          <StatCard
            title="1 Month Return"
            value="6.1%"
            change="vs S&P 500: +1.8%"
            changeType="positive"
          />
          <StatCard
            title="1 Week Return"
            value="0.77%"
            change="vs S&P 500: -0.2%"
            changeType="positive"
          />
          <StatCard
            title="Risk-Adjusted Return"
            value="1.85"
            subtitle="Sharpe Ratio"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Benchmark Comparison</h4>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Your Portfolio (YTD)</span>
                <span className="font-medium text-green-600">+18.2%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">S&P 500 (YTD)</span>
                <span className="font-medium text-blue-600">+16.1%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Outperformance</span>
                <span className="font-medium text-green-600">+2.1%</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Income Analysis</h4>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Dividend Yield</span>
                <span className="font-medium text-gray-900">2.4%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Annual Dividend Income</span>
                <span className="font-medium text-gray-900">$8,275</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Dividend Growth (YoY)</span>
                <span className="font-medium text-green-600">+12.5%</span>
              </div>
            </div>
          </div>
        </div>
      </CollapsibleCard>

      {/* Market Signals */}
      <CollapsibleCard 
        title="Market Signals" 
        icon={<Info className="h-6 w-6 text-purple-600" />}
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Market Trend */}
          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Market Trend</h4>
            <div className="flex items-center space-x-3 mb-4">
              <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-full">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <div className="text-lg font-semibold text-green-600">Bullish</div>
                <div className="text-sm text-gray-500">Market sentiment is positive</div>
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">VIX (Fear Index)</span>
                <span className="font-medium text-green-600">18.2 (Low)</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Market Breadth</span>
                <span className="font-medium text-green-600">72% Advancing</span>
              </div>
            </div>
          </div>

          {/* RSI Status */}
          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">RSI Status (Major Holdings)</h4>
            <div className="space-y-3">
              {rsiData.map((stock, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="font-medium text-gray-900">{stock.symbol}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">RSI: {stock.rsi}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRsiColor(stock.rsi)}`}>
                      {stock.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* News & Sentiment */}
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Market News</h4>
            <div className="space-y-3">
              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="text-sm font-medium text-blue-900">Fed Signals Dovish Stance</div>
                <div className="text-xs text-blue-700 mt-1">Positive for growth stocks in your portfolio</div>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <div className="text-sm font-medium text-green-900">Tech Earnings Beat Expectations</div>
                <div className="text-xs text-green-700 mt-1">AAPL, MSFT report strong Q3 results</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Analyst Sentiment</h4>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Positive</span>
                  <span>68%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '68%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Neutral</span>
                  <span>22%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '22%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Negative</span>
                  <span>10%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-red-500 h-2 rounded-full" style={{ width: '10%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CollapsibleCard>

      {/* Personalized Actions */}
      <CollapsibleCard 
        title="Personalized Actions" 
        icon={<CheckCircle className="h-6 w-6 text-blue-600" />}
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Rebalancing Suggestions</h4>
            <div className="space-y-3">
              <div className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-yellow-900">Reduce Technology Exposure</div>
                  <div className="text-xs text-yellow-700">Consider reducing tech allocation by 8% (from 45% to 37%)</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-green-900">Add Bond Allocation</div>
                  <div className="text-xs text-green-700">Consider adding 5% in bonds for stability and income</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <Info className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-blue-900">Increase International Exposure</div>
                  <div className="text-xs text-blue-700">Add 3% international stocks for better diversification</div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Stock-Specific Actions</h4>
            <div className="space-y-3">
              <div className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-red-900">TSLA - Overbought Signal</div>
                  <div className="text-xs text-red-700">RSI at 82, consider trimming position by 25%</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                <TrendingUp className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-green-900">MSFT - Attractive Entry</div>
                  <div className="text-xs text-green-700">RSI at 45, good opportunity to add to position</div>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <Info className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-blue-900">Dividend Opportunity</div>
                  <div className="text-xs text-blue-700">JNJ yielding 3.2%, consider for income diversification</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CollapsibleCard>

      {/* Forecast / Scenario Analysis */}
      <CollapsibleCard 
        title="Forecast / Scenario Analysis" 
        icon={<TrendingUp className="h-6 w-6 text-indigo-600" />}
        defaultExpanded={false}
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* What-If Analysis */}
          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">What-If Scenarios</h4>
            <div className="space-y-4">
              <div className="p-3 bg-red-50 rounded-lg">
                <div className="text-sm font-medium text-red-900">Market Correction (-10%)</div>
                <div className="text-xs text-red-700 mb-2">If S&P 500 drops 10%, your portfolio may drop ~7%</div>
                <div className="text-sm font-semibold text-red-900">Estimated Value: $320,900</div>
              </div>
              <div className="p-3 bg-yellow-50 rounded-lg">
                <div className="text-sm font-medium text-yellow-900">Recession Scenario (-20%)</div>
                <div className="text-xs text-yellow-700 mb-2">In a recession, portfolio could decline ~15%</div>
                <div className="text-sm font-semibold text-yellow-900">Estimated Value: $293,100</div>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <div className="text-sm font-medium text-green-900">Bull Market (+15%)</div>
                <div className="text-xs text-green-700 mb-2">Continued bull market could boost portfolio ~18%</div>
                <div className="text-sm font-semibold text-green-900">Estimated Value: $406,900</div>
              </div>
            </div>
          </div>

          {/* Future Projection Chart */}
          <div className="bg-white rounded-lg p-4 border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">6-Month Projection</h4>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={forecastData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => [`$${Number(value).toLocaleString()}`, '']} />
                <Line 
                  type="monotone" 
                  dataKey="conservative" 
                  stroke="#EF4444" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="Conservative"
                />
                <Line 
                  type="monotone" 
                  dataKey="moderate" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  name="Moderate"
                />
                <Line 
                  type="monotone" 
                  dataKey="aggressive" 
                  stroke="#10B981" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="Aggressive"
                />
              </LineChart>
            </ResponsiveContainer>
            <div className="mt-2 text-xs text-gray-500">
              Based on historical performance and current market conditions
            </div>
          </div>
        </div>
      </CollapsibleCard>
    </div>
  )
}

export default InsightsTab
