import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { checkHealth } from './api'
import Navbar from './components/Navbar'
import BackendOffline from './components/BackendOffline'
import HomePage from './pages/HomePage'
import GuidedDecisionPage from './pages/GuidedDecisionPage'
import AskAIPage from './pages/AskAIPage'
import ResultPage from './pages/ResultPage'
import HistoryPage from './pages/HistoryPage'
import HistoryDetailPage from './pages/HistoryDetailPage'
import LoadingSpinner from './components/LoadingSpinner'

function App() {
  const [backendStatus, setBackendStatus] = useState('checking') // 'checking' | 'online' | 'offline'

  const checkBackendHealth = async () => {
    setBackendStatus('checking')
    try {
      await checkHealth()
      setBackendStatus('online')
    } catch {
      setBackendStatus('offline')
    }
  }

  useEffect(() => {
    checkBackendHealth()
  }, [])

  if (backendStatus === 'checking') {
    return (
      <div className="min-h-screen bg-charcoal-950 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-charcoal-400 font-body">Connecting to backend...</p>
        </div>
      </div>
    )
  }

  if (backendStatus === 'offline') {
    return <BackendOffline onRetry={checkBackendHealth} />
  }

  return (
    <Router>
      <div className="min-h-screen bg-charcoal-950 font-body">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/guided" element={<GuidedDecisionPage />} />
            <Route path="/ask" element={<AskAIPage />} />
            <Route path="/result" element={<ResultPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/history/:id" element={<HistoryDetailPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
