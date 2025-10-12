'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import YachtLayout from '@/components/Layout/YachtLayout'
import { YachtCard } from '@/components/Cards/YachtCard'

export default function AuthPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      // Simple demo login - in production, this would call your auth API
      if (email === 'demo@portora.com' && password === 'demo123') {
        // Store user data in localStorage
        localStorage.setItem('loggedIn', 'true')
        localStorage.setItem('userEmail', email)
        localStorage.setItem('userId', '1')
        localStorage.setItem('userName', 'Demo User')
        
        // Redirect to dashboard
        router.push('/dashboard')
      } else {
        setError('Invalid credentials. Use demo@portora.com / demo123')
      }
    } catch (err) {
      setError('Login failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDemoLogin = () => {
    setEmail('demo@portora.com')
    setPassword('demo123')
  }

  return (
    <YachtLayout 
      title="Wealtheon Authentication" 
      subtitle="Yacht Club Premium – Secure Access to Your Portfolio"
    >
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-primary">
            Sign in to your account
          </h2>
          <p className="mt-2 text-textSecondary">
            Or{' '}
            <button
              onClick={handleDemoLogin}
              className="font-medium text-accent hover:text-primary transition-colors"
            >
              use demo credentials
            </button>
          </p>
        </div>

        <YachtCard title="Login" borderColor="#1C3D5A">
          <form className="space-y-6" onSubmit={handleLogin}>
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="text-sm text-red-800">
                  {error}
                </div>
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-primary">
                Email address
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-cardBeige rounded-md placeholder-textSecondary bg-yachtBackground text-primary focus:outline-none focus:ring-accent focus:border-accent sm:text-sm"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-primary">
                Password
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-cardBeige rounded-md placeholder-textSecondary bg-yachtBackground text-primary focus:outline-none focus:ring-accent focus:border-accent sm:text-sm"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-secondary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-cardBeige" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-yachtBackground text-textSecondary">
                  Demo Credentials
                </span>
              </div>
            </div>

            <div className="mt-6">
              <div className="bg-accent/10 border border-accent rounded-md p-4">
                <div className="text-sm text-primary">
                  <p className="font-medium mb-2">Demo Login:</p>
                  <p><strong>Email:</strong> demo@portora.com</p>
                  <p><strong>Password:</strong> demo123</p>
                </div>
              </div>
            </div>
          </div>
        </YachtCard>
      </div>
    </YachtLayout>
  )
}
