import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList
} from 'recharts'

const COLORS = {
  HIGH: '#10b981',
  MEDIUM: '#f59e0b',
  LOW: '#ef4444',
}

function getBarColor(score) {
  if (score >= 75) return '#10b981'
  if (score >= 55) return '#f59e0b'
  return '#ef4444'
}

function CustomTooltip({ active, payload }) {
  if (active && payload && payload.length) {
    const d = payload[0].payload
    return (
      <div className="bg-charcoal-800 border border-charcoal-700 rounded-lg p-3 shadow-lg max-w-xs">
        <p className="font-medium text-charcoal-100 text-sm mb-1">{d.label}</p>
        <p className="text-xs text-charcoal-400 mb-2">{d.description}</p>
        <p className="text-amber-400 font-bold">{d.score}%</p>
      </div>
    )
  }
  return null
}

export default function FactorChart({ factors }) {
  if (!factors || factors.length === 0) {
    return (
      <div className="text-center py-8 text-charcoal-500">
        No factor data available
      </div>
    )
  }

  // Take top 6, sort descending
  const data = [...factors]
    .sort((a, b) => b.score - a.score)
    .slice(0, 6)
    .map(f => ({
      label: f.label,
      score: Math.round(f.score),
      description: f.description,
      factor: f.factor,
    }))

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={data.length * 52 + 20}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 60, left: 0, bottom: 5 }}
        >
          <XAxis
            type="number"
            domain={[0, 100]}
            tick={{ fill: '#6b7a8f', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="label"
            width={150}
            tick={{ fill: '#b3bcc8', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
          <Bar dataKey="score" radius={[0, 6, 6, 0]} maxBarSize={28}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.score)} />
            ))}
            <LabelList
              dataKey="score"
              position="right"
              formatter={(v) => `${v}%`}
              style={{ fill: '#b3bcc8', fontSize: '12px', fontWeight: '600' }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
