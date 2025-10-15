'use client'

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { 
  TrendingUp, 
  DollarSign, 
  Activity,
  Home,
  Database,
  Brain,
  Plus
} from 'lucide-react'
import Link from 'next/link'
import { yachtClubTheme } from '@/styles/yachtClubTheme'
import { formatCurrency, formatPercent, formatCount } from '@/lib/formatters'
import ProtectedRoute from '@/components/Auth/ProtectedRoute'
import { useAuth } from '@/hooks/useAuth'

export default function SimpleDashboard() {
  const { user } = useAuth()
  const router = useRouter()
  
  // State for portfolio data
  const [portfolioData, setPortfolioData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

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
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        const userId = user.uid
        console.log('🔍 Fetching portfolio data for user:', userId)
        
        const response = await fetch(`/api/portfolio?user_id=${userId}`)
        if (response.ok) {
          const data = await response.json()
          console.log('📊 Portfolio data response:', data)
          
          if (data.data && data.data.length > 0) {
            console.log('✅ User has portfolio data:', data.data.length, 'holdings')
            setPortfolioData(data.data)
          } else {
            console.log('⚠️ No portfolio data found')
            setPortfolioData([])
          }
        } else {
          console.log('❌ API error')
          setPortfolioData([])
        }
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
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-[#1C3D5A] mb-2">Portfolio Overview</h1>
            <p className="text-[#5A6A73]">Yacht Club Premium – Sophisticated Wealth Management</p>
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
              {/* Empty State */}
              {portfolioData.length === 0 && (
                <div className="text-center py-20">
                  <div className="max-w-md mx-auto">
                    <div className="w-24 h-24 bg-[#F5F1EB] rounded-full flex items-center justify-center mx-auto mb-6">
                      <TrendingUp className="w-12 h-12 text-[#C9A66B]" />
                    </div>
                    <h2 className="text-2xl font-bold text-[#1C3D5A] mb-4">No Portfolio Data Found</h2>
                    <p className="text-[#5A6A73] mb-8">
                      It looks like you haven't added any portfolio holdings yet. 
                      Get started by adding your investments to see your portfolio overview.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                      <Link 
                        href="/holdings/manage" 
                        className="bg-[#C9A66B] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#1C3D5A] transition-colors flex items-center justify-center"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Add Holdings
                      </Link>
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

              {/* Summary Tab */}
              {activeTab === 'summary' && portfolioData.length > 0 && (
                <div className="space-y-6">
                  {/* 7 Key Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-[#FDFBF7] p-6 rounded-2xl shadow-lg border">
                      <div className="flex items-center mb-4">
                        <div className="p-2 bg-[#EDE9E3] rounded-lg mr-3">
                          <DollarSign className="w-5 h-5 text-[#1C3D5A]" />
                        </div>
                        <h3 className="text-lg font-medium text-[#1C3D5A]">Total Portfolio Value</h3>
                      </div>
                      <h2 className="text-2xl font-semibold text-[#1C3D5A]">{formatCurrency(metrics.totalValue)}</h2>
                    </div>

                    <div className="bg-[#FDFBF7] p-6 rounded-2xl shadow-lg border">
                      <div className="flex items-center mb-4">
                        <div className="p-2 bg-[#EDE9E3] rounded-lg mr-3">
                          <Activity className="w-5 h-5 text-[#1C3D5A]" />
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
