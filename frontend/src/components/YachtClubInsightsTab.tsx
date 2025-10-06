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

// Yacht Club Theme
const yachtClubTheme = {
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
  }
}

// Animated Card Component
const AnimatedCard: React.FC<{
  children: React.ReactNode
  delay?: number
  className?: string
}> = ({ children, delay = 0, className = '' }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      className={`bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border ${className}`}
      style={{ 
        borderColor: yachtClubTheme.colors.cardBeige,
        boxShadow: `0 4px 6px -1px ${yachtClubTheme.colors.cardBeige}40, 0 2px 4px -1px ${yachtClubTheme.colors.cardBeige}20`
      }}
      whileHover={{ 
        y: -2,
        boxShadow: `0 10px 25px -5px ${yachtClubTheme.colors.accent}30, 0 4px 6px -2px ${yachtClubTheme.colors.cardBeige}40`
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
}> = ({ title, value, change, changeType = 'neutral', icon }) => {
  
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive': return { color: yachtClubTheme.colors.success }
      case 'negative': return { color: yachtClubTheme.colors.danger }
      default: return { color: yachtClubTheme.colors.textSecondary }
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
      backgroundColor: `${yachtClubTheme.colors.cardBeige}20`,
      border: `1px solid ${yachtClubTheme.colors.cardBeige}60`
    }}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium" style={{ color: yachtClubTheme.colors.textSecondary }}>
          {title}
        </span>
        {icon}
      </div>
      <div className="text-2xl font-bold mb-1" style={{ color: yachtClubTheme.colors.primary }}>
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

// Main Yacht Club InsightsTab Component
const YachtClubInsightsTab: React.FC = () => {
  // Mock data
  const portfolioTrendData = [
    { date: 'Oct 1', value: 325000 },
    { date: 'Oct 3', value: 327500 },
    { date: 'Oct 5', value: 329800 },
    { date: 'Oct 7', value: 331200 },
    { date: 'Oct 9', value: 333500 },
    { date: 'Oct 11', value: 335800 },
    { date: 'Oct 13', value: 337200 },
    { date: 'Oct 15', value: 340100 },
    { date: 'Oct 17', value: 338900 },
    { date: 'Oct 19', value: 341500 },
    { date: 'Oct 21', value: 343200 },
    { date: 'Oct 23', value: 340800 },
    { date: 'Oct 25', value: 342600 },
    { date: 'Oct 27', value: 339200 },
    { date: 'Oct 29', value: 342000 },
    { date: 'Oct 31', value: 344800 }
  ]

  const sectorAllocation = [
    { name: 'Technology', value: 45, color: yachtClubTheme.colors.primary },     // Navy
    { name: 'Healthcare', value: 15, color: yachtClubTheme.colors.secondary },   // Brown
    { name: 'Finance', value: 12, color: yachtClubTheme.colors.accent },         // Sand Gold
    { name: 'Consumer', value: 18, color: yachtClubTheme.colors.textSecondary }, // Blue-Gray
    { name: 'Energy', value: 6, color: yachtClubTheme.colors.cardBeige },        // Card Beige
    { name: 'Other', value: 4, color: '#8B9CAB' }                                // Muted Blue-Gray
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
    <div className="min-h-screen p-6" style={{ backgroundColor: yachtClubTheme.colors.background }}>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2 pb-2" style={{ 
            color: yachtClubTheme.colors.text,
            borderBottom: `2px solid ${yachtClubTheme.colors.accent}`
          }}>
            Portfolio Insights
          </h1>
          <p style={{ color: yachtClubTheme.colors.textSecondary, opacity: 0.8 }}>
            Yacht Club Premium - Sophisticated Wealth Management
          </p>
        </div>
      </div>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Portfolio Health Snapshot */}
        <AnimatedCard delay={0.1} className="p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg" style={{ backgroundColor: `${yachtClubTheme.colors.primary}20` }}>
              <TrendingUp className="h-6 w-6" style={{ color: yachtClubTheme.colors.primary }} />
            </div>
            <h2 className="text-xl font-semibold pb-2" style={{ 
              color: yachtClubTheme.colors.primary,
              borderBottom: `2px solid ${yachtClubTheme.colors.accent}`
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
            />
            <MetricCard
              title="Weekly Change"
              value="+$2,625"
              change="+0.77%"
              changeType="positive"
              icon={<BarChart3 className="h-5 w-5 text-gray-400" />}
            />
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={portfolioTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" stroke="#6B7280" fontSize={12} />
                <YAxis stroke="#6B7280" fontSize={12} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px'
                  }} 
                />
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={yachtClubTheme.colors.primary} stopOpacity={0.3}/>
                    <stop offset="95%" stopColor={yachtClubTheme.colors.primary} stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke={yachtClubTheme.colors.primary}
                  strokeWidth={3}
                  fill="url(#colorValue)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </AnimatedCard>

        {/* Risk & Diversification */}
        <AnimatedCard delay={0.2} className="p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg" style={{ backgroundColor: `${yachtClubTheme.colors.accent}20` }}>
              <Shield className="h-6 w-6" style={{ color: yachtClubTheme.colors.accent }} />
            </div>
            <h2 className="text-xl font-semibold pb-2" style={{ 
              color: yachtClubTheme.colors.primary,
              borderBottom: `2px solid ${yachtClubTheme.colors.accent}`
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
            backgroundColor: `${yachtClubTheme.colors.accent}15`,
            borderColor: yachtClubTheme.colors.accent,
            color: yachtClubTheme.colors.secondary
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
        <AnimatedCard delay={0.3} className="p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg" style={{ backgroundColor: `${yachtClubTheme.colors.secondary}20` }}>
              <BarChart3 className="h-6 w-6" style={{ color: yachtClubTheme.colors.secondary }} />
            </div>
            <h2 className="text-xl font-semibold pb-2" style={{ 
              color: yachtClubTheme.colors.primary,
              borderBottom: `2px solid ${yachtClubTheme.colors.accent}`
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
            />
            <MetricCard
              title="Sharpe Ratio"
              value="1.85"
              change="Excellent"
              changeType="positive"
            />
          </div>

          <div className="p-4 rounded-lg border" style={{
            backgroundColor: `${yachtClubTheme.colors.success}15`,
            borderColor: yachtClubTheme.colors.success,
            color: yachtClubTheme.colors.primary
          }}>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5" />
              <span className="text-sm font-medium">
                Outperforming benchmark by 2.1%
              </span>
            </div>
            <p className="text-xs mt-1 opacity-80">
              Strong risk-adjusted returns this quarter
            </p>
          </div>
        </AnimatedCard>

        {/* Market Signals */}
        <AnimatedCard delay={0.4} className="p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg" style={{ backgroundColor: `${yachtClubTheme.colors.accent}20` }}>
              <Zap className="h-6 w-6" style={{ color: yachtClubTheme.colors.accent }} />
            </div>
            <h2 className="text-xl font-semibold pb-2" style={{ 
              color: yachtClubTheme.colors.primary,
              borderBottom: `2px solid ${yachtClubTheme.colors.accent}`
            }}>
              Market Signals
            </h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg" style={{ 
              backgroundColor: `${yachtClubTheme.colors.primary}10`,
              border: `1px solid ${yachtClubTheme.colors.accent}`
            }}>
              <span className="font-medium" style={{ color: yachtClubTheme.colors.primary }}>Market Trend</span>
              <span className="px-3 py-1 rounded-full text-sm font-medium text-white" style={{ 
                backgroundColor: yachtClubTheme.colors.success 
              }}>
                Bullish
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 rounded-lg" style={{ backgroundColor: `${yachtClubTheme.colors.cardBeige}30` }}>
                <div className="text-sm" style={{ color: yachtClubTheme.colors.textSecondary }}>AAPL RSI</div>
                <div className="text-lg font-bold" style={{ color: yachtClubTheme.colors.primary }}>65</div>
              </div>
              <div className="text-center p-3 rounded-lg" style={{ backgroundColor: `${yachtClubTheme.colors.cardBeige}30` }}>
                <div className="text-sm" style={{ color: yachtClubTheme.colors.textSecondary }}>MSFT RSI</div>
                <div className="text-lg font-bold" style={{ color: yachtClubTheme.colors.primary }}>58</div>
              </div>
            </div>

            <div className="p-3 rounded-lg" style={{ backgroundColor: `${yachtClubTheme.colors.accent}10` }}>
              <div className="flex items-center space-x-2 mb-2">
                <Info className="h-4 w-4" style={{ color: yachtClubTheme.colors.accent }} />
                <span className="text-sm font-medium" style={{ color: yachtClubTheme.colors.secondary }}>
                  Market Alert
                </span>
              </div>
              <p className="text-xs" style={{ color: yachtClubTheme.colors.textSecondary }}>
                Fed meeting next week may impact tech sector volatility
              </p>
            </div>
          </div>
        </AnimatedCard>

        {/* Personalized Actions */}
        <AnimatedCard delay={0.5} className="p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg" style={{ backgroundColor: `${yachtClubTheme.colors.primary}20` }}>
              <Target className="h-6 w-6" style={{ color: yachtClubTheme.colors.primary }} />
            </div>
            <h2 className="text-xl font-semibold pb-2" style={{ 
              color: yachtClubTheme.colors.primary,
              borderBottom: `2px solid ${yachtClubTheme.colors.accent}`
            }}>
              Personalized Actions
            </h2>
          </div>

          <div className="space-y-4">
            <div className="p-4 rounded-lg" style={{ 
              backgroundColor: yachtClubTheme.colors.accent,
              color: yachtClubTheme.colors.primary
            }}>
              <div className="flex items-center space-x-2 mb-2">
                <Target className="h-5 w-5" />
                <span className="font-medium">Next Best Action</span>
              </div>
              <p className="text-sm">Rebalance: Reduce AAPL by 3%, add VTI for diversification</p>
            </div>

            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 mt-0.5" style={{ color: yachtClubTheme.colors.success }} />
                <div>
                  <p className="text-sm font-medium" style={{ color: yachtClubTheme.colors.primary }}>
                    Consider taking profits on NVDA
                  </p>
                  <p className="text-xs" style={{ color: yachtClubTheme.colors.textSecondary }}>
                    Up 45% this quarter, may face resistance
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <AlertTriangle className="h-5 w-5 mt-0.5" style={{ color: yachtClubTheme.colors.accent }} />
                <div>
                  <p className="text-sm font-medium" style={{ color: yachtClubTheme.colors.primary }}>
                    Monitor bond allocation
                  </p>
                  <p className="text-xs" style={{ color: yachtClubTheme.colors.textSecondary }}>
                    Consider increasing to 15% for stability
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <XCircle className="h-5 w-5 mt-0.5" style={{ color: yachtClubTheme.colors.danger }} />
                <div>
                  <p className="text-sm font-medium" style={{ color: yachtClubTheme.colors.primary }}>
                    Review RIVN position
                  </p>
                  <p className="text-xs" style={{ color: yachtClubTheme.colors.textSecondary }}>
                    High volatility, consider stop-loss
                  </p>
                </div>
              </div>
            </div>
          </div>
        </AnimatedCard>

        {/* Forecast / Scenario Analysis */}
        <AnimatedCard delay={0.6} className="p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 rounded-lg" style={{ backgroundColor: `${yachtClubTheme.colors.secondary}20` }}>
              <TrendingUp className="h-6 w-6" style={{ color: yachtClubTheme.colors.secondary }} />
            </div>
            <h2 className="text-xl font-semibold pb-2" style={{ 
              color: yachtClubTheme.colors.primary,
              borderBottom: `2px solid ${yachtClubTheme.colors.accent}`
            }}>
              Forecast & Scenario Analysis
            </h2>
          </div>

          <div className="mb-6">
            <div className="flex space-x-2 mb-4">
              {['Conservative', 'Moderate', 'Aggressive'].map((scenario, index) => (
                <button
                  key={scenario}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    index === 1 ? 'text-white' : ''
                  }`}
                  style={{
                    backgroundColor: index === 1 ? yachtClubTheme.colors.primary : `${yachtClubTheme.colors.cardBeige}40`,
                    color: index === 1 ? 'white' : yachtClubTheme.colors.textSecondary
                  }}
                >
                  {scenario}
                </button>
              ))}
            </div>

            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={forecastData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="month" stroke="#6B7280" fontSize={12} />
                  <YAxis stroke="#6B7280" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #E5E7EB',
                      borderRadius: '8px'
                    }} 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="conservative" 
                    stroke={yachtClubTheme.colors.textSecondary} 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="moderate" 
                    stroke={yachtClubTheme.colors.primary} 
                    strokeWidth={3}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="aggressive" 
                    stroke={yachtClubTheme.colors.secondary}
                    strokeWidth={2}
                    strokeDasharray="5 5"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 text-center">
            {[
              { label: 'Conservative', value: '$363K', change: '+5.3%' },
              { label: 'Moderate', value: '$377K', change: '+9.4%' },
              { label: 'Aggressive', value: '$393K', change: '+14.0%' }
            ].map((projection, index) => (
              <div key={projection.label} className="p-3 rounded-lg" style={{ 
                backgroundColor: `${yachtClubTheme.colors.cardBeige}30` 
              }}>
                <div className="text-xs" style={{ color: yachtClubTheme.colors.textSecondary }}>
                  {projection.label}
                </div>
                <div className="text-sm font-bold" style={{ color: yachtClubTheme.colors.primary }}>
                  {projection.value}
                </div>
                <div className="text-xs" style={{ color: yachtClubTheme.colors.success }}>
                  {projection.change}
                </div>
              </div>
            ))}
          </div>
        </AnimatedCard>

      </div>
    </div>
  )
}

export default YachtClubInsightsTab
