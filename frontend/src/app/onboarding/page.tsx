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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      if (!user) {
        throw new Error('User not authenticated')
      }

      // Update user document with onboarding data
      await setDoc(doc(db, 'users', user.uid), {
        uid: user.uid,
        email: user.email,
        name: formData.name,
        createdAt: new Date(),
        lastLogin: new Date(),
        portfolioValue: parseFloat(formData.initialInvestment) || 0,
        lastYearValue: parseFloat(formData.initialInvestment) || 0,
        investmentGoal: formData.investmentGoal,
        riskTolerance: formData.riskTolerance,
        investmentExperience: formData.investmentExperience,
        onboardingCompleted: true
      }, { merge: true })

      // Create sample portfolio data for new user
      const samplePortfolio = [
        {
          Ticker: 'AAPL',
          Qty: Math.floor(parseFloat(formData.initialInvestment) * 0.3 / 175),
          Current_Price: 175.00,
          Total_Value: parseFloat(formData.initialInvestment) * 0.3,
          Gain_Loss: 0,
          Gain_Loss_Percent: 0,
          Category: 'Stock',
          Sector: 'Technology'
        },
        {
          Ticker: 'VOO',
          Qty: Math.floor(parseFloat(formData.initialInvestment) * 0.4 / 520),
          Current_Price: 520.00,
          Total_Value: parseFloat(formData.initialInvestment) * 0.4,
          Gain_Loss: 0,
          Gain_Loss_Percent: 0,
          Category: 'ETF',
          Sector: 'Diversified'
        },
        {
          Ticker: 'Cash',
          Qty: 1,
          Current_Price: parseFloat(formData.initialInvestment) * 0.3,
          Total_Value: parseFloat(formData.initialInvestment) * 0.3,
          Gain_Loss: 0,
          Gain_Loss_Percent: 0,
          Category: 'Cash',
          Sector: 'Cash'
        }
      ]

      // Store sample portfolio data
      await setDoc(doc(db, 'portfolio_data', user.uid), {
        user_id: user.uid,
        data: samplePortfolio,
        lastUpdated: new Date()
      })

      // Redirect to dashboard
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
    { number: 3, title: 'Portfolio Setup', icon: TrendingUp },
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
