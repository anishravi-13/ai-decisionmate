export default function LoadingSpinner({ size = 'md', className = '' }) {
  const sizes = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-3',
  }
  return (
    <div
      className={`${sizes[size]} border-charcoal-700 border-t-amber-400 rounded-full animate-spin mx-auto ${className}`}
      style={{ borderWidth: size === 'lg' ? '3px' : '2px' }}
      role="status"
      aria-label="Loading"
    />
  )
}
