'use client';

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';
import { Users, TrendingUp, Target, Award, Activity, TrendingDown } from 'lucide-react';

interface CommunityData {
  community_stats: {
    total_users: number;
    active_users_30d: number;
    average_portfolio_value: number;
    median_portfolio_value: number;
    top_performers_count: number;
  };
  performance_benchmarks: {
    community_median_1y_return: number;
    community_median_volatility: number;
    community_median_sharpe_ratio: number;
    community_median_max_drawdown: number;
    top_quartile_1y_return: number;
    bottom_quartile_1y_return: number;
  };
  allocation_benchmarks: {
    community_avg_equity_allocation: number;
    community_avg_bond_allocation: number;
    community_avg_cash_allocation: number;
    community_avg_crypto_allocation: number;
    community_avg_international_allocation: number;
  };
  sector_performance: Record<string, { avg_allocation: number; avg_return: number }>;
  risk_profiles: Record<string, { count: number; avg_return: number; avg_volatility: number }>;
  popular_strategies: Array<{ name: string; users: number; avg_return: number }>;
  recent_trends: {
    most_bought_stocks: Array<{ symbol: string; buys: number; avg_price: number }>;
    most_sold_stocks: Array<{ symbol: string; sells: number; avg_price: number }>;
  };
}

export default function CommunityBenchmark() {
  const [data, setData] = useState<CommunityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCommunityData();
  }, []);

  const fetchCommunityData = async () => {
    try {
      const response = await fetch('http://localhost:8000/community/comparison');
      if (response.ok) {
        const communityData = await response.json();
        setData(communityData);
      } else {
        setError('Failed to fetch community data');
      }
    } catch (err) {
      setError('Error fetching community data');
      console.error('Error fetching community data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-gray-200 rounded-lg h-32"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-gray-200 rounded-lg h-64"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <div className="text-red-500 mb-4">
            <Activity className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Unable to load community data</h3>
          <p className="text-gray-500">{error}</p>
          <button
            onClick={fetchCommunityData}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Prepare data for charts
  const allocationData = [
    { name: 'Equity', value: data.allocation_benchmarks.community_avg_equity_allocation, color: '#3B82F6' },
    { name: 'Bonds', value: data.allocation_benchmarks.community_avg_bond_allocation, color: '#10B981' },
    { name: 'Cash', value: data.allocation_benchmarks.community_avg_cash_allocation, color: '#F59E0B' },
    { name: 'Crypto', value: data.allocation_benchmarks.community_avg_crypto_allocation, color: '#8B5CF6' },
    { name: 'International', value: data.allocation_benchmarks.community_avg_international_allocation, color: '#EF4444' }
  ];

  const sectorData = Object.entries(data.sector_performance).map(([sector, info]) => ({
    sector: sector.charAt(0).toUpperCase() + sector.slice(1),
    allocation: info.avg_allocation,
    return: info.avg_return
  }));

  const riskProfileData = Object.entries(data.risk_profiles).map(([profile, info]) => ({
    profile: profile.charAt(0).toUpperCase() + profile.slice(1),
    users: info.count,
    return: info.avg_return,
    volatility: info.avg_volatility
  }));

  const strategyData = data.popular_strategies.map(strategy => ({
    name: strategy.name,
    users: strategy.users,
    return: strategy.avg_return
  }));

  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Community Benchmark</h1>
          <p className="text-gray-600">Compare your performance with the EaseLi community</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Users className="w-4 h-4" />
          <span>{data.community_stats.total_users.toLocaleString()} active users</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Users (30d)</p>
              <p className="text-2xl font-bold text-gray-900">{data.community_stats.active_users_30d.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Median 1Y Return</p>
              <p className="text-2xl font-bold text-gray-900">{data.performance_benchmarks.community_median_1y_return}%</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Portfolio Value</p>
              <p className="text-2xl font-bold text-gray-900">${(data.community_stats.average_portfolio_value / 1000).toFixed(0)}k</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Award className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Top Performers</p>
              <p className="text-2xl font-bold text-gray-900">{data.community_stats.top_performers_count.toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Community Allocation */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Community Asset Allocation</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value}%`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sector Performance */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sector Performance</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sectorData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="sector" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip formatter={(value, name) => [`${value}%`, name === 'allocation' ? 'Allocation' : 'Return']} />
                <Bar dataKey="allocation" fill="#3B82F6" name="Allocation" />
                <Bar dataKey="return" fill="#10B981" name="Return" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Profiles */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Profile Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskProfileData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="profile" type="category" width={100} />
                <Tooltip formatter={(value, name) => [value, name === 'users' ? 'Users' : 'Return %']} />
                <Bar dataKey="users" fill="#8B5CF6" name="Users" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Popular Strategies */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Popular Investment Strategies</h3>
          <div className="space-y-4">
            {strategyData.map((strategy, index) => (
              <div key={strategy.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-medium text-blue-600">
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{strategy.name}</p>
                    <p className="text-sm text-gray-500">{strategy.users.toLocaleString()} users</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-green-600">+{strategy.return}%</p>
                  <p className="text-sm text-gray-500">avg return</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Most Bought Stocks */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
            Most Bought Stocks
          </h3>
          <div className="space-y-3">
            {data.recent_trends.most_bought_stocks.map((stock, index) => (
              <div key={stock.symbol} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center text-sm font-medium text-green-600">
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{stock.symbol}</p>
                    <p className="text-sm text-gray-500">{stock.buys} buys</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">${stock.avg_price.toFixed(2)}</p>
                  <p className="text-sm text-gray-500">avg price</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Most Sold Stocks */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingDown className="w-5 h-5 text-red-600 mr-2" />
            Most Sold Stocks
          </h3>
          <div className="space-y-3">
            {data.recent_trends.most_sold_stocks.map((stock, index) => (
              <div key={stock.symbol} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center text-sm font-medium text-red-600">
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{stock.symbol}</p>
                    <p className="text-sm text-gray-500">{stock.sells} sells</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">${stock.avg_price.toFixed(2)}</p>
                  <p className="text-sm text-gray-500">avg price</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Performance Insights */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Community Performance Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <p className="text-3xl font-bold text-blue-600">{data.performance_benchmarks.community_median_1y_return}%</p>
            <p className="text-sm text-gray-600">Median 1-Year Return</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-purple-600">{data.performance_benchmarks.community_median_volatility}%</p>
            <p className="text-sm text-gray-600">Median Volatility</p>
          </div>
          <div className="text-center">
            <p className="text-3xl font-bold text-green-600">{data.performance_benchmarks.community_median_sharpe_ratio}</p>
            <p className="text-sm text-gray-600">Median Sharpe Ratio</p>
          </div>
        </div>
      </div>
    </div>
  );
}
