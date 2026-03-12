import { useState } from 'react'
import { useStore } from '../../store/useStore'
import { SignalCard } from '../Signals/SignalCard'
import { Zap, Globe2, Sliders, AlertTriangle, Loader, TrendingUp, TrendingDown, Minus } from 'lucide-react'

const DIRECTION_STYLE = {
  BUY:     { color: '#4ade80', icon: TrendingUp,   bg: 'rgba(74,222,128,0.1)',  border: '#166534' },
  SELL:    { color: '#f87171', icon: TrendingDown,  bg: 'rgba(248,113,113,0.1)', border: '#991b1b' },
  NEUTRAL: { color: '#94a3b8', icon: Minus,         bg: 'rgba(148,163,184,0.1)', border: '#334155' },
}

function NarrativesTab() {
  const { narratives, signals } = useStore()
  return (
    <div style={{ padding: '12px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <p style={{ fontSize: '10px', fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
        Macro Stories — {narratives.length} active clusters
      </p>
      {narratives.map(n => {
        const clusterSignals = signals.filter(s => s.cluster === n.title)
        return (
          <div key={n.id} style={{ borderRadius: '12px', border: '1px solid #1e293b', background: '#0f172a', padding: '16px' }}>
            <div style={{ marginBottom: '8px' }}>
              <p style={{ fontSize: '13px', fontWeight: 700, color: '#f1f5f9' }}>{n.title}</p>
              <p style={{ fontSize: '10px', fontFamily: 'monospace', color: '#475569', marginTop: '2px' }}>
                {n.regions?.join(', ')} · {clusterSignals.length} signals
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <span style={{ fontSize: '10px', fontFamily: 'monospace', color: '#475569', width: '56px' }}>Strength</span>
              <div style={{ flex: 1, height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${Math.round(n.strength * 100)}%`, background: 'linear-gradient(90deg, #4f46e5, #818cf8)', borderRadius: '3px' }} />
              </div>
              <span style={{ fontSize: '12px', fontFamily: 'monospace', fontWeight: 700, color: '#818cf8' }}>{Math.round(n.strength * 100)}%</span>
            </div>
            <p style={{ fontSize: '11px', color: '#64748b', lineHeight: 1.5 }}>{n.summary}</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '8px' }}>
              {n.assets?.map(a => (
                <span key={a} style={{ fontSize: '10px', fontFamily: 'monospace', padding: '2px 6px', borderRadius: '4px', background: '#1e293b', color: '#64748b', border: '1px solid #334155' }}>
                  {a}
                </span>
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function WhatIfTab() {
  const { scenario, setScenarioSlider, selectedCountry } = useStore()
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState(null)

  const sliders = [
    { key: 'energy_weight',   label: 'Oil Shock',    desc: 'Boosts energy events → WTI, XLE' },
    { key: 'conflict_weight', label: 'Escalation',   desc: 'Flight-to-safety → Gold, CHF' },
    { key: 'trade_weight',    label: 'Supply Chain', desc: 'Trade/logistics → shipping ETFs' },
    { key: 'cyber_weight',    label: 'Cyber Threat', desc: 'Cyber events → HACK, BUG ETFs' },
    { key: 'monetary_weight', label: 'Rate Change',  desc: 'Central bank → bonds, USD pairs' },
  ]

  async function runSimulation() {
    if (!selectedCountry) {
      setError('Click a country on the map first')
      return
    }
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const r = await fetch(`http://127.0.0.1:8000/api/analyze/${selectedCountry}/scenario`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scenario),
      })
      const d = await r.json()
      setResult(d)
    } catch (e) {
      setError('Backend offline or request failed')
    } finally {
      setLoading(false)
    }
  }

  const sig      = result?.signal
  const dirStyle = sig ? (DIRECTION_STYLE[sig.direction] ?? DIRECTION_STYLE.NEUTRAL) : null
  const DirIcon  = dirStyle?.icon ?? Minus

  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>

      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <AlertTriangle size={13} color="#fbbf24" />
          <p style={{ fontSize: '10px', fontFamily: 'monospace', color: '#fbbf24', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
            Scenario Modifiers
          </p>
        </div>
        <p style={{ fontSize: '11px', color: selectedCountry ? '#67e8f9' : '#475569' }}>
          {selectedCountry
            ? `Target: ${selectedCountry} — adjust sliders and simulate`
            : 'Click a country on the map first'}
        </p>
      </div>

      {/* Sliders */}
      {sliders.map(s => {
        const val    = scenario[s.key]
        const isHigh = val > 1.2
        const isLow  = val < 0.8
        const color  = isHigh ? '#fbbf24' : isLow ? '#60a5fa' : '#64748b'
        return (
          <div key={s.key}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '12px', fontWeight: 600, color: '#e2e8f0' }}>{s.label}</span>
              <span style={{ fontSize: '12px', fontFamily: 'monospace', fontWeight: 700, color }}>{val.toFixed(1)}×</span>
            </div>
            <input
              type="range" min={0} max={2} step={0.05} value={val}
              onChange={e => setScenarioSlider(s.key, parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: color, cursor: 'pointer' }}
            />
            <p style={{ fontSize: '10px', color: '#334155', marginTop: '4px' }}>{s.desc}</p>
          </div>
        )
      })}

      {/* Run button */}
      <button
        onClick={runSimulation}
        disabled={loading || !selectedCountry}
        style={{
          width: '100%', padding: '8px', borderRadius: '8px',
          background: loading || !selectedCountry ? 'rgba(0,180,216,0.05)' : 'rgba(0,180,216,0.15)',
          border: '1px solid #0e7490',
          color: selectedCountry ? '#67e8f9' : '#334155',
          fontSize: '12px', fontFamily: 'monospace', fontWeight: 700,
          cursor: loading || !selectedCountry ? 'not-allowed' : 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
          transition: 'all 0.15s',
        }}
      >
        {loading
          ? <><Loader size={11} style={{ animation: 'spin 1s linear infinite' }} /> Simulating...</>
          : 'Run Simulation →'
        }
      </button>

      {/* Error */}
      {error && (
        <p style={{ fontSize: '11px', color: '#f87171', fontFamily: 'monospace' }}>{error}</p>
      )}

      {/* Result */}
      {result && sig && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>

          {/* GTI delta */}
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 12px', borderRadius: '8px', background: '#0f172a', border: '1px solid #1e293b' }}>
            <div>
              <p style={{ fontSize: '9px', fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase' }}>Scenario GTI</p>
              <p style={{ fontSize: '20px', fontWeight: 700, color: '#f1f5f9', fontFamily: 'monospace' }}>{result.gti?.score}</p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <p style={{ fontSize: '9px', fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase' }}>Delta</p>
              <p style={{ fontSize: '20px', fontWeight: 700, fontFamily: 'monospace', color: result.delta > 0 ? '#f87171' : result.delta < 0 ? '#4ade80' : '#64748b' }}>
                {result.delta > 0 ? '+' : ''}{result.delta}
              </p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <p style={{ fontSize: '9px', fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase' }}>Baseline</p>
              <p style={{ fontSize: '20px', fontWeight: 700, color: '#64748b', fontFamily: 'monospace' }}>{result.baseline_gti?.score}</p>
            </div>
          </div>

          {/* Signal badge */}
          <div style={{
            padding: '10px 12px', borderRadius: '8px',
            background: dirStyle.bg, border: `1px solid ${dirStyle.border}`,
            display: 'flex', alignItems: 'center', gap: '8px',
          }}>
            <DirIcon size={14} color={dirStyle.color} />
            <span style={{ fontSize: '13px', fontWeight: 700, color: dirStyle.color }}>{sig.direction}</span>
            <span style={{ fontSize: '12px', color: '#94a3b8' }}>{sig.asset}</span>
            <span style={{ marginLeft: 'auto', fontSize: '11px', fontFamily: 'monospace', fontWeight: 700, color: dirStyle.color }}>
              {Math.round((sig.confidence ?? 0) * 100)}%
            </span>
          </div>

          {/* Summary */}
          <p style={{ fontSize: '12px', color: '#cbd5e1', lineHeight: 1.5 }}>{sig.summary}</p>

          {/* CoT */}
          <div style={{ background: '#0f172a', borderRadius: '6px', padding: '8px 10px', border: '1px solid #1e293b' }}>
            <p style={{ fontSize: '9px', fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase', marginBottom: '4px' }}>Chain of Thought</p>
            <p style={{ fontSize: '11px', color: '#64748b', lineHeight: 1.6 }}>{sig.reasoning}</p>
          </div>

          {/* Score breakdown */}
          <div style={{ background: '#0f172a', borderRadius: '6px', padding: '8px 10px', border: '1px solid #1e293b' }}>
            <p style={{ fontSize: '9px', fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase', marginBottom: '8px' }}>Score Breakdown</p>
            {Object.entries(result.breakdown || {}).map(([cat, val]) => (
              <div key={cat} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '4px' }}>
                <span style={{ color: '#475569', textTransform: 'capitalize', fontFamily: 'monospace' }}>{cat}</span>
                <span style={{ color: val > 0 ? '#fbbf24' : '#64748b', fontFamily: 'monospace', fontWeight: 700 }}>+{val}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function Sidebar() {
  const { signals, activeTab, setActiveTab, filters, setFilter } = useStore()

  const tabs = [
    { id: 'signals',    label: 'Signals',    icon: Zap,     count: signals.length },
    { id: 'narratives', label: 'Narratives', icon: Globe2,  count: 3 },
    { id: 'whatif',     label: 'What-If',    icon: Sliders, count: null },
  ]

  const REGIONS = ['ALL', 'N. AMERICA', 'EUROPE', 'ASIA PAC.', 'MIDDLE EAST', 'L. AMERICA', 'AFRICA']
  const ASSETS  = ['ALL', 'Equities', 'Bonds', 'Commodities', 'Forex', 'Crypto']

  return (
    <div style={{
      width: '320px', flexShrink: 0, display: 'flex', flexDirection: 'column',
      background: '#080f1e', borderLeft: '1px solid #1e293b', overflow: 'hidden'
    }}>
      {/* Tab bar */}
      <div style={{ display: 'flex', borderBottom: '1px solid #1e293b' }}>
        {tabs.map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
            flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
            gap: '6px', padding: '12px 4px', fontSize: '11px', fontFamily: 'monospace',
            fontWeight: 600, cursor: 'pointer', border: 'none',
            borderBottom: activeTab === tab.id ? '2px solid #00b4d8' : '2px solid transparent',
            color: activeTab === tab.id ? '#00b4d8' : '#475569',
            background: activeTab === tab.id ? '#0f172a' : 'transparent',
            transition: 'all 0.15s',
          }}>
            <tab.icon size={11} />
            {tab.label}
            {tab.count !== null && (
              <span style={{
                fontSize: '9px', padding: '1px 5px', borderRadius: '3px',
                background: activeTab === tab.id ? 'rgba(0,180,216,0.2)' : '#1e293b',
                color: activeTab === tab.id ? '#00b4d8' : '#475569',
              }}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Filters */}
      {activeTab === 'signals' && (
        <div style={{ padding: '8px 12px', borderBottom: '1px solid #1e293b' }}>
          <div style={{ marginBottom: '8px' }}>
            <p style={{ fontSize: '9px', fontFamily: 'monospace', color: '#334155', textTransform: 'uppercase', marginBottom: '4px' }}>Region</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
              {REGIONS.map(r => (
                <button key={r} onClick={() => setFilter('region', r)} style={{
                  fontSize: '9px', fontFamily: 'monospace', padding: '2px 6px', borderRadius: '3px', cursor: 'pointer',
                  border: '1px solid', borderColor: filters.region === r ? '#0e7490' : '#1e293b',
                  background: filters.region === r ? 'rgba(0,180,216,0.15)' : 'transparent',
                  color: filters.region === r ? '#67e8f9' : '#475569',
                }}>{r}</button>
              ))}
            </div>
          </div>
          <div>
            <p style={{ fontSize: '9px', fontFamily: 'monospace', color: '#334155', textTransform: 'uppercase', marginBottom: '4px' }}>Asset Class</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
              {ASSETS.map(a => (
                <button key={a} onClick={() => setFilter('assetClass', a)} style={{
                  fontSize: '9px', fontFamily: 'monospace', padding: '2px 6px', borderRadius: '3px', cursor: 'pointer',
                  border: '1px solid', borderColor: filters.assetClass === a ? '#0e7490' : '#1e293b',
                  background: filters.assetClass === a ? 'rgba(0,180,216,0.15)' : 'transparent',
                  color: filters.assetClass === a ? '#67e8f9' : '#475569',
                }}>{a}</button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Content */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {activeTab === 'signals' && (
          <div style={{ padding: '12px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <p style={{ fontSize: '10px', fontFamily: 'monospace', color: '#334155', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              Active Signals — {signals.length} total
            </p>
            {signals.map(s => <SignalCard key={s.id} signal={s} />)}
          </div>
        )}
        {activeTab === 'narratives' && <NarrativesTab />}
        {activeTab === 'whatif'     && <WhatIfTab />}
      </div>
    </div>
  )
}