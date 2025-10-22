'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { signInWithEmailAndPassword } from 'firebase/auth'
import { auth } from '@/lib/firebaseClient'
import { useAuth } from '@/hooks/useAuth'
import YachtLayout from '@/components/Layout/YachtLayout'
import { Mail, Lock, Eye, EyeOff } from 'lucide-react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()

  // Redirect if already authenticated
  useEffect(() => {
    if (!authLoading && user) {
      console.log('✅ User already authenticated, redirecting to dashboard')
      router.push('/dashboard')
    }
  }, [user, authLoading, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password)
      const user = userCredential.user
      
      console.log('✅ Login successful for user:', user.uid)
      
      // Store user info in localStorage
      localStorage.setItem('userId', user.uid)
      localStorage.setItem('userEmail', user.email || '')
      localStorage.setItem('userName', user.displayName || '')
      localStorage.setItem('loggedIn', 'true')
      
      // Wait a moment for auth state to update, then redirect
      setTimeout(() => {
        console.log('🔄 Redirecting to dashboard...')
        router.push('/dashboard')
      }, 500)
    } catch (error: any) {
      console.error('Login error:', error)
      setError('Incorrect login information')
    } finally {
      setLoading(false)
    }
  }

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <YachtLayout title="Welcome to Portora" subtitle="Yacht Club Premium – Sophisticated Wealth Management">
        <div className="max-w-md mx-auto">
          <div className="bg-[#FDFBF7] p-8 rounded-2xl shadow-lg border border-[#E3DED5] text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#C9A66B] mx-auto mb-4"></div>
            <p className="text-[#5A6A73]">Checking authentication...</p>
          </div>
        </div>
      </YachtLayout>
    )
  }

  return (
    <YachtLayout title="Welcome to Portora" subtitle="Yacht Club Premium – Sophisticated Wealth Management">
      <div className="max-w-md mx-auto">
        <div className="bg-[#FDFBF7] p-8 rounded-2xl shadow-lg border border-[#E3DED5]">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-[#1C3D5A] mb-2">
              Welcome Back
            </h2>
            <p className="text-[#5A6A73]">
              Sign in to your portfolio
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#5A6A73] w-5 h-5" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent bg-white"
                  placeholder="Enter your email"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#5A6A73] w-5 h-5" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-12 py-3 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent bg-white"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#5A6A73] hover:text-[#1C3D5A]"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#1C3D5A] hover:bg-[#C9A66B] text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-[#5A6A73]">
              Don't have an account?{' '}
              <button
                onClick={() => router.push('/auth')}
                className="text-[#C9A66B] hover:text-[#1C3D5A] font-medium"
              >
                Sign up
              </button>
            </p>
          </div>
        </div>
      </div>
    </YachtLayout>
  )
}
