import { useEffect, useRef, useState, useCallback } from 'react'
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet'
import * as d3 from 'd3'
import { useStore } from '../../store/useStore'
import { GTI_COLORS } from '../../data/mockData'
import 'leaflet/dist/leaflet.css'

function getCountryStyle(feature, gtiMap, simulatedGTI) {
  const iso = feature.properties?.['ISO3166-1-Alpha-2']
  const data = (simulatedGTI || gtiMap)[iso]
  const colors = data ? GTI_COLORS[data.level] : GTI_COLORS.UNKNOWN
  return {
    fillColor:   colors.fill,
    fillOpacity: colors.fillOpacity,
    color:       colors.border,
    weight:      0.6,
    opacity:     0.8,
  }
}

const ARC_DATA = [
  { from: [55.75, 37.61],  to: [50.45, 30.52],  color: '#e84040' },
  { from: [31.78, 35.22],  to: [35.68, 51.39],  color: '#f4a261' },
  { from: [39.91, 116.39], to: [25.04, 121.56], color: '#f4a261' },
  { from: [24.68, 46.72],  to: [15.55, 32.53],  color: '#f4a261' },
  { from: [38.89, -77.03], to: [39.91, 116.39], color: '#457b9d' },
  { from: [51.50, -0.12],  to: [55.75, 37.61],  color: '#457b9d' },
]

function ArcSVGLayer() {
  const map = useMap()
  const svgRef = useRef(null)
  const timersRef = useRef([])

  const projectPoint = useCallback((lat, lng) => {
    const p = map.latLngToContainerPoint([lat, lng])
    return [p.x, p.y]
  }, [map])

  const drawArcs = useCallback(() => {
    if (!svgRef.current) return
    timersRef.current.forEach(clearTimeout)
    timersRef.current = []
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()
    const defs = svg.append('defs')

    ARC_DATA.forEach((arc, i) => {
      const [x1, y1] = projectPoint(arc.from[0], arc.from[1])
      const [x2, y2] = projectPoint(arc.to[0], arc.to[1])
      const mx = (x1 + x2) / 2, my = (y1 + y2) / 2
      const dx = x2 - x1, dy = y2 - y1
      const len = Math.sqrt(dx * dx + dy * dy)
      const cx = mx - (dy / len) * (len * 0.35)
      const cy = my + (dx / len) * (len * 0.35)
      const pathD = `M ${x1},${y1} Q ${cx},${cy} ${x2},${y2}`

      const gId = `g${i}`
      const grad = defs.append('linearGradient')
        .attr('id', gId).attr('gradientUnits', 'userSpaceOnUse')
        .attr('x1', x1).attr('y1', y1).attr('x2', x2).attr('y2', y2)
      grad.append('stop').attr('offset', '0%').attr('stop-color', arc.color).attr('stop-opacity', 0.05)
      grad.append('stop').attr('offset', '50%').attr('stop-color', arc.color).attr('stop-opacity', 0.9)
      grad.append('stop').attr('offset', '100%').attr('stop-color', arc.color).attr('stop-opacity', 0.05)

      svg.append('path').attr('d', pathD).attr('fill', 'none')
        .attr('stroke', arc.color).attr('stroke-width', 5).attr('stroke-opacity', 0.08)
      svg.append('path').attr('d', pathD).attr('fill', 'none')
        .attr('stroke', `url(#${gId})`).attr('stroke-width', 1.4).attr('stroke-linecap', 'round')

      const dot = svg.append('circle').attr('r', 3).attr('fill', arc.color).attr('opacity', 0)
      const pathNode = svg.append('path').attr('d', pathD).attr('fill', 'none').attr('stroke', 'none').node()

      function animateDot() {
        const pathLen = pathNode.getTotalLength()
        dot.attr('opacity', 0)
        dot.transition().duration(2600).ease(d3.easeCubicInOut)
          .attrTween('transform', () => t => {
            const p = pathNode.getPointAtLength(t * pathLen)
            return `translate(${p.x},${p.y})`
          })
          .attr('opacity', 1)
          .on('end', () => {
            dot.attr('opacity', 0)
            const t = setTimeout(animateDot, 1500 + Math.random() * 3000)
            timersRef.current.push(t)
          })
      }
      const t = setTimeout(animateDot, i * 700 + Math.random() * 1000)
      timersRef.current.push(t)
    })
  }, [projectPoint])

  useEffect(() => {
    const container = map.getContainer()
    const size = map.getSize()
    const svg = d3.select(container)
      .append('svg')
      .style('position', 'absolute').style('top', 0).style('left', 0)
      .style('pointer-events', 'none').style('z-index', 500)
      .attr('width', size.x).attr('height', size.y)
    svgRef.current = svg.node()
    drawArcs()
    const onMove = () => {
      const s = map.getSize()
      svg.attr('width', s.x).attr('height', s.y)
      drawArcs()
    }
    map.on('zoomend moveend', onMove)
    return () => {
      map.off('zoomend moveend', onMove)
      timersRef.current.forEach(clearTimeout)
      svg.remove()
      svgRef.current = null
    }
  }, [map, drawArcs])

  return null
}

function CountryLayer({ geoJson }) {
  const { gtiMap, simulatedGTI, setSelectedCountry } = useStore()
  const style = useCallback(
    (feature) => getCountryStyle(feature, gtiMap, simulatedGTI),
    [gtiMap, simulatedGTI]
  )
  const onEachFeature = useCallback((feature, layer) => {
    const iso = feature.properties?.['ISO3166-1-Alpha-2']
    const data = gtiMap[iso]
    const name = data?.label || feature.properties?.ADMIN || feature.properties?.name || iso
    layer.on({
      mouseover(e) {
        e.target.setStyle({ weight: 2, color: '#00b4d8', fillOpacity: 0.92 })
        e.target.bindTooltip(
          `<div>
            <div style="font-weight:600;font-size:14px;color:#e2e8f0">${name}</div>
            ${data
              ? `<div style="color:${GTI_COLORS[data.level].fill};font-weight:600;font-size:12px;margin-top:4px">${data.level} RISK · GTI ${data.score}</div>`
              : `<div style="color:#64748b;font-size:12px;margin-top:2px">No data</div>`}
            <div style="color:#64748b;font-size:11px;margin-top:3px">Click to analyze</div>
          </div>`,
          { className: 'country-tooltip', sticky: true, direction: 'top' }
        ).openTooltip()
      },
      mouseout(e) {
        e.target.setStyle(getCountryStyle(feature, gtiMap, simulatedGTI))
        e.target.closeTooltip()
      },
      click() { 
  console.log('clicked iso:', iso)
  setSelectedCountry(iso) 
},
    })
  }, [gtiMap, simulatedGTI, setSelectedCountry])

  if (!geoJson) return null
  return (
    <GeoJSON
      key={`${Object.keys(gtiMap).length}-${JSON.stringify(simulatedGTI)}`}
      data={geoJson}
      style={style}
      onEachFeature={onEachFeature}
    />
  )
}

export default function GeoMap() {
  const [geoJson, setGeoJson] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    fetch('/world.geojson')
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() })
      .then(data => { setGeoJson(data); setLoading(false) })
      .catch(err => {
        console.error('GeoJSON load failed:', err)
        setError('world.geojson not found — put it in frontend/public/')
        setLoading(false)
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
      {error && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-navy-900">
          <div className="text-center max-w-sm px-6">
            <p className="text-red-400 text-sm font-mono mb-2">⚠ Map data not found</p>
            <p className="text-slate-500 text-xs">{error}</p>
          </div>
        </div>
      )}
      <MapContainer
        center={[20, 10]} zoom={2.4} minZoom={2} maxZoom={6}
        style={{ width: '100%', height: '100%', background: '#060b17' }}
        zoomControl={true} worldCopyJump={false}
      >
        <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" attribution="" />
        <CountryLayer geoJson={geoJson} />
        {!loading && !error && <ArcSVGLayer />}
      </MapContainer>
    </div>
  )
}