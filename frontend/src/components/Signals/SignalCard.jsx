import { useState } from 'react'
import { ChevronDown, ChevronRight, ExternalLink, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { useStore } from '../../store/useStore'

const ASSET_CLASS_COLORS = {
  Commodity: 'text-amber-400 bg-amber-900/30 border-amber-800',
  Forex:     'text-cyan-400 bg-cyan-900/30 border-cyan-800',
  Equity:    'text-green-400 bg-green-900/30 border-green-800',
  Bond:      'text-purple-400 bg-purple-900/30 border-purple-800',
  Crypto:    'text-pink-400 bg-pink-900/30 border-pink-800',
}

function SentimentBar({ value }) {
  // value: -1 to 1
  const pct = Math.round(Math.abs(value) * 100)
  const color = value < -0.3 ? 'bg-red-500' : value > 0.3 ? 'bg-green-500' : 'bg-slate-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className={`text-xs font-mono ${value < 0 ? 'text-red-400' : 'text-green-400'}`}>
        {value.toFixed(2)}
      </span>
    </div>
  )
}

function ExplainPanel({ signal }) {
  const [openStep, setOpenStep] = useState(null)
  const steps = [
    { key: 'step1', label: '① Event Summary',          value: signal.cot.step1 },
    { key: 'step2', label: '② Historical Precedent',   value: signal.cot.step2 },
    { key: 'step3', label: '③ Transmission Mechanism', value: signal.cot.step3 },
    { key: 'step7', label: '⑦ Risk Factors',           value: signal.cot.step7.join(' · ') },
  ]

  return (
    <div className="mt-3 space-y-1 slide-in">
      {/* Narrative cluster */}
      <div className="flex items-center gap-2 mb-3 px-3 py-2 bg-indigo-900/30 border border-indigo-800 rounded-lg">
        <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-wider">Narrative Cluster</span>
        <span className="text-xs font-semibold text-indigo-300">{signal.cluster}</span>
      </div>

      {/* CoT Steps */}
      <p className="text-[10px] font-mono text-slate-600 uppercase tracking-wider mb-2 px-1">LLM Chain-of-Thought</p>
      {steps.map(step => (
        <div key={step.key} className="rounded-lg border border-slate-800 overflow-hidden">
          <button
            onClick={() => setOpenStep(openStep === step.key ? null : step.key)}
            className="w-full flex items-center justify-between px-3 py-2 bg-slate-900 hover:bg-slate-800 transition-colors"
          >
            <span className="text-xs font-mono text-slate-400">{step.label}</span>
            {openStep === step.key
              ? <ChevronDown size={12} className="text-slate-500" />
              : <ChevronRight size={12} className="text-slate-500" />
            }
          </button>
          {openStep === step.key && (
            <div className="px-3 py-2 bg-navy-900 border-t border-slate-800">
              <p className="text-xs text-slate-300 leading-relaxed">{step.value}</p>
            </div>
          )}
        </div>
      ))}

      {/* Source articles */}
      <p className="text-[10px] font-mono text-slate-600 uppercase tracking-wider mt-3 mb-2 px-1">Source Articles</p>
      {signal.sources.map(src => (
        <div key={src.id} className="px-3 py-2 bg-slate-900 rounded-lg border border-slate-800">
          <div className="flex items-start justify-between gap-2">
            <p className="text-xs text-slate-300 leading-snug flex-1">{src.title}</p>
            <span className="flex-shrink-0 text-[10px] font-mono text-slate-500 mt-0.5">{src.source}</span>
          </div>
          <div className="mt-1.5 flex items-center gap-2">
            <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
              src.finbert === 'negative' ? 'bg-red-900/40 text-red-400' : 'bg-green-900/40 text-green-400'
            }`}>FinBERT: {src.finbert}</span>
            <div className="flex-1">
              <SentimentBar value={src.sentiment} />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export function SignalCard({ signal }) {
  const [expanded, setExpanded] = useState(false)
  const isBuy = signal.direction === 'BUY'

  const DirectionIcon = isBuy ? TrendingUp : TrendingDown
  const dirColor = isBuy ? 'text-green-400' : 'text-red-400'
  const dirBg    = isBuy ? 'bg-green-900/40 border-green-700' : 'bg-red-900/40 border-red-700'
  const confPct  = Math.round(signal.confidence * 100)

  const timeAgo = (() => {
    const diff = Date.now() - new Date(signal.timestamp)
    const m = Math.floor(diff / 60000)
    return m < 60 ? `${m}m ago` : `${Math.floor(m/60)}h ago`
  })()

  return (
    <div className={`rounded-xl border transition-colors ${
      expanded ? 'border-slate-600 bg-navy-700' : 'border-slate-800 bg-navy-800 hover:border-slate-700'
    }`}>
      {/* Header row */}
      <div className="px-4 py-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            {/* Asset + class */}
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-bold text-white">{signal.asset}</span>
              <span className="text-[10px] font-mono text-slate-500">{signal.ticker}</span>
              <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${ASSET_CLASS_COLORS[signal.assetClass]}`}>
                {signal.assetClass}
              </span>
            </div>
            {/* Trigger */}
            <p className="text-xs text-slate-400 truncate">{signal.trigger}</p>
          </div>

          {/* Direction badge */}
          <div className={`flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border ${dirBg}`}>
            <DirectionIcon size={12} className={dirColor} />
            <span className={`text-xs font-bold font-mono ${dirColor}`}>{signal.direction}</span>
          </div>
        </div>

        {/* Confidence bar */}
        <div className="mt-2.5 flex items-center gap-2">
          <span className="text-[10px] font-mono text-slate-600 uppercase tracking-wider w-20">Confidence</span>
          <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-cyan-600 to-cyan-400"
              style={{ width: `${confPct}%` }}
            />
          </div>
          <span className="text-xs font-mono font-bold text-cyan-400">{confPct}%</span>
        </div>

        {/* Footer row */}
        <div className="mt-2 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
            <span className="text-[10px] text-indigo-400 font-mono">{signal.cluster}</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[10px] text-slate-600 font-mono">{timeAgo}</span>
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1 text-[10px] font-mono text-cyan-500 hover:text-cyan-300 transition-colors"
            >
              {expanded ? 'Hide' : 'Why?'}
              {expanded ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
            </button>
          </div>
        </div>
      </div>

      {/* Explainability panel */}
      {expanded && (
        <div className="px-4 pb-4 border-t border-slate-800 pt-3">
          <ExplainPanel signal={signal} />
        </div>
      )}
    </div>
  )
}

export default SignalCard
