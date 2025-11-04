'use client'

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { 
  TrendingUp, 
  DollarSign, 
  Home,
  Database,
  Brain,
  Plus,
  X,
  CheckCircle,
  AlertCircle,
  User,
  LogOut,
  Wallet,
  BarChart3,
  Search,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Info,
  PieChart as PieChartIcon,
  Target,
  Activity,
  TrendingDown
} from 'lucide-react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts'
import Link from 'next/link'
import { formatCurrency, formatPercent, formatCount } from '@/lib/formatters'
import ProtectedRoute from '@/components/Auth/ProtectedRoute'
import { useAuth } from '@/hooks/useAuth'
import { doc, setDoc } from 'firebase/firestore'
import { db } from '@/lib/firebaseClient'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'

export default function SimpleDashboard() {
  // ALL HOOKS MUST BE CALLED FIRST - NO CONDITIONAL RETURNS BEFORE ALL HOOKS
  const { user, loading: authLoading, logout } = useAuth()
  const router = useRouter()
  
  // State for portfolio data
  const [portfolioData, setPortfolioData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  
  // State for adding holdings
  const [showAddHoldings, setShowAddHoldings] = useState(false)
  const [newHoldings, setNewHoldings] = useState<any[]>([])
  const [currentHolding, setCurrentHolding] = useState({
    ticker: '',
    category: 'Stock',
    qty: 0,
    current_price: 0,
    total_value: 0,
    brokerage: ''
  })
  const [addHoldingLoading, setAddHoldingLoading] = useState(false)
  const [addHoldingError, setAddHoldingError] = useState('')
  const [addHoldingSuccess, setAddHoldingSuccess] = useState('')
  
  // Insights system
  const [investorLevel, setInvestorLevel] = useState<'beginner' | 'intermediate' | 'expert'>('beginner')
  const [insights, setInsights] = useState<any[]>([])

  // Navigation tabs
  const navigationTabs = [
    { id: 'summary', label: 'Summary', icon: Home, description: 'Portfolio overview and key metrics' },
    { id: 'holdings', label: 'Holdings', icon: Database, description: 'Detailed assets and portfolio breakdown' },
    { id: 'insights', label: 'Insights', icon: Brain, description: 'AI insights and analytics' }
  ]

  const [activeTab, setActiveTab] = useState('summary')
  
  // Search and filter state
  const [searchQuery, setSearchQuery] = useState('')
  const [sortColumn, setSortColumn] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc')
  
  // Check portfolio data and redirect accordingly
  useEffect(() => {
    console.log('🔍 Dashboard auth check:', { user: !!user, authLoading, userId: user?.uid })
    
    if (!authLoading && !user) {
      console.log('🔍 No user found, redirecting to login')
      router.replace('/login')
      return
    }
    
    if (user) {
      console.log('✅ User authenticated, staying on dashboard')
    }
  }, [user, authLoading, router])

  // Fetch portfolio data from Firebase
  useEffect(() => {
    const fetchPortfolioData = async () => {
      if (!user) {
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const userId = user.uid
        console.log('🔍 Fetching portfolio data for user:', userId)
        console.log('🔍 User object:', user)
        
        // Try direct Firebase connection first (more reliable)
        try {
          console.log('🔄 Attempting direct Firebase connection...')
          console.log('🔄 Importing Firebase modules...')
          const { db } = await import('@/lib/firebaseClient')
          const { doc, getDoc } = await import('firebase/firestore')
          console.log('🔄 Firebase modules imported successfully')
          console.log('🔄 Database instance:', !!db)
          
          // Try to get portfolio data from portfolio_data collection
          console.log('🔄 Creating document reference for:', userId)
          const portfolioDocRef = doc(db, 'portfolio_data', userId)
          console.log('🔄 Document reference created:', !!portfolioDocRef)
          
          console.log('🔄 Fetching document from Firebase...')
          const portfolioDoc = await getDoc(portfolioDocRef)
          console.log('🔄 Document fetch completed, exists:', portfolioDoc.exists())
          
          if (portfolioDoc.exists()) {
            const portfolioData = portfolioDoc.data()
            console.log('📊 Portfolio data found:', portfolioData)
            console.log('📊 Holdings array:', portfolioData?.holdings)
            console.log('📊 Holdings type:', typeof portfolioData?.holdings)
            console.log('📊 Is array:', Array.isArray(portfolioData?.holdings))
            
            // Check if portfolio data has holdings
            if (portfolioData?.holdings && Array.isArray(portfolioData.holdings)) {
              console.log('✅ Found holdings in portfolio_data collection')
              const holdings = portfolioData.holdings
              
              // Transform the data to match dashboard format with better field mapping
              const transformedHoldings = holdings.map((holding: any) => {
                console.log('🔄 Transforming holding:', holding)
                
                // Calculate total value from shares and current price
                const shares = holding.shares || holding.Qty || holding.qty || holding.quantity || 0
                const currentPrice = holding.current_price || holding.Current_Price || holding.price || 0
                const totalValue = shares * currentPrice || holding.total_value || holding.Total_Value || holding.value || 0
                
                // Calculate gain/loss percentage
                const gainLoss = holding.gain_loss || holding.Gain_Loss || 0
                const gainLossPercent = totalValue > 0 ? (gainLoss / (totalValue - gainLoss)) * 100 : 0
                
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
                }
                
                console.log('✅ Transformed holding:', transformed)
                return transformed
              })
              
              console.log('✅ Transformed holdings:', transformedHoldings)
              setPortfolioData(transformedHoldings)
              setLoading(false)
              return
            } else {
              console.log('⚠️ No holdings array found in portfolio data')
            }
          } else {
            console.log('⚠️ No portfolio document found for user:', userId)
          }
          
          console.log('⚠️ No portfolio data found in portfolio_data collection')
        } catch (firebaseError) {
          console.log('❌ Direct Firebase connection failed:', firebaseError)
          
          // Try API as fallback
          try {
            console.log('🔄 Trying API as fallback...')
            const response = await fetch(`/api/portfolio?user_id=${userId}`)
            console.log('🔍 Portfolio API response status:', response.status)
            
            if (response.ok) {
              const data = await response.json()
              console.log('📊 Portfolio data response:', data)
              
              if (data.data && data.data.length > 0) {
                console.log('✅ User has portfolio data from API:', data.data.length, 'holdings')
                console.log('📊 Holdings data:', data.data)
                setPortfolioData(data.data)
                setLoading(false)
                return
              }
            } else {
              console.log('⚠️ API returned error status:', response.status)
            }
          } catch (apiError) {
            console.log('❌ API also failed:', apiError)
          }
        }
        
        // No portfolio data found - show empty state with options
        console.log('⚠️ No portfolio data available - showing empty state')
        setPortfolioData([])
        setLoading(false)
        
      } catch (error) {
        console.log('❌ Error fetching data:', error)
        setPortfolioData([])
        setLoading(false)
        // No redirect - show empty state with options
      }
    }

    fetchPortfolioData()
  }, [user])

  // Calculate metrics from portfolio data
  const calculateMetrics = () => {
    if (portfolioData.length === 0) {
      return {
        totalValue: 0,
        cashAllocation: 0,
        stockAllocation: 0,
        holdingsCount: 0,
        topSector: 'N/A',
        topPerformer: 'N/A',
        goalProgress: 0
      }
    }

    const totalValue = portfolioData.reduce((sum, holding) => sum + (holding.Total_Value || 0), 0)
    const cashValue = portfolioData
      .filter(h => h.Ticker?.includes('Cash') || h.Category === 'Cash')
      .reduce((sum, holding) => sum + (holding.Total_Value || 0), 0)
    const stockValue = portfolioData
      .filter(h => h.Category === 'Stock' || h.Category === 'ETF')
      .reduce((sum, holding) => sum + (holding.Total_Value || 0), 0)

    const cashAllocation = totalValue > 0 ? (cashValue / totalValue) * 100 : 0
    const stockAllocation = totalValue > 0 ? (stockValue / totalValue) * 100 : 0
    const holdingsCount = portfolioData.length

    // Find top sector
    const sectors = portfolioData.reduce((acc, holding) => {
      const sector = holding.Category || 'Unknown'
      acc[sector] = (acc[sector] || 0) + (holding.Total_Value || 0)
      return acc
    }, {} as Record<string, number>)

    const topSector = Object.entries(sectors).reduce((a, b) => sectors[a[0]] > sectors[b[0]] ? a : b, ['N/A', 0])[0]

    // Find top performer
    const topPerformer = portfolioData.reduce((best, holding) => {
      const gainPercent = holding.Gain_Loss_Percent || 0
      const bestGainPercent = best.Gain_Loss_Percent || 0
      return gainPercent > bestGainPercent ? holding : best
    }, portfolioData[0] || {})

    return {
      totalValue,
      cashAllocation,
      stockAllocation,
      holdingsCount,
      topSector,
      topPerformer: topPerformer.Ticker || 'N/A',
      goalProgress: 0 // Will be calculated when we have user data
    }
  }

  const metrics = calculateMetrics()

  // Calculate chart data and insights
  const getPortfolioTrend = () => {
    // Generate mock trend data based on current value
    const currentValue = metrics.totalValue
    return [
      { date: 'Jan', value: currentValue * 0.8 },
      { date: 'Feb', value: currentValue * 0.85 },
      { date: 'Mar', value: currentValue * 0.9 },
      { date: 'Apr', value: currentValue * 0.95 },
      { date: 'May', value: currentValue }
    ]
  }

  const getAllocationData = () => {
    if (portfolioData.length === 0) return []
    
    const categories = portfolioData.reduce((acc, holding) => {
      const category = holding.Category || holding.category || 'Other'
      const value = holding.Total_Value || holding.total_value || 0
      acc[category] = (acc[category] || 0) + value
      return acc
    }, {} as Record<string, number>)

    return Object.entries(categories).map(([name, value]) => ({ name, value }))
  }

  const getGainersAndLosers = () => {
    if (portfolioData.length === 0) return { gainers: [], losers: [] }
    
    const sorted = [...portfolioData].sort((a, b) => {
      const aPercent = a.Gain_Loss_Percent || a.gain_loss_percent || 0
      const bPercent = b.Gain_Loss_Percent || b.gain_loss_percent || 0
      return bPercent - aPercent
    })

    const gainers = sorted
      .filter(h => (h.Gain_Loss_Percent || h.gain_loss_percent || 0) > 0)
      .slice(0, 3)
      .map(h => ({
        ticker: h.Ticker || h.ticker || h.symbol || 'Unknown',
        change: `+${formatPercent(h.Gain_Loss_Percent || h.gain_loss_percent || 0)}`
      }))

    const losers = sorted
      .filter(h => (h.Gain_Loss_Percent || h.gain_loss_percent || 0) < 0)
      .slice(-2)
      .map(h => ({
        ticker: h.Ticker || h.ticker || h.symbol || 'Unknown',
        change: formatPercent(h.Gain_Loss_Percent || h.gain_loss_percent || 0)
      }))

    return { gainers, losers }
  }

  const getSectorBreakdown = () => {
    if (portfolioData.length === 0) return []
    
    const sectors = portfolioData.reduce((acc, holding) => {
      const sector = holding.Category || holding.category || 'Other'
      const value = holding.Total_Value || holding.total_value || 0
      acc[sector] = (acc[sector] || 0) + value
      return acc
    }, {} as Record<string, number>)

    const sectorValues = Object.values(sectors) as number[]
    const total = sectorValues.reduce((sum, val) => sum + val, 0)
    
    return Object.entries(sectors)
      .map(([sector, value]) => ({
        sector,
        value: total > 0 ? ((value as number) / total) * 100 : 0
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 4)
  }

  const calculateHealthScore = () => {
    if (portfolioData.length === 0) return 0
    
    let score = 50 // Base score
    
    // Diversification bonus
    const uniqueHoldings = new Set(portfolioData.map(h => h.Ticker || h.ticker || h.symbol)).size
    score += Math.min(uniqueHoldings * 2, 20)
    
    // Allocation balance
    const cashRatio = metrics.cashAllocation / 100
    if (cashRatio >= 0.1 && cashRatio <= 0.3) score += 10 // Good cash balance
    if (cashRatio > 0.5) score -= 10 // Too much cash
    
    // Performance bonus
    const avgReturn = portfolioData.reduce((sum, h) => {
      return sum + (h.Gain_Loss_Percent || h.gain_loss_percent || 0)
    }, 0) / portfolioData.length
    if (avgReturn > 0) score += Math.min(avgReturn * 2, 20)
    
    return Math.round(Math.min(Math.max(score, 0), 100))
  }

  const portfolioTrend = getPortfolioTrend()
  const allocationData = getAllocationData()
  const { gainers, losers } = getGainersAndLosers()
  const sectorBreakdown = getSectorBreakdown()
  const healthScore = calculateHealthScore()
  const COLORS = ['#0ea5e9', '#10b981', '#facc15', '#f59e0b', '#8b5cf6']

  // Filter and sort portfolio data
  const filteredAndSortedData = useCallback(() => {
    let filtered = portfolioData

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter((holding) => {
        const ticker = (holding.Ticker || holding.ticker || holding.symbol || '').toLowerCase()
        const category = (holding.Category || holding.category || holding.asset_type || '').toLowerCase()
        return ticker.includes(query) || category.includes(query)
      })
    }

    // Sort
    if (sortColumn) {
      filtered = [...filtered].sort((a, b) => {
        let aVal: number | string = 0
        let bVal: number | string = 0

        switch (sortColumn) {
          case 'ticker':
            aVal = (a.Ticker || a.ticker || a.symbol || '').toLowerCase()
            bVal = (b.Ticker || b.ticker || b.symbol || '').toLowerCase()
            break
          case 'category':
            aVal = (a.Category || a.category || a.asset_type || '').toLowerCase()
            bVal = (b.Category || b.category || b.asset_type || '').toLowerCase()
            break
          case 'value':
            aVal = a.Total_Value || a.total_value || 0
            bVal = b.Total_Value || b.total_value || 0
            break
          case 'gainLoss':
            aVal = a.Gain_Loss || a.gain_loss || 0
            bVal = b.Gain_Loss || b.gain_loss || 0
            break
          case 'percentChange':
            aVal = a.Gain_Loss_Percent || a.gain_loss_percent || 0
            bVal = b.Gain_Loss_Percent || b.gain_loss_percent || 0
            break
          default:
            return 0
        }

        if (typeof aVal === 'string') {
          return sortDirection === 'asc' 
            ? aVal.localeCompare(bVal as string)
            : (bVal as string).localeCompare(aVal)
        } else {
          return sortDirection === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number)
        }
      })
    }

    return filtered
  }, [portfolioData, searchQuery, sortColumn, sortDirection])

  const displayData = filteredAndSortedData()

  // Handle column sorting
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('desc')
    }
  }

  // Get top performer
  const topPerformer = portfolioData.length > 0 
    ? portfolioData.reduce((best, holding) => {
        const gainPercent = holding.Gain_Loss_Percent || holding.gain_loss_percent || 0
        const bestGainPercent = best.Gain_Loss_Percent || best.gain_loss_percent || 0
        return gainPercent > bestGainPercent ? holding : best
      }, portfolioData[0])
    : null

  // Function to add a single holding
  const addSingleHolding = async () => {
    if (!user) {
      setAddHoldingError('User not authenticated')
      return
    }

    if (!currentHolding.ticker || !currentHolding.total_value) {
      setAddHoldingError('Please fill in ticker and total value')
      return
    }

    setAddHoldingLoading(true)
    setAddHoldingError('')
    setAddHoldingSuccess('')

    try {
      const newHolding = {
        Ticker: currentHolding.ticker,
        Category: currentHolding.category,
        Qty: currentHolding.qty || 1,
        Current_Price: currentHolding.current_price || currentHolding.total_value,
        Total_Value: currentHolding.total_value,
        Gain_Loss: 0,
        Gain_Loss_Percent: 0,
        Brokerage: currentHolding.brokerage || 'Manual Entry',
        last_updated: new Date()
      }

      // Add to local state immediately
      setNewHoldings(prev => [...prev, newHolding])
      setPortfolioData(prev => [...prev, newHolding])

      // Clear the form
      setCurrentHolding({
        ticker: '',
        category: 'Stock',
        qty: 0,
        current_price: 0,
        total_value: 0,
        brokerage: ''
      })

      setAddHoldingSuccess(`Added ${currentHolding.ticker} successfully!`)
      setTimeout(() => setAddHoldingSuccess(''), 3000)

    } catch (error: any) {
      setAddHoldingError(error.message)
    } finally {
      setAddHoldingLoading(false)
    }
  }

  // Function to save all holdings to Firebase
  const saveAllHoldings = async () => {
    if (!user || newHoldings.length === 0) return

    setAddHoldingLoading(true)
    setAddHoldingError('')

    try {
      const allHoldings = [...portfolioData, ...newHoldings]
      const totalPortfolioValue = allHoldings.reduce((sum, holding) => sum + (holding.Total_Value || 0), 0)
      
      // Store user's portfolio as single document
      await setDoc(doc(db, 'portfolio_data', user.uid), {
        user_id: user.uid,
        holdings: allHoldings,
        totalPortfolioValue: totalPortfolioValue,
        lastUpdated: new Date()
      })
      
      // Update user document
      await setDoc(doc(db, 'users', user.uid), {
        has_portfolio_data: true,
        portfolioValue: totalPortfolioValue,
        updated_at: new Date().toISOString()
      }, { merge: true })
      
      setAddHoldingSuccess(`Successfully saved ${allHoldings.length} holdings to your portfolio!`)
      setNewHoldings([])
      setShowAddHoldings(false)
      
      // Refresh portfolio data
      const response = await fetch(`/api/portfolio?user_id=${user.uid}`)
      if (response.ok) {
        const data = await response.json()
        if (data.data && data.data.length > 0) {
          setPortfolioData(data.data)
        }
      }
      
    } catch (error: any) {
      setAddHoldingError(error.message)
    } finally {
      setAddHoldingLoading(false)
    }
  }

  // Update insights when portfolio data or investor level changes
  useEffect(() => {
    if (!user || portfolioData.length === 0) {
      setInsights([])
      return
    }

    try {
      const insights = []
      const totalValue = portfolioData.reduce((sum, holding) => sum + (holding.Total_Value || 0), 0)
      const totalGainLoss = portfolioData.reduce((sum, holding) => sum + (holding.Gain_Loss || 0), 0)
      const totalGainLossPercent = totalValue > 0 ? (totalGainLoss / (totalValue - totalGainLoss)) * 100 : 0

      // Beginner insights
      if (investorLevel === 'beginner') {
        insights.push({
          type: 'education',
          title: 'Portfolio Basics',
          message: `Your portfolio is worth $${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}. This is a great start to building wealth!`,
          action: 'Learn about diversification'
        })

        if (portfolioData.length < 3) {
          insights.push({
            type: 'recommendation',
            title: 'Diversification Tip',
            message: 'Consider adding more holdings to reduce risk. A diversified portfolio typically has 10-20 different investments.',
            action: 'Add more holdings'
          })
        }

        if (totalGainLossPercent > 10) {
          insights.push({
            type: 'warning',
            title: 'High Volatility',
            message: 'Your portfolio has significant gains. Consider taking some profits to reduce risk.',
            action: 'Review risk management'
          })
        }
      }

      // Intermediate insights
      if (investorLevel === 'intermediate') {
        const stockAllocation = portfolioData.filter(h => h.Category === 'Stock').reduce((sum, h) => sum + (h.Total_Value || 0), 0) / totalValue * 100
        
        insights.push({
          type: 'analysis',
          title: 'Asset Allocation Analysis',
          message: `Your stock allocation is ${stockAllocation.toFixed(1)}%. Consider balancing with bonds (20-30%) and international exposure (10-20%).`,
          action: 'Rebalance portfolio'
        })

        if (totalGainLossPercent > 0) {
          insights.push({
            type: 'performance',
            title: 'Performance Review',
            message: `Your portfolio is up ${totalGainLossPercent >= 0 ? '+' : ''}${totalGainLossPercent.toFixed(2)}%. Consider rebalancing to maintain your target allocation.`,
            action: 'Review allocation'
          })
        }
      }

      // Expert insights
      if (investorLevel === 'expert') {
        const volatility = portfolioData.reduce((sum, holding) => {
          const weight = (holding.Total_Value || 0) / totalValue
          return sum + (weight * Math.abs(holding.Gain_Loss_Percent || 0))
        }, 0)

        insights.push({
          type: 'advanced',
          title: 'Risk-Adjusted Performance',
          message: `Your portfolio's volatility-adjusted return is ${(totalGainLossPercent / Math.max(volatility, 1)).toFixed(2)}%. Consider optimizing your Sharpe ratio.`,
          action: 'Optimize risk-return'
        })

        const concentration = Math.max(...portfolioData.map(h => (h.Total_Value || 0) / totalValue * 100))
        if (concentration > 20) {
          insights.push({
            type: 'risk',
            title: 'Concentration Risk',
            message: `Your largest holding represents ${concentration.toFixed(1)}% of your portfolio. Consider reducing concentration risk.`,
            action: 'Diversify holdings'
          })
        }
      }

      setInsights(insights)
    } catch (error) {
      console.error('Error generating insights:', error)
      setInsights([])
    }
  }, [portfolioData, investorLevel])

  // Show loading while authentication is being checked - AFTER ALL HOOKS
  if (authLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600 mx-auto mb-4"></div>
          <p className="text-neutral-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gradient-soft flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600"></div>
        </div>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-neutral-50">
        <div className="max-w-screen-xl mx-auto px-8 pt-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div className="text-left flex-1">
              <h1 className="text-4xl font-bold text-neutral-900 mb-2">Portfolio</h1>
              <p className="text-neutral-600 text-sm">Track your investments and performance</p>
            </div>
            
            {/* Profile and Logout Buttons */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-neutral-700">
                <User className="w-4 h-4" />
                <span className="font-medium text-sm">{user?.displayName || user?.email || 'User'}</span>
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-2 bg-gradient-brand text-white px-4 py-2 rounded-xl font-medium text-sm hover:shadow-brand shadow-medium transition-all duration-300"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>

          {/* Top Navigation Tabs */}
          <div className="mb-8 border-b border-neutral-200">
            <nav className="flex gap-1">
              {navigationTabs.map(({ id, label, icon: Icon }) => (
                  <button
                    key={id}
                    onClick={() => setActiveTab(id)}
                  className={`flex items-center gap-2 px-6 py-3 text-sm font-semibold transition-all duration-200 border-b-2 ${
                    activeTab === id
                      ? "text-brand-600 border-brand-600"
                      : "text-neutral-600 border-transparent hover:text-brand-600 hover:border-brand-300"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                  </button>
                ))}
              </nav>
            </div>

            {/* Main Content */}
          <div className="space-y-10">
              {/* Add Holdings Form */}
              {showAddHoldings && (
                <div className="space-y-6">
                  <div className="bg-white p-6 rounded-2xl shadow-medium border border-neutral-200">
                    <div className="flex justify-between items-center mb-6">
                      <h3 className="text-xl font-semibold text-neutral-900">Add New Holdings</h3>
                      <button
                        onClick={() => setShowAddHoldings(false)}
                        className="text-neutral-600 hover:text-neutral-900 transition-colors"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>

                    {/* Current Holdings List */}
                    {newHoldings.length > 0 && (
                      <div className="mb-6">
                        <h4 className="text-lg font-medium text-neutral-900 mb-3">Added Holdings ({newHoldings.length})</h4>
                        <div className="space-y-2">
                          {newHoldings.map((holding, index) => (
                            <div key={index} className="bg-neutral-50 p-3 rounded-xl border border-neutral-200 flex justify-between items-center">
                              <div>
                                <span className="font-medium text-neutral-900">{holding.Ticker}</span>
                                <span className="text-neutral-600 ml-2">({holding.Category})</span>
                              </div>
                              <div className="text-neutral-900 font-medium">
                                {formatCurrency(holding.Total_Value)}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Add Holding Form */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                      <div>
                        <label className="block text-sm font-semibold text-neutral-900 mb-1">Ticker/Symbol</label>
                        <input
                          type="text"
                          placeholder="e.g., AAPL, VTI, BTC"
                          value={currentHolding.ticker}
                          onChange={(e) => setCurrentHolding(prev => ({ ...prev, ticker: e.target.value.toUpperCase() }))}
                          className="w-full px-3 py-2 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all duration-200"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-neutral-900 mb-1">Category</label>
                        <select
                          value={currentHolding.category}
                          onChange={(e) => setCurrentHolding(prev => ({ ...prev, category: e.target.value }))}
                          className="w-full px-3 py-2 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all duration-200"
                        >
                          <option value="Stock">Stock</option>
                          <option value="ETF">ETF</option>
                          <option value="Bond">Bond</option>
                          <option value="Crypto">Crypto</option>
                          <option value="Cash">Cash</option>
                          <option value="Other">Other</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-neutral-900 mb-1">Total Value ($)</label>
                        <input
                          type="number"
                          placeholder="e.g., 10000"
                          value={currentHolding.total_value || ''}
                          onChange={(e) => setCurrentHolding(prev => ({ ...prev, total_value: parseFloat(e.target.value) || 0 }))}
                          className="w-full px-3 py-2 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all duration-200"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-neutral-900 mb-1">Brokerage (Optional)</label>
                        <input
                          type="text"
                          placeholder="e.g., Fidelity, Vanguard"
                          value={currentHolding.brokerage}
                          onChange={(e) => setCurrentHolding(prev => ({ ...prev, brokerage: e.target.value }))}
                          className="w-full px-3 py-2 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all duration-200"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-neutral-900 mb-1">Quantity (Optional)</label>
                        <input
                          type="number"
                          placeholder="e.g., 100"
                          value={currentHolding.qty || ''}
                          onChange={(e) => setCurrentHolding(prev => ({ ...prev, qty: parseFloat(e.target.value) || 0 }))}
                          className="w-full px-3 py-2 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all duration-200"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-semibold text-neutral-900 mb-1">Price per Share (Optional)</label>
                        <input
                          type="number"
                          placeholder="e.g., 150.00"
                          value={currentHolding.current_price || ''}
                          onChange={(e) => setCurrentHolding(prev => ({ ...prev, current_price: parseFloat(e.target.value) || 0 }))}
                          className="w-full px-3 py-2 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all duration-200"
                        />
                      </div>
                    </div>

                    {/* Success/Error Messages */}
                    {addHoldingSuccess && (
                      <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-4">
                        <div className="flex items-center">
                          <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                          <p className="text-green-600">{addHoldingSuccess}</p>
                        </div>
                      </div>
                    )}

                    {addHoldingError && (
                      <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4">
                        <div className="flex items-center">
                          <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                          <p className="text-red-600">{addHoldingError}</p>
                        </div>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                      <button
                        onClick={addSingleHolding}
                        disabled={addHoldingLoading || !currentHolding.ticker || !currentHolding.total_value}
                        className="bg-gradient-brand text-white px-6 py-3 rounded-xl font-semibold hover:shadow-brand shadow-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        {addHoldingLoading ? 'Adding...' : 'Add This Holding'}
                      </button>

                      {newHoldings.length > 0 && (
                        <button
                          onClick={saveAllHoldings}
                          disabled={addHoldingLoading}
                          className="border-2 border-brand-600 text-brand-600 px-6 py-3 rounded-xl font-semibold hover:bg-brand-600 hover:text-white shadow-soft hover:shadow-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                        >
                          {addHoldingLoading ? 'Saving...' : 'Save All Holdings'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Summary Tab */}
              {activeTab === 'summary' && (
              <div className="space-y-10">
                {/* Header */}
                <div className="flex justify-between items-center">
                  <div>
                    <h1 className="text-3xl font-bold text-neutral-900">Your Portfolio Summary</h1>
                    <p className="text-neutral-600 mt-1">
                      Welcome back, {user?.displayName || user?.email?.split('@')[0] || 'User'} 👋 | Last updated: {new Date().toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                    </p>
                  </div>
                  {portfolioData.length > 0 && (
                      <button
                        onClick={() => setShowAddHoldings(true)}
                      className="bg-gradient-brand text-white px-5 py-2 rounded-2xl font-semibold hover:shadow-md shadow-sm transition-all duration-200 flex items-center hover:translate-y-[1px]"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Add More Holdings
                      </button>
                  )}
                </div>

                  {/* Show data if available, otherwise show empty state */}
                  {portfolioData.length > 0 ? (
                    <>
                    {/* Quick Summary Banner */}
                    <div className="bg-brand-50 border border-brand-100 rounded-lg p-4 text-brand-700">
                      <div className="flex items-center gap-2">
                        <Info className="w-4 h-4" />
                        <span className="text-sm font-medium">
                          Your portfolio grew by {formatCurrency(metrics.totalValue * 0.068)} this month 📈 — outperforming 65% of users.
                        </span>
                      </div>
                    </div>

                    {/* KPI Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                      <Card className="hover:shadow-md transition-all duration-200 hover:translate-y-[1px]">
                        <CardContent className="p-6">
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="text-sm font-medium text-neutral-600">Total Portfolio Value</h3>
                            <DollarSign className="w-5 h-5 text-brand-500" />
                    </div>
                          <p className="text-4xl font-bold text-neutral-900 mt-1">{formatCurrency(metrics.totalValue)}</p>
                          <p className="text-xs text-neutral-500 mt-2">Updated 2h ago</p>
                        </CardContent>
                      </Card>

                      <Card className="hover:shadow-md transition-all duration-200 hover:translate-y-[1px] bg-gradient-to-br from-brand-50 via-white to-white">
                        <CardContent className="p-6">
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="text-sm font-medium text-neutral-600">Portfolio Health Score</h3>
                            <Target className="w-5 h-5 text-green-500" />
                    </div>
                          <p className={`text-4xl font-bold mt-1 ${healthScore >= 70 ? 'text-green-600' : healthScore >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                            {healthScore} / 100
                          </p>
                          <Progress value={healthScore} className="mt-3" />
                        </CardContent>
                      </Card>

                      <Card className="hover:shadow-md transition-all duration-200 hover:translate-y-[1px]">
                        <CardContent className="p-6 flex justify-between">
                          <div>
                            <h3 className="text-sm font-medium text-neutral-600 mb-1">Cash Allocation</h3>
                            <p className="text-2xl font-semibold text-brand-600 mt-1">{formatPercent(metrics.cashAllocation)}</p>
                    </div>
                          <PieChartIcon className="w-10 h-10 text-brand-500 self-center" />
                        </CardContent>
                      </Card>

                      <Card className="hover:shadow-md transition-all duration-200 hover:translate-y-[1px]">
                        <CardContent className="p-6 flex justify-between">
                          <div>
                            <h3 className="text-sm font-medium text-neutral-600 mb-1">Stock Allocation</h3>
                            <p className="text-2xl font-semibold text-green-600 mt-1">{formatPercent(metrics.stockAllocation)}</p>
                          </div>
                          <TrendingUp className="w-10 h-10 text-green-500 self-center" />
                        </CardContent>
                      </Card>
                  </div>

                    {/* Section Divider */}
                    <div className="border-t border-neutral-200 pt-10">
                      {/* Performance Section */}
                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <Card className="lg:col-span-2 hover:shadow-md transition-all duration-200 shadow-sm rounded-2xl">
                          <CardContent className="p-6">
                            <div className="flex justify-between items-center mb-3">
                              <h3 className="text-xl font-semibold text-neutral-800">
                                Portfolio Growth (YTD) <span className="text-green-600 font-bold">+6.8%</span> 📈
                              </h3>
                              <select className="text-xs border border-neutral-300 rounded-lg px-3 py-1 bg-white text-neutral-700" defaultValue="1Y">
                                <option>1W</option>
                                <option>1M</option>
                                <option>3M</option>
                                <option>1Y</option>
                                <option>ALL</option>
                              </select>
                                </div>
                            <ResponsiveContainer width="100%" height={250}>
                              <AreaChart data={portfolioTrend}>
                                <defs>
                                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                                  </linearGradient>
                                </defs>
                                <XAxis dataKey="date" />
                                <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                                <Area 
                                  type="monotone" 
                                  dataKey="value" 
                                  stroke="#0ea5e9" 
                                  strokeWidth={3}
                                  fillOpacity={1}
                                  fill="url(#colorValue)"
                                />
                              </AreaChart>
                            </ResponsiveContainer>
                          </CardContent>
                        </Card>

                        <Card className="hover:shadow-md transition-all duration-200 shadow-sm rounded-2xl">
                          <CardContent className="p-6">
                            <h3 className="text-xl font-semibold text-neutral-800 mb-3">Top Movers</h3>
                            <div className="space-y-3">
                              <div>
                                <h4 className="text-xs font-medium text-neutral-500 mb-2">Gainers</h4>
                                {gainers.length > 0 ? (
                                  gainers.map((g) => (
                                    <div key={g.ticker} className="flex justify-between items-center mb-2">
                                      <div className="flex items-center gap-2">
                                        <TrendingUp className="w-3 h-3 text-green-600" />
                                        <span className="text-sm text-neutral-900">{g.ticker}</span>
                                      </div>
                                      <span className="text-green-600 font-semibold text-sm">{g.change}</span>
                                    </div>
                                  ))
                                ) : (
                                  <p className="text-xs text-neutral-500">No gainers</p>
                                )}
                              </div>
                              <div className="border-t border-neutral-200 pt-3 mt-3">
                                <h4 className="text-xs font-medium text-neutral-500 mb-2">Losers</h4>
                                {losers.length > 0 ? (
                                  losers.map((l) => (
                                    <div key={l.ticker} className="flex justify-between items-center mb-2">
                                      <div className="flex items-center gap-2">
                                        <TrendingDown className="w-3 h-3 text-red-600" />
                                        <span className="text-sm text-neutral-900">{l.ticker}</span>
                                      </div>
                                      <span className="text-red-600 font-semibold text-sm">{l.change}</span>
                                    </div>
                                  ))
                                ) : (
                                  <p className="text-xs text-neutral-500">No losers</p>
                                )}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </div>

                    {/* Allocation Section */}
                    <div className="border-t border-neutral-200 pt-10">
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          <Card className="hover:shadow-md transition-all duration-200 shadow-sm rounded-2xl">
                            <CardContent className="p-6">
                              <div className="flex items-center justify-between mb-3">
                                <h3 className="text-xl font-semibold text-neutral-800">Asset Allocation</h3>
                                <span title="Click for detailed breakdown">
                                  <Info className="w-4 h-4 text-neutral-400 cursor-help" />
                                </span>
                              </div>
                              {allocationData.length > 0 ? (
                                <ResponsiveContainer width="100%" height={250}>
                                  <PieChart>
                                    <Pie 
                                      data={allocationData} 
                                      dataKey="value" 
                                      nameKey="name" 
                                      cx="50%" 
                                      cy="50%" 
                                      innerRadius={60} 
                                      outerRadius={100}
                                    >
                                      {allocationData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                      ))}
                                    </Pie>
                                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                                  </PieChart>
                                </ResponsiveContainer>
                              ) : (
                                <div className="h-[250px] flex items-center justify-center text-neutral-500">
                                  No allocation data
                    </div>
                              )}
                            </CardContent>
                          </Card>

                          <Card className="hover:shadow-md transition-all duration-200 shadow-sm rounded-2xl">
                            <CardContent className="p-6">
                              <div className="flex items-center justify-between mb-3">
                                <h3 className="text-xl font-semibold text-neutral-800">Sector Breakdown</h3>
                                <span title="Click for detailed breakdown">
                                  <Info className="w-4 h-4 text-neutral-400 cursor-help" />
                                </span>
                              </div>
                              {sectorBreakdown.length > 0 ? (
                                <ResponsiveContainer width="100%" height={250}>
                                  <BarChart data={sectorBreakdown}>
                                    <XAxis dataKey="sector" />
                                    <YAxis tickFormatter={(v) => `${v}%`} />
                                    <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
                                    <Bar dataKey="value" fill="#10b981" radius={[8, 8, 0, 0]} />
                                  </BarChart>
                                </ResponsiveContainer>
                              ) : (
                                <div className="h-[250px] flex items-center justify-center text-neutral-500">
                                  No sector data
                                </div>
                              )}
                            </CardContent>
                          </Card>
                      </div>
                    </div>

                    {/* Insights Section */}
                    <div className="border-t border-neutral-200 pt-10">
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          <Card className="hover:shadow-md transition-all duration-200 shadow-sm rounded-2xl border-l-4 border-l-brand-500 bg-neutral-50/30">
                            <CardContent className="p-6">
                              <h3 className="text-xl font-semibold text-neutral-800 mb-3">Smart Insights</h3>
                              <ul className="space-y-3 text-sm text-neutral-700">
                                {metrics.cashAllocation > 50 && (
                                  <li className="flex items-start gap-2">
                                    <Brain className="w-4 h-4 text-brand-500 mt-0.5 flex-shrink-0" />
                                    <span>Your cash allocation ({formatPercent(metrics.cashAllocation)}) is higher than average — consider investing idle cash.</span>
                                  </li>
                                )}
                                {gainers.length > 0 && (
                                  <li className="flex items-start gap-2">
                                    <TrendingUp className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                    <span>{gainers[0]?.ticker} contributed most to this month&apos;s gain ({gainers[0]?.change}).</span>
                                  </li>
                                )}
                                {sectorBreakdown.length > 0 && sectorBreakdown[0].value < 50 && (
                                  <li className="flex items-start gap-2">
                                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                    <span>Portfolio diversification is strong — no sector exceeds 50% exposure.</span>
                                  </li>
                                )}
                                {sectorBreakdown.length > 0 && sectorBreakdown[0].value >= 50 && (
                                  <li className="flex items-start gap-2">
                                    <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                                    <span>Consider diversifying — {sectorBreakdown[0].sector} represents {sectorBreakdown[0].value.toFixed(1)}% of your portfolio.</span>
                                  </li>
                                )}
                              </ul>
                            </CardContent>
                          </Card>

                          <Card className="hover:shadow-md transition-all duration-200 shadow-sm rounded-2xl bg-neutral-50/30">
                            <CardContent className="p-6">
                              <h3 className="text-xl font-semibold text-neutral-800 mb-3">Goal Progress</h3>
                              <p className="text-sm text-neutral-600 mb-2">Goal: $200,000 Portfolio Value</p>
                              <Progress value={Math.min((metrics.totalValue / 200000) * 100, 100)} className="h-3" />
                              <p className="text-xs text-neutral-600 mt-3">
                                You&apos;re {((metrics.totalValue / 200000) * 100).toFixed(0)}% toward your goal
                                {metrics.totalValue < 200000 && ` — ${((200000 - metrics.totalValue) / 200000 * 100).toFixed(0)}% remaining`}
                              </p>
                              <p className="text-xs text-neutral-500 mt-2">Target: May 2026</p>
                            </CardContent>
                          </Card>
                      </div>
                    </div>

                    {/* Benchmark & Risk Section */}
                    <div className="border-t border-neutral-200 pt-10">
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          <Card className="hover:shadow-md transition-all duration-200 shadow-sm rounded-2xl">
                            <CardContent className="p-6">
                              <h3 className="text-xl font-semibold text-neutral-800 mb-3">Portfolio vs Benchmark</h3>
                              <ResponsiveContainer width="100%" height={250}>
                                <BarChart data={[
                                  { period: '1M', portfolio: 3.2, sp500: 2.5 },
                                  { period: '3M', portfolio: 8.1, sp500: 7.6 },
                                  { period: '1Y', portfolio: 14.5, sp500: 15.0 },
                                ]}>
                                  <XAxis dataKey="period" />
                                  <YAxis tickFormatter={(v) => `${v}%`} />
                                  <Tooltip formatter={(v: number) => `${v}%`} />
                                  <Bar dataKey="portfolio" fill="#0ea5e9" name="Portfolio" radius={[8, 8, 0, 0]} />
                                  <Bar dataKey="sp500" fill="#9ca3af" name="S&P 500" radius={[8, 8, 0, 0]} />
                                </BarChart>
                              </ResponsiveContainer>
                            </CardContent>
                          </Card>

                          <Card className="hover:shadow-md transition-all duration-200 shadow-sm rounded-2xl">
                            <CardContent className="p-6">
                              <h3 className="text-xl font-semibold text-neutral-800 mb-3">Risk Meter</h3>
                              <div className="flex flex-col items-center justify-center h-[220px]">
                                <div className="w-40 h-40 rounded-full border-8 border-green-400 flex items-center justify-center text-3xl font-semibold text-green-600">
                                  Medium
                                </div>
                                <p className="text-neutral-600 mt-3 text-sm">Volatility: 12.4% | Beta: 0.98</p>
                              </div>
                            </CardContent>
                          </Card>
                      </div>
                    </div>

                    {/* Recent Activity Feed */}
                    <div className="border-t border-neutral-200 pt-10">
                      <Card className="hover:shadow-md transition-all duration-200 shadow-sm rounded-2xl">
                        <CardContent className="p-6">
                          <h3 className="text-xl font-semibold text-neutral-800 mb-3">Recent Activity</h3>
                          <ul className="space-y-3">
                            <li className="flex justify-between items-center text-neutral-700 pb-3 border-b border-neutral-100">
                              <span>💵 Added $1,000 to VTI</span>
                              <span className="text-xs text-neutral-500">Oct 30</span>
                            </li>
                            <li className="flex justify-between items-center text-neutral-700 pb-3 border-b border-neutral-100">
                              <span>📈 Dividend received from JNJ ($120)</span>
                              <span className="text-xs text-neutral-500">Oct 25</span>
                            </li>
                            <li className="flex justify-between items-center text-neutral-700">
                              <span>📉 Sold 10 shares of AAPL</span>
                              <span className="text-xs text-neutral-500">Oct 18</span>
                            </li>
                          </ul>
                        </CardContent>
                      </Card>
                  </div>
                    </>
                  ) : (
                    <div className="text-center py-20">
                      <div className="max-w-md mx-auto">
                        <div className="w-24 h-24 bg-brand-50 rounded-full flex items-center justify-center mx-auto mb-6">
                          <TrendingUp className="w-12 h-12 text-brand-600" />
                        </div>
                        <h2 className="text-2xl font-bold text-neutral-900 mb-4">Complete Your Portfolio Setup</h2>
                        <p className="text-neutral-600 mb-8">
                          To get started with portfolio tracking and insights, please add your investment holdings. 
                          This will help us provide you with accurate analytics and performance tracking.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                          <button 
                            onClick={() => setShowAddHoldings(true)}
                            className="bg-gradient-brand text-white px-6 py-3 rounded-xl font-semibold hover:shadow-brand shadow-medium transition-all duration-300 flex items-center justify-center"
                          >
                            <Plus className="w-4 h-4 mr-2" />
                            Add Holdings
                          </button>
                          <Link 
                            href="/onboarding" 
                            className="border-2 border-brand-600 text-brand-600 px-6 py-3 rounded-xl font-semibold hover:bg-brand-600 hover:text-white shadow-soft hover:shadow-medium transition-all duration-300"
                          >
                            Complete Setup
                          </Link>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Holdings Tab */}
              {activeTab === 'holdings' && (
                <div className="space-y-6">
                  {portfolioData.length > 0 ? (
                    <div className="bg-white p-6 rounded-xl border border-neutral-200 shadow-medium">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-bold text-neutral-900">All Holdings</h3>
                        
                        {/* Search Bar */}
                        <div className="relative w-full max-w-xs">
                          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400" />
                          <input
                            type="text"
                            placeholder="Search by ticker or category..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-xl focus:ring-2 focus:ring-brand-500 focus:border-brand-500 text-sm transition-all duration-200"
                          />
                        </div>
                      </div>

                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b-2 border-neutral-200 bg-neutral-50">
                              <th 
                                className="text-left py-4 px-4 text-neutral-700 font-semibold text-xs cursor-pointer hover:text-brand-600 transition-colors"
                                onClick={() => handleSort('ticker')}
                              >
                                <div className="flex items-center gap-2">
                                  Ticker
                                  {sortColumn === 'ticker' && (
                                    sortDirection === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />
                                  )}
                                  {sortColumn !== 'ticker' && <ArrowUpDown className="w-3 h-3 text-neutral-400" />}
                                </div>
                              </th>
                              <th className="text-left py-4 px-4 text-neutral-700 font-semibold text-xs">Category</th>
                              <th className="text-left py-4 px-4 text-neutral-700 font-semibold text-xs">Quantity</th>
                              <th className="text-left py-4 px-4 text-neutral-700 font-semibold text-xs">Price</th>
                              <th 
                                className="text-left py-4 px-4 text-neutral-700 font-semibold text-xs cursor-pointer hover:text-brand-600 transition-colors"
                                onClick={() => handleSort('value')}
                              >
                                <div className="flex items-center gap-2">
                                  Value
                                  {sortColumn === 'value' && (
                                    sortDirection === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />
                                  )}
                                  {sortColumn !== 'value' && <ArrowUpDown className="w-3 h-3 text-neutral-400" />}
                                </div>
                              </th>
                              <th 
                                className="text-left py-4 px-4 text-neutral-700 font-semibold text-xs cursor-pointer hover:text-brand-600 transition-colors"
                                onClick={() => handleSort('gainLoss')}
                              >
                                <div className="flex items-center gap-2">
                                  Gain/Loss
                                  {sortColumn === 'gainLoss' && (
                                    sortDirection === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />
                                  )}
                                  {sortColumn !== 'gainLoss' && <ArrowUpDown className="w-3 h-3 text-neutral-400" />}
                                </div>
                              </th>
                              <th 
                                className="text-left py-4 px-4 text-neutral-700 font-semibold text-xs cursor-pointer hover:text-brand-600 transition-colors"
                                onClick={() => handleSort('percentChange')}
                              >
                                <div className="flex items-center gap-2">
                                  % Change
                                  {sortColumn === 'percentChange' && (
                                    sortDirection === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />
                                  )}
                                  {sortColumn !== 'percentChange' && <ArrowUpDown className="w-3 h-3 text-neutral-400" />}
                                </div>
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            {displayData.length > 0 ? (
                              displayData.map((holding, index) => (
                                <tr 
                                  key={index} 
                                  className={`border-b border-neutral-100 hover:bg-neutral-50 transition-colors ${
                                    index % 2 === 0 ? 'bg-white' : 'bg-neutral-50/30'
                                  }`}
                                >
                                  <td className="py-5 px-4">
                                  <div className="font-bold text-neutral-900 text-base">{holding.Ticker || holding.ticker || holding.symbol}</div>
                                  <div className="text-xs text-neutral-600">{holding.Category || holding.category || holding.asset_type || 'Unknown'}</div>
                                </td>
                                  <td className="py-5 px-4 text-neutral-700 text-sm">{holding.Category || holding.category || holding.asset_type || 'Unknown'}</td>
                                  <td className="py-5 px-4 text-neutral-700 text-sm">{formatCount(holding.Qty || holding.shares || 0)}</td>
                                  <td className="py-5 px-4 text-neutral-700 text-sm">{formatCurrency(holding.Current_Price || holding.current_price || 0)}</td>
                                  <td className="py-5 px-4">
                                  <div className="font-semibold text-neutral-900 text-sm">{formatCurrency(holding.Total_Value || holding.total_value || 0)}</div>
                                </td>
                                  <td className={`py-5 px-4 font-semibold text-sm ${
                                    (holding.Gain_Loss || holding.gain_loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                                  }`}>
                                    {formatCurrency(holding.Gain_Loss || holding.gain_loss || 0)}
                                </td>
                                  <td className={`py-5 px-4 font-semibold text-sm ${
                                    (holding.Gain_Loss_Percent || holding.gain_loss_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                                  }`}>
                                    {formatPercent(holding.Gain_Loss_Percent || holding.gain_loss_percent || 0)}
                                </td>
                              </tr>
                              ))
                            ) : (
                              <tr>
                                <td colSpan={7} className="py-8 text-center text-neutral-600">
                                  No holdings match your search criteria.
                                </td>
                              </tr>
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-white p-6 rounded-xl border border-neutral-200 shadow-medium text-center">
                      <h3 className="text-lg font-semibold text-neutral-900 mb-2">No Holdings Found</h3>
                      <p className="text-neutral-600 mb-4">You haven&apos;t added any holdings yet.</p>
                      <button
                        onClick={() => setShowAddHoldings(true)}
                        className="bg-gradient-brand text-white px-4 py-2 rounded-xl font-semibold hover:shadow-brand shadow-medium transition-all duration-300"
                      >
                        Add Your First Holding
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Insights Tab */}
              {activeTab === 'insights' && (
                <div className="space-y-6">
                  {/* Investor Level Selector */}
                      <div className="bg-white p-6 rounded-xl border border-neutral-200 shadow-medium">
                        <h3 className="text-lg font-semibold mb-4 text-neutral-900">Your Investment Experience</h3>
                        <div className="flex gap-4">
                          {[
                            { level: 'beginner', label: 'Beginner', description: 'New to investing' },
                            { level: 'intermediate', label: 'Intermediate', description: 'Some experience' },
                            { level: 'expert', label: 'Expert', description: 'Advanced professional' }
                          ].map(({ level, label, description }) => (
                            <button
                              key={level}
                              onClick={() => setInvestorLevel(level as any)}
                              className={`px-4 py-2 rounded-xl border transition-all duration-200 ${
                                investorLevel === level
                                  ? 'bg-gradient-brand text-white border-brand-600 shadow-soft'
                                  : 'bg-white text-neutral-700 border-neutral-300 hover:border-brand-400 hover:bg-neutral-50'
                              }`}
                            >
                              <div className="text-sm font-medium">{label}</div>
                              <div className="text-xs opacity-75">{description}</div>
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Insights Content */}
                      <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-neutral-900">Personalized Insights</h3>
                        {insights.length > 0 ? (
                          insights.map((insight, index) => (
                            <div key={index} className="bg-white p-6 rounded-xl border border-neutral-200 shadow-soft hover:shadow-medium transition-all duration-200">
                              <div className="flex items-start gap-4">
                                <div className={`w-3 h-3 rounded-full mt-2 ${
                                  insight.type === 'education' ? 'bg-blue-500' :
                                  insight.type === 'recommendation' ? 'bg-green-500' :
                                  insight.type === 'warning' ? 'bg-yellow-500' :
                                  insight.type === 'analysis' ? 'bg-purple-500' :
                                  insight.type === 'performance' ? 'bg-brand-500' :
                                  insight.type === 'advanced' ? 'bg-red-500' :
                                  'bg-neutral-500'
                                }`} />
                                <div className="flex-1">
                                  <h4 className="font-semibold text-neutral-900 mb-2">{insight.title}</h4>
                                  <p className="text-neutral-600 mb-3">{insight.message}</p>
                                  <button className="text-brand-600 text-sm font-medium hover:text-brand-700 transition-colors">
                                    {insight.action} →
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="bg-white p-6 rounded-xl border border-neutral-200 shadow-soft text-center">
                            <p className="text-neutral-600">No insights available for your current portfolio.</p>
                          </div>
                        )}
                      </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </ProtectedRoute>
  )
}
