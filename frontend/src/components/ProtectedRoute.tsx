'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from '@/lib/firebaseClient'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState<any>(null)
  const router = useRouter()

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        setUser(user)
        // Store user info in localStorage
        localStorage.setItem('userId', user.uid)
        localStorage.setItem('userEmail', user.email || '')
        localStorage.setItem('userName', user.displayName || '')
        localStorage.setItem('loggedIn', 'true')
      } else {
        setUser(null)
        localStorage.removeItem('userId')
        localStorage.removeItem('userEmail')
        localStorage.removeItem('userName')
        localStorage.removeItem('loggedIn')
        router.push('/login')
      }
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#C9A66B] mx-auto mb-4"></div>
          <p className="text-[#5A6A73]">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return <>{children}</>
}
