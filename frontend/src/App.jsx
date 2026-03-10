import { useState } from 'react'
import GeoMap from './components/Map/GeoMap'
import GlobeView from './components/Map/GlobeView'
import CountryPanel from './components/Map/CountryPanel'
import Sidebar from './components/Layout/Sidebar'
import Navbar from './components/Layout/Navbar'
import Ticker from './components/Layout/Ticker'

export default function App() {
  const [globeMode, setGlobeMode] = useState(false)

  return (
    <div className="flex flex-col h-screen bg-navy-900 overflow-hidden">
      {/* Top nav */}
      <Navbar />

      {/* Main content: map + sidebar */}
      <div className="flex flex-1 overflow-hidden">

        {/* Map area */}
        <div className="relative flex-1 overflow-hidden">

          {/* Globe / Flat toggle button */}
          <button
            onClick={() => setGlobeMode(g => !g)}
            style={{
              position: 'absolute',
              top: 12,
              right: 12,
              zIndex: 1000,
              background: '#0f172a',
              border: '1px solid #1d4ed8',
              color: 'white',
              padding: '6px 14px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: 600,
              boxShadow: '0 0 12px rgba(29,78,216,0.4)',
            }}
          >
            {globeMode ? '🗺 Flat Map' : '🌍 3D Globe'}
          </button>

          {globeMode
            ? <GlobeView />
            : (
              <>
                <GeoMap />
                <CountryPanel />
              </>
            )
          }
        </div>

        {/* Right sidebar */}
        <div style={{ width: '320px', flexShrink: 0, overflowY: 'auto' }}>
          <Sidebar />
        </div>

      </div>

      {/* Bottom ticker */}
      <Ticker />
    </div>
  )
}