'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { 
  ChevronDown,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  Target,
  Shield,
  BarChart3,
  Zap
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
  AreaChart,
  Area
} from 'recharts'

// Theme definitions
const themes = {
  yachtClub: {
    name: 'Yacht Club Premium',
    colors: {
      primary: '#1C3D5A',        // Primary Navy
      secondary: '#7A5C45',      // Secondary Brown
      accent: '#C9A66B',         // Accent Sand Gold
      background: '#FDFBF7',     // Background Light
      cardBeige: '#EDE9E3',      // Card Beige
      text: '#000000',           // Black for headings
      textSecondary: '#5A6A73',  // Neutral Blue-Gray for body
      danger: '#DC2626',         // Danger Red
      warning: '#C9A66B',        // Gold for warnings
      success: '#22C55E'         // Success Green
    },
    classes: {
      header: 'text-navy-900 border-b-2 border-gold-400',
      card: 'bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-beige-200',
      button: 'bg-navy-800 hover:bg-gold-500 text-white transition-colors duration-200',
      accent: 'bg-gold-50 border-gold-200 text-gold-800',
      positive: 'text-green-500',
      negative: 'text-red-600',
      warning: 'bg-gold-50 border-gold-200 text-brown-700',
      success: 'bg-green-50 border-green-200 text-green-700'
    }
  },
}



// Animated Card Component
const AnimatedCard: React.FC<{
  children: React.ReactNode
  delay?: number
  className?: string
  theme: typeof themes.yachtClub
}> = ({ children, delay = 0, className = '', theme }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      className={`bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border ${className}`}
      style={{ 
        borderColor: theme.colors.cardBeige,
        boxShadow: `0 4px 6px -1px ${theme.colors.cardBeige}40, 0 2px 4px -1px ${theme.colors.cardBeige}20`
      }}
      whileHover={{ 
        y: -2,
        boxShadow: `0 10px 25px -5px ${theme.colors.accent}30, 0 4px 6px -2px ${theme.colors.cardBeige}40`
      }}
    >
      {children}
    </motion.div>
  )
}

// Metric Card Component
const MetricCard: React.FC<{
  title: string
  value: string
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  icon?: React.ReactNode
  theme: typeof themes.yachtClub
}> = ({ title, value, change, changeType = 'neutral', icon, theme }) => {
  
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive': return { color: theme.colors.success }
      case 'negative': return { color: theme.colors.danger }
      default: return { color: theme.colors.textSecondary }
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
    <div className="rounded-xl p-4" style={{ 
      backgroundColor: `${theme.colors.cardBeige}20`,
      border: `1px solid ${theme.colors.cardBeige}60`
    }}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium" style={{ color: theme.colors.textSecondary }}>
          {title}
        </span>
        {icon}
      </div>
      <div className="text-2xl font-bold mb-1" style={{ color: theme.colors.primary }}>
        {value}
      </div>
      {change && (
        <div className="flex items-center space-x-1 text-sm" style={getChangeColor()}>
          {getChangeIcon()}
          <span>{change}</span>
        </div>
      )}
    </div>
  )
}

// Main InsightsTab Component
const ThemedInsightsTab: React.FC = () => {
  const theme = themes.yachtClub

  // Mock data
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

  const sectorAllocation = [
    { name: 'Technology', value: 45, color: theme.colors.primary },     // Navy
    { name: 'Healthcare', value: 15, color: theme.colors.secondary },   // Brown
    { name: 'Finance', value: 12, color: theme.colors.accent },         // Sand Gold
    { name: 'Consumer', value: 18, color: theme.colors.textSecondary }, // Blue-Gray
    { name: 'Energy', value: 6, color: theme.colors.cardBeige },        // Card Beige
    { name: 'Other', value: 4, color: '#8B9CAB' }                       // Muted Blue-Gray
  ]

  const forecastData = [
    { month: 'Nov', conservative: 348000, moderate: 352000, aggressive: 358000 },
    { month: 'Dec', conservative: 351000, moderate: 357000, aggressive: 365000 },
    { month: 'Jan', conservative: 354000, moderate: 362000, aggressive: 372000 },
    { month: 'Feb', conservative: 357000, moderate: 367000, aggressive: 379000 },
    { month: 'Mar', conservative: 360000, moderate: 372000, aggressive: 386000 },
    { month: 'Apr', conservative: 363000, moderate: 377000, aggressive: 393000 }
  ]

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: theme.colors.background }}>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2 pb-2" style={{ 
            color: theme.colors.text,
            borderBottom: `2px solid ${theme.colors.accent}`
          }}>
            Portfolio Insights
          </h1>
          <p style={{ color: theme.colors.textSecondary, opacity: 0.8 }}>
            Yacht Club Premium - Sophisticated Wealth Management
          </p>
        </div>
      </div>

        {/* Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Portfolio Health Snapshot */}
          <AnimatedCard delay={0.1} className="p-6" theme={theme}>
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 rounded-lg" style={{ backgroundColor: `${theme.colors.primary}20` }}>
                <TrendingUp className="h-6 w-6" style={{ color: theme.colors.primary }} />
              </div>
              <h2 className="text-xl font-semibold pb-2" style={{ 
                color: theme.colors.primary,
                borderBottom: `2px solid ${theme.colors.accent}`
              }}>
                Portfolio Health Snapshot
              </h2>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <MetricCard
                title="Total Value"
                value="$344,800"
                change="+6.1%"
                changeType="positive"
                icon={<Target className="h-5 w-5 text-gray-400" />}
                theme={theme}
              />
              <MetricCard
                title="Weekly Change"
                value="+$2,625"
                change="+0.77%"
                changeType="positive"
                icon={<BarChart3 className="h-5 w-5 text-gray-400" />}
                theme={theme}
              />
            </div>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={portfolioTrendData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={theme.colors.primary} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={theme.colors.primary} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="date" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Portfolio Value']}
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #E5E7EB',
                      borderRadius: '8px'
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="value" 
                    stroke={theme.colors.primary}
                    strokeWidth={3}
                    fillOpacity={1} 
                    fill="url(#colorValue)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </AnimatedCard>

          {/* Risk & Diversification */}
          <AnimatedCard delay={0.2} className="p-6" theme={theme}>
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 rounded-lg" style={{ backgroundColor: `${theme.colors.accent}20` }}>
                <Shield className="h-6 w-6" style={{ color: theme.colors.accent }} />
              </div>
              <h2 className="text-xl font-semibold pb-2" style={{ 
                color: theme.colors.primary,
                borderBottom: `2px solid ${theme.colors.accent}`
              }}>
                Risk & Diversification
              </h2>
            </div>

            <div className="h-64 mb-6">
              <ResponsiveContainer width="100%" height="100%">
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
            </div>

            <div className="p-4 rounded-lg border" style={{
              backgroundColor: `${theme.colors.accent}15`,
              borderColor: theme.colors.accent,
              color: theme.colors.secondary
            }}>
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5" />
                <span className="text-sm font-medium">
                  Technology sector overweight at 45%
                </span>
              </div>
              <p className="text-xs mt-1 opacity-80">
                Consider reducing tech exposure below 30%
              </p>
            </div>
          </AnimatedCard>

          {/* Performance Insights */}
          <AnimatedCard delay={0.3} className="p-6" theme={theme}>
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 rounded-lg" style={{ backgroundColor: `${theme.colors.secondary}20` }}>
                <BarChart3 className="h-6 w-6" style={{ color: theme.colors.secondary }} />
              </div>
              <h2 className="text-xl font-semibold pb-2" style={{ 
                color: theme.colors.primary,
                borderBottom: `2px solid ${theme.colors.accent}`
              }}>
                Performance Insights
              </h2>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <MetricCard
                title="YTD Return"
                value="18.2%"
                change="vs S&P: +2.1%"
                changeType="positive"
                theme={theme}
              />
              <MetricCard
                title="Sharpe Ratio"
                value="1.85"
                change="Excellent"
                changeType="positive"
                theme={theme}
              />
            </div>

            <div className="p-4 rounded-lg border" style={{
              backgroundColor: `${theme.colors.success}15`,
              borderColor: theme.colors.success,
              color: theme.colors.primary
            }}>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5" />
                <span className="text-sm font-medium">
                  Outperforming benchmark by 2.1%
                </span>
              </div>
            </div>
          </AnimatedCard>

          {/* Market Signals */}
          <AnimatedCard delay={0.4} className="p-6" theme={theme}>
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 rounded-lg" style={{ backgroundColor: `${theme.colors.accent}20` }}>
                <Zap className="h-6 w-6" style={{ color: theme.colors.accent }} />
              </div>
              <h2 className="text-xl font-semibold pb-2" style={{ 
                color: theme.colors.primary,
                borderBottom: `2px solid ${theme.colors.accent}`
              }}>
                Market Signals
              </h2>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  <span className="font-medium text-green-900">Market Trend</span>
                </div>
                <span className="text-sm font-semibold text-green-600">Bullish</span>
              </div>

              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700">RSI Status</h4>
                {[
                  { symbol: 'AAPL', rsi: 68, status: 'Neutral' },
                  { symbol: 'TSLA', rsi: 82, status: 'Overbought' },
                  { symbol: 'MSFT', rsi: 45, status: 'Oversold' }
                ].map((stock, index) => (
                  <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <span className="font-medium">{stock.symbol}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">RSI: {stock.rsi}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        stock.rsi > 70 ? 'bg-red-100 text-red-800' : 
                        stock.rsi < 30 ? 'bg-green-100 text-green-800' : 
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {stock.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </AnimatedCard>

          {/* Personalized Actions */}
          <AnimatedCard delay={0.5} className="p-6" theme={theme}>
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 rounded-lg" style={{ backgroundColor: `${theme.colors.primary}20` }}>
                <Target className="h-6 w-6" style={{ color: theme.colors.primary }} />
              </div>
              <h2 className="text-xl font-semibold pb-2" style={{ 
                color: theme.colors.primary,
                borderBottom: `2px solid ${theme.colors.accent}`
              }}>
                Personalized Actions
              </h2>
            </div>

            <div className="space-y-4">
              <div className={`p-4 rounded-lg border-l-4 ${theme.classes.accent.replace('bg-', 'bg-').replace('border-', 'border-l-')}`} 
                   style={{ borderLeftColor: theme.colors.accent }}>
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="h-5 w-5 mt-0.5" style={{ color: theme.colors.accent }} />
                  <div>
                    <div className="font-medium" style={{ color: theme.colors.accent }}>
                      Next Best Action
                    </div>
                    <div className="text-sm mt-1" style={{ color: theme.colors.text }}>
                      Reduce Technology exposure by 8% and add Bond allocation
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                {[
                  { action: 'TSLA - Consider trimming', type: 'warning', desc: 'RSI at 82, overbought signal' },
                  { action: 'MSFT - Attractive entry', type: 'success', desc: 'RSI at 45, good opportunity' },
                  { action: 'Add defensive positions', type: 'info', desc: 'Consider JNJ for income diversification' }
                ].map((item, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    {item.type === 'warning' && <XCircle className="h-5 w-5 text-red-600 mt-0.5" />}
                    {item.type === 'success' && <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />}
                    {item.type === 'info' && <Info className="h-5 w-5 text-blue-600 mt-0.5" />}
                    <div>
                      <div className="text-sm font-medium text-gray-900">{item.action}</div>
                      <div className="text-xs text-gray-600">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </AnimatedCard>

          {/* Forecast / Scenario Analysis */}
          <AnimatedCard delay={0.6} className="p-6" theme={theme}>
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 rounded-lg" style={{ backgroundColor: `${theme.colors.secondary}20` }}>
                <TrendingUp className="h-6 w-6" style={{ color: theme.colors.secondary }} />
              </div>
              <h2 className="text-xl font-semibold pb-2" style={{ 
                color: theme.colors.primary,
                borderBottom: `2px solid ${theme.colors.accent}`
              }}>
                Forecast Analysis
              </h2>
            </div>

            <div className="h-64 mb-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={forecastData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="month" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    formatter={(value) => [`$${Number(value).toLocaleString()}`, '']}
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #E5E7EB',
                      borderRadius: '8px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="conservative" 
                    stroke="#DC2626" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    name="Conservative"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="moderate" 
                    stroke={theme.colors.primary} 
                    strokeWidth={3}
                    name="Moderate"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="aggressive" 
                    stroke={theme.colors.secondary} 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    name="Aggressive"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-3 gap-3">
              {[
                { scenario: 'Bear Market', impact: '-15%', color: 'text-red-600' },
                { scenario: 'Base Case', impact: '+12%', color: theme.classes.positive },
                { scenario: 'Bull Market', impact: '+25%', color: 'text-green-600' }
              ].map((scenario, index) => (
                <div key={index} className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-xs text-gray-600 mb-1">{scenario.scenario}</div>
                  <div className={`text-lg font-bold ${scenario.color}`}>{scenario.impact}</div>
                </div>
              ))}
            </div>
          </AnimatedCard>

        </div>
    </div>
  )
}

export default ThemedInsightsTab
