"use client"

import Link from "next/link"
import { useState, ReactNode } from "react"
import Container from "@/components/ui/Container"
import { PortoraLogo } from "@/components/PortoraLogo"

const NavLink = ({ href, children }: { href: string; children: ReactNode }) => (
  <Link 
    href={href} 
    className="text-sm font-medium text-neutral-600 hover:text-brand-600 transition-colors duration-200 relative group"
  >
    {children}
    <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-brand-500 group-hover:w-full transition-all duration-300" />
  </Link>
)

export default function Navbar() {
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b border-neutral-200/80 bg-white/98 backdrop-blur-sm">
      <Container className="flex h-16 items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="group-hover:scale-105 transition-transform duration-300">
              <PortoraLogo size={32} iconOnly={true} />
            </div>
            <span className="hidden md:block text-xl font-bold bg-gradient-to-r from-neutral-900 to-neutral-700 bg-clip-text text-transparent">Portora</span>
          </Link>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden items-center gap-8 md:flex">
          <NavLink href="#features">Features</NavLink>
          <NavLink href="#how">How it works</NavLink>
          <NavLink href="#pricing">Pricing</NavLink>
          <NavLink href="#demo">Demo</NavLink>
        </nav>

        {/* Desktop Auth Buttons */}
        <div className="hidden items-center gap-3 md:flex">
          <Link 
            href="/login" 
            className="rounded-xl border border-neutral-300 px-5 py-2.5 text-sm font-semibold text-neutral-700 hover:bg-neutral-50 hover:border-neutral-400 transition-all duration-200 hover:shadow-soft pointer-events-none opacity-50 cursor-not-allowed"
            onClick={(e) => e.preventDefault()}
          >
            Sign in
          </Link>
          <Link 
            href="/signup" 
            className="rounded-xl bg-gradient-brand px-5 py-2.5 text-sm font-semibold text-white hover:shadow-brand shadow-soft transition-all duration-200 hover:scale-105 pointer-events-none opacity-50 cursor-not-allowed"
            onClick={(e) => e.preventDefault()}
          >
            Sign up
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button 
          aria-label="Toggle menu" 
          onClick={() => setOpen(!open)} 
          className="inline-flex items-center justify-center p-2 rounded-lg hover:bg-neutral-100 transition-colors duration-200 md:hidden"
        >
          <svg className="h-5 w-5 text-neutral-600" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth="2" 
              d={open ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} 
            />
          </svg>
        </button>
      </Container>

      {/* Mobile Menu */}
      {open && (
        <div className="border-t border-neutral-200 bg-white md:hidden">
          <Container className="flex flex-col gap-1 py-4">
            <NavLink href="#features">Features</NavLink>
            <NavLink href="#how">How it works</NavLink>
            <NavLink href="#pricing">Pricing</NavLink>
            <NavLink href="#demo">Demo</NavLink>
            <div className="mt-4 flex items-center gap-3 pt-4 border-t border-neutral-200/60">
              <Link 
                href="/login" 
                className="flex-1 rounded-xl border border-neutral-300 px-4 py-2.5 text-center text-sm font-semibold text-neutral-700 hover:bg-neutral-50 transition-colors duration-200 pointer-events-none opacity-50 cursor-not-allowed"
                onClick={(e) => e.preventDefault()}
              >
                Sign in
              </Link>
              <Link 
                href="/signup" 
                className="flex-1 rounded-xl bg-gradient-brand px-4 py-2.5 text-center text-sm font-semibold text-white hover:shadow-brand transition-all duration-200 pointer-events-none opacity-50 cursor-not-allowed"
                onClick={(e) => e.preventDefault()}
              >
                Sign up
              </Link>
            </div>
          </Container>
        </div>
      )}
    </header>
  )
}
