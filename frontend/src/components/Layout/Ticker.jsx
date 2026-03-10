import { useStore } from '../../store/useStore'

const SEVERITY_STYLES = {
  CRITICAL: 'bg-red-900/50 text-red-300 border-red-700',
  HIGH:     'bg-orange-900/50 text-orange-300 border-orange-700',
  MEDIUM:   'bg-blue-900/50 text-blue-300 border-blue-700',
  LOW:      'bg-green-900/50 text-green-300 border-green-700',
}

const SEVERITY_DOT = {
  CRITICAL: 'bg-red-400',
  HIGH:     'bg-orange-400',
  MEDIUM:   'bg-blue-400',
  LOW:      'bg-green-400',
}

export default function Ticker() {
  const { tickerEvents } = useStore()

  // Duplicate events for seamless infinite scroll
  const events = [...tickerEvents, ...tickerEvents]

  return (
    <div className="h-9 bg-navy-800 border-t border-slate-800 flex items-center overflow-hidden relative">
      {/* Left label */}
      <div className="flex-shrink-0 flex items-center gap-2 px-3 h-full bg-navy-900 border-r border-slate-800 z-10">
        <div className="relative w-2 h-2">
          <div className="w-2 h-2 rounded-full bg-red-400 pulse-dot" />
        </div>
        <span className="text-xs font-mono font-semibold text-red-400 uppercase tracking-widest">Live</span>
      </div>

      {/* Scrolling content */}
      <div className="overflow-hidden flex-1">
        <div className="ticker-inner flex items-center gap-8 whitespace-nowrap py-1.5">
          {events.map((event, i) => (
            <div key={`${event.id}-${i}`} className="flex items-center gap-2 flex-shrink-0">
              {/* Severity badge */}
              <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border ${SEVERITY_STYLES[event.severity]}`}>
                {event.severity}
              </span>

              {/* Region tag */}
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider">
                [{event.region}]
              </span>

              {/* Event text */}
              <span className="text-xs text-slate-300">
                {event.text}
              </span>

              {/* Separator */}
              <span className="text-slate-700 mx-2">·</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
