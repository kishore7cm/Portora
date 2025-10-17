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

  // Navigation tabs
  const navigationTabs = [
    { id: 'summary', label: 'Summary', icon: Home, description: 'Portfolio overview and key metrics' },
    { id: 'holdings', label: 'Holdings', icon: Database, description: 'Detailed assets and portfolio breakdown' },
    { id: 'insights', label: 'Insights', icon: Brain, description: 'AI insights and analytics' }
  ]

  const [activeTab, setActiveTab] = useState('summary')

  // Fetch portfolio data from Firebase
  useEffect(() => {
    const fetchPortfolioData = async () => {
      if (!user) {
        console.log('🔍 No user found, setting loading to false')
        setLoading(false)
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
        
        // Fallback: Use test data if API is not available
        console.log('🔄 Using fallback test data')
        const testData = [
          {
            Ticker: 'AAPL',
            Category: 'Stock',
            Qty: 100,
            Current_Price: 150.00,
            Total_Value: 15000.00,
            Gain_Loss: 1000.00,
            Gain_Loss_Percent: 7.14,
            Brokerage: 'Test Brokerage',
            last_updated: new Date()
          },
          {
            Ticker: 'VTI',
            Category: 'ETF',
            Qty: 50,
            Current_Price: 200.00,
            Total_Value: 10000.00,
            Gain_Loss: 500.00,
            Gain_Loss_Percent: 5.26,
            Brokerage: 'Test Brokerage',
            last_updated: new Date()
          },
          {
            Ticker: 'BTC',
            Category: 'Crypto',
            Qty: 0.5,
            Current_Price: 45000.00,
            Total_Value: 22500.00,
            Gain_Loss: 2500.00,
            Gain_Loss_Percent: 12.5,
            Brokerage: 'Crypto Exchange',
            last_updated: new Date()
          }
        ]
        
        console.log('✅ Using fallback test data:', testData.length, 'holdings')
        setPortfolioData(testData)
        
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

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-[#FDFBF7] to-[#EDE9E3]">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div className="text-left flex-1">
              <h1 className="text-5xl font-bold text-[#1C3D5A] mb-1 tracking-tight">Portfolio</h1>
              <p className="text-[#5A6A73] text-sm">Track your investments and performance</p>
            </div>
            
            {/* Profile and Logout Buttons */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-[#1C3D5A]">
                <User className="w-5 h-5" />
                <span className="font-medium">{user?.displayName || user?.email || 'User'}</span>
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-2 bg-[#C9A66B] text-white px-4 py-2 rounded-lg font-semibold hover:bg-[#1C3D5A] transition-colors"
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
                    <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
                      <div className="mb-6">
                        <h3 className="text-sm font-medium text-[#5A6A73] mb-2">Total Portfolio Value</h3>
                        <h2 className="text-6xl font-bold text-[#1C3D5A] tracking-tight">{formatCurrency(metrics.totalValue)}</h2>
                        <div className="flex items-center mt-2">
                          <span className="text-sm text-[#5A6A73]">Total value of all holdings</span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-[#FDFBF7] p-6 rounded-2xl shadow-lg border">
                      <div className="flex items-center mb-4">
                        <div className="p-2 bg-[#EDE9E3] rounded-lg mr-3">
                          <DollarSign className="w-5 h-5 text-[#1C3D5A]" />
                        </div>
                        <h3 className="text-lg font-medium text-[#1C3D5A]">Cash Allocation</h3>
                      </div>
                      <h2 className="text-2xl font-semibold text-[#1C3D5A]">{formatPercent(metrics.cashAllocation)}</h2>
                    </div>

                    <div className="bg-[#FDFBF7] p-6 rounded-2xl shadow-lg border">
                      <div className="flex items-center mb-4">
                        <div className="p-2 bg-[#EDE9E3] rounded-lg mr-3">
                          <TrendingUp className="w-5 h-5 text-[#1C3D5A]" />
                        </div>
                        <h3 className="text-lg font-medium text-[#1C3D5A]">Stock Allocation</h3>
                      </div>
                      <h2 className="text-2xl font-semibold text-[#1C3D5A]">{formatPercent(metrics.stockAllocation)}</h2>
                    </div>

                    <div className="bg-[#FDFBF7] p-6 rounded-2xl shadow-lg border">
                      <div className="flex items-center mb-4">
                        <div className="p-2 bg-[#EDE9E3] rounded-lg mr-3">
                          <Database className="w-5 h-5 text-[#1C3D5A]" />
                        </div>
                        <h3 className="text-lg font-medium text-[#1C3D5A]">Holdings Count</h3>
                      </div>
                      <h2 className="text-2xl font-semibold text-[#1C3D5A]">{formatCount(metrics.holdingsCount)}</h2>
                    </div>
                  </div>

                  {/* Holdings Table */}
                  <div className="bg-white p-6 rounded-2xl shadow-lg border">
                    <h3 className="text-xl font-semibold mb-4 text-[#1C3D5A]">Your Holdings</h3>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-[#EDE9E3]">
                            <th className="text-left py-3 px-4 text-[#1C3D5A] font-medium">Ticker</th>
                            <th className="text-left py-3 px-4 text-[#1C3D5A] font-medium">Category</th>
                            <th className="text-left py-3 px-4 text-[#1C3D5A] font-medium">Quantity</th>
                            <th className="text-left py-3 px-4 text-[#1C3D5A] font-medium">Price</th>
                            <th className="text-left py-3 px-4 text-[#1C3D5A] font-medium">Value</th>
                            <th className="text-left py-3 px-4 text-[#1C3D5A] font-medium">Gain/Loss</th>
                            <th className="text-left py-3 px-4 text-[#1C3D5A] font-medium">% Change</th>
                          </tr>
                        </thead>
                        <tbody>
                          {portfolioData.map((holding, index) => (
                            <tr key={index} className="border-b border-[#EDE9E3] hover:bg-[#F5F1EB]">
                              <td className="py-3 px-4 font-medium text-[#1C3D5A]">{holding.Ticker}</td>
                              <td className="py-3 px-4 text-[#5A6A73]">{holding.Category || 'Unknown'}</td>
                              <td className="py-3 px-4 text-[#5A6A73]">{formatCount(holding.Qty || 0)}</td>
                              <td className="py-3 px-4 text-[#5A6A73]">{formatCurrency(holding.Current_Price || 0)}</td>
                              <td className="py-3 px-4 text-[#1C3D5A] font-medium">{formatCurrency(holding.Total_Value || 0)}</td>
                              <td className={`py-3 px-4 font-medium ${
                                (holding.Gain_Loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {formatCurrency(holding.Gain_Loss || 0)}
                              </td>
                              <td className={`py-3 px-4 font-medium ${
                                (holding.Gain_Loss_Percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {formatPercent(holding.Gain_Loss_Percent || 0)}
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
              {activeTab === 'holdings' && portfolioData.length > 0 && (
                <div className="space-y-6">
                  <div className="bg-white p-6 rounded-2xl shadow-lg border">
                    <h3 className="text-xl font-semibold mb-4 text-[#1C3D5A]">All Holdings</h3>
                    <p className="text-[#5A6A73]">Detailed holdings view coming soon...</p>
                  </div>
                </div>
              )}

              {/* Insights Tab */}
              {activeTab === 'insights' && portfolioData.length > 0 && (
                <div className="space-y-6">
                  <div className="bg-white p-6 rounded-2xl shadow-lg border">
                    <h3 className="text-xl font-semibold mb-4 text-[#1C3D5A]">AI Insights</h3>
                    <p className="text-[#5A6A73]">AI insights and analytics coming soon...</p>
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
