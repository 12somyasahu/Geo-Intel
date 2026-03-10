import { useStore } from '../../store/useStore'
import { SignalCard } from '../Signals/SignalCard'
import { Zap, Globe2, Sliders, AlertTriangle } from 'lucide-react'

const NARRATIVE_DIRECTION_COLORS = {
  BULLISH_GOLD:     'text-amber-400',
  BULLISH_USD:      'text-cyan-400',
  BEARISH_EQUITIES: 'text-red-400',
}

function NarrativesTab() {
  const { narratives, signals } = useStore()
  return (
    <div style={{ padding: '12px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <p style={{ fontSize: '10px', fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
        Macro Stories — {narratives.length} active clusters
      </p>
      {narratives.map(n => {
        const clusterSignals = signals.filter(s => s.cluster === n.name)
        const dirColor = NARRATIVE_DIRECTION_COLORS[n.direction] || '#94a3b8'
        return (
          <div key={n.id} style={{ borderRadius: '12px', border: '1px solid #1e293b', background: '#0f172a', padding: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
              <div>
                <p style={{ fontSize: '13px', fontWeight: 700, color: '#f1f5f9' }}>{n.name}</p>
                <p style={{ fontSize: '10px', fontFamily: 'monospace', color: '#475569', marginTop: '2px' }}>
                  {n.articleCount} articles · {clusterSignals.length} signals
                </p>
              </div>
              <span style={{ fontSize: '10px', fontFamily: 'monospace', padding: '2px 8px', borderRadius: '4px', border: '1px solid #1e293b', color: '#00b4d8', fontWeight: 700 }}>
                {n.direction.replace('_', ' ')}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <span style={{ fontSize: '10px', fontFamily: 'monospace', color: '#475569', width: '56px' }}>Strength</span>
              <div style={{ flex: 1, height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${Math.round(n.strength * 100)}%`, background: 'linear-gradient(90deg, #4f46e5, #818cf8)', borderRadius: '3px' }} />
              </div>
              <span style={{ fontSize: '12px', fontFamily: 'monospace', fontWeight: 700, color: '#818cf8' }}>{Math.round(n.strength * 100)}%</span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
              {n.countries.map(c => (
                <span key={c} style={{ fontSize: '10px', fontFamily: 'monospace', padding: '2px 6px', borderRadius: '4px', background: '#1e293b', color: '#64748b', border: '1px solid #334155' }}>
                  {c}
                </span>
              ))}
            </div>
            {clusterSignals.length > 0 && (
              <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #1e293b' }}>
                {clusterSignals.map(s => (
                  <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                    <span style={{ color: '#94a3b8' }}>{s.asset}</span>
                    <span style={{ fontFamily: 'monospace', fontWeight: 700, color: s.direction === 'BUY' ? '#4ade80' : '#f87171' }}>
                      {s.direction} · {Math.round(s.confidence * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

function WhatIfTab() {
  const { scenario, setScenarioSlider } = useStore()
  const sliders = [
    { key: 'energy_weight',   label: 'Oil Shock',    desc: 'Boosts energy events → WTI, XLE' },
    { key: 'conflict_weight', label: 'Escalation',   desc: 'Flight-to-safety → Gold, CHF' },
    { key: 'trade_weight',    label: 'Supply Chain', desc: 'Trade/logistics → shipping ETFs' },
    { key: 'cyber_weight',    label: 'Cyber Threat', desc: 'Cyber events → HACK, BUG ETFs' },
    { key: 'monetary_weight', label: 'Rate Change',  desc: 'Central bank → bonds, USD pairs' },
  ]
  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <AlertTriangle size={13} color="#fbbf24" />
          <p style={{ fontSize: '10px', fontFamily: 'monospace', color: '#fbbf24', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
            Scenario Modifiers
          </p>
        </div>
        <p style={{ fontSize: '11px', color: '#475569' }}>Sliders inject real weights into the GTI formula.</p>
      </div>
      {sliders.map(s => {
        const val = scenario[s.key]
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
      <button style={{
        width: '100%', padding: '8px', borderRadius: '8px',
        background: 'rgba(0,180,216,0.15)', border: '1px solid #0e7490',
        color: '#67e8f9', fontSize: '12px', fontFamily: 'monospace', fontWeight: 700, cursor: 'pointer'
      }}>
        Run Simulation →
      </button>
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
