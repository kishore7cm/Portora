'use client'

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts'
import { TrendingUp, TrendingDown, DollarSign, BarChart3, Filter, SortAsc, SortDesc, Bot, Target, Bell, Users } from 'lucide-react'
import BotManagement from '../../components/BotManagement'
import Comparison from '../../components/Comparison'
import OnboardingModal from '../../components/OnboardingModal'
import AlertsDropdown from '../../components/AlertsDropdown'
import CommunityBenchmark from '../../components/CommunityBenchmark'
import ThemeToggle from '../../components/ThemeToggle'
import DashboardWidgets from '../../components/DashboardWidgets'
import { PortfolioSummarySkeleton, ChartSkeleton, PieChartSkeleton, TableSkeleton, AlertsSkeleton } from '../../components/LoadingSkeleton'

interface PortfolioData {
  Category: string
  Ticker: string
  Qty: number
  "Curr $": number
  "Curr %": number
  "Tgt %": number
  "Drift %": number
  RSI: number
  MACD: number
  Market: string
  Trend: string
  Action: string
  Score?: number
  Sentiment?: string
}

interface SummaryData {
  Category: string
  "Curr $": number
  "Curr %": number
  "Tgt %": number
  Drift: number
}

interface Sp500Data {
  Ticker: string
  Name?: string
  Sector?: string
  Price?: number
  Change?: number
  "Change %"?: number
  Volume?: number
  MarketCap?: number
  P_E?: number
  RSI: number
  MACD: number
  Trend: string
  Action: string
  Score?: number
  Reason?: string
}

export default function Dashboard() {
  const router = useRouter()
  const [tab, setTab] = useState("portfolio")
  const [portfolioData, setPortfolioData] = useState<PortfolioData[]>([])
  const [summaryData, setSummaryData] = useState<SummaryData[]>([])
  const [sp500Data, setSp500Data] = useState<Sp500Data[]>([])
  const [historicalData, setHistoricalData] = useState<{month: string, value: number}[]>([])
  const [isRefreshingData, setIsRefreshingData] = useState(false)
  const [projections, setProjections] = useState<any>(null)
  const [isLoadingProjections, setIsLoadingProjections] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [portfolioSummary, setPortfolioSummary] = useState({
    netWorth: 0,
    totalGainLoss: 0,
    totalGainLossPercent: 0,
    annualizedReturn: 0
  })
  const [sortConfig, setSortConfig] = useState<{key: string, direction: 'asc' | 'desc'} | null>(null)
  const [historicalDataTable, setHistoricalDataTable] = useState<any[]>([])
  const [historicalDataLoading, setHistoricalDataLoading] = useState(false)
  const [historicalDataFilter, setHistoricalDataFilter] = useState("")
  const [portfolioHealth, setPortfolioHealth] = useState<any>(null)
  const [portfolioHealthLoading, setPortfolioHealthLoading] = useState(false)
  const [historicalDataSortBy, setHistoricalDataSortBy] = useState("ticker")
  const [historicalDataSortOrder, setHistoricalDataSortOrder] = useState<"asc" | "desc">("asc")
  const [filterSector, setFilterSector] = useState<string>('all')
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [showAlerts, setShowAlerts] = useState(false)
  const [unreadAlertCount, setUnreadAlertCount] = useState(0)

  useEffect(() => {
    // Demo mode: no auth redirect
  }, [router])

  // Force refresh to load data on component mount
  useEffect(() => {
    if (tab === "portfolio") {
      fetchPortfolioData()
    }
  }, [tab])

  // Check onboarding status on component mount
  useEffect(() => {
    const checkOnboardingStatus = async () => {
      try {
        // Check localStorage first for demo
        const hasSeenOnboarding = localStorage.getItem('hasSeenOnboarding')
        if (!hasSeenOnboarding) {
          setShowOnboarding(true)
          return
        }

        // In production, check API
        const response = await fetch('http://localhost:8000/onboarding/status')
        if (response.ok) {
          const data = await response.json()
          if (!data.has_seen_onboarding) {
            setShowOnboarding(true)
          }
        }
      } catch (error) {
        console.error('Error checking onboarding status:', error)
        // Default to showing onboarding if there's an error
        setShowOnboarding(true)
      }
    }

    checkOnboardingStatus()
  }, [])

  // Fetch alert count on component mount
  useEffect(() => {
    const fetchAlertCount = async () => {
      try {
        const response = await fetch('http://localhost:8000/alerts/count')
        if (response.ok) {
          const data = await response.json()
          setUnreadAlertCount(data.unread_count || 0)
        }
      } catch (error) {
        console.error('Error fetching alert count:', error)
      }
    }

    fetchAlertCount()
  }, [])

  const handleOnboardingComplete = () => {
    setShowOnboarding(false)
    localStorage.setItem('hasSeenOnboarding', 'true')
  }

  const calculatePortfolioSummary = (data: PortfolioData[]) => {
    const netWorth = data.reduce((sum, item) => sum + (item["Curr $"] || 0), 0)
    
    // Calculate gain/loss based on historical data if available
    let totalGainLoss = 0
    let totalGainLossPercent = 0
    let annualizedReturn = 0
    
    if (historicalData.length > 0) {
      // Use real historical data for calculations
      const currentValue = historicalData[historicalData.length - 1].value
      const initialValue = historicalData[0].value
      
      totalGainLoss = currentValue - initialValue
      totalGainLossPercent = initialValue > 0 ? (totalGainLoss / initialValue) * 100 : 0
      
      // Calculate annualized return based on 6 months of data
      const months = historicalData.length
      const monthlyReturn = totalGainLossPercent / months
      annualizedReturn = monthlyReturn * 12
    } else {
      // Fallback to conservative estimates if no historical data
      totalGainLoss = netWorth * 0.08 // Assume 8% total gain
      totalGainLossPercent = 8
      annualizedReturn = 16 // Assume 16% annualized return
    }
    
    setPortfolioSummary({
      netWorth,
      totalGainLoss,
      totalGainLossPercent,
      annualizedReturn: Math.max(0, annualizedReturn)
    })
  }

  const fetchPortfolioData = async () => {
    setLoading(true)
    setError("")
    try {
      const response = await fetch('http://localhost:8000/portfolio')
      const data = await response.json()
      
      if (data.error) {
        setError(data.error)
      } else {
        setPortfolioData(data.portfolio || [])
        setSummaryData(data.summary || [])
        setHistoricalData(data.historical || [])
        // Calculate summary after setting historical data
        setTimeout(() => {
          calculatePortfolioSummary(data.portfolio || [])
        }, 100)
      }
    } catch (err) {
      setError("Failed to fetch portfolio data")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchSp500Data = async () => {
    setLoading(true)
    setError("")
    try {
      const response = await fetch('http://localhost:8000/sp500')
      const data = await response.json()
      
      if (data.error) {
        setError(data.error)
      } else {
        setSp500Data(data.sp500 || [])
      }
    } catch (err) {
      setError("Failed to fetch S&P 500 data")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const downloadHistoricalData = async () => {
    setIsRefreshingData(true)
    try {
      const response = await fetch('http://localhost:8000/historical-data/download', { credentials: 'include' })
      const data = await response.json()
      
      if (data.error) {
        setError(data.error)
      } else {
        // Refresh portfolio data to get updated historical values
        await fetchPortfolioData()
        alert(`Downloaded historical data: ${data.successful} successful, ${data.failed} failed`)
      }
    } catch (err) {
      setError("Failed to download historical data")
      console.error(err)
    } finally {
      setIsRefreshingData(false)
    }
  }

  const updateDailyData = async () => {
    setIsRefreshingData(true)
    try {
      const response = await fetch('http://localhost:8000/historical-data/update-daily', { credentials: 'include' })
      const data = await response.json()
      
      if (data.error) {
        setError(data.error)
      } else {
        // Refresh portfolio data to get updated historical values
        await fetchPortfolioData()
        alert(`Daily data updated for ${data.tickers?.length || 0} tickers!`)
      }
    } catch (err) {
      setError("Failed to update daily data")
      console.error(err)
    } finally {
      setIsRefreshingData(false)
    }
  }

  const fetchProjections = async () => {
    setIsLoadingProjections(true)
    try {
      const response = await fetch('http://localhost:8000/projections/portfolio', { credentials: 'include' })
      const data = await response.json()
      
      if (data.error) {
        setError(data.error)
      } else {
        setProjections(data.projections)
      }
    } catch (err) {
      setError("Failed to fetch projections")
      console.error(err)
    } finally {
      setIsLoadingProjections(false)
    }
  }

  const fetchHistoricalDataTable = async () => {
    setHistoricalDataLoading(true)
    try {
      // Get all tickers from portfolio
      const portfolioResponse = await fetch('http://localhost:8000/portfolio', { credentials: 'include' })
      const portfolioData = await portfolioResponse.json()
      
      if (portfolioData.error) {
        setError(portfolioData.error)
        return
      }
      
      const tickers = portfolioData.portfolio?.map((item: any) => item.Ticker) || []
      const historicalDataResults = []
      
      // Fetch historical data for each ticker
      for (const ticker of tickers.slice(0, 20)) { // Limit to first 20 for performance
        try {
          const response = await fetch(`http://localhost:8000/analysis/trend/${ticker}`, { credentials: 'include' })
          const data = await response.json()
          
          if (data.trend_analysis) {
            historicalDataResults.push({
              ticker,
              ...data.trend_analysis,
              dataPoints: data.trend_analysis.historical_prices?.length || 0
            })
          }
        } catch (err) {
          console.error(`Error fetching data for ${ticker}:`, err)
        }
      }
      
      setHistoricalDataTable(historicalDataResults)
    } catch (err) {
      setError("Failed to fetch historical data table")
      console.error(err)
    } finally {
      setHistoricalDataLoading(false)
    }
  }

  const fetchPortfolioHealth = async () => {
    setPortfolioHealthLoading(true)
    try {
      const response = await fetch('http://localhost:8000/portfolio-health', { credentials: 'include' })
      const data = await response.json()
      
      if (data.error) {
        setError(data.error)
      } else {
        setPortfolioHealth(data)
      }
    } catch (err) {
      setError("Failed to fetch portfolio health")
      console.error(err)
    } finally {
      setPortfolioHealthLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("loggedIn")
    router.push("/")
  }

  const handleSort = (key: string) => {
    let direction: 'asc' | 'desc' = 'asc'
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc'
    }
    setSortConfig({ key, direction })
  }

  const getSortedAndFilteredData = () => {
    let filtered = portfolioData
    if (filterSector !== 'all') {
      filtered = portfolioData.filter(item => item.Category === filterSector)
    }
    
    if (sortConfig) {
      filtered.sort((a, b) => {
        const aVal = a[sortConfig.key as keyof PortfolioData] || 0
        const bVal = b[sortConfig.key as keyof PortfolioData] || 0
        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1
        return 0
      })
    }
    
    return filtered
  }

  const getSectors = () => {
    const sectors = [...new Set(portfolioData.map(item => item.Category))]
    return sectors
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case 'BUY': return 'text-green-600 bg-green-100'
      case 'SELL': return 'text-red-600 bg-red-100'
      case 'HOLD': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getSectorPerformance = () => {
    const sectorData = summaryData.map(item => ({
      sector: item.Category,
      performance: Math.random() * 20 - 10, // Mock performance data
      allocation: item["Curr %"] || 0
    }))
    return sectorData
  }

  const getTopGainersLosers = () => {
    // Add mock data for missing fields
    const enrichedData = sp500Data.map(item => ({
      ...item,
      Name: item.Name || `${item.Ticker} Corp`,
      Sector: item.Sector || 'Technology',
      Price: item.Price || Math.random() * 500 + 50,
      "Change %": item["Change %"] || (Math.random() * 20 - 10),
      Change: item.Change || (Math.random() * 20 - 10)
    }))
    
    const sorted = enrichedData.sort((a, b) => (b["Change %"] || 0) - (a["Change %"] || 0))
    return {
      gainers: sorted.slice(0, 10),
      losers: sorted.slice(-10).reverse()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Debug Banner */}
      <div className="bg-red-500 text-white p-4 text-center font-bold">
        DEBUG: Dashboard component is rendering!
      </div>
      
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">Portora Portfolio Advisor</h1>
            </div>
            <div className="flex items-center space-x-4">
              {/* Debug Text */}
              <span className="text-red-500 font-bold">DEBUG TEXT</span>
              {/* Debug Test Button */}
              <button 
                onClick={() => alert('Test button clicked')}
                className="bg-blue-500 text-white px-3 py-1 rounded text-sm mr-2"
              >
                Test
              </button>
              
              {/* Simple Theme Toggle */}
              <button 
                onClick={() => alert('Theme toggle clicked')}
                className="bg-yellow-500 text-white px-3 py-1 rounded text-sm mr-2"
              >
                Theme
              </button>
              
              {/* Alerts Bell */}
              <div className="relative">
                <button
                  onClick={() => setShowAlerts(!showAlerts)}
                  className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <Bell className="w-6 h-6" />
                  {unreadAlertCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {unreadAlertCount > 9 ? '9+' : unreadAlertCount}
                    </span>
                  )}
                </button>
                <AlertsDropdown isOpen={showAlerts} onClose={() => setShowAlerts(false)} />
              </div>
              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
      {/* Sidebar */}
        <div className="w-64 bg-white dark:bg-gray-800 shadow-sm min-h-screen border-r border-gray-200 dark:border-gray-700">
          <nav className="mt-5 px-2">
            <button
              onClick={() => setTab("portfolio")}
              className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium mb-1 ${
                tab === "portfolio"
                  ? "bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300"
                  : "text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
              }`}
            >
              📌 Portfolio
            </button>
            <button
              onClick={() => setTab("sp500")}
              className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium mb-1 ${
                tab === "sp500"
                  ? "bg-blue-100 text-blue-700"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              📈 S&P 500
            </button>
        <button
          onClick={() => setTab("bots")}
          className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium mb-1 ${
            tab === "bots"
              ? "bg-blue-100 text-blue-700"
              : "text-gray-600 hover:bg-gray-50"
          }`}
        >
          <Bot className="w-4 h-4 inline mr-1" />
          Trading Bots
        </button>
        <button
          onClick={() => setTab("comparison")}
          className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium mb-1 ${
            tab === "comparison"
              ? "bg-blue-100 text-blue-700"
              : "text-gray-600 hover:bg-gray-50"
          }`}
        >
          <Target className="w-4 h-4 inline mr-1" />
          Comparison
        </button>
        <button
          onClick={() => setTab("community")}
          className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium mb-1 ${
            tab === "community"
              ? "bg-blue-100 text-blue-700"
              : "text-gray-600 hover:bg-gray-50"
          }`}
        >
          <Users className="w-4 h-4 inline mr-1" />
          Community
        </button>
        <button
          onClick={() => setTab("widgets")}
          className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium mb-1 ${
            tab === "widgets"
              ? "bg-blue-100 text-blue-700"
              : "text-gray-600 hover:bg-gray-50"
          }`}
        >
          <BarChart3 className="w-4 h-4 inline mr-1" />
          Widgets
        </button>
            <button
              onClick={() => setTab("projections")}
              className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium mb-1 ${
                tab === "projections"
                  ? "bg-blue-100 text-blue-700"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              🔮 Projections
            </button>
            <button
              onClick={() => setTab("historical")}
              className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium mb-1 ${
                tab === "historical"
                  ? "bg-blue-100 text-blue-700"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              📊 Historical Data
            </button>
          </nav>
        </div>

      {/* Main Content */}
      <main className="flex-1 p-10 bg-gray-50 overflow-y-auto">
        {tab === "portfolio" && (
          <>
              <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">📌 Portfolio Overview</h1>
                <button 
                  onClick={fetchPortfolioData}
                  disabled={loading}
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? "Loading..." : "Refresh Data"}
                </button>
              </div>

              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                  {error}
                </div>
              )}

              {loading && (
                <div className="space-y-6">
                  <PortfolioSummarySkeleton />
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <PieChartSkeleton />
                    <ChartSkeleton />
                  </div>
                  <TableSkeleton />
                </div>
              )}

              {!loading && !error && portfolioData.length > 0 && (
                <div className="space-y-6">
                  {/* Portfolio Summary Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="flex items-center">
                        <DollarSign className="h-8 w-8 text-blue-600" />
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-500">Net Worth</p>
                          <p className="text-2xl font-bold text-gray-900">${portfolioSummary.netWorth.toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="flex items-center">
                        {portfolioSummary.totalGainLoss >= 0 ? (
                          <TrendingUp className="h-8 w-8 text-green-600" />
                        ) : (
                          <TrendingDown className="h-8 w-8 text-red-600" />
                        )}
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-500">Total Gain/Loss</p>
                          <p className={`text-2xl font-bold ${portfolioSummary.totalGainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            ${portfolioSummary.totalGainLoss.toLocaleString()}
                          </p>
                          <p className={`text-sm ${portfolioSummary.totalGainLossPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {portfolioSummary.totalGainLossPercent >= 0 ? '+' : ''}{portfolioSummary.totalGainLossPercent.toFixed(2)}%
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="flex items-center">
                        <BarChart3 className="h-8 w-8 text-purple-600" />
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-500">Annualized Return</p>
                          <p className="text-2xl font-bold text-purple-600">{portfolioSummary.annualizedReturn}%</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="flex items-center">
                        <Filter className="h-8 w-8 text-orange-600" />
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-500">Total Positions</p>
                          <p className="text-2xl font-bold text-orange-600">{portfolioData.length}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Portfolio Health Section */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex justify-between items-center mb-6">
                      <h3 className="text-lg font-semibold">Portfolio Health</h3>
                      <button 
                        onClick={fetchPortfolioHealth}
                        disabled={portfolioHealthLoading}
                        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
                      >
                        {portfolioHealthLoading ? "Loading..." : "Refresh Health"}
                      </button>
                    </div>

                    {portfolioHealthLoading && (
                      <div className="text-center py-8">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
                        <p className="mt-4 text-gray-600">Loading portfolio health...</p>
                      </div>
                    )}

                    {portfolioHealth && !portfolioHealthLoading && (
                      <div className="space-y-6">
                        {/* Health Score */}
                        <div className="text-center">
                          <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-r from-green-400 to-blue-500 text-white">
                            <div className="text-center">
                              <div className="text-4xl font-bold">{portfolioHealth.health}</div>
                              <div className="text-sm opacity-90">Health Score</div>
                            </div>
                          </div>
                        </div>

                        {/* Driver Scores */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="bg-gray-50 rounded-lg p-4 text-center">
                            <div className="text-2xl font-bold text-blue-600">{portfolioHealth.drivers.diversification}</div>
                            <div className="text-sm text-gray-600">Diversification</div>
                          </div>
                          <div className="bg-gray-50 rounded-lg p-4 text-center">
                            <div className="text-2xl font-bold text-purple-600">{portfolioHealth.drivers.concentration}</div>
                            <div className="text-sm text-gray-600">Concentration</div>
                          </div>
                          <div className="bg-gray-50 rounded-lg p-4 text-center">
                            <div className="text-2xl font-bold text-green-600">{portfolioHealth.drivers.cashDrag}</div>
                            <div className="text-sm text-gray-600">Cash Drag</div>
                          </div>
                          <div className="bg-gray-50 rounded-lg p-4 text-center">
                            <div className="text-2xl font-bold text-orange-600">{portfolioHealth.drivers.volProxy}</div>
                            <div className="text-sm text-gray-600">Volatility (proxy)</div>
                          </div>
                        </div>

                        {/* Asset-Class Drift */}
                        <div>
                          <h4 className="text-md font-semibold mb-4">Asset-Class Drift</h4>
                          <div className="space-y-3">
                            {Object.entries(portfolioHealth.driftAsset).map(([assetClass, data]: [string, any]) => (
                              <div key={assetClass} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                <div className="flex-1">
                                  <div className="font-medium capitalize">{assetClass}</div>
                                  <div className="text-sm text-gray-600">
                                    Current: {data.current}% | Target: {data.target}%
                                  </div>
                                </div>
                                <div className={`text-lg font-bold ${
                                  data.delta > 0 ? 'text-red-600' : data.delta < 0 ? 'text-blue-600' : 'text-gray-600'
                                }`}>
                                  {data.delta > 0 ? '+' : ''}{data.delta}%
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Badges */}
                        <div>
                          <h4 className="text-md font-semibold mb-4">Badges</h4>
                          <div className="flex flex-wrap gap-2">
                            {portfolioHealth.badges.map((badge: string, index: number) => (
                              <span 
                                key={index}
                                className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full"
                              >
                                {badge}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}

                    {!portfolioHealth && !portfolioHealthLoading && (
                      <div className="text-center py-8">
                        <h4 className="text-lg font-semibold text-gray-700 mb-2">No Health Data</h4>
                        <p className="text-gray-500 mb-6">
                          Click "Refresh Health" to load portfolio health analysis
                        </p>
                        <button 
                          onClick={fetchPortfolioHealth}
                          className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-medium"
                        >
                          Load Health Data
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Charts Row */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Portfolio Allocation Chart */}
                    <div className="bg-white rounded-lg shadow p-6">
                      <h3 className="text-lg font-semibold mb-4">Portfolio Allocation</h3>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie
                              data={summaryData.map(item => ({
                                name: item.Category,
                                value: item["Curr %"] || 0
                              }))}
                              cx="50%"
                              cy="50%"
                              innerRadius={60}
                              outerRadius={100}
                              paddingAngle={5}
                              dataKey="value"
                            >
                              {summaryData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={`hsl(${index * 137.5}, 70%, 50%)`} />
                              ))}
                            </Pie>
                            <Tooltip formatter={(value) => [`${Number(value).toFixed(2)}%`, 'Allocation']} />
                            <Legend />
                          </PieChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Performance Chart */}
                    <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Portfolio Performance</h3>
              <div className="flex gap-2">
                <button
                  onClick={downloadHistoricalData}
                  disabled={isRefreshingData}
                  className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isRefreshingData ? 'Downloading...' : 'Download 1 Year'}
                </button>
                <button
                  onClick={updateDailyData}
                  disabled={isRefreshingData}
                  className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isRefreshingData ? 'Updating...' : 'Update Daily'}
                </button>
              </div>
            </div>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={historicalData.length > 0 ? historicalData : [
                          { month: 'Jan', value: Math.max(0, portfolioSummary.netWorth * 0.85) },
                          { month: 'Feb', value: Math.max(0, portfolioSummary.netWorth * 0.88) },
                          { month: 'Mar', value: Math.max(0, portfolioSummary.netWorth * 0.92) },
                          { month: 'Apr', value: Math.max(0, portfolioSummary.netWorth * 0.95) },
                          { month: 'May', value: Math.max(0, portfolioSummary.netWorth * 0.98) },
                          { month: 'Jun', value: portfolioSummary.netWorth }
                        ]}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="month" />
                            <YAxis />
                            <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Portfolio Value']} />
                            <Line type="monotone" dataKey="value" stroke="#3B82F6" strokeWidth={2} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>

                  {/* Portfolio vs S&P 500 Comparison */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-4">Portfolio vs S&P 500 Allocation</h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={[
                          { sector: 'Technology', portfolio: 35, sp500: 28 },
                          { sector: 'Healthcare', portfolio: 20, sp500: 13 },
                          { sector: 'Financials', portfolio: 15, sp500: 11 },
                          { sector: 'Consumer Discretionary', portfolio: 12, sp500: 10 },
                          { sector: 'Industrials', portfolio: 8, sp500: 8 },
                          { sector: 'Communication', portfolio: 6, sp500: 9 },
                          { sector: 'Consumer Staples', portfolio: 4, sp500: 6 }
                        ]}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="sector" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="portfolio" fill="#3B82F6" name="Your Portfolio" />
                          <Bar dataKey="sp500" fill="#10B981" name="S&P 500" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Enhanced Portfolio Table */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex justify-between items-center mb-4">
                      <h2 className="text-xl font-semibold">Portfolio Holdings</h2>
                      <div className="flex gap-4">
                        <select
                          value={filterSector}
                          onChange={(e) => setFilterSector(e.target.value)}
                          className="border border-gray-300 rounded px-3 py-2 text-sm"
                        >
                          <option value="all">All Sectors</option>
                          {getSectors().map(sector => (
                            <option key={sector} value={sector}>{sector}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                    
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th 
                              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                              onClick={() => handleSort('Ticker')}
                            >
                              <div className="flex items-center gap-1">
                                Ticker
                                {sortConfig?.key === 'Ticker' && (
                                  sortConfig.direction === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />
                                )}
                              </div>
                            </th>
                            <th 
                              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                              onClick={() => handleSort('Curr $')}
                            >
                              <div className="flex items-center gap-1">
                                Current Value
                                {sortConfig?.key === 'Curr $' && (
                                  sortConfig.direction === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />
                                )}
                              </div>
                            </th>
                            <th 
                              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                              onClick={() => handleSort('Curr %')}
                            >
                              <div className="flex items-center gap-1">
                                Allocation %
                                {sortConfig?.key === 'Curr %' && (
                                  sortConfig.direction === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />
                                )}
                              </div>
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Performance</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RSI</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MACD</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                        {getSortedAndFilteredData().map((item, index) => {
                          // Calculate realistic performance based on actual Score data
                          const baseValue = item["Curr $"] || 0
                          const score = item.Score || 0
                          const gainLossPercent = (score / 100) * 10 // Convert score to percentage
                          const gainLoss = baseValue * (gainLossPercent / 100)
                          return (
                              <tr key={index} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                  {item.Ticker}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  ${item["Curr $"]?.toLocaleString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {item["Curr %"]?.toFixed(1)}%
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                  <div className="flex items-center gap-2">
                                    <span className={`font-medium ${gainLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                      {gainLoss >= 0 ? '+' : ''}${gainLoss.toLocaleString()}
                                    </span>
                                    <span className={`text-xs ${gainLossPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                      ({gainLossPercent >= 0 ? '+' : ''}{gainLossPercent}%)
                                    </span>
                                  </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                    (item.RSI || 0) > 70 ? 'bg-red-100 text-red-800' : 
                                    (item.RSI || 0) < 30 ? 'bg-green-100 text-green-800' : 
                                    'bg-yellow-100 text-yellow-800'
                                  }`}>
                                    {item.RSI?.toFixed(1)}
                                  </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {item.MACD?.toFixed(3)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getActionColor(item.Action)}`}>
                                    {item.Action}
                                  </span>
                                </td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {!loading && !error && portfolioData.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-500 text-lg">No portfolio data available</p>
                  <button 
                    onClick={fetchPortfolioData}
                    className="mt-4 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
                  >
                    Load Portfolio Data
                  </button>
                </div>
              )}
            </>
          )}

        {tab === "bots" && (
            <BotManagement />
        )}
        {tab === "comparison" && (
            <Comparison />
        )}

        {tab === "community" && (
            <CommunityBenchmark />
        )}

        {tab === "widgets" && (
            <DashboardWidgets 
              portfolioData={portfolioData}
              sp500Data={sp500Data}
            />
        )}

        {tab === "sp500" && (
          <>
              <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">📈 S&P 500 Pulse</h1>
                <button 
                  onClick={fetchSp500Data}
                  disabled={loading}
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? "Loading..." : "Refresh Data"}
                </button>
              </div>

              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                  {error}
                </div>
              )}

              {loading && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    {Array.from({ length: 4 }).map((_, index) => (
                      <div key={index} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
                        <div className="animate-pulse">
                          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
                          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-2"></div>
                          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <TableSkeleton rows={10} />
                </div>
              )}

              {!loading && !error && sp500Data.length > 0 && (
                <div className="space-y-6">
                  {/* Market Overview Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="flex items-center">
                        <BarChart3 className="h-8 w-8 text-blue-600" />
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-500">S&P 500 Index</p>
                          <p className="text-2xl font-bold text-gray-900">4,567.89</p>
                          <p className="text-sm text-green-600">+1.23%</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="flex items-center">
                        <TrendingUp className="h-8 w-8 text-green-600" />
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-500">Advancing</p>
                          <p className="text-2xl font-bold text-green-600">312</p>
                          <p className="text-sm text-gray-500">stocks</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="flex items-center">
                        <TrendingDown className="h-8 w-8 text-red-600" />
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-500">Declining</p>
                          <p className="text-2xl font-bold text-red-600">188</p>
                          <p className="text-sm text-gray-500">stocks</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-white rounded-lg shadow p-6">
                      <div className="flex items-center">
                        <DollarSign className="h-8 w-8 text-purple-600" />
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-500">Volume</p>
                          <p className="text-2xl font-bold text-purple-600">3.2B</p>
                          <p className="text-sm text-gray-500">shares</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Sector Performance Heatmap */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-4">Sector Performance Heatmap</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                      {getSectorPerformance().map((sector, index) => (
                        <div key={sector.sector} className="text-center">
                          <div 
                            className={`h-16 rounded-lg flex items-center justify-center text-white font-semibold ${
                              sector.performance > 5 ? 'bg-green-600' :
                              sector.performance > 0 ? 'bg-green-400' :
                              sector.performance > -5 ? 'bg-red-400' : 'bg-red-600'
                            }`}
                          >
                            {sector.performance > 0 ? '+' : ''}{sector.performance.toFixed(1)}%
                          </div>
                          <p className="text-xs text-gray-600 mt-2">{sector.sector}</p>
                          <p className="text-xs text-gray-500">{sector.allocation.toFixed(1)}%</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Top Gainers and Losers */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-white rounded-lg shadow p-6">
                      <h3 className="text-lg font-semibold mb-4 text-green-600">Top 10 Gainers</h3>
                      <div className="space-y-3">
                        {getTopGainersLosers().gainers.map((stock, index) => (
                          <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100">
                            <div>
                              <p className="font-medium text-gray-900">{stock.Ticker}</p>
                              <p className="text-sm text-gray-500">{stock.Name}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-medium text-green-600">+{stock["Change %"]?.toFixed(2)}%</p>
                              <p className="text-sm text-gray-500">${stock.Price?.toFixed(2)}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                      <h3 className="text-lg font-semibold mb-4 text-red-600">Top 10 Losers</h3>
                      <div className="space-y-3">
                        {getTopGainersLosers().losers.map((stock, index) => (
                          <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100">
                            <div>
                              <p className="font-medium text-gray-900">{stock.Ticker}</p>
                              <p className="text-sm text-gray-500">{stock.Name}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-medium text-red-600">{stock["Change %"]?.toFixed(2)}%</p>
                              <p className="text-sm text-gray-500">${stock.Price?.toFixed(2)}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* S&P 500 Table */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-xl font-semibold mb-4">S&P 500 Stocks</h2>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ticker</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sector</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Change %</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RSI</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {getTopGainersLosers().gainers.concat(getTopGainersLosers().losers).slice(0, 20).map((item, index) => (
                            <tr key={index} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                {item.Ticker}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {item.Name}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {item.Sector}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                ${item.Price?.toFixed(2)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                <span className={`font-medium ${(item["Change %"] || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                  {(item["Change %"] || 0) >= 0 ? '+' : ''}{item["Change %"]?.toFixed(2)}%
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                  (item.RSI || 0) > 70 ? 'bg-red-100 text-red-800' : 
                                  (item.RSI || 0) < 30 ? 'bg-green-100 text-green-800' : 
                                  'bg-yellow-100 text-yellow-800'
                                }`}>
                                  {item.RSI?.toFixed(1)}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getActionColor(item.Action)}`}>
                                  {item.Action}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {!loading && !error && sp500Data.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-500 text-lg">No S&P 500 data available</p>
                  <button 
                    onClick={fetchSp500Data}
                    className="mt-4 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
                  >
                    Load S&P 500 Data
                  </button>
                </div>
              )}
            </>
          )}

          {tab === "projections" && (
            <>
              <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">🔮 Portfolio Projections</h1>
                <button 
                  onClick={fetchProjections}
                  disabled={isLoadingProjections}
                  className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:opacity-50"
                >
                  {isLoadingProjections ? "Generating..." : "Generate Projections"}
                </button>
              </div>

              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                  {error}
                </div>
              )}

              {projections && (
                <div className="space-y-6">
                  {/* Projection Summary */}
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h2 className="text-xl font-semibold mb-4">📊 Projection Summary</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h3 className="text-sm font-medium text-blue-600">Current Value</h3>
                        <p className="text-2xl font-bold text-blue-900">
                          ${projections.current_value?.toLocaleString() || 'N/A'}
                        </p>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h3 className="text-sm font-medium text-green-600">30-Day Projection</h3>
                        <p className="text-2xl font-bold text-green-900">
                          ${projections.projected_30_day?.toLocaleString() || 'N/A'}
                        </p>
                        <p className="text-sm text-green-600">
                          {projections.expected_return_30_day > 0 ? '+' : ''}{projections.expected_return_30_day}%
                        </p>
                      </div>
                      <div className="bg-purple-50 p-4 rounded-lg">
                        <h3 className="text-sm font-medium text-purple-600">90-Day Projection</h3>
                        <p className="text-2xl font-bold text-purple-900">
                          ${projections.projected_90_day?.toLocaleString() || 'N/A'}
                        </p>
                        <p className="text-sm text-purple-600">
                          {projections.expected_return_90_day > 0 ? '+' : ''}{projections.expected_return_90_day}%
                        </p>
                      </div>
                    </div>
                    <div className="mt-4 p-3 bg-gray-50 rounded">
                      <p className="text-sm text-gray-600">
                        <strong>Confidence Score:</strong> {(projections.average_confidence * 100).toFixed(1)}%
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Based on historical trend analysis and volatility patterns
                      </p>
                    </div>
                  </div>

                  {/* Projection Chart */}
                  {projections.projections && projections.projections.length > 0 && (
                    <div className="bg-white p-6 rounded-lg shadow">
                      <h2 className="text-xl font-semibold mb-4">📈 90-Day Projection Trend</h2>
                      <div className="h-64">
                        <LineChart data={projections.projections.map((p: any, index: number) => ({
                          day: `Day ${p.day}`,
                          value: p.projected_value,
                          confidence: p.confidence
                        }))}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="day" />
                          <YAxis />
                          <Tooltip 
                            formatter={(value: any, name: string) => [
                              name === 'value' ? `$${Number(value).toLocaleString()}` : `${(Number(value) * 100).toFixed(1)}%`,
                              name === 'value' ? 'Projected Value' : 'Confidence'
                            ]}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="value" 
                            stroke="#8b5cf6" 
                            strokeWidth={2}
                            dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 4 }}
                          />
                        </LineChart>
                      </div>
                    </div>
                  )}

                  {/* Risk Analysis */}
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h2 className="text-xl font-semibold mb-4">⚠️ Risk Analysis</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h3 className="font-medium text-gray-700 mb-2">Projection Methodology</h3>
                        <ul className="text-sm text-gray-600 space-y-1">
                          <li>• Based on historical price trends and volatility</li>
                          <li>• Uses Monte Carlo simulation for price forecasting</li>
                          <li>• Confidence scores reflect data quality and trend strength</li>
                          <li>• Projections are probabilistic, not guarantees</li>
                        </ul>
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-700 mb-2">Important Disclaimers</h3>
                        <ul className="text-sm text-gray-600 space-y-1">
                          <li>• Past performance doesn't guarantee future results</li>
                          <li>• Market conditions can change rapidly</li>
                          <li>• Use projections as guidance, not investment advice</li>
                          <li>• Consider consulting a financial advisor</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {!projections && !isLoadingProjections && (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🔮</div>
                  <h2 className="text-xl font-semibold text-gray-700 mb-2">Generate Portfolio Projections</h2>
                  <p className="text-gray-500 mb-6">
                    Get AI-powered projections based on historical data analysis and trend patterns
                  </p>
                  <button 
                    onClick={fetchProjections}
                    className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 font-medium"
                  >
                    Generate Projections
                  </button>
                </div>
              )}

              {isLoadingProjections && (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Analyzing historical data and generating projections...</p>
                </div>
              )}
            </>
          )}

          {tab === "historical" && (
            <>
              <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">📊 Historical Data Verification</h1>
                <button 
                  onClick={fetchHistoricalDataTable}
                  disabled={historicalDataLoading}
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
                >
                  {historicalDataLoading ? "Loading..." : "Refresh Data"}
                </button>
              </div>

              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
                  {error}
                </div>
              )}

              {/* Filters and Controls */}
              <div className="bg-white p-6 rounded-lg shadow mb-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Filter by Ticker
                    </label>
                    <input
                      type="text"
                      placeholder="Search ticker..."
                      value={historicalDataFilter}
                      onChange={(e) => setHistoricalDataFilter(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Sort By
                    </label>
                    <select
                      value={historicalDataSortBy}
                      onChange={(e) => setHistoricalDataSortBy(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="ticker">Ticker</option>
                      <option value="dataPoints">Data Points</option>
                      <option value="volatility">Volatility</option>
                      <option value="r_squared">R-Squared</option>
                      <option value="slope">Slope</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Sort Order
                    </label>
                    <select
                      value={historicalDataSortOrder}
                      onChange={(e) => setHistoricalDataSortOrder(e.target.value as "asc" | "desc")}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="asc">Ascending</option>
                      <option value="desc">Descending</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Data Summary */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-2xl font-bold text-blue-600">
                    {historicalDataTable.length}
                  </div>
                  <div className="text-sm text-gray-600">Total Assets</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-2xl font-bold text-green-600">
                    {historicalDataTable.filter(item => item.dataPoints > 100).length}
                  </div>
                  <div className="text-sm text-gray-600">Rich Data (&gt;100 points)</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-2xl font-bold text-yellow-600">
                    {historicalDataTable.filter(item => item.dataPoints < 50).length}
                  </div>
                  <div className="text-sm text-gray-600">Limited Data (&lt;50 points)</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                  <div className="text-2xl font-bold text-purple-600">
                    {historicalDataTable.length > 0 ? 
                      (historicalDataTable.reduce((sum, item) => sum + item.dataPoints, 0) / historicalDataTable.length).toFixed(0) : 0
                    }
                  </div>
                  <div className="text-sm text-gray-600">Avg Data Points</div>
                </div>
              </div>

              {/* Data Table */}
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Ticker
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Data Points
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Volatility
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          R-Squared
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Slope
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Trend
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {historicalDataTable
                        .filter(item => 
                          historicalDataFilter === "" || 
                          item.ticker.toLowerCase().includes(historicalDataFilter.toLowerCase())
                        )
                        .sort((a, b) => {
                          const aVal = a[historicalDataSortBy] || 0
                          const bVal = b[historicalDataSortBy] || 0
                          return historicalDataSortOrder === "asc" ? 
                            (aVal > bVal ? 1 : -1) : 
                            (aVal < bVal ? 1 : -1)
                        })
                        .map((item, index) => (
                        <tr key={index} className={index % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {item.ticker}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              item.dataPoints > 100 ? 'bg-green-100 text-green-800' :
                              item.dataPoints > 50 ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {item.dataPoints}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {(item.volatility * 100).toFixed(2)}%
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {(item.r_squared * 100).toFixed(1)}%
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {item.slope > 0 ? '+' : ''}{item.slope.toFixed(4)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              item.slope > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {item.slope > 0 ? '↗️ Up' : '↘️ Down'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              item.dataPoints > 100 ? 'bg-green-100 text-green-800' :
                              item.dataPoints > 50 ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {item.dataPoints > 100 ? '✅ Good' :
                               item.dataPoints > 50 ? '⚠️ Fair' : '❌ Poor'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {historicalDataTable.length === 0 && !historicalDataLoading && (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📊</div>
                  <h2 className="text-xl font-semibold text-gray-700 mb-2">No Historical Data</h2>
                  <p className="text-gray-500 mb-6">
                    Click "Refresh Data" to load historical data verification table
                  </p>
                  <button 
                    onClick={fetchHistoricalDataTable}
                    className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-medium"
                  >
                    Load Historical Data
                  </button>
                </div>
              )}

              {historicalDataLoading && (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Loading historical data verification...</p>
                </div>
              )}
          </>
        )}
      </main>
      </div>

      {/* Onboarding Modal */}
      <OnboardingModal
        isOpen={showOnboarding}
        onClose={() => setShowOnboarding(false)}
        onComplete={handleOnboardingComplete}
      />
    </div>
  )
}
