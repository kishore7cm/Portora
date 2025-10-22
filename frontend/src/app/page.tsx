'use client'

import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Link from 'next/link'
import { 
  TrendingUp, 
  Shield, 
  BarChart3, 
  Users, 
  Target, 
  Zap,
  ArrowRight,
  CheckCircle,
  Star,
  Globe,
  Smartphone,
  Lock
} from 'lucide-react'

export default function LandingPage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (loading) return // Don't redirect while loading
    
    // Simple redirect logic - no state tracking to prevent loops
    if (!user) {
      console.log('🔍 No user found, redirecting to login')
      router.replace('/login')
    } else {
      console.log('✅ User authenticated, redirecting to dashboard')
      router.replace('/dashboard')
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#FDFBF7] to-[#EDE9E3] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#C9A66B] mx-auto mb-4"></div>
          <p className="text-[#5A6A73]">Loading...</p>
        </div>
      </div>
    )
  }

  if (user) {
    return null // Will redirect to dashboard
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FDFBF7] to-[#EDE9E3]">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-[#E3DED5] sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-[#1C3D5A]">Portora</h1>
              </div>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-8">
                <Link href="#features" className="text-[#5A6A73] hover:text-[#1C3D5A] transition-colors">Features</Link>
                <Link href="#pricing" className="text-[#5A6A73] hover:text-[#1C3D5A] transition-colors">Pricing</Link>
                <Link href="/about" className="text-[#5A6A73] hover:text-[#1C3D5A] transition-colors">About</Link>
                <Link href="/contact" className="text-[#5A6A73] hover:text-[#1C3D5A] transition-colors">Contact</Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                href="/auth" 
                className="text-[#5A6A73] hover:text-[#1C3D5A] transition-colors"
              >
                Sign In
              </Link>
              <Link 
                href="/auth" 
                className="bg-[#C9A66B] text-white px-6 py-2 rounded-lg hover:bg-[#1C3D5A] transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-[#1C3D5A] mb-6">
            Sophisticated
            <span className="block text-[#C9A66B]">Wealth Management</span>
          </h1>
          <p className="text-xl text-[#5A6A73] mb-8 max-w-3xl mx-auto">
            Yacht Club Premium portfolio management with AI insights, real-time analytics, 
            and professional-grade tools for serious investors.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/auth" 
              className="bg-[#C9A66B] text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-[#1C3D5A] transition-colors flex items-center justify-center"
            >
              Start Your Journey
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            <Link 
              href="#features" 
              className="border-2 border-[#C9A66B] text-[#C9A66B] px-8 py-4 rounded-lg text-lg font-semibold hover:bg-[#C9A66B] hover:text-white transition-colors"
            >
              Explore Features
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-[#1C3D5A] mb-4">Premium Features</h2>
            <p className="text-xl text-[#5A6A73] max-w-2xl mx-auto">
              Everything you need for professional portfolio management
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: <TrendingUp className="w-8 h-8" />,
                title: "Real-Time Analytics",
                description: "Live portfolio tracking with advanced metrics and performance insights."
              },
              {
                icon: <Shield className="w-8 h-8" />,
                title: "Secure & Private",
                description: "Bank-grade security with end-to-end encryption for your financial data."
              },
              {
                icon: <BarChart3 className="w-8 h-8" />,
                title: "AI Insights",
                description: "Smart recommendations powered by machine learning and market analysis."
              },
              {
                icon: <Users className="w-8 h-8" />,
                title: "Community",
                description: "Connect with other investors and share strategies in our exclusive community."
              },
              {
                icon: <Target className="w-8 h-8" />,
                title: "Goal Tracking",
                description: "Set and monitor your financial goals with personalized progress tracking."
              },
              {
                icon: <Zap className="w-8 h-8" />,
                title: "Automation",
                description: "Automated portfolio rebalancing and smart trading suggestions."
              }
            ].map((feature, index) => (
              <div key={index} className="bg-[#FDFBF7] p-8 rounded-2xl shadow-lg border border-[#E3DED5] hover:shadow-xl transition-shadow">
                <div className="text-[#C9A66B] mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-[#1C3D5A] mb-3">{feature.title}</h3>
                <p className="text-[#5A6A73]">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-[#1C3D5A] text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            {[
              { number: "10K+", label: "Active Users" },
              { number: "$2.5B+", label: "Assets Managed" },
              { number: "99.9%", label: "Uptime" },
              { number: "4.9★", label: "User Rating" }
            ].map((stat, index) => (
              <div key={index}>
                <div className="text-4xl font-bold text-[#C9A66B] mb-2">{stat.number}</div>
                <div className="text-lg text-gray-300">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-[#1C3D5A] mb-6">
            Ready to Elevate Your Portfolio?
          </h2>
          <p className="text-xl text-[#5A6A73] mb-8">
            Join thousands of sophisticated investors who trust Portora for their wealth management.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/auth" 
              className="bg-[#C9A66B] text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-[#1C3D5A] transition-colors flex items-center justify-center"
            >
              Get Started Free
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            <Link 
              href="/contact" 
              className="border-2 border-[#C9A66B] text-[#C9A66B] px-8 py-4 rounded-lg text-lg font-semibold hover:bg-[#C9A66B] hover:text-white transition-colors"
            >
              Schedule Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#1C3D5A] text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-2xl font-bold text-[#C9A66B] mb-4">Portora</h3>
              <p className="text-gray-300">
                Sophisticated wealth management for the modern investor.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-300">
                <li><Link href="#features" className="hover:text-[#C9A66B] transition-colors">Features</Link></li>
                <li><Link href="#pricing" className="hover:text-[#C9A66B] transition-colors">Pricing</Link></li>
                <li><Link href="/about" className="hover:text-[#C9A66B] transition-colors">About</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-300">
                <li><Link href="/contact" className="hover:text-[#C9A66B] transition-colors">Contact</Link></li>
                <li><Link href="#" className="hover:text-[#C9A66B] transition-colors">Help Center</Link></li>
                <li><Link href="#" className="hover:text-[#C9A66B] transition-colors">Documentation</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-300">
                <li><Link href="#" className="hover:text-[#C9A66B] transition-colors">Privacy Policy</Link></li>
                <li><Link href="#" className="hover:text-[#C9A66B] transition-colors">Terms of Service</Link></li>
                <li><Link href="#" className="hover:text-[#C9A66B] transition-colors">Security</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-300">
            <p>&copy; 2025 Portora. All rights reserved. Yacht Club Premium © 2025</p>
          </div>
        </div>
      </footer>
    </div>
  )
}