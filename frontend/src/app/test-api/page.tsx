'use client'

import { useState, useEffect } from 'react'
import YachtLayout from '@/components/Layout/YachtLayout'
import { YachtCard } from '@/components/Cards/YachtCard'

export default function TestAPI() {
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const testAPI = async () => {
    setLoading(true)
    setError(null)
    try {
      console.log('Testing API call...')
      const response = await fetch('http://localhost:8001/portfolio?user_id=1')
      console.log('Response status:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log('API Response:', data)
        setResult(data)
      } else {
        setError(`HTTP Error: ${response.status}`)
      }
    } catch (err: any) {
      console.error('API Error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    testAPI()
  }, [])

  return (
    <YachtLayout 
      title="API Test Page" 
      subtitle="Yacht Club Premium – Development Testing Interface"
    >
      <div className="max-w-4xl mx-auto space-y-6">
        <YachtCard title="Test Results" borderColor="#1C3D5A">
          <button 
            onClick={testAPI}
            disabled={loading}
            className="mb-4 px-4 py-2 bg-primary text-white rounded-md hover:bg-secondary disabled:opacity-50 transition-colors"
          >
            {loading ? 'Testing...' : 'Test API Again'}
          </button>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-800 rounded-md">
              <strong>Error:</strong> {error}
            </div>
          )}

          {result && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 text-green-800 rounded-md">
              <strong>Success!</strong> API call completed successfully.
            </div>
          )}

          {result && (
            <div className="bg-cardBeige p-4 rounded-md">
              <h3 className="text-lg font-medium text-primary mb-2">API Response:</h3>
              <pre className="text-sm text-textSecondary overflow-auto">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </YachtCard>

        <YachtCard title="Debug Info" borderColor="#C9A66B">
          <div className="space-y-2 text-sm text-textSecondary">
            <p><strong>Frontend URL:</strong> {typeof window !== 'undefined' ? window.location.origin : 'N/A'}</p>
            <p><strong>Backend URL:</strong> http://localhost:8001</p>
            <p><strong>User ID:</strong> {typeof window !== 'undefined' ? localStorage.getItem('userId') || '1' : 'N/A'}</p>
            <p><strong>Timestamp:</strong> {new Date().toISOString()}</p>
          </div>
        </YachtCard>
      </div>
    </YachtLayout>
  )
}
