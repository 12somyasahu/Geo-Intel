import { useState } from 'react'
import { X, Zap, Loader, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { useStore } from '../../store/useStore'
import { GTI_COLORS } from '../../data/mockData'

const DIRECTION_STYLE = {
  BUY:     { color: '#4ade80', icon: TrendingUp,   bg: 'rgba(74,222,128,0.1)',  border: '#166534' },
  SELL:    { color: '#f87171', icon: TrendingDown,  bg: 'rgba(248,113,113,0.1)', border: '#991b1b' },
  NEUTRAL: { color: '#94a3b8', icon: Minus,         bg: 'rgba(148,163,184,0.1)', border: '#334155' },
}

export default function CountryPanel() {
  const { selectedCountry, gtiMap, setSelectedCountry, signals } = useStore()
  const [loading, setLoading]   = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [error, setError]       = useState(null)

  if (!selectedCountry) return null

  const data   = gtiMap[selectedCountry]
  const colors = data ? GTI_COLORS[data.level] : GTI_COLORS.UNKNOWN
  const countrySignals = signals.filter(s =>
    s.affectedCountries?.includes(selectedCountry)
  )

  async function runAnalysis() {
    setLoading(true)
    setError(null)
    setAnalysis(null)
    try {
      const r = await fetch(`http://127.0.0.1:8000/api/analyze/${selectedCountry}`)
      const d = await r.json()
      setAnalysis(d)
    } catch (e) {
      setError('Backend offline or request failed')
    } finally {
      setLoading(false)
    }
  }

  function handleClose() {
    setSelectedCountry(null)
    setAnalysis(null)
    setError(null)
  }

  const sig = analysis?.signal
  const dirStyle = sig ? (DIRECTION_STYLE[sig.direction] ?? DIRECTION_STYLE.NEUTRAL) : null
  const DirIcon  = dirStyle?.icon ?? Minus

  return (
    <div style={{
      position: 'absolute', bottom: 48, left: 16, width: 300,
      background: 'rgba(8,15,30,0.97)', backdropFilter: 'blur(12px)',
      border: '1px solid #1e293b', borderRadius: 12,
      boxShadow: '0 8px 32px rgba(0,0,0,0.6)', zIndex: 10000,
      overflow: 'hidden', maxHeight: '80vh', overflowY: 'auto',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '12px 16px', borderBottom: '1px solid #1e293b',
        borderLeft: `3px solid ${colors?.fill ?? '#334155'}`,
      }}>
        <div>
          <p style={{ fontSize: 13, fontWeight: 700, color: '#f1f5f9' }}>
            {data?.label || selectedCountry}
          </p>
          <p style={{ fontSize: 10, fontFamily: 'monospace', color: colors?.fill ?? '#64748b' }}>
            {data ? `${data.level} RISK · GTI ${data.score}/100` : 'No data'}
          </p>
        </div>
        <button onClick={handleClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#475569' }}>
          <X size={14} />
        </button>
      </div>

      {/* GTI bar */}
      {data && (
        <div style={{ padding: '12px 16px', borderBottom: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <span style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase' }}>GTI Score</span>
            <span style={{ fontSize: 12, fontFamily: 'monospace', fontWeight: 700, color: colors?.fill }}>{data.score}</span>
          </div>
          <div style={{ height: 6, background: '#1e293b', borderRadius: 3, overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${data.score}%`, background: colors?.fill, borderRadius: 3, transition: 'width 0.7s' }} />
          </div>
        </div>
      )}

      {/* Live signal result */}
      {analysis && sig && (
        <div style={{ padding: '12px 16px', borderBottom: '1px solid #1e293b' }}>
          {/* Direction badge */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10,
            padding: '8px 12px', borderRadius: 8,
            background: dirStyle.bg, border: `1px solid ${dirStyle.border}`,
          }}>
            <DirIcon size={14} color={dirStyle.color} />
            <span style={{ fontSize: 13, fontWeight: 700, color: dirStyle.color }}>{sig.direction}</span>
            <span style={{ fontSize: 12, color: '#94a3b8' }}>{sig.asset}</span>
            <span style={{ marginLeft: 'auto', fontSize: 11, fontFamily: 'monospace', fontWeight: 700, color: dirStyle.color }}>
              {Math.round((sig.confidence ?? 0) * 100)}%
            </span>
          </div>

          {/* Summary */}
          <p style={{ fontSize: 12, color: '#cbd5e1', marginBottom: 8, lineHeight: 1.5 }}>
            {sig.summary}
          </p>

          {/* Reasoning */}
          <div style={{ background: '#0f172a', borderRadius: 6, padding: '8px 10px', border: '1px solid #1e293b' }}>
            <p style={{ fontSize: 9, fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase', marginBottom: 4 }}>
              Chain of Thought
            </p>
            <p style={{ fontSize: 11, color: '#64748b', lineHeight: 1.6 }}>{sig.reasoning}</p>
          </div>

          {/* Headlines count */}
          <p style={{ fontSize: 10, color: '#334155', fontFamily: 'monospace', marginTop: 8 }}>
            Based on {analysis.headlines?.length ?? 0} live headlines · GTI {analysis.gti?.score} ({analysis.gti?.level})
          </p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{ padding: '10px 16px', color: '#f87171', fontSize: 11, borderBottom: '1px solid #1e293b' }}>
          {error}
        </div>
      )}

      {/* Existing mock signals */}
      {countrySignals.length > 0 && (
        <div style={{ padding: '10px 16px', borderBottom: '1px solid #1e293b' }}>
          <p style={{ fontSize: 10, fontFamily: 'monospace', color: '#334155', textTransform: 'uppercase', marginBottom: 6 }}>
            Cached Signals ({countrySignals.length})
          </p>
          {countrySignals.map(s => (
            <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
              <span style={{ color: '#94a3b8' }}>{s.asset}</span>
              <span style={{ fontFamily: 'monospace', fontWeight: 700, color: s.direction === 'BUY' ? '#4ade80' : '#f87171' }}>
                {s.direction} {Math.round(s.confidence * 100)}%
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Analyze button */}
      <div style={{ padding: '12px 16px' }}>
        <button
          onClick={runAnalysis}
          disabled={loading}
          style={{
            width: '100%', padding: '8px', borderRadius: 8, cursor: loading ? 'not-allowed' : 'pointer',
            background: loading ? 'rgba(0,180,216,0.05)' : 'rgba(0,180,216,0.15)',
            border: '1px solid #0e7490', color: '#67e8f9',
            fontSize: 12, fontFamily: 'monospace', fontWeight: 700,
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
            transition: 'all 0.15s',
          }}
        >
          {loading
            ? <><Loader size={11} style={{ animation: 'spin 1s linear infinite' }} /> Analyzing...</>
            : <><Zap size={11} /> Run Live Analysis →</>
          }
        </button>
        <p style={{ fontSize: 10, color: '#1e293b', textAlign: 'center', marginTop: 4, fontFamily: 'monospace' }}>
          GNews + Groq Llama 3.3 70B · live data
        </p>
      </div>
    </div>
  )
}