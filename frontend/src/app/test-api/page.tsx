'use client'

import { useState, useEffect } from 'react'

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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">API Test Page</h1>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Test Results</h2>
          
          <button 
            onClick={testAPI}
            disabled={loading}
            className="mb-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Test API Again'}
          </button>

          {error && (
            <div className="mb-4 p-4 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-md">
              <strong>Error:</strong> {error}
            </div>
          )}

          {result && (
            <div className="mb-4 p-4 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-md">
              <strong>Success!</strong> API call completed successfully.
            </div>
          )}

          {result && (
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-md">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">API Response:</h3>
              <pre className="text-sm text-gray-600 dark:text-gray-300 overflow-auto">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Debug Info</h2>
          <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
            <p><strong>Frontend URL:</strong> {typeof window !== 'undefined' ? window.location.origin : 'N/A'}</p>
            <p><strong>Backend URL:</strong> http://localhost:8001</p>
            <p><strong>User ID:</strong> {typeof window !== 'undefined' ? localStorage.getItem('userId') || '1' : 'N/A'}</p>
            <p><strong>Timestamp:</strong> {new Date().toISOString()}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
