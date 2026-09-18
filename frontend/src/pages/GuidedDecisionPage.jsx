import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { HelpCircle, ChevronRight, ArrowLeft, Send } from 'lucide-react'
import { CATEGORIES, CATEGORY_QUESTIONS } from '../data/categoryQuestions'
import { guidedAnalyze } from '../api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorBanner from '../components/ErrorBanner'

function CategorySelector({ selected, onSelect }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      {CATEGORIES.map(cat => (
        <button
          key={cat.id}
          onClick={() => onSelect(cat.id)}
          className={`p-4 rounded-xl border text-left transition-all duration-200 ${
            selected === cat.id
              ? 'bg-amber-500/15 border-amber-500/40 text-amber-300'
              : 'bg-charcoal-800 border-charcoal-700 text-charcoal-300 hover:border-charcoal-600 hover:text-charcoal-100'
          }`}
        >
          <div className="text-2xl mb-2">{cat.emoji}</div>
          <div className="font-medium text-sm leading-tight">{cat.label}</div>
          <div className="text-xs text-charcoal-500 mt-1 leading-tight">{cat.description}</div>
        </button>
      ))}
    </div>
  )
}

function QuestionField({ question, value, onChange }) {
  if (question.type === 'radio') {
    return (
      <div className="space-y-2">
        {question.options.map(opt => (
          <label
            key={opt.value}
            className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
              value === opt.value
                ? 'bg-amber-500/10 border-amber-500/40'
                : 'bg-charcoal-800 border-charcoal-700 hover:border-charcoal-600'
            }`}
          >
            <input
              type="radio"
              name={question.id}
              value={opt.value}
              checked={value === opt.value}
              onChange={() => onChange(question.id, opt.value)}
              className="sr-only"
            />
            <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
              value === opt.value ? 'border-amber-400' : 'border-charcoal-600'
            }`}>
              {value === opt.value && <div className="w-2 h-2 rounded-full bg-amber-400" />}
            </div>
            <span className="text-sm text-charcoal-200">{opt.label}</span>
          </label>
        ))}
      </div>
    )
  }

  if (question.type === 'checkboxes') {
    const selected = Array.isArray(value) ? value : []
    return (
      <div className="space-y-2">
        {question.options.map(opt => {
          const checked = selected.includes(opt.value)
          return (
            <label
              key={opt.value}
              className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                checked ? 'bg-amber-500/10 border-amber-500/40' : 'bg-charcoal-800 border-charcoal-700 hover:border-charcoal-600'
              }`}
            >
              <input
                type="checkbox"
                checked={checked}
                onChange={() => {
                  const next = checked
                    ? selected.filter(v => v !== opt.value)
                    : [...selected, opt.value]
                  onChange(question.id, next)
                }}
                className="sr-only"
              />
              <div className={`w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0 ${
                checked ? 'bg-amber-400 border-amber-400' : 'border-charcoal-600'
              }`}>
                {checked && <span className="text-charcoal-950 text-xs font-bold">✓</span>}
              </div>
              <span className="text-sm text-charcoal-200">{opt.label}</span>
            </label>
          )
        })}
      </div>
    )
  }

  if (question.type === 'number') {
    return (
      <input
        type="number"
        className="input-field"
        value={value || ''}
        onChange={e => onChange(question.id, e.target.value ? Number(e.target.value) : '')}
        placeholder={question.placeholder}
        min={question.min}
        max={question.max}
        aria-label={question.label}
      />
    )
  }

  // text
  return (
    <input
      type="text"
      className="input-field"
      value={value || ''}
      onChange={e => onChange(question.id, e.target.value)}
      placeholder={question.placeholder}
      aria-label={question.label}
    />
  )
}

export default function GuidedDecisionPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const initialCategory = searchParams.get('category') || ''

  const [step, setStep] = useState(initialCategory ? 'questions' : 'category')
  const [selectedCategory, setSelectedCategory] = useState(initialCategory)
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const questions = CATEGORY_QUESTIONS[selectedCategory] || []

  const handleCategorySelect = (catId) => {
    setSelectedCategory(catId)
    setAnswers({})
    setStep('questions')
  }

  const handleAnswer = (id, val) => {
    setAnswers(prev => ({ ...prev, [id]: val }))
  }

  const handleSubmit = async () => {
    const requiredMissing = questions
      .filter(q => q.required && !answers[q.id])
      .map(q => q.label)

    if (requiredMissing.length > 0) {
      setError(`Please answer required questions: ${requiredMissing.join(', ')}`)
      return
    }

    setLoading(true)
    setError(null)
    try {
      const quantity = answers.quantity ? Number(answers.quantity) : undefined
      const resp = await guidedAnalyze({
        category: selectedCategory,
        answers,
        quantity,
        location: answers.location || undefined,
      })
      navigate('/result', {
        state: {
          result: resp.data.result,
          historyId: resp.data.history_id,
          inputData: answers,
          mode: 'guided',
        }
      })
    } catch (e) {
      let msg = 'Analysis failed. Please check your inputs and try again.'
      if (e.response?.data?.detail) {
        if (typeof e.response.data.detail === 'string') {
          msg = e.response.data.detail
        } else if (Array.isArray(e.response.data.detail)) {
          msg = e.response.data.detail.map(d => d.msg || JSON.stringify(d)).join('; ')
        }
      } else if (e.message) {
        msg = `Connection error (${e.message}). Please ensure the server is active on port 7000.`
      }
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const cat = CATEGORIES.find(c => c.id === selectedCategory)

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center">
          <HelpCircle className="w-5 h-5 text-amber-400" />
        </div>
        <div>
          <h1 className="font-heading text-2xl font-bold text-charcoal-100">Guided Decision</h1>
          <p className="text-charcoal-400 text-sm">Answer structured questions to get an explainable recommendation</p>
        </div>
      </div>

      {/* Step: Category */}
      {step === 'category' && (
        <div>
          <h2 className="font-heading text-lg font-semibold text-charcoal-200 mb-4">Select a decision category</h2>
          <CategorySelector selected={selectedCategory} onSelect={handleCategorySelect} />
        </div>
      )}

      {/* Step: Questions */}
      {step === 'questions' && (
        <div>
          {/* Back */}
          <button
            onClick={() => setStep('category')}
            className="flex items-center gap-2 text-charcoal-400 hover:text-charcoal-100 text-sm mb-6 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Change category
          </button>

          {/* Category header */}
          {cat && (
            <div className="flex items-center gap-3 mb-6 p-4 card">
              <span className="text-3xl">{cat.emoji}</span>
              <div>
                <h2 className="font-heading text-xl font-semibold text-charcoal-100">{cat.label}</h2>
                <p className="text-charcoal-400 text-sm">{cat.description}</p>
              </div>
            </div>
          )}

          {/* Questions */}
          <div className="space-y-6">
            {questions.map(q => (
              <div key={q.id}>
                <label className="label">
                  {q.label}
                  {q.required && <span className="text-amber-400 ml-1">*</span>}
                </label>
                <QuestionField
                  question={q}
                  value={answers[q.id]}
                  onChange={handleAnswer}
                />
              </div>
            ))}
          </div>

          {error && <div className="mt-4"><ErrorBanner message={error} onDismiss={() => setError(null)} /></div>}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="btn-primary w-full mt-8 flex items-center justify-center gap-2 text-base py-4"
          >
            {loading ? (
              <><LoadingSpinner size="sm" /> Analyzing...</>
            ) : (
              <><Send className="w-4 h-4" /> Get Recommendation</>
            )}
          </button>
        </div>
      )}
    </div>
  )
}
