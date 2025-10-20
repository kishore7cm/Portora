'use client'

import { useEffect, useState } from "react"
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
  LogOut
} from 'lucide-react'
import Link from 'next/link'
import { yachtClubTheme } from '@/styles/yachtClubTheme'
import { formatCurrency, formatPercent, formatCount } from '@/lib/formatters'
import ProtectedRoute from '@/components/Auth/ProtectedRoute'
import { useAuth } from '@/hooks/useAuth'
import { doc, setDoc } from 'firebase/firestore'
import { db } from '@/lib/firebaseClient'

export default function SimpleDashboard() {
  const { user, logout } = useAuth()
  const router = useRouter()
  
  // State for portfolio data
  const [portfolioData, setPortfolioData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  
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

  // Redirect to onboarding if no user
  useEffect(() => {
    if (!user) {
      console.log('🔍 No user found, redirecting to onboarding')
      router.push('/onboarding')
      return
    }
  }, [user, router])

  // Fetch portfolio data from Firebase
  useEffect(() => {
    const fetchPortfolioData = async () => {
      if (!user) {
        return
      }

      try {
        setLoading(true)
        const userId = user.uid
        console.log('🔍 Fetching portfolio data for user:', userId)
        console.log('🔍 User object:', user)
        
        // Try API first, but fallback to test data if API fails
        try {
          console.log('🔄 Testing portfolio API endpoint...')
          const response = await fetch(`/api/portfolio?user_id=${userId}`)
          console.log('🔍 Portfolio API response status:', response.status)
          
          if (response.ok) {
            const data = await response.json()
            console.log('📊 Portfolio data response:', data)
            
            if (data.data && data.data.length > 0) {
              console.log('✅ User has portfolio data:', data.data.length, 'holdings')
              console.log('📊 Holdings data:', data.data)
              setPortfolioData(data.data)
              return
            }
          } else {
            console.log('⚠️ API returned error status:', response.status)
            throw new Error(`API returned ${response.status}: ${response.statusText}`)
          }
        } catch (apiError) {
          console.log('⚠️ API failed, trying direct Firebase connection:', apiError)
          
          // Try direct Firebase connection as fallback
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
              
              // Check if portfolio data has holdings
              if (portfolioData.holdings && Array.isArray(portfolioData.holdings)) {
                console.log('✅ Found holdings in portfolio_data collection')
                const holdings = portfolioData.holdings
                
                // Transform the data to match dashboard format
                const transformedHoldings = holdings.map((holding: any) => ({
                  Ticker: holding.Ticker || holding.ticker || holding.symbol,
                  Category: holding.Category || holding.category || holding.asset_type || 'Stock',
                  Qty: holding.Qty || holding.qty || holding.quantity || 0,
                  Current_Price: holding.Current_Price || holding.current_price || holding.price || 0,
                  Total_Value: holding.Total_Value || holding.total_value || holding.value || 0,
                  Gain_Loss: holding.Gain_Loss || holding.gain_loss || 0,
                  Gain_Loss_Percent: holding.Gain_Loss_Percent || holding.gain_loss_percent || 0,
                  Brokerage: holding.Brokerage || holding.brokerage || 'Unknown',
                  last_updated: holding.last_updated || new Date().toISOString()
                }))
                
                console.log('✅ Transformed holdings:', transformedHoldings)
                setPortfolioData(transformedHoldings)
                return
              }
            }
            
            console.log('⚠️ No portfolio data found in portfolio_data collection')
          } catch (firebaseError) {
            console.log('❌ Direct Firebase connection failed:', firebaseError)
          }
        }
        
        // No fallback test data - show empty state instead
        console.log('⚠️ No portfolio data available - showing empty state')
        setPortfolioData([])
        
      } catch (error) {
        console.log('❌ Error fetching data:', error)
        setPortfolioData([])
      } finally {
        setLoading(false)
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

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gradient-to-br from-[#FDFBF7] to-[#EDE9E3] flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#C9A66B]"></div>
        </div>
      </ProtectedRoute>
    )
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

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-white">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div className="text-left flex-1">
              <h1 className="text-4xl font-bold text-black mb-2">Portfolio</h1>
              <p className="text-gray-500 text-sm">Track your investments and performance</p>
            </div>
            
            {/* Profile and Logout Buttons */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-gray-700">
                <User className="w-4 h-4" />
                <span className="font-medium text-sm">{user?.displayName || user?.email || 'User'}</span>
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-2 bg-[#C9A66B] text-white px-4 py-2 rounded-lg font-medium text-sm hover:bg-[#1C3D5A] transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>

          <div className="flex gap-6">
            {/* Sidebar */}
            <div className="w-64 flex-shrink-0">
              <nav className="bg-[#F5F1EB] rounded-lg p-4 shadow-lg space-y-2">
                {navigationTabs.map(({ id, label, icon: Icon, description }) => (
                  <button
                    key={id}
                    onClick={() => setActiveTab(id)}
                    className={`w-full flex items-center px-3 py-2 rounded-lg text-[#1C3D5A] hover:bg-[#EDE9E3] hover:text-[#C9A66B] transition-all ${
                      activeTab === id ? "bg-[#1C3D5A] text-[#FDFBF7]" : ""
                    }`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    <span className="font-medium">{label}</span>
                  </button>
                ))}
              </nav>
            </div>

            {/* Main Content */}
            <div className="flex-1 min-w-0">
              {/* Debug Information */}
              {process.env.NODE_ENV === 'development' && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                  <h4 className="font-medium text-yellow-800 mb-2">Debug Information:</h4>
                  <div className="text-sm text-yellow-700 space-y-1">
                    <p>User: {user ? `${user.email} (${user.uid})` : 'Not logged in'}</p>
                    <p>Loading: {loading ? 'Yes' : 'No'}</p>
                    <p>Portfolio Data Count: {portfolioData.length}</p>
                    <p>Show Add Holdings: {showAddHoldings ? 'Yes' : 'No'}</p>
                    <p>Active Tab: {activeTab}</p>
                    <p>Summary Tab Condition: {activeTab === 'summary' && portfolioData.length > 0 ? 'TRUE' : 'FALSE'}</p>
                    {portfolioData.length > 0 && (
                      <div>
                        <p>First Holding: {JSON.stringify(portfolioData[0], null, 2)}</p>
                        <p>All Holdings: {JSON.stringify(portfolioData, null, 2)}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}


              {/* Add Holdings Form */}
              {showAddHoldings && (
                <div className="space-y-6">
                  <div className="bg-white p-6 rounded-2xl shadow-lg border">
                    <div className="flex justify-between items-center mb-6">
                      <h3 className="text-xl font-semibold text-[#1C3D5A]">Add New Holdings</h3>
                      <button
                        onClick={() => setShowAddHoldings(false)}
                        className="text-[#5A6A73] hover:text-[#1C3D5A] transition-colors"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>

                    {/* Current Holdings List */}
                    {newHoldings.length > 0 && (
                      <div className="mb-6">
                        <h4 className="text-lg font-medium text-[#1C3D5A] mb-3">Added Holdings ({newHoldings.length})</h4>
                        <div className="space-y-2">
                          {newHoldings.map((holding, index) => (
                            <div key={index} className="bg-[#F5F1EB] p-3 rounded-lg flex justify-between items-center">
                              <div>
                                <span className="font-medium text-[#1C3D5A]">{holding.Ticker}</span>
                                <span className="text-[#5A6A73] ml-2">({holding.Category})</span>
                              </div>
                              <div className="text-[#1C3D5A] font-medium">
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
                        <label className="block text-sm font-medium text-[#1C3D5A] mb-1">Ticker/Symbol</label>
                        <input
                          type="text"
                          placeholder="e.g., AAPL, VTI, BTC"
                          value={currentHolding.ticker}
                          onChange={(e) => setCurrentHolding(prev => ({ ...prev, ticker: e.target.value.toUpperCase() }))}
                          className="w-full px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-[#1C3D5A] mb-1">Category</label>
                        <select
                          value={currentHolding.category}
                          onChange={(e) => setCurrentHolding(prev => ({ ...prev, category: e.target.value }))}
                          className="w-full px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
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
                        <label className="block text-sm font-medium text-[#1C3D5A] mb-1">Total Value ($)</label>
                        <input
                          type="number"
                          placeholder="e.g., 10000"
                          value={currentHolding.total_value || ''}
                          onChange={(e) => setCurrentHolding(prev => ({ ...prev, total_value: parseFloat(e.target.value) || 0 }))}
                          className="w-full px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-[#1C3D5A] mb-1">Brokerage (Optional)</label>
                        <input
                          type="text"
                          placeholder="e.g., Fidelity, Vanguard"
                          value={currentHolding.brokerage}
                          onChange={(e) => setCurrentHolding(prev => ({ ...prev, brokerage: e.target.value }))}
                          className="w-full px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-[#1C3D5A] mb-1">Quantity (Optional)</label>
                        <input
                          type="number"
                          placeholder="e.g., 100"
                          value={currentHolding.qty || ''}
                          onChange={(e) => setCurrentHolding(prev => ({ ...prev, qty: parseFloat(e.target.value) || 0 }))}
                          className="w-full px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-[#1C3D5A] mb-1">Price per Share (Optional)</label>
                        <input
                          type="number"
                          placeholder="e.g., 150.00"
                          value={currentHolding.current_price || ''}
                          onChange={(e) => setCurrentHolding(prev => ({ ...prev, current_price: parseFloat(e.target.value) || 0 }))}
                          className="w-full px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                        />
                      </div>
                    </div>

                    {/* Success/Error Messages */}
                    {addHoldingSuccess && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                        <div className="flex items-center">
                          <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                          <p className="text-green-600">{addHoldingSuccess}</p>
                        </div>
                      </div>
                    )}

                    {addHoldingError && (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
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
                        className="bg-[#C9A66B] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#1C3D5A] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        {addHoldingLoading ? 'Adding...' : 'Add This Holding'}
                      </button>

                      {newHoldings.length > 0 && (
                        <button
                          onClick={saveAllHoldings}
                          disabled={addHoldingLoading}
                          className="bg-[#1C3D5A] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#C9A66B] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
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
                <div className="space-y-6">
                  
                  {/* Add Holdings Button */}
                  {portfolioData.length > 0 && (
                    <div className="flex justify-end">
                      <button
                        onClick={() => setShowAddHoldings(true)}
                        className="bg-[#C9A66B] text-white px-4 py-2 rounded-lg font-semibold hover:bg-[#1C3D5A] transition-colors flex items-center"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Add More Holdings
                      </button>
                    </div>
                  )}

                  {/* Show data if available, otherwise show empty state */}
                  {portfolioData.length > 0 ? (
                    <>
                      {/* 7 Key Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-white p-6 rounded-lg border border-gray-200">
                      <h3 className="text-xs font-medium text-gray-500 mb-2">Total Portfolio Value</h3>
                      <h2 className="text-xl font-bold text-black">{formatCurrency(metrics.totalValue)}</h2>
                      <p className="text-xs text-gray-400 mt-2">Total value of all holdings</p>
                    </div>

                    <div className="bg-white p-6 rounded-lg border border-gray-200">
                      <h3 className="text-xs font-medium text-gray-500 mb-2">Cash Allocation</h3>
                      <h2 className="text-lg font-bold text-black">{formatPercent(metrics.cashAllocation)}</h2>
                    </div>

                    <div className="bg-white p-6 rounded-lg border border-gray-200">
                      <h3 className="text-xs font-medium text-gray-500 mb-2">Stock Allocation</h3>
                      <h2 className="text-lg font-bold text-black">{formatPercent(metrics.stockAllocation)}</h2>
                    </div>

                    <div className="bg-white p-6 rounded-lg border border-gray-200">
                      <h3 className="text-xs font-medium text-gray-500 mb-2">Holdings Count</h3>
                      <h2 className="text-lg font-bold text-black">{formatCount(metrics.holdingsCount)}</h2>
                    </div>
                  </div>

                  {/* Holdings Table */}
                  <div className="bg-white p-6 rounded-lg border border-gray-200">
                    <h3 className="text-base font-semibold mb-4 text-black">Your Holdings</h3>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-gray-200">
                            <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">Ticker</th>
                            <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">Category</th>
                            <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">Quantity</th>
                            <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">Price</th>
                            <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">Value</th>
                            <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">Gain/Loss</th>
                            <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">% Change</th>
                          </tr>
                        </thead>
                        <tbody>
                          {portfolioData.map((holding, index) => (
                            <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                              <td className="py-4 px-4">
                                <div className="font-bold text-black text-base">{holding.Ticker || holding.ticker || holding.symbol}</div>
                                <div className="text-xs text-gray-500">{holding.Category || holding.category || holding.asset_type || 'Unknown'}</div>
                              </td>
                              <td className="py-4 px-4 text-gray-600 text-sm">{formatCount(holding.Qty || holding.shares || 0)}</td>
                              <td className="py-4 px-4 text-gray-600 text-sm">{formatCurrency(holding.Current_Price || holding.current_price || 0)}</td>
                              <td className="py-4 px-4">
                                <div className="font-semibold text-black text-sm">{formatCurrency(holding.Total_Value || holding.total_value || 0)}</div>
                                <div className={`text-xs font-medium ${
                                  (holding.Gain_Loss_Percent || holding.gain_loss_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                  {formatPercent(holding.Gain_Loss_Percent || holding.gain_loss_percent || 0)}
                                </div>
                              </td>
                              <td className={`py-4 px-4 font-semibold text-sm ${
                                (holding.Gain_Loss || holding.gain_loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {formatCurrency(holding.Gain_Loss || holding.gain_loss || 0)}
                              </td>
                              <td className={`py-4 px-4 font-semibold text-sm ${
                                (holding.Gain_Loss_Percent || holding.gain_loss_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {formatPercent(holding.Gain_Loss_Percent || holding.gain_loss_percent || 0)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                    </>
                  ) : (
                    <div className="text-center py-20">
                      <div className="max-w-md mx-auto">
                        <div className="w-24 h-24 bg-[#F5F1EB] rounded-full flex items-center justify-center mx-auto mb-6">
                          <TrendingUp className="w-12 h-12 text-[#C9A66B]" />
                        </div>
                        <h2 className="text-2xl font-bold text-[#1C3D5A] mb-4">Complete Your Portfolio Setup</h2>
                        <p className="text-[#5A6A73] mb-8">
                          To get started with portfolio tracking and insights, please add your investment holdings. 
                          This will help us provide you with accurate analytics and performance tracking.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                          <button 
                            onClick={() => setShowAddHoldings(true)}
                            className="bg-[#C9A66B] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#1C3D5A] transition-colors flex items-center justify-center"
                          >
                            <Plus className="w-4 h-4 mr-2" />
                            Add Holdings
                          </button>
                          <Link 
                            href="/onboarding" 
                            className="border-2 border-[#C9A66B] text-[#C9A66B] px-6 py-3 rounded-lg font-semibold hover:bg-[#C9A66B] hover:text-white transition-colors"
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
                    <div className="bg-white p-6 rounded-lg border border-gray-200">
                      <h3 className="text-base font-semibold mb-4 text-black">All Holdings</h3>
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="border-b border-gray-200">
                              <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">Ticker</th>
                              <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">Category</th>
                              <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">Quantity</th>
                              <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">Price</th>
                              <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">Value</th>
                              <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">Gain/Loss</th>
                              <th className="text-left py-3 px-4 text-gray-500 font-medium text-xs">% Change</th>
                            </tr>
                          </thead>
                          <tbody>
                            {portfolioData.map((holding, index) => (
                              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                                <td className="py-4 px-4">
                                  <div className="font-bold text-black text-base">{holding.Ticker || holding.ticker || holding.symbol}</div>
                                  <div className="text-xs text-gray-500">{holding.Category || holding.category || holding.asset_type || 'Unknown'}</div>
                                </td>
                                <td className="py-4 px-4 text-gray-600 text-sm">{formatCount(holding.Qty || holding.shares || 0)}</td>
                                <td className="py-4 px-4 text-gray-600 text-sm">{formatCurrency(holding.Current_Price || holding.current_price || 0)}</td>
                                <td className="py-4 px-4">
                                  <div className="font-semibold text-black text-sm">{formatCurrency(holding.Total_Value || holding.total_value || 0)}</div>
                                  <div className={`text-xs font-medium ${
                                    (holding.Gain_Loss_Percent || holding.gain_loss_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                                  }`}>
                                    {formatPercent(holding.Gain_Loss_Percent || holding.gain_loss_percent || 0)}
                                  </div>
                                </td>
                                <td className="py-4 px-4">
                                  <div className={`font-semibold text-sm ${
                                    (holding.Gain_Loss || holding.gain_loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                                  }`}>
                                    {formatCurrency(holding.Gain_Loss || holding.gain_loss || 0)}
                                  </div>
                                </td>
                                <td className="py-4 px-4">
                                  <div className={`text-sm font-medium ${
                                    (holding.Gain_Loss_Percent || holding.gain_loss_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                                  }`}>
                                    {formatPercent(holding.Gain_Loss_Percent || holding.gain_loss_percent || 0)}
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-white p-6 rounded-lg border border-gray-200 text-center">
                      <h3 className="text-lg font-semibold text-gray-700 mb-2">No Holdings Found</h3>
                      <p className="text-gray-500 mb-4">You haven't added any holdings yet.</p>
                      <button
                        onClick={() => setShowAddHoldings(true)}
                        className="bg-[#C9A66B] text-white px-4 py-2 rounded-lg font-semibold hover:bg-[#1C3D5A] transition-colors"
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
                      <div className="bg-white p-6 rounded-lg border border-gray-200">
                        <h3 className="text-lg font-semibold mb-4 text-black">Your Investment Experience</h3>
                        <div className="flex gap-4">
                          {[
                            { level: 'beginner', label: 'Beginner', description: 'New to investing' },
                            { level: 'intermediate', label: 'Intermediate', description: 'Some experience' },
                            { level: 'expert', label: 'Expert', description: 'Advanced professional' }
                          ].map(({ level, label, description }) => (
                            <button
                              key={level}
                              onClick={() => setInvestorLevel(level as any)}
                              className={`px-4 py-2 rounded-lg border transition-colors ${
                                investorLevel === level
                                  ? 'bg-[#C9A66B] text-white border-[#C9A66B]'
                                  : 'bg-white text-gray-700 border-gray-300 hover:border-[#C9A66B]'
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
                        <h3 className="text-lg font-semibold text-black">Personalized Insights</h3>
                        {insights.length > 0 ? (
                          insights.map((insight, index) => (
                            <div key={index} className="bg-white p-6 rounded-lg border border-gray-200">
                              <div className="flex items-start gap-4">
                                <div className={`w-3 h-3 rounded-full mt-2 ${
                                  insight.type === 'education' ? 'bg-blue-500' :
                                  insight.type === 'recommendation' ? 'bg-green-500' :
                                  insight.type === 'warning' ? 'bg-yellow-500' :
                                  insight.type === 'analysis' ? 'bg-purple-500' :
                                  insight.type === 'performance' ? 'bg-indigo-500' :
                                  insight.type === 'advanced' ? 'bg-red-500' :
                                  'bg-gray-500'
                                }`} />
                                <div className="flex-1">
                                  <h4 className="font-semibold text-black mb-2">{insight.title}</h4>
                                  <p className="text-gray-600 mb-3">{insight.message}</p>
                                  <button className="text-[#C9A66B] text-sm font-medium hover:underline">
                                    {insight.action} →
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="bg-white p-6 rounded-lg border border-gray-200 text-center">
                            <p className="text-gray-500">No insights available for your current portfolio.</p>
                          </div>
                        )}
                      </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}
