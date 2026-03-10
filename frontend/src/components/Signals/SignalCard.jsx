import { useState } from 'react'
import { ChevronDown, ChevronRight, TrendingUp, TrendingDown } from 'lucide-react'

function SentimentBar({ value }) {
  const pct = Math.round(Math.abs(value) * 100)
  const color = value < -0.3 ? '#f87171' : value > 0.3 ? '#4ade80' : '#64748b'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <div style={{ flex: 1, height: '4px', background: '#1e293b', borderRadius: '2px', overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: '2px' }} />
      </div>
      <span style={{ fontSize: '11px', fontFamily: 'monospace', color }}>{value.toFixed(2)}</span>
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
    <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
      {/* Cluster badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 12px', background: 'rgba(99,102,241,0.15)', border: '1px solid #3730a3', borderRadius: '8px', marginBottom: '8px' }}>
        <span style={{ fontSize: '10px', fontFamily: 'monospace', color: '#818cf8', textTransform: 'uppercase' }}>Narrative Cluster</span>
        <span style={{ fontSize: '11px', fontWeight: 600, color: '#a5b4fc' }}>{signal.cluster}</span>
      </div>

      <p style={{ fontSize: '10px', fontFamily: 'monospace', color: '#334155', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '4px' }}>LLM Chain-of-Thought</p>

      {steps.map(step => (
        <div key={step.key} style={{ borderRadius: '8px', border: '1px solid #1e293b', overflow: 'hidden' }}>
          <button onClick={() => setOpenStep(openStep === step.key ? null : step.key)}
            style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: '#0f172a', border: 'none', cursor: 'pointer', color: '#64748b', fontSize: '11px', fontFamily: 'monospace' }}>
            {step.label}
            {openStep === step.key ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
          </button>
          {openStep === step.key && (
            <div style={{ padding: '8px 12px', background: '#080f1e', borderTop: '1px solid #1e293b' }}>
              <p style={{ fontSize: '11px', color: '#94a3b8', lineHeight: '1.6' }}>{step.value}</p>
            </div>
          )}
        </div>
      ))}

      <p style={{ fontSize: '10px', fontFamily: 'monospace', color: '#334155', textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: '8px', marginBottom: '4px' }}>Source Articles</p>
      {signal.sources.map(src => (
        <div key={src.id} style={{ padding: '8px 12px', background: '#0f172a', borderRadius: '8px', border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '8px', marginBottom: '6px' }}>
            <p style={{ fontSize: '11px', color: '#94a3b8', lineHeight: '1.4', flex: 1 }}>{src.title}</p>
            <span style={{ fontSize: '10px', fontFamily: 'monospace', color: '#475569', flexShrink: 0 }}>{src.source}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '10px', padding: '2px 6px', borderRadius: '4px', fontFamily: 'monospace', background: src.finbert === 'negative' ? 'rgba(239,68,68,0.2)' : 'rgba(74,222,128,0.2)', color: src.finbert === 'negative' ? '#f87171' : '#4ade80' }}>
              FinBERT: {src.finbert}
            </span>
            <div style={{ flex: 1 }}><SentimentBar value={src.sentiment} /></div>
          </div>
        </div>
      ))}
    </div>
  )
}

export function SignalCard({ signal }) {
  const [expanded, setExpanded] = useState(false)
  const isBuy = signal.direction === 'BUY'
  const confPct = Math.round(signal.confidence * 100)
  const timeAgo = (() => {
    const m = Math.floor((Date.now() - new Date(signal.timestamp)) / 60000)
    return m < 60 ? `${m}m ago` : `${Math.floor(m / 60)}h ago`
  })()

  return (
    <div style={{
      borderRadius: '12px', border: `1px solid ${expanded ? '#334155' : '#1e293b'}`,
      background: expanded ? '#0d1626' : '#0a1220', transition: 'all 0.15s'
    }}>
      <div style={{ padding: '12px 16px' }}>
        {/* Top row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px', marginBottom: '8px' }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '13px', fontWeight: 700, color: '#f1f5f9' }}>{signal.asset}</span>
              <span style={{ fontSize: '10px', fontFamily: 'monospace', color: '#475569' }}>{signal.ticker}</span>
            </div>
            <p style={{ fontSize: '11px', color: '#475569', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{signal.trigger}</p>
          </div>
          {/* Direction badge */}
          <div style={{
            flexShrink: 0, display: 'flex', alignItems: 'center', gap: '6px',
            padding: '6px 10px', borderRadius: '8px',
            background: isBuy ? 'rgba(74,222,128,0.15)' : 'rgba(248,113,113,0.15)',
            border: `1px solid ${isBuy ? '#166534' : '#991b1b'}`,
          }}>
            {isBuy ? <TrendingUp size={11} color="#4ade80" /> : <TrendingDown size={11} color="#f87171" />}
            <span style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: 700, color: isBuy ? '#4ade80' : '#f87171' }}>
              {signal.direction}
            </span>
          </div>
        </div>

        {/* Confidence bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span style={{ fontSize: '10px', fontFamily: 'monospace', color: '#334155', width: '72px' }}>Confidence</span>
          <div style={{ flex: 1, height: '4px', background: '#1e293b', borderRadius: '2px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${confPct}%`, background: 'linear-gradient(90deg, #0369a1, #00b4d8)', borderRadius: '2px' }} />
          </div>
          <span style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: 700, color: '#00b4d8' }}>{confPct}%</span>
        </div>

        {/* Footer */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#6366f1' }} />
            <span style={{ fontSize: '10px', fontFamily: 'monospace', color: '#6366f1' }}>{signal.cluster}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '10px', fontFamily: 'monospace', color: '#334155' }}>{timeAgo}</span>
            <button onClick={() => setExpanded(!expanded)} style={{
              display: 'flex', alignItems: 'center', gap: '4px',
              fontSize: '10px', fontFamily: 'monospace', color: '#00b4d8',
              background: 'none', border: 'none', cursor: 'pointer', padding: 0
            }}>
              {expanded ? 'Hide' : 'Why?'}
              {expanded ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
            </button>
          </div>
        </div>
      </div>

      {expanded && (
        <div style={{ padding: '0 16px 16px', borderTop: '1px solid #1e293b', paddingTop: '12px' }}>
          <ExplainPanel signal={signal} />
        </div>
      )}
    </div>
  )
}

export default SignalCard
