'use client'

import React, { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, BarChart3, Users, Target, AlertCircle } from 'lucide-react'

interface ComparisonData {
  user: {
    one_year_return: number
    volatility: number
    dividend_yield: number
    allocation: {
      equity: number
      bond: number
      cash: number
    }
  }
  sp500: {
    one_year_return: number
    volatility: number
    dividend_yield: number
    allocation: {
      equity: number
      bond: number
      cash: number
    }
  }
  model6040: {
    one_year_return: number
    volatility: number
    dividend_yield: number
    allocation: {
      equity: number
      bond: number
      cash: number
    }
  }
  allWeather: {
    one_year_return: number
    volatility: number
    dividend_yield: number
    allocation: {
      equity: number
      bond: number
      cash: number
    }
  }
  community: {
    median_one_year_return: number
    median_volatility: number
    average_dividend_yield: number
    average_allocation: {
      equity: number
      bond: number
      cash: number
    }
  }
}

const Comparison: React.FC = () => {
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchComparisonData()
  }, [])

  const fetchComparisonData = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/comparison', {
        credentials: 'include'
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch comparison data')
      }
      
      const result = await response.json()
      
      if (result.status === 'success') {
        setComparisonData(result.data)
      } else {
        throw new Error(result.message || 'Failed to load comparison data')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`
  }

  const formatAllocation = (value: number) => {
    return `${value.toFixed(1)}%`
  }

  const getPerformanceColor = (userValue: number, benchmarkValue: number) => {
    if (userValue > benchmarkValue) return 'text-green-600'
    if (userValue < benchmarkValue) return 'text-red-600'
    return 'text-gray-600'
  }

  const getPerformanceIcon = (userValue: number, benchmarkValue: number) => {
    if (userValue > benchmarkValue) return <TrendingUp className="w-4 h-4" />
    if (userValue < benchmarkValue) return <TrendingDown className="w-4 h-4" />
    return <BarChart3 className="w-4 h-4" />
  }

  const generateInsight = () => {
    if (!comparisonData) return "Loading insights..."

    const user = comparisonData.user
    const community = comparisonData.community
    const sp500 = comparisonData.sp500

    const beatsCommunity = user.one_year_return > community.median_one_year_return
    const beatsSP500 = user.one_year_return > sp500.one_year_return
    const lowerVolatility = user.volatility < community.median_volatility

    let insight = "Your portfolio performance analysis: "
    
    if (beatsCommunity && beatsSP500) {
      insight += "🎉 Outstanding! You're outperforming both the community median and S&P 500."
    } else if (beatsCommunity) {
      insight += "👍 Great job! You're beating the community median return."
    } else if (beatsSP500) {
      insight += "📈 Good work! You're outperforming the S&P 500."
    } else {
      insight += "📊 Your returns are below benchmarks. Consider reviewing your strategy."
    }

    if (lowerVolatility) {
      insight += " Your portfolio also shows lower volatility than the community average."
    }

    return insight
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading comparison data...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-2">Error loading comparison data</p>
          <p className="text-gray-600 text-sm">{error}</p>
          <button
            onClick={fetchComparisonData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (!comparisonData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">No comparison data available</p>
          <p className="text-gray-500 text-sm">Connect your portfolio to see comparisons</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Comparison</h1>
          <p className="text-gray-600">Benchmark your portfolio against market indices and community</p>
        </div>
        <button
          onClick={fetchComparisonData}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center"
        >
          <BarChart3 className="w-4 h-4 mr-2" />
          Refresh Data
        </button>
      </div>

      {/* Performance vs Benchmarks */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Performance vs Benchmarks</h2>
          <p className="text-sm text-gray-600">Compare your 1-year performance against major benchmarks</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Metric
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  You
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  S&P 500
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  60/40
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  All-Weather
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  1Y Return
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-lg font-semibold text-gray-900">
                    {formatPercentage(comparisonData.user.one_year_return)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatPercentage(comparisonData.sp500.one_year_return)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatPercentage(comparisonData.model6040.one_year_return)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatPercentage(comparisonData.allWeather.one_year_return)}
                  </span>
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Volatility
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-lg font-semibold text-gray-900">
                    {formatPercentage(comparisonData.user.volatility)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatPercentage(comparisonData.sp500.volatility)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatPercentage(comparisonData.model6040.volatility)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatPercentage(comparisonData.allWeather.volatility)}
                  </span>
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Dividend Yield
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-lg font-semibold text-gray-900">
                    {formatPercentage(comparisonData.user.dividend_yield)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatPercentage(comparisonData.sp500.dividend_yield)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatPercentage(comparisonData.model6040.dividend_yield)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatPercentage(comparisonData.allWeather.dividend_yield)}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Allocation vs Benchmarks & Community */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Allocation vs Benchmarks & Community</h2>
          <p className="text-sm text-gray-600">Compare your asset allocation against benchmarks and community averages</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Asset Class
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  You
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  S&P 500
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  60/40
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  All-Weather
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Community
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Equity
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-lg font-semibold text-gray-900">
                    {formatAllocation(comparisonData.user.allocation.equity)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatAllocation(comparisonData.sp500.allocation.equity)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatAllocation(comparisonData.model6040.allocation.equity)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatAllocation(comparisonData.allWeather.allocation.equity)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatAllocation(comparisonData.community.average_allocation.equity)}
                  </span>
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Bond
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-lg font-semibold text-gray-900">
                    {formatAllocation(comparisonData.user.allocation.bond)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatAllocation(comparisonData.sp500.allocation.bond)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatAllocation(comparisonData.model6040.allocation.bond)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatAllocation(comparisonData.allWeather.allocation.bond)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatAllocation(comparisonData.community.average_allocation.bond)}
                  </span>
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Cash
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-lg font-semibold text-gray-900">
                    {formatAllocation(comparisonData.user.allocation.cash)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatAllocation(comparisonData.sp500.allocation.cash)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatAllocation(comparisonData.model6040.allocation.cash)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatAllocation(comparisonData.allWeather.allocation.cash)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {formatAllocation(comparisonData.community.average_allocation.cash)}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Your Standing */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
        <div className="px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Your Standing</h2>
          <div className="flex items-start">
            <Users className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
            <p className="text-gray-700 leading-relaxed">
              {generateInsight()}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Comparison
