'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import Container from '@/components/ui/Container'

export default function PricingSection() {
  const [isMonthly, setIsMonthly] = useState(true)
  const [isVisible, setIsVisible] = useState(false)
  const sectionRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
        }
      },
      { threshold: 0.1 }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current)
      }
    }
  }, [])

  const monthlyPrices = {
    free: 0,
    pro: 14.99,
    elite: 29.99
  }

  const yearlyPrices = {
    free: 0,
    pro: 11.99, // ~20% off
    elite: 23.99 // ~20% off
  }

  const prices = isMonthly ? monthlyPrices : yearlyPrices

  return (
    <section 
      ref={sectionRef}
      id="pricing" 
      className="relative py-16 md:py-24 bg-gradient-to-b from-brand-50/50 via-white to-brand-50/30 overflow-hidden"
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(14,165,233,0.05),transparent_50%)]" />
      <Container className="relative">
        <div 
          className={`mx-auto max-w-3xl text-center mb-12 transition-opacity duration-1000 ${isVisible ? 'opacity-100' : 'opacity-0'}`}
        >
          <h2 className="text-3xl font-bold tracking-tight text-neutral-900 md:text-4xl lg:text-5xl">
            Simple pricing
          </h2>
          <p className="mt-4 text-lg text-neutral-600 md:text-xl">
            Start free during beta. Upgrade anytime to unlock advanced features.
          </p>
        </div>

        {/* Monthly/Yearly Toggle */}
        <div 
          className={`flex justify-center mb-12 transition-opacity duration-1000 delay-200 ${isVisible ? 'opacity-100' : 'opacity-0'}`}
        >
          <div className="inline-flex items-center gap-3 bg-white p-1.5 rounded-xl border border-neutral-200 shadow-soft">
            <button
              onClick={() => setIsMonthly(true)}
              className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${
                isMonthly 
                  ? 'bg-gradient-brand text-white shadow-soft' 
                  : 'text-neutral-600 hover:text-neutral-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setIsMonthly(false)}
              className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-200 ${
                !isMonthly 
                  ? 'bg-gradient-brand text-white shadow-soft' 
                  : 'text-neutral-600 hover:text-neutral-900'
              }`}
            >
              Yearly
              <span className="ml-1.5 text-xs text-brand-600 font-normal">Save 20%</span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div 
          className={`grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-8 transition-opacity duration-1000 delay-300 ${isVisible ? 'opacity-100' : 'opacity-0'}`}
        >
          {/* Free Tier */}
          <div className="relative rounded-2xl border-2 border-neutral-200 bg-white p-8 text-center shadow-medium hover:shadow-strong hover:scale-105 hover:border-brand-300 transition-all duration-300 group">
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
              <span className="rounded-full bg-gradient-to-r from-brand-100 to-brand-50 px-4 py-1.5 text-sm font-semibold text-brand-700 shadow-soft">
                Beta Access
              </span>
            </div>
            <div className="mt-4">
              <h3 className="text-2xl font-bold text-neutral-900 mb-2">Free</h3>
              <div className="text-5xl font-bold bg-gradient-to-r from-neutral-900 to-neutral-700 bg-clip-text text-transparent">
                ${prices.free}
              </div>
              <div className="mt-2 text-lg text-neutral-600">Free during beta</div>
              <ul className="mt-6 space-y-3 text-left text-neutral-600">
                <li className="flex items-center gap-3">
                  <span className="text-brand-600 font-bold">✓</span>
                  Portfolio tracking
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-brand-600 font-bold">✓</span>
                  Smart insights
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-brand-600 font-bold">✓</span>
                  CSV import
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-brand-600 font-bold">✓</span>
                  Email support
                </li>
              </ul>
              <Link 
                href="/signup" 
                className="mt-8 inline-block w-full rounded-xl bg-gradient-brand px-6 py-4 font-semibold text-white hover:shadow-brand shadow-medium hover:scale-105 transition-all duration-300"
              >
                Join the Beta
              </Link>
            </div>
          </div>

          {/* Pro Tier - Highlighted */}
          <div className="relative rounded-2xl border-2 border-brand-400 bg-gradient-to-br from-brand-50/50 to-white p-8 text-center shadow-strong hover:shadow-brand hover:scale-105 transition-all duration-300 group transform md:-mt-2 md:mb-2">
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
              <span className="rounded-full bg-gradient-brand px-4 py-1.5 text-sm font-semibold text-white shadow-brand">
                Most Popular
              </span>
            </div>
            <div className="mt-4">
              <h3 className="text-2xl font-bold text-neutral-900 mb-2">Pro</h3>
              <div className="text-5xl font-bold bg-gradient-to-r from-brand-600 to-brand-500 bg-clip-text text-transparent">
                ${prices.pro}
                <span className="text-2xl text-neutral-500">/mo</span>
              </div>
              <div className="mt-2 text-lg text-neutral-600">
                {isMonthly ? 'For active investors' : 'Billed annually ($143.88/year)'}
              </div>
              <ul className="mt-6 space-y-3 text-left text-neutral-600">
                <li className="flex items-center gap-3">
                  <span className="text-brand-600 font-bold">✓</span>
                  <span>All Free features</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-brand-600 font-bold">✓</span>
                  AI insights
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-brand-600 font-bold">✓</span>
                  Drift alerts
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-brand-600 font-bold">✓</span>
                  PDF reports
                </li>
              </ul>
              <Link 
                href="/signup" 
                className="mt-8 inline-block w-full rounded-xl bg-gradient-brand px-6 py-4 font-semibold text-white hover:shadow-brand shadow-medium hover:scale-105 transition-all duration-300"
              >
                Start Free Trial
              </Link>
            </div>
          </div>

          {/* Elite Tier */}
          <div className="relative rounded-2xl border-2 border-neutral-200 bg-white p-8 text-center shadow-medium hover:shadow-strong hover:scale-105 hover:border-brand-300 transition-all duration-300 group">
            <div className="mt-4">
              <h3 className="text-2xl font-bold text-neutral-900 mb-2">Elite</h3>
              <div className="text-5xl font-bold bg-gradient-to-r from-neutral-900 to-neutral-700 bg-clip-text text-transparent">
                ${prices.elite}
                <span className="text-2xl text-neutral-500">/mo</span>
              </div>
              <div className="mt-2 text-lg text-neutral-600">
                {isMonthly ? 'For power users & multi-asset portfolios' : 'Billed annually ($287.88/year)'}
              </div>
              <ul className="mt-6 space-y-3 text-left text-neutral-600">
                <li className="flex items-center gap-3">
                  <span className="text-brand-600 font-bold">✓</span>
                  <span>All Pro features</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-brand-600 font-bold">✓</span>
                  Backtesting
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-brand-600 font-bold">✓</span>
                  Advanced analytics
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-brand-600 font-bold">✓</span>
                  Priority support
                </li>
              </ul>
              <Link 
                href="/signup" 
                className="mt-8 inline-block w-full rounded-xl border-2 border-brand-600 px-6 py-4 font-semibold text-brand-600 hover:bg-brand-600 hover:text-white shadow-soft hover:shadow-medium transition-all duration-300 pointer-events-none opacity-50 cursor-not-allowed"
                onClick={(e) => e.preventDefault()}
              >
                Upgrade Now
              </Link>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div 
          className={`text-center mt-8 transition-opacity duration-1000 delay-500 ${isVisible ? 'opacity-100' : 'opacity-0'}`}
        >
          <p className="text-sm text-neutral-500">
            *All plans include portfolio syncing and AI-powered insights.*
          </p>
        </div>
      </Container>
    </section>
  )
}

