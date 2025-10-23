'use client'

import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function LandingPage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (loading) return
    
    if (user) {
      router.replace('/dashboard')
    } else {
      router.replace('/login')
    }
  }, [user, loading])

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FDFBF7] to-[#EDE9E3] flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#C9A66B] mx-auto mb-4"></div>
        <p className="text-[#5A6A73]">Loading...</p>
      </div>
    </div>
  )
}