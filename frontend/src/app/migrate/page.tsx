'use client'

import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import YachtLayout from '@/components/Layout/YachtLayout'
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react'

export default function MigratePage() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')
  const { user } = useAuth()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError('')
      setResult(null)
    }
  }

  const parseCSV = (csvText: string) => {
    const lines = csvText.split('\n')
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
    
    const holdings = lines.slice(1).map(line => {
      const values = line.split(',').map(v => v.trim().replace(/"/g, ''))
      const holding: any = {}
      
      headers.forEach((header, index) => {
        const value = values[index]
        if (value) {
          // Convert numeric fields
          if (['shares', 'purchase_price', 'total_cost', 'total_value'].includes(header)) {
            holding[header] = parseFloat(value)
          } else {
            holding[header] = value
          }
        }
      })
      
      return holding
    }).filter(h => h.symbol && h.shares) // Filter out empty rows
    
    return holdings
  }

  const handleUpload = async () => {
    if (!file || !user) {
      setError('Please select a file and ensure you are logged in')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const csvText = await file.text()
      const holdings = parseCSV(csvText)
      
      console.log('📊 Parsed holdings:', holdings)
      
      // Send to migration API
      const response = await fetch('/api/migrate-portfolio', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: user.uid,
          holdings: holdings
        })
      })

      const data = await response.json()
      
      if (response.ok) {
        setResult(data)
        console.log('✅ Migration successful:', data)
      } else {
        setError(data.error || 'Migration failed')
        console.error('❌ Migration failed:', data)
      }
    } catch (err: any) {
      setError(err.message)
      console.error('❌ Upload error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return (
      <YachtLayout title="Portfolio Migration" subtitle="Please log in to migrate your portfolio">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-[#C9A66B] mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-[#1C3D5A] mb-2">Authentication Required</h2>
          <p className="text-[#5A6A73]">Please log in to migrate your portfolio data.</p>
        </div>
      </YachtLayout>
    )
  }

  return (
    <YachtLayout title="Portfolio Migration" subtitle="Upload your CSV to create your portfolio document">
      <div className="max-w-2xl mx-auto">
        <div className="bg-[#FDFBF7] p-8 rounded-2xl shadow-lg border border-[#E3DED5]">
          <div className="text-center mb-8">
            <Upload className="w-16 h-16 text-[#C9A66B] mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-[#1C3D5A] mb-2">
              Migrate Your Portfolio
            </h2>
            <p className="text-[#5A6A73]">
              Upload your portfolio CSV file to create a single document with all your holdings.
            </p>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                Select CSV File
              </label>
              <div className="border-2 border-dashed border-[#E3DED5] rounded-lg p-6 text-center hover:border-[#C9A66B] transition-colors">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="hidden"
                  id="csv-upload"
                />
                <label htmlFor="csv-upload" className="cursor-pointer">
                  <FileText className="w-8 h-8 text-[#5A6A73] mx-auto mb-2" />
                  <p className="text-[#5A6A73]">
                    {file ? file.name : 'Click to select CSV file'}
                  </p>
                </label>
              </div>
            </div>

            {file && (
              <div className="bg-[#EDE9E3] p-4 rounded-lg">
                <h3 className="font-medium text-[#1C3D5A] mb-2">Selected File:</h3>
                <p className="text-sm text-[#5A6A73]">{file.name}</p>
                <p className="text-sm text-[#5A6A73]">
                  Size: {(file.size / 1024).toFixed(2)} KB
                </p>
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

            <button
              onClick={handleUpload}
              disabled={!file || loading}
              className="w-full px-6 py-3 bg-[#C9A66B] text-white rounded-lg hover:bg-[#1C3D5A] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Migrating...' : 'Migrate Portfolio'}
            </button>
          </div>
        </div>
      </div>
    </YachtLayout>
  )
}
