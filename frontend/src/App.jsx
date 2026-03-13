import { useEffect, useState } from 'react'
import { useStore } from './store/useStore'
import GeoMap from './components/Map/GeoMap'
import GlobeView from './components/Map/GlobeView'
import CountryPanel from './components/Map/CountryPanel'
import Sidebar from './components/Layout/Sidebar'
import Navbar from './components/Layout/Navbar'
import Ticker from './components/Layout/Ticker'

const LOADING_MESSAGES = [
  { ms: 0,     text: 'Connecting to intelligence backend...' },
  { ms: 4000,  text: 'Waking up Render server (first load ~40s)...' },
  { ms: 10000, text: 'Fetching live geopolitical data...' },
  { ms: 18000, text: 'Scoring conflict intensity with VADER NLP...' },
  { ms: 26000, text: 'Running transmission model...' },
  { ms: 34000, text: 'Generating market signals...' },
  { ms: 42000, text: 'Almost there...' },
]

function LoadingScreen() {
  const [msgIndex, setMsgIndex] = useState(0)
  const [elapsed, setElapsed]   = useState(0)

  useEffect(() => {
    const start = Date.now()
    const interval = setInterval(() => {
      const ms = Date.now() - start
      setElapsed(Math.floor(ms / 1000))
      const next = [...LOADING_MESSAGES].reverse().find(m => ms >= m.ms)
      if (next) setMsgIndex(LOADING_MESSAGES.indexOf(next))
    }, 500)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 99999,
      background: '#060b17',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      gap: 24,
    }}>
      {/* Logo */}
      <div style={{ textAlign: 'center', marginBottom: 8 }}>
        <p style={{ fontSize: 28, fontWeight: 800, color: '#f1f5f9', letterSpacing: '0.15em', fontFamily: 'monospace' }}>
          GEO<span style={{ color: '#00b4d8' }}>·</span>INTEL
        </p>
        <p style={{ fontSize: 11, color: '#475569', fontFamily: 'monospace', letterSpacing: '0.2em', marginTop: 4 }}>
          GEOPOLITICAL MARKET INTELLIGENCE
        </p>
      </div>

      {/* Spinner */}
      <div style={{
        width: 48, height: 48,
        border: '2px solid #1e293b',
        borderTop: '2px solid #00b4d8',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
      }} />

      {/* Message */}
      <div style={{ textAlign: 'center', maxWidth: 320 }}>
        <p style={{ fontSize: 13, color: '#67e8f9', fontFamily: 'monospace', marginBottom: 6 }}>
          {LOADING_MESSAGES[msgIndex].text}
        </p>
        <p style={{ fontSize: 11, color: '#334155', fontFamily: 'monospace' }}>
          {elapsed}s elapsed
        </p>
      </div>

      {/* Progress dots */}
      <div style={{ display: 'flex', gap: 6 }}>
        {LOADING_MESSAGES.map((_, i) => (
          <div key={i} style={{
            width: 6, height: 6, borderRadius: '50%',
            background: i <= msgIndex ? '#00b4d8' : '#1e293b',
            transition: 'background 0.3s',
          }} />
        ))}
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

export default function App() {
  const bootstrap = useStore(s => s.bootstrap)
  const gtiMap    = useStore(s => s.gtiMap)
  const [globeMode, setGlobeMode] = useState(false)
  const [ready, setReady]         = useState(false)

  useEffect(() => {
    bootstrap().then(() => setReady(true))
  }, [])

  // Show loading until GTI data arrives
  const hasData = Object.keys(gtiMap).length > 0
  if (!ready && !hasData) return <LoadingScreen />

  return (
    <div className="flex flex-col h-screen bg-navy-900 overflow-hidden">
      <Navbar />

      <div className="flex flex-1 overflow-hidden">
        <div className="relative flex-1" style={{ overflow: 'visible' }}>
          <button
            onClick={() => setGlobeMode(g => !g)}
            style={{
              position: 'absolute', top: 12, right: 12, zIndex: 1000,
              background: '#0f172a', border: '1px solid #1d4ed8',
              color: 'white', padding: '6px 14px', borderRadius: '6px',
              cursor: 'pointer', fontSize: '13px', fontWeight: 600,
              boxShadow: '0 0 12px rgba(29,78,216,0.4)',
            }}
          >
            {globeMode ? '🗺 Flat Map' : '🌍 3D Globe'}
          </button>

          {globeMode
            ? <GlobeView />
            : (<><GeoMap /><CountryPanel /></>)
          }
        </div>

        <div style={{ width: '320px', flexShrink: 0, overflowY: 'auto' }}>
          <Sidebar />
        </div>
      </div>

      <Ticker />
    </div>
  )
}