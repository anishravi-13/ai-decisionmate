import { Star, ExternalLink, Tag } from 'lucide-react'

export default function ProductCard({ product }) {
  if (!product) return null

  const matchColor =
    product.match_pct >= 80 ? 'text-emerald-400' :
    product.match_pct >= 60 ? 'text-amber-400' : 'text-charcoal-400'

  return (
    <div className="card card-hover p-4 flex flex-col gap-3">
      {/* Demo badge */}
      <div className="flex items-center justify-between">
        <span className="badge bg-charcoal-800 border border-charcoal-700 text-charcoal-400 text-xs">
          <Tag className="w-3 h-3 mr-1" />
          Demo catalog
        </span>
        <span className={`font-bold text-sm ${matchColor}`}>
          {Math.round(product.match_pct)}% match
        </span>
      </div>

      {/* Name */}
      <h3 className="font-heading font-semibold text-charcoal-100 leading-snug">
        {product.name}
      </h3>

      {/* Price + Rating */}
      <div className="flex items-center gap-4 text-sm">
        {product.price && (
          <span className="text-amber-400 font-semibold">{product.price}</span>
        )}
        {product.rating && (
          <span className="flex items-center gap-1 text-charcoal-400">
            <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
            {product.rating}
          </span>
        )}
      </div>

      {/* Specs */}
      {product.specs && Object.keys(product.specs).length > 0 && (
        <div className="grid grid-cols-2 gap-x-3 gap-y-1">
          {Object.entries(product.specs).slice(0, 6).map(([k, v]) => (
            <div key={k} className="text-xs">
              <span className="text-charcoal-500">{k.replace(/_/g, ' ')}: </span>
              <span className="text-charcoal-300">{v}</span>
            </div>
          ))}
        </div>
      )}

      {/* Why match */}
      <p className="text-xs text-emerald-400 bg-emerald-500/10 rounded-lg px-3 py-2">
        ✓ {product.why_match}
      </p>

      {/* Trade-offs */}
      {product.trade_offs && product.trade_offs.length > 0 && (
        <div>
          {product.trade_offs.slice(0, 2).map((t, i) => (
            <p key={i} className="text-xs text-charcoal-500">⚠ {t}</p>
          ))}
        </div>
      )}

      {/* View Product (searches the web) */}
      <a
        href={`https://www.google.com/search?q=${encodeURIComponent(product.name + ' buy price India')}`}
        target="_blank"
        rel="noopener noreferrer"
        className="btn-secondary text-sm py-2 flex items-center justify-center gap-2 mt-auto"
      >
        <ExternalLink className="w-3.5 h-3.5" />
        View Product
      </a>
    </div>
  )
}
