'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { doc, setDoc } from 'firebase/firestore'
import { db } from '@/lib/firebaseClient'
import YachtLayout from '@/components/Layout/YachtLayout'
import { DollarSign, TrendingUp, Target, User } from 'lucide-react'

export default function OnboardingPage() {
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [dataOption, setDataOption] = useState<'csv' | 'manual' | null>(null)
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [csvPreview, setCsvPreview] = useState<any[]>([])
  const [manualHoldings, setManualHoldings] = useState<any[]>([])
  const { user } = useAuth()
  const router = useRouter()

  // Form data
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    initialInvestment: '',
    investmentGoal: '',
    riskTolerance: 'moderate',
    investmentExperience: 'intermediate'
  })

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

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
      asset_type: 'Stock'
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      if (!user) {
        throw new Error('User not authenticated')
      }

      // Update user document with onboarding data
      const userNetWorth = parseFloat(formData.initialInvestment) || 0
      await setDoc(doc(db, 'users', user.uid), {
        uid: user.uid,
        email: user.email,
        name: formData.name,
        createdAt: new Date(),
        lastLogin: new Date(),
        portfolioValue: userNetWorth,
        last_year_value: userNetWorth,
        investmentGoal: formData.investmentGoal,
        riskTolerance: formData.riskTolerance,
        investmentExperience: formData.investmentExperience,
        onboardingCompleted: true,
        has_portfolio_data: false
      }, { merge: true })

      // Handle portfolio data based on user's choice
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
          asset_type: holding.asset_type,
          category: holding.asset_type,
          sector: 'Technology',
          brokerage: 'Manual Entry',
          shares: holding.shares,
          purchase_price: holding.purchase_price,
          current_price: holding.purchase_price,
          total_cost: holding.shares * holding.purchase_price,
          total_value: holding.total_value,
          gain_loss: holding.total_value - (holding.shares * holding.purchase_price),
          gain_loss_percent: (holding.shares * holding.purchase_price) > 0 ? 
            ((holding.total_value - (holding.shares * holding.purchase_price)) / (holding.shares * holding.purchase_price)) * 100 : 0,
          last_updated: new Date()
        }))
        
        await savePortfolioData(holdings)
      } else {
        // No portfolio data - just cash
        const cashHolding = {
          symbol: 'CASH',
          ticker: 'CASH',
          asset_type: 'Cash',
          category: 'Cash',
          sector: 'Cash',
          brokerage: 'Cash Account',
          shares: 1,
          purchase_price: userNetWorth,
          current_price: userNetWorth,
          total_cost: userNetWorth,
          total_value: userNetWorth,
          gain_loss: 0,
          gain_loss_percent: 0,
          last_updated: new Date()
        }
        
        await savePortfolioData([cashHolding])
      }

      // Redirect to dashboard
      router.push('/dashboard')
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
  }

  const handleSkip = async () => {
    if (!user) return
    
    setLoading(true)
    try {
      await setDoc(doc(db, 'users', user.uid), {
        onboardingCompleted: true,
        has_portfolio_data: false,
        updated_at: new Date().toISOString()
      }, { merge: true })
      
      router.push('/dashboard')
    } catch (error: any) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const steps = [
    { number: 1, title: 'Personal Info', icon: User },
    { number: 2, title: 'Investment Goals', icon: Target },
    { number: 3, title: 'Portfolio Data', icon: TrendingUp },
    { number: 4, title: 'Complete', icon: DollarSign }
  ]

  return (
    <YachtLayout title="Welcome to Portora" subtitle="Let's set up your portfolio">
      <div className="max-w-2xl mx-auto">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {steps.map((stepItem, index) => (
              <div key={stepItem.number} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  step >= stepItem.number 
                    ? 'bg-[#C9A66B] border-[#C9A66B] text-white' 
                    : 'border-[#E3DED5] text-[#5A6A73]'
                }`}>
                  <stepItem.icon className="w-5 h-5" />
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-16 h-0.5 mx-2 ${
                    step > stepItem.number ? 'bg-[#C9A66B]' : 'bg-[#E3DED5]'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="text-center">
            <h2 className="text-xl font-semibold text-[#1C3D5A]">
              {steps[step - 1].title}
            </h2>
          </div>
        </div>

        {/* Form Content */}
        <div className="bg-[#FDFBF7] p-8 rounded-2xl shadow-lg border border-[#E3DED5]">
          <form onSubmit={handleSubmit} className="space-y-6">
            {step === 1 && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className="w-full px-4 py-3 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                    placeholder="Enter your full name"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className="w-full px-4 py-3 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                    placeholder="Enter your email"
                    required
                  />
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                    Investment Goal
                  </label>
                  <select
                    value={formData.investmentGoal}
                    onChange={(e) => handleInputChange('investmentGoal', e.target.value)}
                    className="w-full px-4 py-3 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                    required
                  >
                    <option value="">Select your goal</option>
                    <option value="retirement">Retirement Planning</option>
                    <option value="wealth-building">Wealth Building</option>
                    <option value="education">Education Fund</option>
                    <option value="home-purchase">Home Purchase</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                    Risk Tolerance
                  </label>
                  <div className="space-y-2">
                    {[
                      { value: 'conservative', label: 'Conservative - Low risk, steady growth' },
                      { value: 'moderate', label: 'Moderate - Balanced risk and return' },
                      { value: 'aggressive', label: 'Aggressive - High risk, high potential return' }
                    ].map((option) => (
                      <label key={option.value} className="flex items-center space-x-3">
                        <input
                          type="radio"
                          name="riskTolerance"
                          value={option.value}
                          checked={formData.riskTolerance === option.value}
                          onChange={(e) => handleInputChange('riskTolerance', e.target.value)}
                          className="text-[#C9A66B] focus:ring-[#C9A66B]"
                        />
                        <span className="text-[#5A6A73]">{option.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                    Initial Investment Amount
                  </label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#5A6A73] w-5 h-5" />
                    <input
                      type="number"
                      value={formData.initialInvestment}
                      onChange={(e) => handleInputChange('initialInvestment', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                      placeholder="Enter your initial investment"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                    Investment Experience
                  </label>
                  <select
                    value={formData.investmentExperience}
                    onChange={(e) => handleInputChange('investmentExperience', e.target.value)}
                    className="w-full px-4 py-3 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                    required
                  >
                    <option value="">Select your experience level</option>
                    <option value="beginner">Beginner - New to investing</option>
                    <option value="intermediate">Intermediate - Some experience</option>
                    <option value="advanced">Advanced - Experienced investor</option>
                  </select>
                </div>
                
                {/* Portfolio Data Options */}
                <div className="border-t border-[#E3DED5] pt-6">
                  <h3 className="text-lg font-semibold text-[#1C3D5A] mb-4">Add Your Portfolio Data (Optional)</h3>
                  
                  <div className="space-y-4">
                    {/* CSV Upload Option */}
                    <div className="border border-[#E3DED5] rounded-lg p-4">
                      <div className="flex items-center mb-3">
                        <input
                          type="radio"
                          name="dataOption"
                          value="csv"
                          checked={dataOption === 'csv'}
                          onChange={(e) => setDataOption(e.target.value as 'csv')}
                          className="text-[#C9A66B] focus:ring-[#C9A66B]"
                        />
                        <label className="ml-3 font-medium text-[#1C3D5A]">Upload CSV File</label>
                      </div>
                      {dataOption === 'csv' && (
                        <div className="ml-6 space-y-4">
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
                                        <th key={key} className="text-left py-2 pr-4">{key}</th>
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
                    <div className="border border-[#E3DED5] rounded-lg p-4">
                      <div className="flex items-center mb-3">
                        <input
                          type="radio"
                          name="dataOption"
                          value="manual"
                          checked={dataOption === 'manual'}
                          onChange={(e) => setDataOption(e.target.value as 'manual')}
                          className="text-[#C9A66B] focus:ring-[#C9A66B]"
                        />
                        <label className="ml-3 font-medium text-[#1C3D5A]">Add Holdings Manually</label>
                      </div>
                      {dataOption === 'manual' && (
                        <div className="ml-6 space-y-4">
                          <button
                            type="button"
                            onClick={addManualHolding}
                            className="bg-[#C9A66B] text-white px-4 py-2 rounded-lg hover:bg-[#1C3D5A] transition-colors"
                          >
                            Add Holding
                          </button>
                          {manualHoldings.map((holding, index) => (
                            <div key={index} className="bg-[#F5F1EB] p-4 rounded-lg space-y-3">
                              <div className="flex justify-between items-center">
                                <h4 className="font-medium text-[#1C3D5A]">Holding {index + 1}</h4>
                                <button
                                  type="button"
                                  onClick={() => removeManualHolding(index)}
                                  className="text-red-500 hover:text-red-700"
                                >
                                  Remove
                                </button>
                              </div>
                              <div className="grid grid-cols-2 gap-3">
                                <input
                                  type="text"
                                  placeholder="Symbol (e.g., AAPL)"
                                  value={holding.symbol}
                                  onChange={(e) => updateManualHolding(index, 'symbol', e.target.value)}
                                  className="px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                                />
                                <input
                                  type="number"
                                  placeholder="Shares"
                                  value={holding.shares}
                                  onChange={(e) => updateManualHolding(index, 'shares', parseFloat(e.target.value) || 0)}
                                  className="px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                                />
                                <input
                                  type="number"
                                  placeholder="Purchase Price"
                                  value={holding.purchase_price}
                                  onChange={(e) => updateManualHolding(index, 'purchase_price', parseFloat(e.target.value) || 0)}
                                  className="px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                                />
                                <input
                                  type="number"
                                  placeholder="Current Value"
                                  value={holding.total_value}
                                  onChange={(e) => updateManualHolding(index, 'total_value', parseFloat(e.target.value) || 0)}
                                  className="px-3 py-2 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                                />
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Skip Option */}
                    <div className="text-center pt-4">
                      <button
                        type="button"
                        onClick={handleSkip}
                        className="text-[#5A6A73] hover:text-[#C9A66B] transition-colors underline"
                      >
                        Skip for now - I'll add my portfolio later
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-[#C9A66B] rounded-full flex items-center justify-center mx-auto">
                  <DollarSign className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-[#1C3D5A]">
                  Portfolio Setup Complete!
                </h3>
                <p className="text-[#5A6A73]">
                  We've created a sample portfolio for you to get started. 
                  You can modify it later in your dashboard.
                </p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}

            <div className="flex justify-between">
              {step > 1 && (
                <button
                  type="button"
                  onClick={() => setStep(step - 1)}
                  className="px-6 py-3 border border-[#E3DED5] text-[#5A6A73] rounded-lg hover:bg-[#F5F1EB] transition-colors"
                >
                  Previous
                </button>
              )}
              
              <div className="ml-auto">
                {step < 4 ? (
                  <button
                    type="button"
                    onClick={() => setStep(step + 1)}
                    className="px-6 py-3 bg-[#1C3D5A] text-white rounded-lg hover:bg-[#C9A66B] transition-colors"
                  >
                    Next
                  </button>
                ) : (
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-6 py-3 bg-[#C9A66B] text-white rounded-lg hover:bg-[#1C3D5A] transition-colors disabled:opacity-50"
                  >
                    {loading ? 'Setting up...' : 'Complete Setup'}
                  </button>
                )}
              </div>
            </div>
          </form>
        </div>
      </div>
    </YachtLayout>
  )
}
