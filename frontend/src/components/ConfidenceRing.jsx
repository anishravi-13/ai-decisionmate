/**
 * ConfidenceRing – SVG circular progress ring showing confidence %.
 */
export default function ConfidenceRing({ confidence, band, size = 120 }) {
  const radius = (size - 16) / 2
  const circumference = 2 * Math.PI * radius
  const progress = (confidence / 100) * circumference
  const offset = circumference - progress

  const bandColors = {
    HIGH: { stroke: '#10b981', text: 'text-emerald-400', bg: 'bg-emerald-500/15 border-emerald-500/30' },
    MEDIUM: { stroke: '#f59e0b', text: 'text-amber-400', bg: 'bg-amber-500/15 border-amber-500/30' },
    LOW: { stroke: '#ef4444', text: 'text-red-400', bg: 'bg-red-500/15 border-red-500/30' },
  }
  const colors = bandColors[band] || bandColors.MEDIUM

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
          {/* Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#3d4452"
            strokeWidth="8"
          />
          {/* Progress */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={colors.stroke}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.8s ease-out' }}
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-heading font-bold leading-none ${colors.text}`}
                style={{ fontSize: size * 0.22 }}>
            {Math.round(confidence)}%
          </span>
        </div>
      </div>
      <span className={`badge border px-3 py-1 font-semibold text-xs ${colors.text} ${colors.bg}`}>
        {band} CONFIDENCE
      </span>
    </div>
  )
}
