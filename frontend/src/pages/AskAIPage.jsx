import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Brain, Send, Lightbulb, AlertCircle, Sparkles } from 'lucide-react'
import { analyzeDecision } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorBanner from '../components/ErrorBanner'

const EXAMPLES = [
  'I had a fight with my best friend and he told me not to talk to him. He is all I have. What should I do?',
  'I have diarrhea and stomach cramps. What should I eat and what should I avoid right now?',
  'Should I join an early-stage startup with equity or accept a corporate offer with higher pay?',
  'I need a laptop under ₹60,000 for CSE, Python, VS Code and beginner AI/ML.',
  'Should I rent an apartment near my office or buy a flat in the suburbs?',
  'I want to adopt a pet. I live in a 2BHK apartment and work 8 hours a day. What breed suits me best?',
  'Which smartphone under ₹25,000 has the best camera and long battery life?',
]

export default function AskAIPage() {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [location, setLocation] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSubmit(e)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim() || query.trim().length < 10) {
      setError('Please describe your situation in at least 10 characters.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const resp = await analyzeDecision({ query: query.trim(), location: location || undefined })
      navigate('/result', {
        state: {
          result: resp.data.result,
          historyId: resp.data.history_id,
          inputData: { query },
          mode: 'ask',
          originalQuery: query,
        }
      })
    } catch (e) {
      const msg = e.response?.data?.detail || 'Analysis failed. Please try again.'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center">
          <Brain className="w-5 h-5 text-amber-400" />
        </div>
        <div>
          <h1 className="font-heading text-2xl font-bold text-charcoal-100 flex items-center gap-2">
            Ask AI
            <span className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 border border-emerald-500/30 text-emerald-400">
              <Sparkles className="w-3.5 h-3.5" /> Powered by Gemini AI
            </span>
          </h1>
          <p className="text-charcoal-400 text-sm">Ask literally ANY question, decision, or dilemma — get structured, explainable guidance</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Main textarea */}
        <div>
          <label className="label" htmlFor="query">
            Describe your situation, problem, requirements, or decision
          </label>
          <textarea
            id="query"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="input-field min-h-[160px] resize-y"
            placeholder="e.g. 'I had a fight with my best friend. He said not to talk to him, but he is all I have. What should I do?' or 'I have diarrhea, what should I eat?' or 'Should I switch to AI/ML or stay in web dev?'"
            maxLength={2000}
            aria-describedby="query-hint"
          />
          <p id="query-hint" className="text-xs text-charcoal-500 mt-1.5 flex justify-between">
            <span>Tip: Press Ctrl + Enter to submit. Be as specific as you like!</span>
            <span>{query.length}/2000</span>
          </p>
        </div>

        {/* Location */}
        <div>
          <label className="label" htmlFor="location">Your city or location <span className="text-charcoal-500 font-normal">(optional — for nearby suggestions)</span></label>
          <input
            id="location"
            type="text"
            className="input-field"
            value={location}
            onChange={e => setLocation(e.target.value)}
            placeholder="e.g. Mumbai, Bangalore, Delhi..."
          />
        </div>

        {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full flex items-center justify-center gap-2 py-4 text-base"
        >
          {loading ? (
            <><LoadingSpinner size="sm" /> Analyzing your situation...</>
          ) : (
            <><Send className="w-4 h-4" /> Get AI Recommendation</>
          )}
        </button>
      </form>

      {/* Examples */}
      <div className="mt-8">
        <div className="flex items-center gap-2 mb-3">
          <Lightbulb className="w-4 h-4 text-amber-400" />
          <span className="text-sm font-medium text-charcoal-400">Example queries</span>
        </div>
        <div className="space-y-2">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              onClick={() => setQuery(ex)}
              className="w-full text-left text-sm text-charcoal-400 hover:text-charcoal-100 bg-charcoal-900 hover:bg-charcoal-800 border border-charcoal-800 hover:border-charcoal-700 rounded-xl px-4 py-3 transition-all duration-150"
            >
              "{ex}"
            </button>
          ))}
        </div>
      </div>

      {/* Info box */}
      <div className="mt-6 bg-charcoal-900/50 border border-charcoal-800 rounded-xl p-4">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-charcoal-400">
            <p className="font-medium text-charcoal-300 mb-1">What you'll get</p>
            <ul className="space-y-1">
              <li>• Explainable recommendation with factor scores</li>
              <li>• Confidence level based on your input completeness</li>
              <li>• Impact analysis: immediate, cost, long-term</li>
              <li>• Alternative options with trade-offs</li>
              <li>• Interactive what-if analysis</li>
              <li>• Demo product catalog where applicable</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
