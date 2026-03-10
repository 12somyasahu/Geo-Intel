import { useStore } from '../../store/useStore'
import { SignalCard } from '../Signals/SignalCard'
import { Zap, Globe2, Sliders, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react'

const NARRATIVE_DIRECTION_COLORS = {
  BULLISH_GOLD:      { text: 'text-amber-400', bg: 'bg-amber-900/30 border-amber-800' },
  BULLISH_USD:       { text: 'text-cyan-400',  bg: 'bg-cyan-900/30 border-cyan-800' },
  BEARISH_EQUITIES:  { text: 'text-red-400',   bg: 'bg-red-900/30 border-red-800' },
}

function NarrativesTab() {
  const { narratives, signals } = useStore()
  return (
    <div className="space-y-3 p-3">
      <p className="text-[10px] font-mono text-slate-600 uppercase tracking-wider px-1">
        Macro Stories — {narratives.length} active clusters
      </p>
      {narratives.map(n => {
        const clusterSignals = signals.filter(s => s.cluster === n.name)
        const colors = NARRATIVE_DIRECTION_COLORS[n.direction] || { text: 'text-slate-400', bg: 'bg-slate-800 border-slate-700' }
        return (
          <div key={n.id} className="rounded-xl border border-slate-800 bg-navy-800 p-4">
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-sm font-bold text-white">{n.name}</p>
                <p className="text-[10px] font-mono text-slate-500 mt-0.5">
                  {n.articleCount} articles · {clusterSignals.length} signals
                </p>
              </div>
              <span className={`text-[10px] font-mono px-2 py-1 rounded border font-bold ${colors.text} ${colors.bg}`}>
                {n.direction.replace('_', ' ')}
              </span>
            </div>
            {/* Strength bar */}
            <div className="flex items-center gap-2 mb-3">
              <span className="text-[10px] font-mono text-slate-600 w-14">Strength</span>
              <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-indigo-700 to-indigo-400"
                     style={{ width: `${Math.round(n.strength * 100)}%` }} />
              </div>
              <span className="text-xs font-mono font-bold text-indigo-400">{Math.round(n.strength * 100)}%</span>
            </div>
            {/* Country tags */}
            <div className="flex flex-wrap gap-1">
              {n.countries.map(c => (
                <span key={c} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                  {c}
                </span>
              ))}
            </div>
            {/* Child signals */}
            {clusterSignals.length > 0 && (
              <div className="mt-3 pt-3 border-t border-slate-800 space-y-1">
                {clusterSignals.map(s => (
                  <div key={s.id} className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">{s.asset}</span>
                    <span className={s.direction === 'BUY' ? 'text-green-400 font-mono' : 'text-red-400 font-mono'}>
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
    { key: 'energy_weight',   label: 'Oil Shock',      desc: 'Boosts energy events → WTI, XLE',       color: 'accent-amber-400' },
    { key: 'conflict_weight', label: 'Escalation',     desc: 'Flight-to-safety → Gold, CHF',           color: 'accent-red-500' },
    { key: 'trade_weight',    label: 'Supply Chain',   desc: 'Trade/logistics → shipping ETFs',         color: 'accent-blue-400' },
    { key: 'cyber_weight',    label: 'Cyber Threat',   desc: 'Cyber events → HACK, BUG ETFs',          color: 'accent-purple-400' },
    { key: 'monetary_weight', label: 'Rate Change',    desc: 'Central bank events → bonds, USD pairs', color: 'accent-cyan-400' },
  ]

  return (
    <div className="p-4 space-y-5">
      <div className="flex items-center gap-2 mb-1">
        <AlertTriangle size={13} className="text-amber-400" />
        <p className="text-[10px] font-mono text-amber-400 uppercase tracking-wider">Scenario Modifiers — wired to scoring model</p>
      </div>
      <p className="text-xs text-slate-500 -mt-2">
        These sliders inject real feature weights into the GTI formula. Not cosmetic.
      </p>

      {sliders.map(s => {
        const val = scenario[s.key]
        const pct = Math.round((val / 2) * 100)
        return (
          <div key={s.key}>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-slate-300">{s.label}</span>
              <span className={`text-xs font-mono font-bold ${val > 1.2 ? 'text-amber-400' : val < 0.8 ? 'text-blue-400' : 'text-slate-400'}`}>
                {val.toFixed(1)}×
              </span>
            </div>
            <input
              type="range" min={0} max={2} step={0.05}
              value={val}
              onChange={e => setScenarioSlider(s.key, parseFloat(e.target.value))}
              className="w-full h-1.5 rounded-lg appearance-none cursor-pointer bg-slate-800"
              style={{ accentColor: val > 1.2 ? '#f59e0b' : val < 0.8 ? '#60a5fa' : '#64748b' }}
            />
            <p className="text-[10px] text-slate-600 mt-1">{s.desc}</p>
          </div>
        )
      })}

      <button className="w-full mt-2 py-2 rounded-lg bg-cyan-900/40 border border-cyan-700 text-cyan-300 text-xs font-mono font-semibold hover:bg-cyan-900/70 transition-colors">
        Run Simulation →
      </button>
      <p className="text-[10px] text-slate-600 text-center">
        Sends POST /api/simulate · backend recomputes GTI + signals
      </p>
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

  const REGION_OPTIONS = ['ALL', 'N. AMERICA', 'EUROPE', 'ASIA PAC.', 'MIDDLE EAST', 'L. AMERICA', 'AFRICA']
  const ASSET_OPTIONS  = ['ALL', 'Equities', 'Bonds', 'Commodities', 'Forex', 'Crypto']

  return (
    <div className="w-80 flex-shrink-0 flex flex-col bg-navy-900 border-l border-slate-800 overflow-hidden">
      {/* Tab bar */}
      <div className="flex border-b border-slate-800">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 flex items-center justify-center gap-1.5 py-3 text-xs font-mono font-semibold transition-colors border-b-2 ${
              activeTab === tab.id
                ? 'border-cyan-500 text-cyan-400 bg-navy-800'
                : 'border-transparent text-slate-600 hover:text-slate-400'
            }`}
          >
            <tab.icon size={11} />
            {tab.label}
            {tab.count !== null && (
              <span className={`text-[9px] px-1 rounded ${activeTab === tab.id ? 'bg-cyan-900 text-cyan-400' : 'bg-slate-800 text-slate-600'}`}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Filter bar — only on signals tab */}
      {activeTab === 'signals' && (
        <div className="px-3 py-2 border-b border-slate-800 space-y-2">
          <div>
            <p className="text-[9px] font-mono text-slate-700 uppercase mb-1">Region</p>
            <div className="flex flex-wrap gap-1">
              {REGION_OPTIONS.map(r => (
                <button
                  key={r}
                  onClick={() => setFilter('region', r)}
                  className={`text-[9px] font-mono px-1.5 py-0.5 rounded border transition-colors ${
                    filters.region === r
                      ? 'bg-cyan-900/50 border-cyan-700 text-cyan-400'
                      : 'bg-slate-900 border-slate-800 text-slate-600 hover:text-slate-400'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>
          <div>
            <p className="text-[9px] font-mono text-slate-700 uppercase mb-1">Asset Class</p>
            <div className="flex flex-wrap gap-1">
              {ASSET_OPTIONS.map(a => (
                <button
                  key={a}
                  onClick={() => setFilter('assetClass', a)}
                  className={`text-[9px] font-mono px-1.5 py-0.5 rounded border transition-colors ${
                    filters.assetClass === a
                      ? 'bg-cyan-900/50 border-cyan-700 text-cyan-400'
                      : 'bg-slate-900 border-slate-800 text-slate-600 hover:text-slate-400'
                  }`}
                >
                  {a}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'signals' && (
          <div className="p-3 space-y-3">
            <p className="text-[10px] font-mono text-slate-600 uppercase tracking-wider px-1">
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
