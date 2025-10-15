'use client'

import { useState } from 'react'
import Link from 'next/link'
import { 
  Mail, 
  Phone, 
  MapPin, 
  Clock,
  Send,
  MessageCircle,
  Headphones,
  FileText
} from 'lucide-react'

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    setIsSubmitted(true)
    setIsSubmitting(false)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

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
                <Link href="/about" className="text-[#5A6A73] hover:text-[#1C3D5A] transition-colors">About</Link>
                <Link href="/contact" className="text-[#1C3D5A] font-semibold">Contact</Link>
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
            Get in <span className="text-[#C9A66B]">Touch</span>
          </h1>
          <p className="text-xl text-[#5A6A73] mb-8">
            We'd love to hear from you. Send us a message and we'll respond as soon as possible.
          </p>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Contact Form */}
            <div className="bg-[#FDFBF7] p-8 rounded-2xl shadow-lg border border-[#E3DED5]">
              <h2 className="text-3xl font-bold text-[#1C3D5A] mb-6">Send us a Message</h2>
              
              {isSubmitted ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Send className="w-8 h-8 text-green-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-[#1C3D5A] mb-2">Message Sent!</h3>
                  <p className="text-[#5A6A73] mb-6">Thank you for your message. We'll get back to you within 24 hours.</p>
                  <button 
                    onClick={() => setIsSubmitted(false)}
                    className="text-[#C9A66B] hover:text-[#1C3D5A] transition-colors"
                  >
                    Send Another Message
                  </button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                        Name *
                      </label>
                      <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-3 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                        placeholder="Your full name"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                        Email *
                      </label>
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-3 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                        placeholder="your@email.com"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                      Subject *
                    </label>
                    <select
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-3 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                    >
                      <option value="">Select a subject</option>
                      <option value="general">General Inquiry</option>
                      <option value="support">Technical Support</option>
                      <option value="billing">Billing Question</option>
                      <option value="feature">Feature Request</option>
                      <option value="partnership">Partnership</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-[#1C3D5A] mb-2">
                      Message *
                    </label>
                    <textarea
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      required
                      rows={6}
                      className="w-full px-4 py-3 border border-[#E3DED5] rounded-lg focus:ring-2 focus:ring-[#C9A66B] focus:border-transparent"
                      placeholder="Tell us how we can help you..."
                    />
                  </div>
                  
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full bg-[#C9A66B] text-white px-6 py-4 rounded-lg font-semibold hover:bg-[#1C3D5A] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {isSubmitting ? 'Sending...' : 'Send Message'}
                    <Send className="ml-2 w-4 h-4" />
                  </button>
                </form>
              )}
            </div>

            {/* Contact Info */}
            <div className="space-y-8">
              <div>
                <h2 className="text-3xl font-bold text-[#1C3D5A] mb-6">Contact Information</h2>
                <p className="text-lg text-[#5A6A73] mb-8">
                  We're here to help! Reach out to us through any of these channels.
                </p>
              </div>

              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="bg-[#C9A66B] p-3 rounded-lg">
                    <Mail className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#1C3D5A] mb-1">Email</h3>
                    <p className="text-[#5A6A73]">support@portora.com</p>
                    <p className="text-sm text-[#5A6A73]">We'll respond within 24 hours</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="bg-[#C9A66B] p-3 rounded-lg">
                    <Phone className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#1C3D5A] mb-1">Phone</h3>
                    <p className="text-[#5A6A73]">+1 (555) 123-4567</p>
                    <p className="text-sm text-[#5A6A73]">Mon-Fri 9AM-6PM EST</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="bg-[#C9A66B] p-3 rounded-lg">
                    <MapPin className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#1C3D5A] mb-1">Office</h3>
                    <p className="text-[#5A6A73]">123 Financial District</p>
                    <p className="text-[#5A6A73]">New York, NY 10004</p>
                  </div>
                </div>

                <div className="flex items-start space-x-4">
                  <div className="bg-[#C9A66B] p-3 rounded-lg">
                    <Clock className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#1C3D5A] mb-1">Business Hours</h3>
                    <p className="text-[#5A6A73]">Monday - Friday: 9:00 AM - 6:00 PM</p>
                    <p className="text-[#5A6A73]">Saturday: 10:00 AM - 4:00 PM</p>
                    <p className="text-[#5A6A73]">Sunday: Closed</p>
                  </div>
                </div>
              </div>

              {/* Quick Links */}
              <div className="bg-[#FDFBF7] p-6 rounded-2xl border border-[#E3DED5]">
                <h3 className="font-semibold text-[#1C3D5A] mb-4">Quick Links</h3>
                <div className="space-y-3">
                  <Link href="#" className="flex items-center text-[#5A6A73] hover:text-[#C9A66B] transition-colors">
                    <MessageCircle className="w-4 h-4 mr-2" />
                    Live Chat Support
                  </Link>
                  <Link href="#" className="flex items-center text-[#5A6A73] hover:text-[#C9A66B] transition-colors">
                    <Headphones className="w-4 h-4 mr-2" />
                    Help Center
                  </Link>
                  <Link href="#" className="flex items-center text-[#5A6A73] hover:text-[#C9A66B] transition-colors">
                    <FileText className="w-4 h-4 mr-2" />
                    Documentation
                  </Link>
                </div>
              </div>
            </div>
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
