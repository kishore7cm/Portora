import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: "Portora — Smarter Portfolio Insights",
  description: "Track, analyze, and optimize your investments with clean dashboards and smart insights.",
  openGraph: {
    title: "Portora — Smarter Portfolio Insights",
    description: "Track, analyze, and optimize your investments.",
    url: "https://portora.ai",
    siteName: "Portora",
    type: "website"
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased bg-white text-slate-900`}>
        {children}
      </body>
    </html>
  )
}