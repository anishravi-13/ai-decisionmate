import { useState, useEffect, useCallback } from 'react'
import { SlidersHorizontal, RefreshCw } from 'lucide-react'
import { whatIfAnalysis } from '../api'
import LoadingSpinner from './LoadingSpinner'

function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debounced
}

export default function WhatIfPanel({ originalResult, category, originalInput }) {
  const isRelationship = category === 'relationship' || category === 'personal'

  // Product / general state
  const [budget, setBudget] = useState(originalInput?.budget || 50000)
  const [performance, setPerformance] = useState(originalInput?.performance_priority || 'medium')
  const [quantity, setQuantity] = useState(originalInput?.quantity || 1)

  // Relationship specific state
  const [coolingDays, setCoolingDays] = useState(originalInput?.cooling_off_days || 3)
  const [conflictIntensity, setConflictIntensity] = useState(originalInput?.conflict_intensity || 'high')
  const [faultAttribution, setFaultAttribution] = useState(originalInput?.fault_attribution || 'mutual_or_unclear')
  const [askedForSpace, setAskedForSpace] = useState(originalInput?.asked_for_space || 'yes')

  const [result, setResult] = useState(null)
  const [changed, setChanged] = useState(false)
  const [changeReason, setChangeReason] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const debouncedBudget = useDebounce(budget, 350)
  const debouncedPerf = useDebounce(performance, 350)
  const debouncedQty = useDebounce(quantity, 350)

  const debouncedCooling = useDebounce(coolingDays, 350)
  const debouncedConflict = useDebounce(conflictIntensity, 350)
  const debouncedFault = useDebounce(faultAttribution, 350)
  const debouncedSpace = useDebounce(askedForSpace, 350)

  const runWhatIf = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      let changes = {}
      if (isRelationship) {
        changes = {
          cooling_off_days: debouncedCooling,
          conflict_intensity: debouncedConflict,
          fault_attribution: debouncedFault,
          asked_for_space: debouncedSpace,
          recommendation: originalResult?.recommendation,
        }
      } else {
        changes = {
          budget: debouncedBudget,
          performance_priority: debouncedPerf,
          quantity: debouncedQty,
          recommendation: originalResult?.recommendation,
        }
      }

      const resp = await whatIfAnalysis({
        original_request: { ...originalInput, recommendation: originalResult?.recommendation },
        changes,
        category,
      })
      setResult(resp.data.result)
      setChanged(resp.data.recommendation_changed)
      setChangeReason(resp.data.changed_because || '')
    } catch (e) {
      setError('What-if analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [
    isRelationship,
    debouncedCooling,
    debouncedConflict,
    debouncedFault,
    debouncedSpace,
    debouncedBudget,
    debouncedPerf,
    debouncedQty,
    category,
    originalInput,
    originalResult,
  ])

  useEffect(() => {
    runWhatIf()
  }, [runWhatIf])

  const perfOptions = ['low', 'medium', 'high']
  const budgetMin = 10000
  const budgetMax = 300000
  const budgetPct = ((budget - budgetMin) / (budgetMax - budgetMin)) * 100

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2 mb-1">
        <SlidersHorizontal className="w-4 h-4 text-amber-400" />
        <p className="text-xs text-charcoal-400">
          {isRelationship
            ? 'Adjust cooling-off time, fault ownership, or boundary factors to simulate different scenarios.'
            : 'Adjust parameters to see how recommendations change in real time.'}
        </p>
      </div>

      {isRelationship ? (
        <>
          {/* Cooling-off period slider */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="label mb-0">Cooling-Off Wait Time</label>
              <span className="text-amber-400 font-semibold text-sm">{coolingDays} days</span>
            </div>
            <input
              type="range"
              min={1}
              max={14}
              step={1}
              value={coolingDays}
              onChange={e => setCoolingDays(Number(e.target.value))}
              style={{ '--value': `${((coolingDays - 1) / 13) * 100}%` }}
              className="w-full"
              aria-label="Cooling-off wait days slider"
            />
            <div className="flex justify-between text-xs text-charcoal-600 mt-1">
              <span>1 day (immediate)</span>
              <span>14 days (long space)</span>
            </div>
          </div>

          {/* Conflict Intensity */}
          <div>
            <label className="label">Conflict Severity</label>
            <div className="flex gap-2">
              {[
                { id: 'low', label: 'Minor' },
                { id: 'medium', label: 'Moderate' },
                { id: 'high', label: 'Heated Fight' },
              ].map(opt => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => setConflictIntensity(opt.id)}
                  className={`flex-1 py-2 rounded-lg text-xs sm:text-sm font-medium border transition-all ${
                    conflictIntensity === opt.id
                      ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
                      : 'bg-charcoal-800 border-charcoal-700 text-charcoal-400 hover:border-charcoal-600'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Fault Attribution */}
          <div>
            <label className="label">Primary Responsibility</label>
            <div className="flex gap-2">
              {[
                { id: 'mostly_mine', label: 'My Mistake' },
                { id: 'mutual_or_unclear', label: 'Mutual' },
                { id: 'mostly_theirs', label: 'Their Fault' },
              ].map(opt => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => setFaultAttribution(opt.id)}
                  className={`flex-1 py-2 rounded-lg text-xs sm:text-sm font-medium border transition-all ${
                    faultAttribution === opt.id
                      ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
                      : 'bg-charcoal-800 border-charcoal-700 text-charcoal-400 hover:border-charcoal-600'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Boundary / Asked for space */}
          <div>
            <label className="label">Did They Say "Do Not Talk to Me"?</label>
            <div className="flex gap-2">
              {[
                { id: 'yes', label: 'Yes (Explicit Boundary)' },
                { id: 'no', label: 'No (Channel Open)' },
              ].map(opt => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => setAskedForSpace(opt.id)}
                  className={`flex-1 py-2 rounded-lg text-xs sm:text-sm font-medium border transition-all ${
                    askedForSpace === opt.id
                      ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
                      : 'bg-charcoal-800 border-charcoal-700 text-charcoal-400 hover:border-charcoal-600'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        </>
      ) : (
        <>
          {/* Budget slider */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="label mb-0">Budget</label>
              <span className="text-amber-400 font-semibold text-sm">₹{Number(budget).toLocaleString('en-IN')}</span>
            </div>
            <input
              type="range"
              min={budgetMin}
              max={budgetMax}
              step={5000}
              value={budget}
              onChange={e => setBudget(Number(e.target.value))}
              style={{ '--value': `${budgetPct}%` }}
              className="w-full"
              aria-label="Budget slider"
            />
            <div className="flex justify-between text-xs text-charcoal-600 mt-1">
              <span>₹10,000</span>
              <span>₹3,00,000</span>
            </div>
          </div>

          {/* Performance */}
          <div>
            <label className="label">Performance Priority</label>
            <div className="flex gap-2">
              {perfOptions.map(opt => (
                <button
                  key={opt}
                  type="button"
                  onClick={() => setPerformance(opt)}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium border transition-all ${
                    performance === opt
                      ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
                      : 'bg-charcoal-800 border-charcoal-700 text-charcoal-400 hover:border-charcoal-600'
                  }`}
                >
                  {opt.charAt(0).toUpperCase() + opt.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Quantity */}
          {(category === 'company_bulk' || originalInput?.quantity > 1) && (
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="label mb-0">Quantity</label>
                <span className="text-amber-400 font-semibold text-sm">{quantity} units</span>
              </div>
              <input
                type="range"
                min={1}
                max={100}
                step={1}
                value={quantity}
                onChange={e => setQuantity(Number(e.target.value))}
                style={{ '--value': `${((quantity - 1) / 99) * 100}%` }}
                className="w-full"
                aria-label="Quantity slider"
              />
              <div className="flex justify-between text-xs text-charcoal-600 mt-1">
                <span>1</span>
                <span>100</span>
              </div>
            </div>
          )}
        </>
      )}

      {/* Result */}
      <div className="bg-charcoal-800/50 rounded-xl p-4 border border-charcoal-700 min-h-[80px]">
        {loading ? (
          <div className="flex items-center gap-3">
            <LoadingSpinner size="sm" />
            <span className="text-charcoal-400 text-sm">Recalculating...</span>
          </div>
        ) : error ? (
          <p className="text-red-400 text-sm">{error}</p>
        ) : result ? (
          <div>
            {changed && (
              <div className="mb-2 flex items-center gap-2">
                <RefreshCw className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                <span className="text-xs text-amber-400 font-medium">Recommendation updated</span>
              </div>
            )}
            <p className="text-charcoal-100 text-sm font-medium">{result.recommendation}</p>
            <div className="flex items-center gap-3 mt-2 flex-wrap">
              <span
                className={`text-xs font-semibold ${
                  result.confidence_band === 'HIGH'
                    ? 'text-emerald-400'
                    : result.confidence_band === 'MEDIUM'
                    ? 'text-amber-400'
                    : 'text-red-400'
                }`}
              >
                {Math.round(result.confidence)}% {result.confidence_band}
              </span>
              {changeReason && (
                <span className="text-xs text-charcoal-400">
                  {changeReason.split('.')[0]}.
                </span>
              )}
            </div>
          </div>
        ) : (
          <p className="text-charcoal-500 text-sm">Adjust controls to see what-if analysis.</p>
        )}
      </div>
    </div>
  )
}
