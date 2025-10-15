'use client'

import Link from 'next/link'
import { 
  TrendingUp, 
  Shield, 
  Users, 
  Target, 
  BarChart3,
  CheckCircle,
  ArrowRight,
  Globe,
  Smartphone,
  Lock
} from 'lucide-react'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FDFBF7] to-[#EDE9E3]">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-[#E3DED5] sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link href="/" className="text-2xl font-bold text-[#1C3D5A]">Portora</Link>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-8">
                <Link href="/#features" className="text-[#5A6A73] hover:text-[#1C3D5A] transition-colors">Features</Link>
                <Link href="/#pricing" className="text-[#5A6A73] hover:text-[#1C3D5A] transition-colors">Pricing</Link>
                <Link href="/about" className="text-[#1C3D5A] font-semibold">About</Link>
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
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-[#1C3D5A] mb-6">
            About <span className="text-[#C9A66B]">Portora</span>
          </h1>
          <p className="text-xl text-[#5A6A73] mb-8">
            We're revolutionizing wealth management with sophisticated tools, 
            AI-powered insights, and a premium experience for serious investors.
          </p>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-white/50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-[#1C3D5A] mb-6">Our Mission</h2>
              <p className="text-lg text-[#5A6A73] mb-6">
                To democratize sophisticated wealth management tools and make them accessible 
                to every serious investor, regardless of portfolio size.
              </p>
              <p className="text-lg text-[#5A6A73] mb-8">
                We believe that everyone deserves access to the same level of portfolio 
                management sophistication that was once reserved for institutional investors.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link 
                  href="/auth" 
                  className="bg-[#C9A66B] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#1C3D5A] transition-colors flex items-center justify-center"
                >
                  Join Our Mission
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Link>
                <Link 
                  href="/contact" 
                  className="border-2 border-[#C9A66B] text-[#C9A66B] px-6 py-3 rounded-lg font-semibold hover:bg-[#C9A66B] hover:text-white transition-colors"
                >
                  Learn More
                </Link>
              </div>
            </div>
            <div className="bg-[#FDFBF7] p-8 rounded-2xl shadow-lg border border-[#E3DED5]">
              <div className="grid grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-[#C9A66B] mb-2">10K+</div>
                  <div className="text-sm text-[#5A6A73]">Active Users</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-[#C9A66B] mb-2">$2.5B+</div>
                  <div className="text-sm text-[#5A6A73]">Assets Managed</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-[#C9A66B] mb-2">99.9%</div>
                  <div className="text-sm text-[#5A6A73]">Uptime</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-[#C9A66B] mb-2">4.9★</div>
                  <div className="text-sm text-[#5A6A73]">User Rating</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-[#1C3D5A] mb-4">Our Values</h2>
            <p className="text-xl text-[#5A6A73] max-w-2xl mx-auto">
              The principles that guide everything we do
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: <Shield className="w-8 h-8" />,
                title: "Security First",
                description: "Your financial data is protected with bank-grade security and end-to-end encryption."
              },
              {
                icon: <TrendingUp className="w-8 h-8" />,
                title: "Performance Focused",
                description: "We optimize for real results, not just pretty charts. Every feature drives portfolio performance."
              },
              {
                icon: <Users className="w-8 h-8" />,
                title: "Community Driven",
                description: "We believe in the power of community and shared knowledge among sophisticated investors."
              },
              {
                icon: <Target className="w-8 h-8" />,
                title: "Goal Oriented",
                description: "Every tool is designed to help you achieve your specific financial goals and objectives."
              },
              {
                icon: <BarChart3 className="w-8 h-8" />,
                title: "Data Driven",
                description: "Our insights are powered by real market data and sophisticated analytics, not guesswork."
              },
              {
                icon: <Globe className="w-8 h-8" />,
                title: "Accessible",
                description: "Sophisticated tools should be accessible to every serious investor, regardless of portfolio size."
              }
            ].map((value, index) => (
              <div key={index} className="bg-[#FDFBF7] p-8 rounded-2xl shadow-lg border border-[#E3DED5] hover:shadow-xl transition-shadow">
                <div className="text-[#C9A66B] mb-4">{value.icon}</div>
                <h3 className="text-xl font-semibold text-[#1C3D5A] mb-3">{value.title}</h3>
                <p className="text-[#5A6A73]">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 bg-[#1C3D5A] text-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Meet Our Team</h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              A diverse group of financial experts, engineers, and visionaries
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                name: "Alex Chen",
                role: "Founder & CEO",
                description: "Former Goldman Sachs VP with 15+ years in quantitative finance and portfolio management."
              },
              {
                name: "Sarah Johnson",
                role: "CTO",
                description: "Ex-Google engineer specializing in machine learning and financial data systems."
              },
              {
                name: "Michael Rodriguez",
                role: "Head of Product",
                description: "Former BlackRock portfolio manager with deep expertise in institutional investing."
              }
            ].map((member, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20">
                <h3 className="text-xl font-semibold text-[#C9A66B] mb-2">{member.name}</h3>
                <p className="text-lg text-gray-300 mb-3">{member.role}</p>
                <p className="text-gray-300">{member.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-[#1C3D5A] mb-6">
            Ready to Join Us?
          </h2>
          <p className="text-xl text-[#5A6A73] mb-8">
            Become part of the sophisticated investor community that's transforming wealth management.
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
              Contact Us
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
                <li><Link href="/#features" className="hover:text-[#C9A66B] transition-colors">Features</Link></li>
                <li><Link href="/#pricing" className="hover:text-[#C9A66B] transition-colors">Pricing</Link></li>
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
