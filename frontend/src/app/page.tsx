import Navbar from "@/components/site/Navbar"
import Footer from "@/components/site/Footer"
import PricingSection from "@/components/site/PricingSection"
import Container from "@/components/ui/Container"
import Link from "next/link"

export default function Page() {
  return (
    <>
      <Navbar />
      
      {/* Hero Section */}
      <section className="relative bg-gradient-hero overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(14,165,233,0.03),transparent_50%)]" />
        <Container className="relative py-20 md:py-32">
          <div className="mx-auto max-w-4xl text-center">
            <h1 className="text-4xl font-bold tracking-tight text-neutral-900 md:text-6xl lg:text-7xl">
              Smarter portfolio insights —
              <span className="bg-gradient-to-r from-brand-600 via-brand-500 to-brand-400 bg-clip-text text-transparent"> without the noise</span>
            </h1>
            <p className="mt-6 text-lg leading-8 text-neutral-600 md:text-xl max-w-2xl mx-auto">
              Connect accounts, visualize allocation, and get actionable signals to keep your investments on track.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row sm:gap-6">
              <Link 
                href="/signup" 
                className="w-full rounded-xl bg-gradient-brand px-8 py-4 text-center font-semibold text-white hover:shadow-brand shadow-medium hover:scale-105 transition-all duration-300 sm:w-auto pointer-events-none opacity-50 cursor-not-allowed"
                onClick={(e) => e.preventDefault()}
              >
                Get started
              </Link>
              <a 
                href="#demo" 
                className="w-full rounded-xl border-2 border-neutral-300 px-8 py-4 text-center font-semibold text-neutral-800 hover:bg-neutral-50 hover:border-brand-400 hover:text-brand-600 transition-all duration-300 shadow-soft hover:shadow-medium sm:w-auto pointer-events-none opacity-50 cursor-not-allowed"
                onClick={(e) => e.preventDefault()}
              >
                View demo
              </a>
            </div>
          </div>
          
          {/* Trust Row */}
          <div className="mx-auto mt-16 grid max-w-5xl grid-cols-2 gap-8 opacity-50 sm:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-12 rounded-lg bg-gradient-to-r from-neutral-200 via-neutral-100 to-neutral-200 animate-pulse" style={{ animationDelay: `${i * 0.2}s` }} />
            ))}
          </div>
        </Container>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 md:py-24">
        <Container>
          <div className="mx-auto max-w-3xl text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 md:text-4xl lg:text-5xl">
              Features that matter
            </h2>
            <p className="mt-4 text-lg text-slate-600 md:text-xl">
              Everything you need to see the big picture and act with confidence.
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-2 lg:gap-12">
            {[
              { 
                title: "Portfolio Summary", 
                body: "See total value, drift, sectors, and concentration at a glance.",
                icon: "📊"
              },
              { 
                title: "Smart Insights", 
                body: "Signals on allocation, momentum, and unusual moves.",
                icon: "🧠"
              },
              { 
                title: "Secure Sync", 
                body: "Bring data via CSV now; Plaid integration coming soon.",
                icon: "🔒"
              },
              { 
                title: "Alerts & Nudges", 
                body: "Get reminders when allocations drift or cash piles up.",
                icon: "🔔"
              }
            ].map((feature) => (
              <div 
                key={feature.title} 
                className="group rounded-2xl border border-neutral-200 bg-white p-8 shadow-soft hover:shadow-medium transition-all duration-300 hover:-translate-y-1 hover:border-brand-200"
              >
                <div className="mb-4 text-3xl group-hover:scale-110 transition-transform duration-300">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3 group-hover:text-brand-600 transition-colors">{feature.title}</h3>
                <p className="text-neutral-600 leading-relaxed">{feature.body}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* How it works Section */}
      <section id="how" className="bg-slate-50 py-16 md:py-24">
        <Container>
          <h2 className="text-center text-3xl font-bold tracking-tight text-slate-900 md:text-4xl lg:text-5xl mb-16">
            How it works
          </h2>
          <div className="grid gap-8 md:grid-cols-3">
            {[
              { 
                step: "1", 
                title: "Create your account", 
                body: "Sign up in minutes and set your goals.",
                icon: "👤"
              },
              { 
                step: "2", 
                title: "Add your data", 
                body: "Upload a CSV of holdings (or connect a broker soon).",
                icon: "📁"
              },
              { 
                step: "3", 
                title: "Act on insights", 
                body: "Get allocation and timing nudges you can trust.",
                icon: "⚡"
              }
            ].map((step) => (
              <div key={step.step} className="relative rounded-2xl border border-neutral-200 bg-white p-8 text-center shadow-soft hover:shadow-medium transition-all duration-300 hover:border-brand-200 group">
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-brand-100 to-brand-50 font-bold text-brand-700 text-sm shadow-soft group-hover:scale-110 transition-transform duration-300">
                    {step.step}
                  </div>
                </div>
                <div className="mt-4 text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">{step.icon}</div>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3 group-hover:text-brand-600 transition-colors">{step.title}</h3>
                <p className="text-neutral-600 leading-relaxed">{step.body}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      <PricingSection />

      {/* Demo Section */}
      <section id="demo" className="bg-slate-50 py-16 md:py-24">
        <Container>
          <div className="mx-auto max-w-4xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 md:text-4xl lg:text-5xl mb-8">
              See it in action
            </h2>
            <p className="text-lg text-slate-600 md:text-xl mb-12">
              Watch how Portora transforms your portfolio data into actionable insights.
            </p>
            <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-lg">
              <div className="aspect-video rounded-xl bg-slate-100 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl mb-4">🎬</div>
                  <div className="text-slate-600 font-medium">Demo video coming soon</div>
                </div>
              </div>
            </div>
          </div>
        </Container>
      </section>

      {/* CTA Section */}
      <section className="relative bg-gradient-brand py-16 md:py-20 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_50%,rgba(255,255,255,0.1),transparent_50%)]" />
        <Container className="relative text-center text-white">
          <h3 className="text-3xl font-bold md:text-4xl lg:text-5xl">
            Ready to get clarity on your portfolio?
          </h3>
          <p className="mt-4 text-lg text-white/90 md:text-xl max-w-2xl mx-auto">
            Sign up and see your portfolio summary in minutes.
          </p>
          <Link 
            href="/signup" 
            className="mt-8 inline-block rounded-xl bg-white px-8 py-4 font-semibold text-brand-600 hover:bg-neutral-50 shadow-strong hover:shadow-brand hover:scale-105 transition-all duration-300 pointer-events-none opacity-50 cursor-not-allowed"
            onClick={(e) => e.preventDefault()}
          >
            Get started
          </Link>
        </Container>
      </section>

      <Footer />
    </>
  )
}