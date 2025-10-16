'use client'

import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { doc, setDoc } from 'firebase/firestore'
import { db } from '@/lib/firebaseClient'
import YachtLayout from '@/components/Layout/YachtLayout'
import { Upload, Plus, Trash2, FileText, CheckCircle, AlertCircle } from 'lucide-react'

export default function ManageHoldingsPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [dataOption, setDataOption] = useState<'csv' | 'manual' | null>(null)
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [csvPreview, setCsvPreview] = useState<any[]>([])
  const [manualHoldings, setManualHoldings] = useState<any[]>([])
  const { user } = useAuth()
  const router = useRouter()

  const handleCsvUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setCsvFile(file)
      parseCsvFile(file)
    }
  }

  const parseCsvFile = (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const csv = e.target?.result as string
      const lines = csv.split('\n')
      const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
      
      const data = lines.slice(1).map(line => {
        const values = line.split(',').map(v => v.trim().replace(/"/g, ''))
        const row: any = {}
        headers.forEach((header, index) => {
          const value = values[index]
          if (value) {
            if (['shares', 'purchase_price', 'total_cost', 'total_value'].includes(header)) {
              row[header] = parseFloat(value)
            } else {
              row[header] = value
            }
          }
        })
        return row
      }).filter(row => row.symbol && row.shares)
      
      setCsvPreview(data.slice(0, 5)) // Show first 5 rows as preview
    }
    reader.readAsText(file)
  }

  const addManualHolding = () => {
    setManualHoldings(prev => [...prev, {
      symbol: '',
      shares: 0,
      purchase_price: 0,
      total_value: 0,
      asset_type: '',
      brokerage: ''
    }])
  }

  const updateManualHolding = (index: number, field: string, value: any) => {
    setManualHoldings(prev => prev.map((holding, i) => 
      i === index ? { ...holding, [field]: value } : holding
    ))
  }

  const removeManualHolding = (index: number) => {
    setManualHoldings(prev => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = async () => {
    if (!user) {
      setError('User not authenticated')
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')

    try {
      let holdings: any[] = []
      
      if (dataOption === 'csv' && csvFile) {
        // Use CSV data
        const reader = new FileReader()
        reader.onload = async (e) => {
          const csv = e.target?.result as string
          const lines = csv.split('\n')
          const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
          
          const csvData = lines.slice(1).map(line => {
            const values = line.split(',').map(v => v.trim().replace(/"/g, ''))
            const row: any = {}
            headers.forEach((header, index) => {
              const value = values[index]
              if (value) {
                if (['shares', 'purchase_price', 'total_cost', 'total_value'].includes(header)) {
                  row[header] = parseFloat(value)
                } else {
                  row[header] = value
                }
              }
            })
            return row
          }).filter(row => row.symbol && row.shares)
          
          holdings = csvData.map(row => ({
            symbol: row.symbol,
            ticker: row.symbol,
            asset_type: row.asset_type || 'Stock',
            category: row.asset_type || 'Stock',
            sector: row.sector || 'Technology',
            brokerage: row.account_name || 'Unknown',
            shares: row.shares,
            purchase_price: row.purchase_price,
            current_price: row.purchase_price,
            total_cost: row.total_cost,
            total_value: row.total_value,
            gain_loss: row.total_value - row.total_cost,
            gain_loss_percent: row.total_cost > 0 ? ((row.total_value - row.total_cost) / row.total_cost) * 100 : 0,
            last_updated: new Date()
          }))
          
          await savePortfolioData(holdings)
        }
        reader.readAsText(csvFile)
      } else if (dataOption === 'manual' && manualHoldings.length > 0) {
        // Use manual data
        holdings = manualHoldings.map(holding => ({
          symbol: holding.symbol,
          ticker: holding.symbol,
          asset_type: holding.asset_type || 'Stock',
          category: holding.asset_type || 'Stock',
          sector: holding.asset_type === 'Crypto' ? 'Crypto' : 
                  holding.asset_type === 'Bond' ? 'Fixed Income' : 
                  holding.asset_type === 'ETF' ? 'ETF' : 'Technology',
          brokerage: holding.brokerage || 'Manual Entry',
          shares: holding.shares || 0,
          purchase_price: holding.purchase_price || 0,
          current_price: holding.purchase_price || 0,
          total_cost: (holding.shares || 0) * (holding.purchase_price || 0),
          total_value: holding.total_value || 0,
          gain_loss: (holding.total_value || 0) - ((holding.shares || 0) * (holding.purchase_price || 0)),
          gain_loss_percent: ((holding.shares || 0) * (holding.purchase_price || 0)) > 0 ? 
            (((holding.total_value || 0) - ((holding.shares || 0) * (holding.purchase_price || 0))) / ((holding.shares || 0) * (holding.purchase_price || 0))) * 100 : 0,
          last_updated: new Date()
        }))
        
        await savePortfolioData(holdings)
      } else {
        setError('Please select a data option and provide data')
        return
      }
    } catch (error: any) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const savePortfolioData = async (holdings: any[]) => {
    if (!user) return
    
    const totalPortfolioValue = holdings.reduce((sum, holding) => sum + holding.total_value, 0)
    
    // Store user's portfolio as single document
    await setDoc(doc(db, 'portfolio_data', user.uid), {
      user_id: user.uid,
      holdings: holdings,
      totalPortfolioValue: totalPortfolioValue,
      lastUpdated: new Date()
    })
    
    // Update user document
    await setDoc(doc(db, 'users', user.uid), {
      has_portfolio_data: true,
      portfolioValue: totalPortfolioValue,
      updated_at: new Date().toISOString()
    }, { merge: true })
    
    setSuccess(`Successfully added ${holdings.length} holdings to your portfolio!`)
    
    // Redirect to dashboard after a short delay
    setTimeout(() => {
      router.push('/dashboard')
    }, 2000)
  }

  if (!user) {
    return (
      <YachtLayout title="Manage Holdings" subtitle="Please log in to manage your holdings">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-[#C9A66B] mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-[#1C3D5A] mb-2">Authentication Required</h2>
          <p className="text-[#5A6A73]">Please log in to manage your portfolio holdings.</p>
        </div>
      </YachtLayout>
    )
  }

  return (
    <YachtLayout title="Manage Holdings" subtitle="Add or update your portfolio holdings">
      <div className="max-w-4xl mx-auto">
        <div className="bg-[#FDFBF7] p-8 rounded-2xl shadow-lg border border-[#E3DED5]">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-[#1C3D5A] mb-4">Add Portfolio Holdings</h2>
            <p className="text-[#5A6A73]">
              Choose how you'd like to add your portfolio data
            </p>
          </div>

          <div className="space-y-6">
            {/* CSV Upload Option */}
            <div className="border border-[#E3DED5] rounded-lg p-6">
              <div className="flex items-center mb-4">
                <input
                  type="radio"
                  name="dataOption"
                  value="csv"
                  checked={dataOption === 'csv'}
                  onChange={(e) => setDataOption(e.target.value as 'csv')}
                  className="text-[#C9A66B] focus:ring-[#C9A66B]"
                />
                <label className="ml-3 font-semibold text-[#1C3D5A] text-lg">Upload CSV File</label>
              </div>
              {dataOption === 'csv' && (
                <div className="space-y-4">
                  <div className="bg-[#F5F1EB] p-4 rounded-lg">
                    <h4 className="font-medium text-[#1C3D5A] mb-2">CSV Format Requirements:</h4>
                    <p className="text-sm text-[#5A6A73] mb-2">Your CSV should include these columns:</p>
                    <ul className="text-sm text-[#5A6A73] list-disc list-inside">
                      <li>symbol - Stock/ETF symbol (e.g., AAPL, VOO)</li>
                      <li>shares - Number of shares</li>
                      <li>purchase_price - Price per share</li>
                      <li>total_cost - Total cost basis</li>
                      <li>total_value - Current total value</li>
                      <li>asset_type - Type (Stock, ETF, Crypto, etc.)</li>
                      <li>account_name - Brokerage account name (optional)</li>
                    </ul>
                  </div>
                  
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleCsvUpload}
                    className="w-full px-4 py-3 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                  />
                  
                  {csvPreview.length > 0 && (
                    <div className="bg-[#F5F1EB] p-4 rounded-lg">
                      <h4 className="font-medium text-[#1C3D5A] mb-2">Preview (first 5 rows):</h4>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-[#E3DED5]">
                              {Object.keys(csvPreview[0] || {}).map(key => (
                                <th key={key} className="text-left py-2 pr-4 font-medium">{key}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {csvPreview.map((row, index) => (
                              <tr key={index} className="border-b border-[#E3DED5]">
                                {Object.values(row).map((value, i) => (
                                  <td key={i} className="py-2 pr-4">{String(value)}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Manual Entry Option */}
            <div className="border border-[#E3DED5] rounded-lg p-6">
              <div className="flex items-center mb-4">
                <input
                  type="radio"
                  name="dataOption"
                  value="manual"
                  checked={dataOption === 'manual'}
                  onChange={(e) => setDataOption(e.target.value as 'manual')}
                  className="text-[#C9A66B] focus:ring-[#C9A66B]"
                />
                <label className="ml-3 font-semibold text-[#1C3D5A] text-lg">Add Holdings Manually</label>
              </div>
              {dataOption === 'manual' && (
                <div className="space-y-4">
                  <button
                    type="button"
                    onClick={addManualHolding}
                    className="bg-[#C9A66B] text-white px-4 py-2 rounded-lg hover:bg-[#1C3D5A] transition-colors flex items-center"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Holding
                  </button>
                  
                  {manualHoldings.map((holding, index) => (
                    <div key={index} className="bg-[#F5F1EB] p-4 rounded-lg space-y-3">
                      <div className="flex justify-between items-center">
                        <h4 className="font-medium text-[#1C3D5A]">Holding {index + 1}</h4>
                        <button
                          type="button"
                          onClick={() => removeManualHolding(index)}
                          className="text-red-500 hover:text-red-700 flex items-center"
                        >
                          <Trash2 className="w-4 h-4 mr-1" />
                          Remove
                        </button>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Brokerage Name */}
                        <div>
                          <label className="block text-sm font-medium text-[#1C3D5A] mb-1">Brokerage Name</label>
                          <input
                            type="text"
                            placeholder="e.g., Fidelity, Vanguard, Robinhood"
                            value={holding.brokerage || ''}
                            onChange={(e) => updateManualHolding(index, 'brokerage', e.target.value)}
                            className="w-full px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                          />
                        </div>

                        {/* Asset Type */}
                        <div>
                          <label className="block text-sm font-medium text-[#1C3D5A] mb-1">Asset Type</label>
                          <select
                            value={holding.asset_type || ''}
                            onChange={(e) => updateManualHolding(index, 'asset_type', e.target.value)}
                            className="w-full px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                          >
                            <option value="">Select asset type</option>
                            <option value="Stock">Stock</option>
                            <option value="ETF">ETF</option>
                            <option value="Bond">Bond</option>
                            <option value="Crypto">Crypto</option>
                            <option value="Cash">Cash</option>
                            <option value="Other">Other</option>
                          </select>
                        </div>

                        {/* Ticker/Symbol */}
                        <div>
                          <label className="block text-sm font-medium text-[#1C3D5A] mb-1">Ticker/Symbol</label>
                          <input
                            type="text"
                            placeholder="e.g., AAPL, VTI, BTC"
                            value={holding.symbol || ''}
                            onChange={(e) => updateManualHolding(index, 'symbol', e.target.value)}
                            className="w-full px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                          />
                        </div>

                        {/* Current Value */}
                        <div>
                          <label className="block text-sm font-medium text-[#1C3D5A] mb-1">Current Value ($)</label>
                          <input
                            type="number"
                            placeholder="e.g., 10000"
                            value={holding.total_value || ''}
                            onChange={(e) => updateManualHolding(index, 'total_value', parseFloat(e.target.value) || 0)}
                            className="w-full px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                          />
                        </div>

                        {/* Additional Fields - Shares and Purchase Price (optional) */}
                        <div>
                          <label className="block text-sm font-medium text-[#1C3D5A] mb-1">Shares/Quantity (Optional)</label>
                          <input
                            type="number"
                            placeholder="e.g., 100"
                            value={holding.shares || ''}
                            onChange={(e) => updateManualHolding(index, 'shares', parseFloat(e.target.value) || 0)}
                            className="w-full px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-[#1C3D5A] mb-1">Purchase Price (Optional)</label>
                          <input
                            type="number"
                            placeholder="e.g., 150.00"
                            value={holding.purchase_price || ''}
                            onChange={(e) => updateManualHolding(index, 'purchase_price', parseFloat(e.target.value) || 0)}
                            className="w-full px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Success/Error Messages */}
            {success && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <p className="text-green-600">{success}</p>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                  <p className="text-red-600">{error}</p>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex justify-center pt-6">
              <button
                onClick={handleSubmit}
                disabled={loading || (!csvFile && manualHoldings.length === 0)}
                className="bg-[#C9A66B] text-white px-8 py-4 rounded-lg font-semibold hover:bg-[#1C3D5A] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {loading ? 'Processing...' : 'Add Holdings'}
                <Upload className="ml-2 w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </YachtLayout>
  )
}
