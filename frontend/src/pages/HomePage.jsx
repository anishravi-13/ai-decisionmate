import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import {
  Brain, Zap, TrendingUp, ShieldCheck, Clock, ArrowRight,
  Sparkles, ChevronRight, History, HelpCircle
} from 'lucide-react'
import { CATEGORIES } from '../data/categoryQuestions'
import { getHistory } from '../api'

function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-charcoal-950 via-navy-950/20 to-charcoal-950 pointer-events-none" />
      <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 rounded-full px-4 py-1.5 mb-6">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span className="text-amber-400 text-sm font-medium">Explainable AI Decision Support</span>
          </div>

          <h1 className="font-heading text-4xl sm:text-5xl lg:text-6xl font-bold text-charcoal-50 leading-tight mb-4">
            Understand your options.
            <br />
            <span className="text-gradient">Decide with confidence.</span>
          </h1>

          <p className="text-charcoal-400 text-lg sm:text-xl leading-relaxed mb-8 max-w-2xl">
            AI DecisionMate analyzes your requirements, explains every recommendation,
            shows confidence levels, and helps you understand the real-world impact
            of your decisions — from laptop selection to company bulk purchases.
          </p>

          <div className="flex flex-col sm:flex-row gap-3">
            <Link to="/guided" className="btn-primary flex items-center justify-center gap-2 text-base">
              <HelpCircle className="w-5 h-5" />
              Guided Decision
            </Link>
            <Link to="/ask" className="btn-secondary flex items-center justify-center gap-2 text-base">
              <Brain className="w-5 h-5" />
              Ask AI
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}

function FeatureCard({ icon: Icon, title, description, color }) {
  return (
    <div className="card p-5 flex gap-4">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <h3 className="font-heading font-semibold text-charcoal-100 mb-1">{title}</h3>
        <p className="text-sm text-charcoal-400 leading-relaxed">{description}</p>
      </div>
    </div>
  )
}

function CategoryGrid() {
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="font-heading text-2xl font-bold text-charcoal-100">Quick Decision Categories</h2>
          <p className="text-charcoal-400 text-sm mt-1">Select a category to start a guided decision</p>
        </div>
        <Link to="/guided" className="text-amber-400 text-sm font-medium flex items-center gap-1 hover:text-amber-300 transition-colors">
          View all <ChevronRight className="w-4 h-4" />
        </Link>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 xl:grid-cols-7 gap-3">
        {CATEGORIES.slice(0, 14).map(cat => (
          <Link
            key={cat.id}
            to={`/guided?category=${cat.id}`}
            className="card card-hover p-4 flex flex-col items-center gap-2 text-center group cursor-pointer"
          >
            <span className="text-2xl" role="img" aria-label={cat.label}>{cat.emoji}</span>
            <span className="text-xs font-medium text-charcoal-300 group-hover:text-charcoal-100 transition-colors leading-tight">
              {cat.label}
            </span>
          </Link>
        ))}
      </div>
    </section>
  )
}

function HowItWorks() {
  const steps = [
    { num: '01', title: 'Describe your decision', desc: 'Use guided questions or free text to describe what you need.' },
    { num: '02', title: 'AI analyzes requirements', desc: 'The engine scores your requirements and generates weighted recommendations.' },
    { num: '03', title: 'See the explanation', desc: 'Understand exactly why each option was recommended with factor scores.' },
    { num: '04', title: 'Explore impact & alternatives', desc: 'See real-world impact, alternatives, and what-if scenarios.' },
  ]
  return (
    <section className="bg-charcoal-900/50 border-y border-charcoal-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h2 className="font-heading text-2xl font-bold text-charcoal-100 mb-8 text-center">How It Works</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((s, i) => (
            <div key={s.num} className="relative">
              {i < steps.length - 1 && (
                <div className="hidden lg:block absolute top-6 left-full w-full h-px bg-charcoal-700 z-0" />
              )}
              <div className="relative z-10">
                <div className="w-12 h-12 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center mb-3">
                  <span className="font-heading font-bold text-amber-400 text-sm">{s.num}</span>
                </div>
                <h3 className="font-heading font-semibold text-charcoal-100 mb-1">{s.title}</h3>
                <p className="text-sm text-charcoal-400">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function RecentDecisions({ history }) {
  if (!history || history.length === 0) return null
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center justify-between mb-5">
        <h2 className="font-heading text-xl font-bold text-charcoal-100 flex items-center gap-2">
          <History className="w-5 h-5 text-amber-400" />
          Recent Decisions
        </h2>
        <Link to="/history" className="text-amber-400 text-sm hover:text-amber-300 flex items-center gap-1 transition-colors">
          View all <ChevronRight className="w-4 h-4" />
        </Link>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {history.slice(0, 3).map(item => (
          <Link
            key={item.id}
            to={`/history/${item.id}`}
            className="card card-hover p-4 block"
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <span className="badge bg-amber-500/10 border border-amber-500/20 text-amber-400 capitalize">
                {item.category.replace(/_/g, ' ')}
              </span>
              <span className={`text-xs font-semibold ${
                item.confidence_band === 'HIGH' ? 'text-emerald-400' :
                item.confidence_band === 'MEDIUM' ? 'text-amber-400' : 'text-red-400'
              }`}>
                {Math.round(item.confidence || 0)}%
              </span>
            </div>
            <p className="text-sm text-charcoal-200 font-medium line-clamp-2 mb-2">
              {item.recommendation || item.user_query || 'Decision'}
            </p>
            <p className="text-xs text-charcoal-500">
              {new Date(item.timestamp).toLocaleDateString('en-IN', {
                day: 'numeric', month: 'short', year: 'numeric'
              })}
            </p>
          </Link>
        ))}
      </div>
    </section>
  )
}

export default function HomePage() {
  const [history, setHistory] = useState([])

  useEffect(() => {
    getHistory().then(r => setHistory(r.data)).catch(() => {})
  }, [])

  return (
    <div>
      <HeroSection />

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <FeatureCard icon={Brain} title="Explainable AI" description="See exactly why each option was recommended with factor contribution scores." color="bg-amber-500/15 text-amber-400" />
          <FeatureCard icon={ShieldCheck} title="Confidence Levels" description="Every recommendation includes a confidence score based on requirement completeness." color="bg-emerald-500/15 text-emerald-400" />
          <FeatureCard icon={TrendingUp} title="Impact Analysis" description="Understand immediate effects, long-term considerations, and trade-offs." color="bg-blue-500/15 text-blue-400" />
          <FeatureCard icon={Zap} title="What-If Analysis" description="Adjust budget, performance, and quantity to see how recommendations change." color="bg-purple-500/15 text-purple-400" />
        </div>
      </section>

      <CategoryGrid />
      <HowItWorks />
      <RecentDecisions history={history} />

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="card p-8 bg-gradient-to-r from-charcoal-900 to-navy-950/30 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div>
            <h2 className="font-heading text-2xl font-bold text-charcoal-100 mb-2">Ready to make a better decision?</h2>
            <p className="text-charcoal-400">Describe your situation and get an explainable, confidence-backed recommendation in seconds.</p>
          </div>
          <div className="flex gap-3 flex-shrink-0">
            <Link to="/ask" className="btn-primary flex items-center gap-2">
              Ask AI <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
