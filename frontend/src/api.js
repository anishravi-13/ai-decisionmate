import axios from 'axios'

const BASE_URL = (typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '3000'))
  ? 'http://localhost:7000'
  : ''

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Health check
export const checkHealth = () => api.get('/health')

// Gemini AI status
export const checkGeminiStatus = () => api.get('/gemini-status')

// Analyze free-text input
export const analyzeDecision = (data) => api.post('/analyze', data)

// Guided decision
export const guidedAnalyze = (data) => api.post('/guided-analyze', data)

// What-if analysis
export const whatIfAnalysis = (data) => api.post('/whatif', data)

// Product search
export const searchProducts = (data) => api.post('/products', data)

// Nearby business search
export const searchNearby = (data) => api.post('/nearby', data)

// History
export const getHistory = () => api.get('/history')
export const getHistoryItem = (id) => api.get(`/history/${id}`)
export const deleteHistoryItem = (id) => api.delete(`/history/${id}`)
export const deleteAllHistory = () => api.delete('/history')

// Counterfactual
export const getCounterfactual = (data) => api.post('/counterfactual', data)

// Impact analysis
export const getImpact = (data) => api.post('/impact', data)

export default api
