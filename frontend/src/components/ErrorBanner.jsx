import { AlertCircle, X } from 'lucide-react'
import { useState } from 'react'

export default function ErrorBanner({ message, onDismiss }) {
  const [visible, setVisible] = useState(true)
  if (!visible) return null

  const handleDismiss = () => {
    setVisible(false)
    onDismiss?.()
  }

  return (
    <div className="bg-red-950 border border-red-800 rounded-xl p-4 flex items-start gap-3 animate-fade-in">
      <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
      <p className="text-sm text-red-200 flex-1">{message}</p>
      <button
        onClick={handleDismiss}
        className="text-red-500 hover:text-red-300 transition-colors"
        aria-label="Dismiss error"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}
