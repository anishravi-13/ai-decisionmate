import { Link, useLocation } from 'react-router-dom'
import { Brain, History, LayoutDashboard, MessageSquare, HelpCircle } from 'lucide-react'
import { useState } from 'react'

const navLinks = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/guided', label: 'Guided Decisions', icon: HelpCircle },
  { path: '/ask', label: 'Ask AI', icon: MessageSquare },
  { path: '/history', label: 'History', icon: History },
]

export default function Navbar() {
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <nav className="sticky top-0 z-50 bg-charcoal-950/90 backdrop-blur-md border-b border-charcoal-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-amber-500 flex items-center justify-center shadow-glow-amber group-hover:bg-amber-400 transition-colors">
              <Brain className="w-5 h-5 text-charcoal-950" />
            </div>
            <div>
              <span className="font-heading font-bold text-lg text-charcoal-100 leading-none block">AI DecisionMate</span>
              <span className="text-xs text-amber-400 leading-none">Explainable AI</span>
            </div>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map(({ path, label, icon: Icon }) => {
              const active = location.pathname === path
              return (
                <Link
                  key={path}
                  to={path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    active
                      ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                      : 'text-charcoal-400 hover:text-charcoal-100 hover:bg-charcoal-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </Link>
              )
            })}
          </div>

          {/* Mobile menu toggle */}
          <button
            className="md:hidden p-2 rounded-lg text-charcoal-400 hover:text-charcoal-100 hover:bg-charcoal-800 transition-colors"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
          >
            <div className="w-5 h-5 flex flex-col justify-center gap-1">
              <span className={`block h-0.5 bg-current transition-all ${menuOpen ? 'rotate-45 translate-y-1.5' : ''}`} />
              <span className={`block h-0.5 bg-current transition-all ${menuOpen ? 'opacity-0' : ''}`} />
              <span className={`block h-0.5 bg-current transition-all ${menuOpen ? '-rotate-45 -translate-y-1.5' : ''}`} />
            </div>
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden pb-4 flex flex-col gap-1 border-t border-charcoal-800 mt-2 pt-2">
            {navLinks.map(({ path, label, icon: Icon }) => {
              const active = location.pathname === path
              return (
                <Link
                  key={path}
                  to={path}
                  onClick={() => setMenuOpen(false)}
                  className={`flex items-center gap-2 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                    active
                      ? 'bg-amber-500/15 text-amber-400'
                      : 'text-charcoal-400 hover:text-charcoal-100 hover:bg-charcoal-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </nav>
  )
}
