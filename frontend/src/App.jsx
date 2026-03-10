import GeoMap from './components/Map/GeoMap'
import CountryPanel from './components/Map/CountryPanel'
import Sidebar from './components/Layout/Sidebar'
import Navbar from './components/Layout/Navbar'
import Ticker from './components/Layout/Ticker'

export default function App() {
  return (
    <div className="flex flex-col h-screen bg-navy-900 overflow-hidden">
      {/* Top nav */}
      <Navbar />

      {/* Main content: map + sidebar */}
      <div className="flex flex-1 overflow-hidden">
        {/* Map area */}
        <div className="relative flex-1 overflow-hidden">
          <GeoMap />
          <CountryPanel />
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
