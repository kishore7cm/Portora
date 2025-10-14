'use client'

import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import YachtLayout from '@/components/Layout/YachtLayout'

export default function Home() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [checkingData, setCheckingData] = useState(false)

  useEffect(() => {
    const checkUserAndRedirect = async () => {
      if (!loading && user) {
        setCheckingData(true)
        try {
          // Check if user has portfolio data
          const response = await fetch(`/api/portfolio?user_id=${user.uid}`)
          if (response.ok) {
            const data = await response.json()
            if (data.data && data.data.length > 0) {
              router.push('/dashboard')
            } else {
              router.push('/onboarding')
            }
          } else {
            router.push('/onboarding')
          }
        } catch (error) {
          router.push('/onboarding')
        } finally {
          setCheckingData(false)
        }
      } else if (!loading && !user) {
        router.push('/auth')
      }
    }

    checkUserAndRedirect()
  }, [user, loading, router])

  if (loading || checkingData) {
    return (
      <YachtLayout title="Loading..." subtitle="Initializing Portora">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#C9A66B] mx-auto mb-4"></div>
          <p className="text-[#5A6A73]">
            {loading ? 'Loading...' : 'Checking your portfolio...'}
          </p>
        </div>
      </YachtLayout>
    )
  }

  return (
    <YachtLayout 
      title="Portora Portfolio Management" 
      subtitle="Yacht Club Premium – Sophisticated Wealth Management"
    >
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-[#1C3D5A]">Portora Portfolio Management</h1>
        <p className="text-[#5A6A73] mt-2">Redirecting...</p>
        <a href="/auth" className="text-[#C9A66B] hover:text-[#1C3D5A] transition-colors">Click here if not redirected</a>
      </div>
    </YachtLayout>
  )
}