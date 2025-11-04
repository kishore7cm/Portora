import Container from "@/components/ui/Container"
import Link from "next/link"
import { PortoraLogo } from "@/components/PortoraLogo"

export default function Footer() {
  return (
    <footer className="border-t border-neutral-200 bg-white">
      <Container className="flex flex-col items-center justify-between gap-4 py-8 md:flex-row">
        <div className="flex items-center gap-3 text-sm text-neutral-600">
          <PortoraLogo size={24} iconOnly={true} />
          <span>© {new Date().getFullYear()} Portora</span>
        </div>
        <nav className="flex items-center gap-6 text-sm text-neutral-600">
          <Link href="/about" className="hover:text-brand-600 transition-colors duration-200">
            About
          </Link>
          <Link href="/privacy" className="hover:text-brand-600 transition-colors duration-200">
            Privacy
          </Link>
          <Link href="/terms" className="hover:text-brand-600 transition-colors duration-200">
            Terms
          </Link>
          <Link href="/contact" className="hover:text-brand-600 transition-colors duration-200">
            Contact
          </Link>
        </nav>
      </Container>
    </footer>
  )
}
