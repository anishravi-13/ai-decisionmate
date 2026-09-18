import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { History, Trash2, Trash, AlertTriangle, ChevronRight, Clock } from 'lucide-react'
import { getHistory, deleteHistoryItem, deleteAllHistory } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorBanner from '../components/ErrorBanner'

function ConfirmDialog({ message, onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="card p-6 max-w-sm w-full shadow-xl animate-fade-in">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-red-500/15 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-red-400" />
          </div>
          <h2 className="font-heading font-semibold text-charcoal-100">Confirm Delete</h2>
        </div>
        <p className="text-sm text-charcoal-400 mb-6">{message}</p>
        <div className="flex gap-3">
          <button onClick={onCancel} className="btn-secondary flex-1">Cancel</button>
          <button onClick={onConfirm} className="btn-danger flex-1">Delete</button>
        </div>
      </div>
    </div>
  )
}

function HistoryCard({ item, onDelete }) {
  const bandColor = item.confidence_band === 'HIGH' ? 'text-emerald-400' :
    item.confidence_band === 'MEDIUM' ? 'text-amber-400' : 'text-red-400'

  const bandBg = item.confidence_band === 'HIGH' ? 'bg-emerald-500/10 border-emerald-500/20' :
    item.confidence_band === 'MEDIUM' ? 'bg-amber-500/10 border-amber-500/20' : 'bg-red-500/10 border-red-500/20'

  return (
    <div className="card card-hover group relative">
      <Link to={`/history/${item.id}`} className="block p-5">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="badge bg-charcoal-800 border border-charcoal-700 text-charcoal-300 capitalize">
              {item.category?.replace(/_/g, ' ')}
            </span>
            {item.confidence_band && (
              <span className={`badge border ${bandColor} ${bandBg} text-xs`}>
                {item.confidence_band}
              </span>
            )}
          </div>
          <div className="text-right flex-shrink-0">
            {item.confidence !== null && item.confidence !== undefined && (
              <span className={`text-lg font-bold font-heading ${bandColor}`}>
                {Math.round(item.confidence)}%
              </span>
            )}
          </div>
        </div>

        <p className="text-sm text-charcoal-200 font-medium line-clamp-2 mb-2">
          {item.recommendation || item.user_query || 'Decision record'}
        </p>

        {item.user_query && item.recommendation && (
          <p className="text-xs text-charcoal-500 line-clamp-1 mb-3">
            "{item.user_query}"
          </p>
        )}

        <div className="flex items-center gap-1.5 text-charcoal-500">
          <Clock className="w-3.5 h-3.5" />
          <span className="text-xs">
            {new Date(item.timestamp).toLocaleString('en-IN', {
              day: 'numeric', month: 'short', year: 'numeric',
              hour: '2-digit', minute: '2-digit'
            })}
          </span>
        </div>
      </Link>

      {/* Delete button */}
      <button
        onClick={(e) => { e.preventDefault(); onDelete(item.id) }}
        className="absolute top-4 right-4 p-2 rounded-lg text-charcoal-600 hover:text-red-400 hover:bg-red-500/10 transition-all opacity-0 group-hover:opacity-100"
        aria-label="Delete this history item"
        title="Delete"
      >
        <Trash2 className="w-4 h-4" />
      </button>

      <Link
        to={`/history/${item.id}`}
        className="absolute bottom-4 right-4 text-charcoal-600 hover:text-amber-400 transition-colors opacity-0 group-hover:opacity-100"
        aria-label="View full decision"
      >
        <ChevronRight className="w-4 h-4" />
      </Link>
    </div>
  )
}

export default function HistoryPage() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [confirm, setConfirm] = useState(null) // { type: 'single'|'all', id?: number }

  const fetchHistory = async () => {
    setLoading(true)
    setError(null)
    try {
      const resp = await getHistory()
      setHistory(resp.data)
    } catch (e) {
      setError('Failed to load history. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchHistory() }, [])

  const handleDeleteOne = (id) => {
    setConfirm({ type: 'single', id })
  }

  const handleDeleteAll = () => {
    setConfirm({ type: 'all' })
  }

  const handleConfirmDelete = async () => {
    const c = confirm
    setConfirm(null)
    try {
      if (c.type === 'single') {
        await deleteHistoryItem(c.id)
        setHistory(prev => prev.filter(h => h.id !== c.id))
      } else {
        await deleteAllHistory()
        setHistory([])
      }
    } catch (e) {
      setError('Deletion failed. Please try again.')
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center">
            <History className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h1 className="font-heading text-2xl font-bold text-charcoal-100">Decision History</h1>
            <p className="text-charcoal-400 text-sm">{history.length} saved decision{history.length !== 1 ? 's' : ''}</p>
          </div>
        </div>

        {history.length > 0 && (
          <button
            onClick={handleDeleteAll}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-red-400 border border-red-500/20 hover:bg-red-500/10 text-sm font-medium transition-all"
          >
            <Trash className="w-4 h-4" />
            Delete All
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4">
          <ErrorBanner message={error} onDismiss={() => setError(null)} />
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center py-20 gap-4">
          <LoadingSpinner size="lg" />
          <p className="text-charcoal-400">Loading history...</p>
        </div>
      ) : history.length === 0 ? (
        <div className="text-center py-20">
          <div className="w-16 h-16 rounded-2xl bg-charcoal-800 border border-charcoal-700 flex items-center justify-center mx-auto mb-4">
            <History className="w-8 h-8 text-charcoal-600" />
          </div>
          <h2 className="font-heading text-lg font-semibold text-charcoal-300 mb-2">No history yet</h2>
          <p className="text-charcoal-500 text-sm mb-6">Make your first decision to see it here.</p>
          <div className="flex gap-3 justify-center">
            <Link to="/guided" className="btn-primary">Guided Decision</Link>
            <Link to="/ask" className="btn-secondary">Ask AI</Link>
          </div>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {history.map(item => (
            <HistoryCard key={item.id} item={item} onDelete={handleDeleteOne} />
          ))}
        </div>
      )}

      {/* Confirm dialog */}
      {confirm && (
        <ConfirmDialog
          message={
            confirm.type === 'all'
              ? `Delete all ${history.length} decision records permanently? This cannot be undone.`
              : 'Delete this decision record permanently?'
          }
          onConfirm={handleConfirmDelete}
          onCancel={() => setConfirm(null)}
        />
      )}
    </div>
  )
}
