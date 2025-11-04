'use client'

import Link from 'next/link'
import Navbar from '@/components/site/Navbar'
import Footer from '@/components/site/Footer'
import Container from '@/components/ui/Container'
import { 
  Check, 
  X, 
  Star,
  ArrowRight,
  Crown,
  Zap,
  Shield
} from 'lucide-react'

export default function PricingPage() {
  const plans = [
    {
      name: "Starter",
      price: "Free",
      description: "Perfect for getting started with portfolio management",
      features: [
        "Up to 5 holdings",
        "Basic portfolio tracking",
        "Email support",
        "Mobile app access",
        "Basic analytics"
      ],
      limitations: [
        "No AI insights",
        "No advanced analytics",
        "No community access"
      ],
      cta: "Get Started Free",
      popular: false
    },
    {
      name: "Professional",
      price: "$29",
      period: "/month",
      description: "For serious investors who want advanced tools",
      features: [
        "Unlimited holdings",
        "Advanced analytics",
        "AI-powered insights",
        "Priority support",
        "Community access",
        "Goal tracking",
        "Performance benchmarking",
        "Export capabilities"
      ],
      limitations: [],
      cta: "Start Free Trial",
      popular: true
    },
    {
      name: "Premium",
      price: "$99",
      period: "/month",
      description: "For sophisticated investors and institutions",
      features: [
        "Everything in Professional",
        "Custom integrations",
        "Dedicated account manager",
        "White-label options",
        "Advanced automation",
        "Institutional reporting",
        "API access",
        "Custom analytics"
      ],
      limitations: [],
      cta: "Contact Sales",
      popular: false
    }
  ]

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-soft">

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-[#1C3D5A] mb-6">
            Simple, Transparent <span className="text-[#C9A66B]">Pricing</span>
          </h1>
          <p className="text-xl text-[#5A6A73] mb-8">
            Choose the plan that fits your investment journey. 
            All plans include our core portfolio management features.
          </p>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <div 
                key={index} 
                className={`relative bg-[#FDFBF7] rounded-2xl shadow-lg border-2 p-8 ${
                  plan.popular 
                    ? 'border-[#C9A66B] ring-2 ring-[#C9A66B] ring-opacity-20' 
                    : 'border-[#E3DED5]'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="bg-[#C9A66B] text-white px-4 py-2 rounded-full text-sm font-semibold flex items-center">
                      <Star className="w-4 h-4 mr-1" />
                      Most Popular
                    </div>
                  </div>
                )}
                
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-[#1C3D5A] mb-2">{plan.name}</h3>
                  <div className="flex items-baseline justify-center mb-2">
                    <span className="text-4xl font-bold text-[#C9A66B]">{plan.price}</span>
                    {plan.period && (
                      <span className="text-lg text-[#5A6A73] ml-1">{plan.period}</span>
                    )}
                  </div>
                  <p className="text-[#5A6A73]">{plan.description}</p>
                </div>

                <div className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-center">
                      <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                      <span className="text-[#5A6A73]">{feature}</span>
                    </div>
                  ))}
                  {plan.limitations.map((limitation, limitationIndex) => (
                    <div key={limitationIndex} className="flex items-center">
                      <X className="w-5 h-5 text-red-400 mr-3 flex-shrink-0" />
                      <span className="text-gray-400">{limitation}</span>
                    </div>
                  ))}
                </div>

                <Link
                  href={plan.cta === "Contact Sales" ? "/contact" : "/signup"}
                  className={`w-full block text-center py-3 px-6 rounded-xl font-semibold transition-all duration-300 ${
                    plan.popular
                      ? 'bg-gradient-brand text-white hover:shadow-brand shadow-medium'
                      : 'border-2 border-brand-600 text-brand-600 hover:bg-brand-600 hover:text-white shadow-soft'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Comparison */}
      <section className="py-20 bg-white/50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-[#1C3D5A] mb-4">Feature Comparison</h2>
            <p className="text-xl text-[#5A6A73]">
              See what's included in each plan
            </p>
          </div>

          <div className="bg-[#FDFBF7] rounded-2xl shadow-lg border border-[#E3DED5] overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-[#1C3D5A] text-white">
                  <tr>
                    <th className="px-6 py-4 text-left">Features</th>
                    <th className="px-6 py-4 text-center">Starter</th>
                    <th className="px-6 py-4 text-center">Professional</th>
                    <th className="px-6 py-4 text-center">Premium</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { feature: "Portfolio Holdings", starter: "5", professional: "Unlimited", premium: "Unlimited" },
                    { feature: "Real-time Analytics", starter: "Basic", professional: "Advanced", premium: "Advanced" },
                    { feature: "AI Insights", starter: "❌", professional: "✅", premium: "✅" },
                    { feature: "Community Access", starter: "❌", professional: "✅", premium: "✅" },
                    { feature: "Goal Tracking", starter: "❌", professional: "✅", premium: "✅" },
                    { feature: "API Access", starter: "❌", professional: "❌", premium: "✅" },
                    { feature: "Custom Integrations", starter: "❌", professional: "❌", premium: "✅" },
                    { feature: "Dedicated Support", starter: "Email", professional: "Priority", premium: "Dedicated Manager" }
                  ].map((row, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-[#FDFBF7]'}>
                      <td className="px-6 py-4 font-medium text-[#1C3D5A]">{row.feature}</td>
                      <td className="px-6 py-4 text-center text-[#5A6A73]">{row.starter}</td>
                      <td className="px-6 py-4 text-center text-[#5A6A73]">{row.professional}</td>
                      <td className="px-6 py-4 text-center text-[#5A6A73]">{row.premium}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-[#1C3D5A] mb-4">Frequently Asked Questions</h2>
            <p className="text-xl text-[#5A6A73]">
              Everything you need to know about our pricing
            </p>
          </div>

          <div className="space-y-8">
            {[
              {
                question: "Can I change plans anytime?",
                answer: "Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately, and we'll prorate any billing differences."
              },
              {
                question: "Is there a free trial?",
                answer: "Yes! All paid plans come with a 14-day free trial. No credit card required to start your trial."
              },
              {
                question: "What happens to my data if I cancel?",
                answer: "Your data is always yours. You can export all your portfolio data before canceling, and we'll keep it for 30 days in case you want to reactivate."
              },
              {
                question: "Do you offer discounts for annual billing?",
                answer: "Yes! Save 20% when you pay annually. Contact our sales team for custom enterprise pricing."
              },
              {
                question: "What payment methods do you accept?",
                answer: "We accept all major credit cards, PayPal, and bank transfers for annual plans. Enterprise customers can also pay via invoice."
              }
            ].map((faq, index) => (
              <div key={index} className="bg-[#FDFBF7] p-6 rounded-2xl border border-[#E3DED5]">
                <h3 className="text-lg font-semibold text-[#1C3D5A] mb-3">{faq.question}</h3>
                <p className="text-[#5A6A73]">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-[#1C3D5A] text-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of investors who trust Portora for their portfolio management.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/signup" 
              className="rounded-xl bg-gradient-brand text-white px-8 py-4 text-lg font-semibold hover:shadow-brand shadow-medium transition-all duration-300 flex items-center justify-center"
            >
              Start Free Trial
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            <Link 
              href="/contact" 
              className="rounded-xl border-2 border-brand-600 text-brand-600 px-8 py-4 text-lg font-semibold hover:bg-brand-600 hover:text-white transition-all duration-300 shadow-soft"
            >
              Contact Sales
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
    </>
  )
}
