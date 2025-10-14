'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import YachtLayout from '@/components/Layout/YachtLayout'
import { Database, ArrowRight, CheckCircle, AlertCircle } from 'lucide-react'

export default function MigrateExistingPage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')
  const [existingData, setExistingData] = useState<any>(null)
  const { user } = useAuth()

  useEffect(() => {
    if (user) {
      checkExistingData()
    }
  }, [user])

  const checkExistingData = async () => {
    if (!user) return

    try {
      const response = await fetch(`/api/check-existing-data?user_id=${user.uid}`)
      if (response.ok) {
        const data = await response.json()
        setExistingData(data.data)
        console.log('📊 Existing data:', data.data)
      }
    } catch (error) {
      console.error('❌ Error checking existing data:', error)
    }
  }

  const migrateLegacyData = async () => {
    if (!user) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      // Get legacy data (user_id = 1)
      const response = await fetch(`/api/portfolio?user_id=1`)
      if (response.ok) {
        const data = await response.json()
        if (data.data && data.data.length > 0) {
          // Migrate to new structure
          const migrateResponse = await fetch('/api/migrate-portfolio', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              userId: user.uid,
              holdings: data.data.map(holding => ({
                symbol: holding.Ticker,
                asset_type: holding.Category,
                purchase_price: holding.Current_Price,
                shares: holding.Qty,
                total_cost: holding.Cost_Basis,
                total_value: holding.Total_Value,
                account_name: 'Legacy Account'
              }))
            })
          })

          const migrateData = await migrateResponse.json()
          
          if (migrateResponse.ok) {
            setResult(migrateData)
            console.log('✅ Migration successful:', migrateData)
            // Refresh existing data check
            checkExistingData()
          } else {
            setError(migrateData.error || 'Migration failed')
            console.error('❌ Migration failed:', migrateData)
          }
        } else {
          setError('No legacy data found to migrate')
        }
      } else {
        setError('Failed to fetch legacy data')
      }
    } catch (err: any) {
      setError(err.message)
      console.error('❌ Migration error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return (
      <YachtLayout title="Data Migration" subtitle="Please log in to migrate your data">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-[#C9A66B] mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-[#1C3D5A] mb-2">Authentication Required</h2>
          <p className="text-[#5A6A73]">Please log in to migrate your portfolio data.</p>
        </div>
      </YachtLayout>
    )
  }

  return (
    <YachtLayout title="Data Migration" subtitle="Migrate your existing portfolio data">
      <div className="max-w-4xl mx-auto">
        <div className="bg-[#FDFBF7] p-8 rounded-2xl shadow-lg border border-[#E3DED5]">
          <div className="text-center mb-8">
            <Database className="w-16 h-16 text-[#C9A66B] mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-[#1C3D5A] mb-2">
              Portfolio Data Migration
            </h2>
            <p className="text-[#5A6A73]">
              Migrate your existing portfolio data to the new optimized structure.
            </p>
          </div>

          {existingData && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-[#EDE9E3] p-6 rounded-lg">
                <h3 className="font-semibold text-[#1C3D5A] mb-2">New Structure</h3>
                <p className="text-sm text-[#5A6A73]">
                  {existingData.new_structure.exists ? 
                    `✅ ${existingData.new_structure.holdings_count} holdings` : 
                    '❌ No data'
                  }
                </p>
              </div>
              
              <div className="bg-[#EDE9E3] p-6 rounded-lg">
                <h3 className="font-semibold text-[#1C3D5A] mb-2">Old Structure</h3>
                <p className="text-sm text-[#5A6A73]">
                  {existingData.old_structure.exists ? 
                    `✅ ${existingData.old_structure.documents_count} documents` : 
                    '❌ No data'
                  }
                </p>
              </div>
              
              <div className="bg-[#EDE9E3] p-6 rounded-lg">
                <h3 className="font-semibold text-[#1C3D5A] mb-2">Legacy Data</h3>
                <p className="text-sm text-[#5A6A73]">
                  {existingData.legacy_data.exists ? 
                    `✅ ${existingData.legacy_data.documents_count} documents` : 
                    '❌ No data'
                  }
                </p>
              </div>
            </div>
          )}

          {existingData?.legacy_data.exists && !existingData?.new_structure.exists && (
            <div className="bg-[#EDE9E3] p-6 rounded-lg mb-6">
              <div className="flex items-center mb-4">
                <AlertCircle className="w-6 h-6 text-[#C9A66B] mr-3" />
                <h3 className="font-semibold text-[#1C3D5A]">Legacy Data Found</h3>
              </div>
              <p className="text-[#5A6A73] mb-4">
                We found {existingData.legacy_data.documents_count} portfolio documents in the legacy format. 
                You can migrate them to the new optimized structure.
              </p>
              <button
                onClick={migrateLegacyData}
                disabled={loading}
                className="px-6 py-3 bg-[#C9A66B] text-white rounded-lg hover:bg-[#1C3D5A] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {loading ? 'Migrating...' : 'Migrate Legacy Data'}
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </div>
          )}

          {existingData?.new_structure.exists && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center">
                <CheckCircle className="w-6 h-6 text-green-500 mr-3" />
                <div>
                  <h3 className="font-semibold text-green-800">Migration Complete</h3>
                  <p className="text-green-600 text-sm">
                    Your portfolio data has been migrated to the new structure with {existingData.new_structure.holdings_count} holdings.
                  </p>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            </div>
          )}

          {result && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                <div>
                  <p className="text-green-600 font-medium">Migration Successful!</p>
                  <p className="text-green-600 text-sm">
                    {result.total_holdings} holdings migrated
                  </p>
                  <p className="text-green-600 text-sm">
                    Total Portfolio Value: ${result.total_portfolio_value?.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </YachtLayout>
  )
}
