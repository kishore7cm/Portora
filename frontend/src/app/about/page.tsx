'use client'

import Link from 'next/link'
import Navbar from '@/components/site/Navbar'
import Footer from '@/components/site/Footer'
import Container from '@/components/ui/Container'
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
    <div className="min-h-screen bg-gradient-soft">
      <Navbar />

      {/* Hero Section */}
      <section className="py-20 md:py-32">
        <Container>
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-neutral-900 mb-6">
              About <span className="bg-gradient-to-r from-brand-600 via-brand-500 to-brand-400 bg-clip-text text-transparent">Portora</span>
            </h1>
            <p className="text-xl text-neutral-600 mb-8">
              We're revolutionizing wealth management with sophisticated tools, 
              AI-powered insights, and a premium experience for serious investors.
            </p>
          </div>
        </Container>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-white">
        <Container>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-neutral-900 mb-6">Our Mission</h2>
              <p className="text-lg text-neutral-600 mb-6">
                To democratize sophisticated wealth management tools and make them accessible 
                to every serious investor, regardless of portfolio size.
              </p>
              <p className="text-lg text-neutral-600 mb-8">
                We believe that everyone deserves access to the same level of portfolio 
                management sophistication that was once reserved for institutional investors.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link 
                  href="/signup" 
                  className="rounded-xl bg-gradient-brand text-white px-6 py-3 font-semibold hover:shadow-brand shadow-medium transition-all duration-300 flex items-center justify-center"
                >
                  Join Our Mission
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Link>
                <Link 
                  href="/contact" 
                  className="rounded-xl border-2 border-brand-600 text-brand-600 px-6 py-3 font-semibold hover:bg-brand-600 hover:text-white transition-all duration-300 shadow-soft"
                >
                  Learn More
                </Link>
              </div>
            </div>
            <div className="bg-neutral-50 p-8 rounded-2xl shadow-medium border border-neutral-200">
              <div className="grid grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-brand-600 mb-2">10K+</div>
                  <div className="text-sm text-neutral-600">Active Users</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-brand-600 mb-2">$2.5B+</div>
                  <div className="text-sm text-neutral-600">Assets Managed</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-brand-600 mb-2">99.9%</div>
                  <div className="text-sm text-neutral-600">Uptime</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-brand-600 mb-2">4.9★</div>
                  <div className="text-sm text-neutral-600">User Rating</div>
                </div>
              </div>
            </div>
          </div>
        </Container>
      </section>

      {/* Values Section */}
      <section className="py-20 bg-neutral-50">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-neutral-900 mb-4">Our Values</h2>
            <p className="text-xl text-neutral-600 max-w-2xl mx-auto">
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
              <div key={index} className="bg-white p-8 rounded-2xl shadow-soft border border-neutral-200 hover:shadow-medium hover:border-brand-200 transition-all duration-300 group">
                <div className="text-brand-600 mb-4 group-hover:scale-110 transition-transform duration-300">{value.icon}</div>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3 group-hover:text-brand-600 transition-colors">{value.title}</h3>
                <p className="text-neutral-600">{value.description}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Team Section */}
      <section className="py-20 bg-gradient-brand text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),transparent_70%)]" />
        <Container className="relative">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Meet Our Team</h2>
            <p className="text-xl text-white/90 max-w-2xl mx-auto">
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
              <div key={index} className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20 hover:bg-white/15 transition-all duration-300">
                <h3 className="text-xl font-semibold text-white mb-2">{member.name}</h3>
                <p className="text-lg text-white/80 mb-3">{member.role}</p>
                <p className="text-white/70">{member.description}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-white">
        <Container>
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold text-neutral-900 mb-6">
              Ready to Join Us?
            </h2>
            <p className="text-xl text-neutral-600 mb-8">
              Become part of the sophisticated investor community that's transforming wealth management.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                href="/signup" 
                className="rounded-xl bg-gradient-brand text-white px-8 py-4 text-lg font-semibold hover:shadow-brand shadow-medium transition-all duration-300 flex items-center justify-center"
              >
                Get Started Free
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              <Link 
                href="/contact" 
                className="rounded-xl border-2 border-brand-600 text-brand-600 px-8 py-4 text-lg font-semibold hover:bg-brand-600 hover:text-white transition-all duration-300 shadow-soft"
              >
                Contact Us
              </Link>
            </div>
          </div>
        </Container>
      </section>

      <Footer />
    </div>
  )
}
