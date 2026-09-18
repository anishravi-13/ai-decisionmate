import { useLocation, useNavigate, Link } from 'react-router-dom'
import { useState } from 'react'
import {
  CheckCircle, TrendingUp, AlertTriangle, Layers, MapPin,
  Package, SlidersHorizontal, ArrowLeft, GitBranch, ChevronDown, ChevronUp, Info
} from 'lucide-react'
import ConfidenceRing from '../components/ConfidenceRing'
import FactorChart from '../components/FactorChart'
import ProductCard from '../components/ProductCard'
import WhatIfPanel from '../components/WhatIfPanel'
import { searchNearby, getCounterfactual } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'

function SectionCard({ title, icon: Icon, children, iconColor = 'text-amber-400', defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="card overflow-hidden">
      <button
        className="w-full flex items-center justify-between p-5 hover:bg-charcoal-800/50 transition-colors"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
      >
        <div className="flex items-center gap-3">
          <Icon className={`w-5 h-5 ${iconColor}`} />
          <h2 className="font-heading font-semibold text-charcoal-100">{title}</h2>
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-charcoal-500" /> : <ChevronDown className="w-4 h-4 text-charcoal-500" />}
      </button>
      {open && <div className="px-5 pb-5">{children}</div>}
    </div>
  )
}

function ImpactSection({ impact }) {
  if (!impact) return null
  const sections = [
    { key: 'immediate', label: 'Immediate Impact', icon: '⚡', color: 'text-amber-400' },
    { key: 'cost_impact', label: 'Cost Impact', icon: '💰', color: 'text-emerald-400' },
    { key: 'long_term', label: 'Long-term Considerations', icon: '🔮', color: 'text-blue-400' },
    { key: 'trade_offs', label: 'Trade-offs', icon: '⚖️', color: 'text-purple-400' },
    { key: 'risks', label: 'Risks & Limitations', icon: '⚠️', color: 'text-red-400' },
    { key: 'maintenance', label: 'Maintenance', icon: '🔧', color: 'text-charcoal-400' },
  ]
  return (
    <div className="grid sm:grid-cols-2 gap-4">
      {sections.map(s => {
        const items = impact[s.key] || []
        if (items.length === 0) return null
        return (
          <div key={s.key} className="bg-charcoal-800/50 rounded-xl p-4 border border-charcoal-700">
            <div className="flex items-center gap-2 mb-3">
              <span>{s.icon}</span>
              <h3 className={`font-medium text-sm ${s.color}`}>{s.label}</h3>
            </div>
            <ul className="space-y-1.5">
              {items.map((item, i) => (
                <li key={i} className="text-xs text-charcoal-300 flex gap-2">
                  <span className="text-charcoal-600 flex-shrink-0">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )
      })}
    </div>
  )
}

function AlternativesSection({ alternatives }) {
  if (!alternatives || alternatives.length === 0) return null
  const labels = ['Recommended', 'Alternative A', 'Alternative B']
  const colors = ['border-amber-500/40 bg-amber-500/5', 'border-charcoal-700', 'border-charcoal-700']

  return (
    <div className="space-y-3">
      {alternatives.map((alt, i) => (
        <div key={i} className={`rounded-xl border p-4 ${colors[i] || 'border-charcoal-700'}`}>
          <div className="flex items-start justify-between gap-3 mb-2">
            <div>
              <span className={`text-xs font-semibold uppercase tracking-wide ${i === 0 ? 'text-amber-400' : 'text-charcoal-500'}`}>
                {labels[i] || `Option ${i + 1}`}
              </span>
              <p className="text-charcoal-100 font-medium text-sm mt-0.5">{alt.name}</p>
              {alt.estimated_price && (
                <p className="text-xs text-charcoal-500 mt-0.5">{alt.estimated_price}</p>
              )}
            </div>
            <span className={`text-sm font-bold ${
              alt.score >= 80 ? 'text-emerald-400' :
              alt.score >= 60 ? 'text-amber-400' : 'text-charcoal-400'
            }`}>{Math.round(alt.score)}%</span>
          </div>
          <div className="grid sm:grid-cols-2 gap-2 mt-2">
            <div className="text-xs">
              <span className="text-emerald-400">✓ </span>
              <span className="text-charcoal-300">{alt.key_advantage}</span>
            </div>
            <div className="text-xs">
              <span className="text-amber-400">⚖ </span>
              <span className="text-charcoal-400">{alt.key_tradeoff}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

function NearbySection({ category }) {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [location, setLocation] = useState('')
  const [searched, setSearched] = useState(false)

  const handleSearch = async () => {
    setLoading(true)
    try {
      const resp = await searchNearby({ category, location: location || undefined, radius_km: 10 })
      setData(resp.data)
    } catch (e) {
      setData({ success: false, businesses: [], message: 'Search failed.', live_data: false })
    } finally {
      setLoading(false)
      setSearched(true)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          type="text"
          className="input-field flex-1"
          value={location}
          onChange={e => setLocation(e.target.value)}
          placeholder="Enter your city (e.g. Mumbai)"
          aria-label="Location for nearby search"
        />
        <button onClick={handleSearch} disabled={loading} className="btn-primary flex items-center gap-2 px-4 py-2.5">
          {loading ? <LoadingSpinner size="sm" /> : <MapPin className="w-4 h-4" />}
          Find Nearby
        </button>
      </div>

      {searched && data && (
        <div>
          {data.message && (
            <div className="bg-charcoal-800/50 border border-charcoal-700 rounded-xl p-4">
              <p className="text-sm text-charcoal-300">{data.message}</p>
              {!data.live_data && (
                <div className="mt-3 space-y-1">
                  <p className="text-xs text-amber-400 font-medium">Alternative options:</p>
                  <p className="text-xs text-charcoal-400">• Search Google Maps: "{category.replace(/_/g, ' ')} stores near me"</p>
                  <p className="text-xs text-charcoal-400">• Check Justdial or Sulekha for local {category.replace(/_/g, ' ')} shops</p>
                  <p className="text-xs text-charcoal-400">• Visit brand authorised dealers in your city</p>
                </div>
              )}
            </div>
          )}
          {data.businesses && data.businesses.length > 0 && (
            <div className="space-y-2">
              {data.businesses.map((b, i) => (
                <div key={i} className="card p-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-charcoal-100 text-sm">{b.name}</p>
                      {b.address && <p className="text-xs text-charcoal-400">{b.address}</p>}
                    </div>
                    {b.rating && <span className="text-xs text-amber-400">★ {b.rating}</span>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function CounterfactualSection({ category, inputData, recommendation }) {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleRun = async () => {
    setLoading(true)
    try {
      const resp = await getCounterfactual({
        category,
        current_input: inputData || {},
        current_recommendation: recommendation,
      })
      setResult(resp.data)
    } catch (e) {
      setResult({ success: false, description: 'Counterfactual analysis failed.', change_required: null })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-charcoal-400">
        Find the minimum input change that would produce a different recommendation.
        <span className="text-amber-400/70"> (Estimated what-if scenario)</span>
      </p>
      {!result && (
        <button onClick={handleRun} disabled={loading} className="btn-secondary flex items-center gap-2">
          {loading ? <LoadingSpinner size="sm" /> : <GitBranch className="w-4 h-4" />}
          Run Counterfactual Analysis
        </button>
      )}
      {result && (
        <div className="bg-charcoal-800/50 border border-charcoal-700 rounded-xl p-4">
          {result.change_required ? (
            <div>
              <p className="text-sm font-medium text-amber-400 mb-2">
                Suggested change: {result.change_required.factor?.replace(/_/g, ' ')}
              </p>
              <div className="grid grid-cols-2 gap-3 text-sm mb-3">
                <div>
                  <span className="text-charcoal-500 text-xs">Current</span>
                  <p className="text-charcoal-200">{result.change_required.current_value}</p>
                </div>
                <div>
                  <span className="text-charcoal-500 text-xs">Suggested</span>
                  <p className="text-emerald-400">{result.change_required.suggested_value}</p>
                </div>
              </div>
              <p className="text-xs text-charcoal-400">{result.description}</p>
              {result.new_recommendation && (
                <p className="text-xs text-amber-400 mt-2 font-medium">
                  New recommendation: {result.new_recommendation}
                </p>
              )}
            </div>
          ) : (
            <p className="text-sm text-charcoal-300">{result.description}</p>
          )}
          <button onClick={() => setResult(null)} className="text-xs text-charcoal-500 hover:text-charcoal-300 mt-2">Run again</button>
        </div>
      )}
    </div>
  )
}

export default function ResultPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const { result, historyId, inputData, mode, originalQuery } = location.state || {}

  if (!result) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <p className="text-charcoal-400 mb-4">No result found. Please make a decision first.</p>
        <Link to="/" className="btn-primary">Go to Dashboard</Link>
      </div>
    )
  }

  const category = result.category || 'general'
  const showNearby = result.nearby_available

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-charcoal-400 hover:text-charcoal-100 text-sm mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back
      </button>

      {/* Query */}
      {(originalQuery || inputData?.query) && (
        <div className="bg-charcoal-900 border border-charcoal-800 rounded-xl px-4 py-3 mb-6">
          <p className="text-xs text-charcoal-500 mb-1">Your query</p>
          <p className="text-sm text-charcoal-200">"{originalQuery || inputData?.query}"</p>
        </div>
      )}

      {/* MAIN RECOMMENDATION — visually dominant */}
      <div className="card p-6 mb-6 bg-gradient-to-br from-charcoal-900 to-charcoal-800/50 border-charcoal-700">
        <p className="text-xs font-semibold uppercase tracking-widest text-amber-400 mb-3 flex items-center gap-2">
          <CheckCircle className="w-4 h-4" />
          Decision Recommendation
        </p>

        <div className="flex flex-col lg:flex-row lg:items-start gap-6">
          {/* Text */}
          <div className="flex-1">
            <p className="text-xs text-charcoal-500 mb-1 capitalize">
              {category.replace(/_/g, ' ')} Decision
            </p>
            <h1 className="font-heading text-2xl sm:text-3xl font-bold text-charcoal-50 leading-snug mb-4">
              {result.recommendation}
            </h1>

            {/* Bulk summary */}
            {result.bulk_summary && (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-3">
                {Object.entries(result.bulk_summary).filter(([k]) => k !== 'note').slice(0, 6).map(([k, v]) => (
                  <div key={k} className="bg-charcoal-800/60 rounded-lg px-3 py-2">
                    <p className="text-xs text-charcoal-500 capitalize">{k.replace(/_/g, ' ')}</p>
                    <p className="text-sm text-charcoal-100 font-medium mt-0.5">{v}</p>
                  </div>
                ))}
              </div>
            )}
            {result.bulk_summary?.note && (
              <p className="text-xs text-charcoal-500 mt-2 italic">{result.bulk_summary.note}</p>
            )}

            {/* Explanation */}
            {result.explanation && (
              <div className="mt-4 bg-charcoal-800/40 border border-charcoal-700 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Info className="w-4 h-4 text-amber-400 flex-shrink-0" />
                  <span className="text-xs font-medium text-amber-400">Why this recommendation?</span>
                </div>
                <p className="text-sm text-charcoal-300 leading-relaxed"
                   dangerouslySetInnerHTML={{ __html: result.explanation.replace(/\*\*(.*?)\*\*/g, '<strong class="text-charcoal-100">$1</strong>') }} />
              </div>
            )}
          </div>

          {/* Confidence ring */}
          <div className="flex-shrink-0 flex flex-col items-center">
            <ConfidenceRing
              confidence={result.confidence}
              band={result.confidence_band}
              size={130}
            />
            <p className="text-xs text-charcoal-500 mt-3 max-w-[140px] text-center leading-snug">
              {result.confidence_explanation?.split('.')[0]}.
            </p>
          </div>
        </div>

        {/* Follow-up questions */}
        {result.follow_up_questions?.length > 0 && (
          <div className="mt-4 bg-amber-500/10 border border-amber-500/20 rounded-xl p-4">
            <p className="text-xs font-medium text-amber-400 mb-2">To improve confidence, provide:</p>
            <ul className="space-y-1">
              {result.follow_up_questions.map((q, i) => (
                <li key={i} className="text-xs text-charcoal-300">• {q}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* FACTORS */}
      <SectionCard title="Why This Decision?" icon={TrendingUp} iconColor="text-amber-400">
        <FactorChart factors={result.factors} />
        {result.confidence_explanation && (
          <div className="mt-4 bg-charcoal-800/40 rounded-xl p-3">
            <p className="text-xs text-charcoal-400">{result.confidence_explanation}</p>
          </div>
        )}
      </SectionCard>

      {/* IMPACT */}
      {result.impact && (
        <div className="mt-4">
          <SectionCard title="Impact Analysis" icon={AlertTriangle} iconColor="text-amber-400">
            <ImpactSection impact={result.impact} />
          </SectionCard>
        </div>
      )}

      {/* ALTERNATIVES */}
      {result.alternatives?.length > 0 && (
        <div className="mt-4">
          <SectionCard title="Alternatives & Trade-offs" icon={Layers} iconColor="text-purple-400">
            <AlternativesSection alternatives={result.alternatives} />
          </SectionCard>
        </div>
      )}

      {/* WHAT-IF */}
      <div className="mt-4">
        <SectionCard title="What-If Analysis" icon={SlidersHorizontal} iconColor="text-blue-400">
          <WhatIfPanel
            originalResult={result}
            category={category}
            originalInput={inputData || {}}
          />
        </SectionCard>
      </div>

      {/* COUNTERFACTUAL */}
      <div className="mt-4">
        <SectionCard title="Counterfactual Analysis" icon={GitBranch} iconColor="text-emerald-400" defaultOpen={false}>
          <CounterfactualSection
            category={category}
            inputData={inputData}
            recommendation={result.recommendation}
          />
        </SectionCard>
      </div>

      {/* PRODUCTS */}
      {result.products?.length > 0 && (
        <div className="mt-4">
          <SectionCard title="Demo Product Options" icon={Package} iconColor="text-emerald-400">
            <div className="mb-3 flex items-center gap-2">
              <span className="badge bg-charcoal-800 border border-charcoal-700 text-charcoal-400 text-xs">
                📋 Demo catalog data — not live market prices
              </span>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {result.products.map(product => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </SectionCard>
        </div>
      )}

      {/* NEARBY */}
      {showNearby && (
        <div className="mt-4">
          <SectionCard title="Find Nearby Shops" icon={MapPin} iconColor="text-emerald-400">
            <NearbySection category={category} />
          </SectionCard>
        </div>
      )}

      {/* History link */}
      {historyId && (
        <div className="mt-6 text-center">
          <p className="text-xs text-charcoal-500">
            Decision saved to history. <Link to="/history" className="text-amber-400 hover:text-amber-300">View History</Link>
          </p>
        </div>
      )}
    </div>
  )
}
