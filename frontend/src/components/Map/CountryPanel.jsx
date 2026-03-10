import { X, AlertTriangle, Zap } from 'lucide-react'
import { useStore } from '../../store/useStore'
import { GTI_COLORS } from '../../data/mockData'

export default function CountryPanel() {
  const { selectedCountry, gtiMap, setSelectedCountry, signals } = useStore()

  if (!selectedCountry) return null

  const data = gtiMap[selectedCountry]
  const countrySignals = signals.filter(s => s.affectedCountries.includes(selectedCountry))
  const colors = data ? GTI_COLORS[data.level] : GTI_COLORS.UNKNOWN

  return (
    <div className="absolute bottom-12 left-4 w-72 bg-navy-900/95 backdrop-blur-md border border-slate-700 rounded-xl shadow-2xl z-50 slide-in overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800"
           style={{ borderLeft: `3px solid ${colors.fill}` }}>
        <div>
          <p className="text-sm font-bold text-white">{data?.label || selectedCountry}</p>
          <p className="text-[10px] font-mono" style={{ color: colors.fill }}>
            {data ? `${data.level} RISK · GTI ${data.score}/100` : 'No data available'}
          </p>
        </div>
        <button
          onClick={() => setSelectedCountry(null)}
          className="text-slate-600 hover:text-slate-400 transition-colors"
        >
          <X size={14} />
        </button>
      </div>

      {/* GTI bar */}
      {data && (
        <div className="px-4 py-3 border-b border-slate-800">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono text-slate-600 uppercase">GTI Score</span>
            <span className="text-xs font-mono font-bold" style={{ color: colors.fill }}>{data.score}</span>
          </div>
          <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full rounded-full transition-all duration-700"
                 style={{ width: `${data.score}%`, backgroundColor: colors.fill }} />
          </div>
        </div>
      )}

      {/* Active signals for this country */}
      <div className="px-4 py-3">
        <p className="text-[10px] font-mono text-slate-600 uppercase tracking-wider mb-2">
          Active Signals ({countrySignals.length})
        </p>
        {countrySignals.length === 0 ? (
          <p className="text-xs text-slate-600">No active signals for this region</p>
        ) : (
          <div className="space-y-2">
            {countrySignals.map(s => (
              <div key={s.id} className="flex items-center justify-between text-xs">
                <span className="text-slate-400">{s.asset}</span>
                <span className={`font-mono font-bold ${s.direction === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                  {s.direction} {Math.round(s.confidence * 100)}%
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Analyze button */}
      <div className="px-4 pb-3">
        <button className="w-full py-2 rounded-lg bg-cyan-900/40 border border-cyan-800 text-cyan-300 text-xs font-mono font-semibold hover:bg-cyan-900/70 transition-colors flex items-center justify-center gap-2">
          <Zap size={11} />
          Run Live Analysis →
        </button>
        <p className="text-[10px] text-slate-700 text-center mt-1">
          Triggers agentic Tavily search for {selectedCountry}
        </p>
      </div>
    </div>
  )
}
