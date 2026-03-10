import { useEffect, useRef, useState, useCallback } from 'react'
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet'
import * as d3 from 'd3'
import { useStore } from '../../store/useStore'
import { GTI_COLORS } from '../../data/mockData'
import 'leaflet/dist/leaflet.css'

// ── Country color logic ────────────────────────────────────────────────────
function getCountryStyle(feature, gtiMap, simulatedGTI) {
  const iso = feature.properties?.ISO_A2
  const data = (simulatedGTI || gtiMap)[iso]
  const colors = data ? GTI_COLORS[data.level] : GTI_COLORS.UNKNOWN
  return {
    fillColor:    colors.fill,
    fillOpacity:  colors.fillOpacity,
    color:        colors.border,
    weight:       0.6,
    opacity:      0.8,
  }
}

// ── Arc layer overlay (D3 SVG) ─────────────────────────────────────────────
const ARC_DATA = [
  { from: [55.75, 37.61],  to: [50.45, 30.52],  color: '#e84040', label: 'RU→UA' },   // Moscow→Kyiv
  { from: [31.78, 35.22],  to: [35.68, 51.39],  color: '#f4a261', label: 'IL→IR' },   // Jerusalem→Tehran
  { from: [39.91, 116.39], to: [25.04, 121.56], color: '#f4a261', label: 'CN→TW' },   // Beijing→Taipei
  { from: [24.68, 46.72],  to: [15.55, 32.53],  color: '#f4a261', label: 'SA→SD' },   // Riyadh→Khartoum
  { from: [38.71, -9.14],  to: [55.75, 37.61],  color: '#457b9d', label: 'EU→RU' },   // Lisbon→Moscow (sanctions)
  { from: [38.89, -77.03], to: [39.91, 116.39], color: '#457b9d', label: 'US→CN' },   // DC→Beijing (tariffs)
]

function ArcSVGLayer() {
  const map = useMap()
  const svgRef = useRef(null)

  const projectPoint = useCallback((lat, lng) => {
    const point = map.latLngToContainerPoint([lat, lng])
    return [point.x, point.y]
  }, [map])

  const drawArcs = useCallback(() => {
    if (!svgRef.current) return
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const defs = svg.append('defs')

    ARC_DATA.forEach((arc, i) => {
      const [x1, y1] = projectPoint(arc.from[0], arc.from[1])
      const [x2, y2] = projectPoint(arc.to[0], arc.to[1])

      // Control point for bezier — perpendicular midpoint elevated
      const mx = (x1 + x2) / 2
      const my = (y1 + y2) / 2
      const dx = x2 - x1
      const dy = y2 - y1
      const len = Math.sqrt(dx * dx + dy * dy)
      const cx = mx - (dy / len) * (len * 0.35)
      const cy = my + (dx / len) * (len * 0.35)

      const gradId = `arcGrad${i}`
      const grad = defs.append('linearGradient')
        .attr('id', gradId)
        .attr('gradientUnits', 'userSpaceOnUse')
        .attr('x1', x1).attr('y1', y1)
        .attr('x2', x2).attr('y2', y2)
      grad.append('stop').attr('offset', '0%').attr('stop-color', arc.color).attr('stop-opacity', 0.1)
      grad.append('stop').attr('offset', '50%').attr('stop-color', arc.color).attr('stop-opacity', 0.85)
      grad.append('stop').attr('offset', '100%').attr('stop-color', arc.color).attr('stop-opacity', 0.1)

      const pathD = `M ${x1},${y1} Q ${cx},${cy} ${x2},${y2}`

      // Glow base
      svg.append('path')
        .attr('d', pathD)
        .attr('fill', 'none')
        .attr('stroke', arc.color)
        .attr('stroke-width', 4)
        .attr('stroke-opacity', 0.12)
        .attr('filter', `blur(4px)`)

      // Main arc
      const path = svg.append('path')
        .attr('d', pathD)
        .attr('fill', 'none')
        .attr('stroke', `url(#${gradId})`)
        .attr('stroke-width', 1.5)
        .attr('stroke-linecap', 'round')

      // Animate traveling dot
      const totalLen = 300 // approximate
      const dot = svg.append('circle')
        .attr('r', 3)
        .attr('fill', arc.color)
        .attr('filter', 'blur(0.5px)')

      const pathNode = svg.append('path')
        .attr('d', pathD)
        .attr('fill', 'none')
        .attr('stroke', 'none')
        .node()

      function animateDot() {
        const pathLen = pathNode.getTotalLength()
        dot
          .attr('opacity', 0)
          .transition()
          .delay(i * 800 + Math.random() * 2000)
          .duration(2800)
          .ease(d3.easeCubicInOut)
          .attrTween('transform', () => t => {
            const p = pathNode.getPointAtLength(t * pathLen)
            return `translate(${p.x},${p.y})`
          })
          .attr('opacity', 1)
          .on('start', () => dot.attr('opacity', 0.9))
          .on('end', () => { dot.attr('opacity', 0); setTimeout(animateDot, 1500 + Math.random() * 3000) })
      }
      animateDot()
    })
  }, [projectPoint])

  useEffect(() => {
    const container = map.getContainer()
    const size = map.getSize()

    if (!svgRef.current) {
      const svg = d3.select(container)
        .append('svg')
        .attr('class', 'arc-overlay')
        .attr('width', size.x)
        .attr('height', size.y)
      svgRef.current = svg.node()
    }
    drawArcs()

    map.on('zoom move zoomend moveend', drawArcs)
    return () => {
      map.off('zoom move zoomend moveend', drawArcs)
      if (svgRef.current) svgRef.current.remove()
      svgRef.current = null
    }
  }, [map, drawArcs])

  return null
}

// ── Country interactive layer ──────────────────────────────────────────────
function CountryLayer({ geoJson }) {
  const { gtiMap, simulatedGTI, setSelectedCountry, selectedCountry } = useStore()
  const map = useMap()

  const onEachFeature = useCallback((feature, layer) => {
    const iso = feature.properties?.ISO_A2
    const data = gtiMap[iso]
    const name = data?.label || feature.properties?.ADMIN || iso

    layer.on({
      mouseover(e) {
        const l = e.target
        l.setStyle({ weight: 2, color: '#00b4d8', fillOpacity: Math.min((l.options.fillOpacity || 0.4) + 0.2, 0.95) })
        l.bindTooltip(
          `<div style="font-family:Inter,sans-serif">
            <div style="font-weight:600;font-size:14px;color:#e2e8f0">${name}</div>
            ${data
              ? `<div style="color:${GTI_COLORS[data.level].fill};font-weight:600;font-size:12px;margin-top:4px">
                  ${data.level} RISK &nbsp;·&nbsp; GTI ${data.score}
                 </div>`
              : `<div style="color:#64748b;font-size:12px">No data</div>`
            }
            <div style="color:#64748b;font-size:11px;margin-top:3px">Click to analyze</div>
          </div>`,
          { className: 'country-tooltip', sticky: true, direction: 'top' }
        ).openTooltip()
      },
      mouseout(e) {
        const style = getCountryStyle(feature, gtiMap, simulatedGTI)
        e.target.setStyle(style)
        e.target.closeTooltip()
      },
      click() {
        setSelectedCountry(iso)
      },
    })
  }, [gtiMap, simulatedGTI, setSelectedCountry])

  const style = useCallback((feature) =>
    getCountryStyle(feature, gtiMap, simulatedGTI),
  [gtiMap, simulatedGTI])

  if (!geoJson) return null
  return (
    <GeoJSON
      key={JSON.stringify(simulatedGTI)}  // re-renders when scenario changes
      data={geoJson}
      style={style}
      onEachFeature={onEachFeature}
    />
  )
}

// ── Main GeoMap export ─────────────────────────────────────────────────────
export default function GeoMap() {
  const [geoJson, setGeoJson] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Low-res world GeoJSON (110m = fast load, ~400KB)
    fetch('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson')
      .then(r => r.json())
      .then(data => { setGeoJson(data); setLoading(false) })
      .catch(() => {
        // fallback: try alternate source
        fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
          .then(r => r.json())
          .then(data => { setGeoJson(data); setLoading(false) })
      })
  }, [])

  return (
    <div className="relative w-full h-full">
      {loading && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-navy-900">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-slate-400 text-sm font-mono">Loading intelligence layer…</p>
          </div>
        </div>
      )}

      <MapContainer
        center={[20, 10]}
        zoom={2.4}
        minZoom={2}
        maxZoom={6}
        style={{ width: '100%', height: '100%', background: '#060b17' }}
        zoomControl={true}
        worldCopyJump={false}
        maxBoundsViscosity={0.8}
      >
        {/* Dark basemap tile layer */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution=""
        />

        <CountryLayer geoJson={geoJson} />
        <ArcSVGLayer />
      </MapContainer>
    </div>
  )
}
