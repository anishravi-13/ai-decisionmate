import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Trash2, Clock, AlertTriangle } from 'lucide-react'
import { getHistoryItem, deleteHistoryItem } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorBanner from '../components/ErrorBanner'
import ConfidenceRing from '../components/ConfidenceRing'
import FactorChart from '../components/FactorChart'

function ConfirmDialog({ onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="card p-6 max-w-sm w-full shadow-xl animate-fade-in">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-red-500/15 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-red-400" />
          </div>
          <h2 className="font-heading font-semibold text-charcoal-100">Confirm Delete</h2>
        </div>
        <p className="text-sm text-charcoal-400 mb-6">Delete this decision record permanently? This cannot be undone.</p>
        <div className="flex gap-3">
          <button onClick={onCancel} className="btn-secondary flex-1">Cancel</button>
          <button onClick={onConfirm} className="btn-danger flex-1">Delete</button>
        </div>
      </div>
    </div>
  )
}

export default function HistoryDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showConfirm, setShowConfirm] = useState(false)

  useEffect(() => {
    setLoading(true)
    getHistoryItem(id)
      .then(r => setItem(r.data))
      .catch(e => {
        if (e.response?.status === 404) {
          setError('This history record was not found.')
        } else {
          setError('Failed to load history record.')
        }
      })
      .finally(() => setLoading(false))
  }, [id])

  const handleDelete = async () => {
    try {
      await deleteHistoryItem(id)
      navigate('/history', { replace: true })
    } catch {
      setError('Failed to delete. Please try again.')
      setShowConfirm(false)
    }
  }

  const result = item?.result || {}
  const factors = result.factors || item?.factors || []
  const impact = result.impact || {}

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Nav */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate('/history')}
          className="flex items-center gap-2 text-charcoal-400 hover:text-charcoal-100 text-sm transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to History
        </button>
        {item && (
          <button
            onClick={() => setShowConfirm(true)}
            className="flex items-center gap-2 text-red-400 hover:text-red-300 text-sm border border-red-500/20 hover:border-red-500/40 hover:bg-red-500/10 px-3 py-1.5 rounded-lg transition-all"
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </button>
        )}
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {loading ? (
        <div className="flex flex-col items-center py-20 gap-4">
          <LoadingSpinner size="lg" />
          <p className="text-charcoal-400">Loading...</p>
        </div>
      ) : item ? (
        <div className="space-y-5">
          {/* Header card */}
          <div className="card p-6">
            <div className="flex items-start gap-3 mb-4">
              <span className="badge bg-amber-500/10 border border-amber-500/20 text-amber-400 capitalize">
                {item.category?.replace(/_/g, ' ')}
              </span>
              <div className="flex items-center gap-1.5 text-charcoal-500 text-xs ml-auto">
                <Clock className="w-3.5 h-3.5" />
                {new Date(item.timestamp).toLocaleString('en-IN', {
                  day: 'numeric', month: 'long', year: 'numeric',
                  hour: '2-digit', minute: '2-digit'
                })}
              </div>
            </div>

            {item.user_query && (
              <div className="bg-charcoal-800/50 rounded-xl px-4 py-3 mb-4">
                <p className="text-xs text-charcoal-500 mb-1">Query</p>
                <p className="text-sm text-charcoal-200">"{item.user_query}"</p>
              </div>
            )}

            <div className="flex flex-col lg:flex-row lg:items-start gap-6">
              <div className="flex-1">
                <p className="text-xs text-charcoal-500 mb-1">Recommendation</p>
                <h1 className="font-heading text-xl font-bold text-charcoal-100 leading-snug">
                  {item.recommendation || result.recommendation || 'N/A'}
                </h1>
              </div>
              {item.confidence !== null && item.confidence !== undefined && (
                <div className="flex-shrink-0">
                  <ConfidenceRing
                    confidence={item.confidence}
                    band={item.confidence_band || 'MEDIUM'}
                    size={110}
                  />
                </div>
              )}
            </div>
          </div>

          {/* Factors */}
          {factors.length > 0 && (
            <div className="card p-5">
              <h2 className="font-heading font-semibold text-charcoal-100 mb-4">Decision Factors</h2>
              <FactorChart factors={factors} />
            </div>
          )}

          {/* Explanation */}
          {result.explanation && (
            <div className="card p-5">
              <h2 className="font-heading font-semibold text-charcoal-100 mb-3">Explanation</h2>
              <p className="text-sm text-charcoal-300 leading-relaxed"
                 dangerouslySetInnerHTML={{ __html: result.explanation.replace(/\*\*(.*?)\*\*/g, '<strong class="text-charcoal-100">$1</strong>') }} />
            </div>
          )}

          {/* Impact summary */}
          {impact && Object.keys(impact).length > 0 && (
            <div className="card p-5">
              <h2 className="font-heading font-semibold text-charcoal-100 mb-4">Impact Summary</h2>
              <div className="grid sm:grid-cols-2 gap-3">
                {impact.immediate?.length > 0 && (
                  <div className="bg-charcoal-800/50 rounded-xl p-3 border border-charcoal-700">
                    <p className="text-xs font-medium text-amber-400 mb-2">⚡ Immediate</p>
                    <ul className="space-y-1">
                      {impact.immediate.map((i, idx) => (
                        <li key={idx} className="text-xs text-charcoal-300">• {i}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {impact.long_term?.length > 0 && (
                  <div className="bg-charcoal-800/50 rounded-xl p-3 border border-charcoal-700">
                    <p className="text-xs font-medium text-blue-400 mb-2">🔮 Long-term</p>
                    <ul className="space-y-1">
                      {impact.long_term.map((i, idx) => (
                        <li key={idx} className="text-xs text-charcoal-300">• {i}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Alternatives */}
          {result.alternatives?.length > 0 && (
            <div className="card p-5">
              <h2 className="font-heading font-semibold text-charcoal-100 mb-3">Alternatives</h2>
              <div className="space-y-2">
                {result.alternatives.map((alt, i) => (
                  <div key={i} className="bg-charcoal-800/50 rounded-xl p-3 border border-charcoal-700">
                    <div className="flex justify-between items-start">
                      <p className="text-sm text-charcoal-200 font-medium flex-1">{alt.name}</p>
                      <span className="text-sm font-bold text-amber-400 ml-2">{Math.round(alt.score)}%</span>
                    </div>
                    <p className="text-xs text-emerald-400 mt-1">✓ {alt.key_advantage}</p>
                    <p className="text-xs text-charcoal-500">⚖ {alt.key_tradeoff}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Input data */}
          {item.input_data && Object.keys(item.input_data).length > 0 && (
            <div className="card p-5">
              <h2 className="font-heading font-semibold text-charcoal-100 mb-3">Input Data</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {Object.entries(item.input_data)
                  .filter(([k, v]) => v && k !== 'query')
                  .map(([k, v]) => (
                    <div key={k} className="bg-charcoal-800/50 rounded-lg px-3 py-2">
                      <p className="text-xs text-charcoal-500 capitalize">{k.replace(/_/g, ' ')}</p>
                      <p className="text-sm text-charcoal-200 font-medium mt-0.5 truncate">
                        {Array.isArray(v) ? v.join(', ') : String(v)}
                      </p>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        !error && (
          <div className="text-center py-16">
            <p className="text-charcoal-400 mb-4">Record not found.</p>
            <Link to="/history" className="btn-secondary">Back to History</Link>
          </div>
        )
      )}

      {showConfirm && (
        <ConfirmDialog
          onConfirm={handleDelete}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </div>
  )
}
