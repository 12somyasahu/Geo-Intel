import { Activity, Github, ExternalLink } from 'lucide-react'

export default function Navbar() {
  return (
    <header className="h-12 flex-shrink-0 bg-navy-900 border-b border-slate-800 flex items-center justify-between px-4 z-50">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-cyan-400 relative pulse-dot" />
        </div>
        <span className="text-sm font-bold tracking-wider text-white glow-cyan">GEO·INTEL</span>
        <span className="text-[10px] font-mono text-slate-600 hidden sm:block">Geopolitical Market Intelligence</span>
      </div>

      {/* GTI Legend */}
      <div className="hidden md:flex items-center gap-4">
        <span className="text-[10px] font-mono text-slate-700 uppercase">GTI Level</span>
        {[
          { label: 'CRITICAL', color: '#e84040' },
          { label: 'HIGH',     color: '#f4a261' },
          { label: 'MEDIUM',   color: '#457b9d' },
          { label: 'LOW',      color: '#2d6a4f' },
        ].map(({ label, color }) => (
          <div key={label} className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: color }} />
            <span className="text-[10px] font-mono text-slate-500">{label}</span>
          </div>
        ))}
      </div>

      {/* Right */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-[10px] font-mono text-green-400">
          <Activity size={10} />
          <span>LIVE</span>
        </div>
        <a href="https://github.com/12somyasahu" target="_blank" rel="noreferrer"
           className="text-slate-600 hover:text-slate-400 transition-colors">
          <Github size={14} />
        </a>
      </div>
    </header>
  )
}
