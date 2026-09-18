import { AlertTriangle, RefreshCw, Server } from 'lucide-react'

export default function BackendOffline({ onRetry }) {
  return (
    <div className="min-h-screen bg-charcoal-950 flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center">
        {/* Icon */}
        <div className="w-20 h-20 rounded-2xl bg-charcoal-900 border border-charcoal-700 flex items-center justify-center mx-auto mb-6">
          <Server className="w-10 h-10 text-charcoal-500" />
        </div>

        {/* Title */}
        <h1 className="font-heading text-2xl font-bold text-charcoal-100 mb-2">
          Backend Not Running
        </h1>
        <p className="text-charcoal-400 mb-6">
          The AI DecisionMate backend server is not reachable on{' '}
          <code className="bg-charcoal-800 text-amber-400 px-1.5 py-0.5 rounded text-sm">
            http://localhost:8000
          </code>
        </p>

        {/* Instructions */}
        <div className="card p-5 text-left mb-6">
          <div className="flex items-start gap-3 mb-4">
            <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm font-medium text-charcoal-200">Start the backend server first:</p>
          </div>
          <div className="bg-charcoal-950 rounded-xl p-4 font-mono text-sm space-y-1">
            <p className="text-charcoal-500"># Open a terminal and run:</p>
            <p className="text-emerald-400">cd backend</p>
            <p className="text-emerald-400">pip install -r requirements.txt</p>
            <p className="text-emerald-400">uvicorn main:app --reload --port 8000</p>
          </div>
        </div>

        {/* Retry */}
        <button
          onClick={onRetry}
          className="btn-primary flex items-center gap-2 mx-auto"
        >
          <RefreshCw className="w-4 h-4" />
          Retry Connection
        </button>

        <p className="mt-4 text-xs text-charcoal-600">
          Once the server is running, click Retry or refresh the page.
        </p>
      </div>
    </div>
  )
}
