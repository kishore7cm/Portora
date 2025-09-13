"use client"

import React, { useState, useEffect } from 'react'
import { Bot, Play, Square, Pause, Settings, TrendingUp, Activity } from 'lucide-react'

interface BotData {
  id: number
  name: string
  bot_type: string
  status: string
  config: any
  performance_data: any
  created_at: string
  last_run: string | null
}

interface BotType {
  value: string
  name: string
}

const BotManagement: React.FC = () => {
  const [bots, setBots] = useState<BotData[]>([])
  const [botTypes, setBotTypes] = useState<BotType[]>([])
  const [loading, setLoading] = useState(false)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newBot, setNewBot] = useState({
    name: '',
    bot_type: '',
    config: {}
  })

  useEffect(() => {
    fetchBots()
    fetchBotTypes()
  }, [])

  const fetchBots = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/bots', { credentials: 'include' })
      const data = await response.json()
      
      if (data.status === 'success') {
        setBots(data.bots)
      }
    } catch (error) {
      console.error('Error fetching bots:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchBotTypes = async () => {
    try {
      const response = await fetch('http://localhost:8000/bots/types', { credentials: 'include' })
      const data = await response.json()
      
      if (data.status === 'success') {
        setBotTypes(data.bot_types)
      }
    } catch (error) {
      console.error('Error fetching bot types:', error)
    }
  }

  const createBot = async () => {
    try {
      const response = await fetch('http://localhost:8000/bots', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(newBot),
      })
      
      const data = await response.json()
      
      if (data.success) {
        setShowCreateForm(false)
        setNewBot({ name: '', bot_type: '', config: {} })
        fetchBots()
      }
    } catch (error) {
      console.error('Error creating bot:', error)
    }
  }

  const startBot = async (botId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/bots/${botId}/start`, {
        method: 'POST',
        credentials: 'include',
      })
      
      const data = await response.json()
      
      if (data.success) {
        fetchBots()
      }
    } catch (error) {
      console.error('Error starting bot:', error)
    }
  }

  const stopBot = async (botId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/bots/${botId}/stop`, {
        method: 'POST',
        credentials: 'include',
      })
      
      const data = await response.json()
      
      if (data.success) {
        fetchBots()
      }
    } catch (error) {
      console.error('Error stopping bot:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'inactive':
        return 'bg-gray-100 text-gray-800'
      case 'paused':
        return 'bg-yellow-100 text-yellow-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      case 'stopped':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getBotTypeIcon = (botType: string) => {
    switch (botType) {
      case 'dollar_cost_averaging':
        return <TrendingUp className="w-5 h-5" />
      case 'momentum_trading':
        return <Activity className="w-5 h-5" />
      case 'mean_reversion':
        return <Settings className="w-5 h-5" />
      case 'grid_trading':
        return <Bot className="w-5 h-5" />
      case 'arbitrage':
        return <Activity className="w-5 h-5" />
      case 'news_based':
        return <Bot className="w-5 h-5" />
      case 'technical_analysis':
        return <TrendingUp className="w-5 h-5" />
      default:
        return <Bot className="w-5 h-5" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Trading Bots</h2>
          <p className="text-gray-600">Manage your automated trading strategies</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <Bot className="w-4 h-4" />
          Create Bot
        </button>
      </div>

      {/* Create Bot Form */}
      {showCreateForm && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold mb-4">Create New Bot</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bot Name
              </label>
              <input
                type="text"
                value={newBot.name}
                onChange={(e) => setNewBot({ ...newBot, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter bot name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bot Type
              </label>
              <select
                value={newBot.bot_type}
                onChange={(e) => setNewBot({ ...newBot, bot_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select bot type</option>
                {botTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-2">
              <button
                onClick={createBot}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Create Bot
              </button>
              <button
                onClick={() => setShowCreateForm(false)}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bots List */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading bots...</p>
        </div>
      ) : bots.length === 0 ? (
        <div className="text-center py-8">
          <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">No Bots Created</h3>
          <p className="text-gray-500 mb-6">
            Create your first trading bot to get started with automated trading
          </p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Create Your First Bot
          </button>
        </div>
      ) : (
        <div className="grid gap-6">
          {bots.map((bot) => (
            <div key={bot.id} className="bg-white p-6 rounded-lg shadow border">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getBotTypeIcon(bot.bot_type)}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{bot.name}</h3>
                    <p className="text-sm text-gray-600 capitalize">
                      {bot.bot_type.replace('_', ' ')}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(bot.status)}`}>
                    {bot.status}
                  </span>
                  <div className="flex gap-1">
                    {bot.status === 'active' ? (
                      <button
                        onClick={() => stopBot(bot.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-md"
                        title="Stop Bot"
                      >
                        <Square className="w-4 h-4" />
                      </button>
                    ) : (
                      <button
                        onClick={() => startBot(bot.id)}
                        className="p-2 text-green-600 hover:bg-green-50 rounded-md"
                        title="Start Bot"
                      >
                        <Play className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      className="p-2 text-gray-600 hover:bg-gray-50 rounded-md"
                      title="Configure Bot"
                    >
                      <Settings className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Bot Performance */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {bot.performance_data?.total_trades || 0}
                  </div>
                  <div className="text-sm text-gray-600">Total Trades</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    ${bot.performance_data?.total_volume?.toFixed(2) || '0.00'}
                  </div>
                  <div className="text-sm text-gray-600">Total Volume</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {bot.performance_data?.profit_loss?.toFixed(2) || '0.00'}%
                  </div>
                  <div className="text-sm text-gray-600">P&L</div>
                </div>
              </div>

              {/* Bot Details */}
              <div className="text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Created:</span>
                  <span>{new Date(bot.created_at).toLocaleDateString()}</span>
                </div>
                {bot.last_run && (
                  <div className="flex justify-between">
                    <span>Last Run:</span>
                    <span>{new Date(bot.last_run).toLocaleString()}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default BotManagement
