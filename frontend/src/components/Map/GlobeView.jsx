import { useRef, useEffect, useState } from "react";
import Globe from "react-globe.gl";
import { MOCK_GTI } from "../../data/mockData";

const GTI_COLORS = {
  CRITICAL: "#ef4444",
  HIGH:     "#f97316",
  MEDIUM:   "#3b82f6",
  LOW:      "#22c55e",
  MINIMAL:  "#1e3a5f",
};

const ARCS = [
  { startLat: 55.75, startLng: 37.61, endLat: 50.45, endLng: 30.52, label: "RU→UA" },
  { startLat: 31.77, startLng: 35.21, endLat: 35.68, endLng: 51.38, label: "IL→IR" },
  { startLat: 39.90, startLng: 116.39, endLat: 25.03, endLng: 121.56, label: "CN→TW" },
  { startLat: 38.89, startLng: -77.03, endLat: 39.90, endLng: 116.39, label: "US→CN" },
];

const COUNTRY_CENTERS = {
  RU: { lat: 55.75, lng: 37.61, name: "Russia" },
  UA: { lat: 50.45, lng: 30.52, name: "Ukraine" },
  IL: { lat: 31.77, lng: 35.21, name: "Israel" },
  IR: { lat: 35.68, lng: 51.38, name: "Iran" },
  CN: { lat: 39.90, lng: 116.39, name: "China" },
  TW: { lat: 25.03, lng: 121.56, name: "Taiwan" },
  US: { lat: 38.89, lng: -77.03, name: "USA" },
  SA: { lat: 24.68, lng: 46.72, name: "Saudi Arabia" },
  IN: { lat: 28.61, lng: 77.20, name: "India" },
  PK: { lat: 33.72, lng: 73.06, name: "Pakistan" },
  SY: { lat: 33.51, lng: 36.29, name: "Syria" },
  IQ: { lat: 33.34, lng: 44.40, name: "Iraq" },
  MM: { lat: 19.74, lng: 96.07, name: "Myanmar" },
  ET: { lat:  9.03, lng: 38.74, name: "Ethiopia" },
  SD: { lat: 15.55, lng: 32.53, name: "Sudan" },
  YE: { lat: 15.35, lng: 44.20, name: "Yemen" },
  AF: { lat: 34.52, lng: 69.18, name: "Afghanistan" },
  KP: { lat: 39.01, lng: 125.75, name: "North Korea" },
  VE: { lat: 10.48, lng: -66.90, name: "Venezuela" },
  BR: { lat: -15.78, lng: -47.93, name: "Brazil" },
  GB: { lat: 51.50, lng: -0.12,  name: "UK" },
  DE: { lat: 52.52, lng: 13.40,  name: "Germany" },
  FR: { lat: 48.85, lng:  2.35,  name: "France" },
  JP: { lat: 35.68, lng: 139.69, name: "Japan" },
  KR: { lat: 37.56, lng: 126.97, name: "South Korea" },
};

const POINTS = Object.entries(COUNTRY_CENTERS).map(([iso, c]) => {
  const gti = MOCK_GTI[iso];
  return {
    lat: c.lat, lng: c.lng, name: c.name, iso,
    color: gti ? (GTI_COLORS[gti.level] ?? "#334155") : "#334155",
    size: gti ? Math.max(0.25, gti.score / 100 * 0.6) : 0.15,
    label: gti ? `${c.name} — GTI ${gti.score} (${gti.level})` : c.name,
  };
});

const RINGS = POINTS.filter(p => p.size > 0.35);

export default function GlobeView({ onCountryClick }) {
  const globeRef = useRef();
  const containerRef = useRef();
  const [dims, setDims] = useState({ w: 800, h: 600 });
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const obs = new ResizeObserver(entries => {
      for (const e of entries) {
        const { width, height } = e.contentRect;
        if (width > 100) setDims({ w: Math.floor(width), h: Math.floor(height) });
      }
    });
    if (containerRef.current) obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  // Delay mount slightly so React finishes layout first
  useEffect(() => {
    const t = setTimeout(() => setReady(true), 150);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    if (!globeRef.current || !ready) return;
    globeRef.current.pointOfView({ lat: 20, lng: 10, altitude: 2.5 }, 1200);
    const ctrl = globeRef.current.controls();
    ctrl.autoRotate = true;
    ctrl.autoRotateSpeed = 0.35;
    ctrl.enableDamping = true;
    ctrl.dampingFactor = 0.1;
  }, [ready]);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height: "100%", background: "#020818", overflow: "hidden" }}
    >
      {ready && (
        <Globe
          ref={globeRef}
          width={dims.w}
          height={dims.h}
          backgroundColor="#020818"
          globeImageUrl="https://unpkg.com/three-globe/example/img/earth-night.jpg"
          pointsData={POINTS}
          pointLat="lat"
          pointLng="lng"
          pointColor="color"
          pointAltitude="size"
          pointRadius={0.45}
          pointLabel="label"
          onPointClick={(d) => onCountryClick?.(d.iso)}
          ringsData={RINGS}
          ringColor={(d) => d.color}
          ringMaxRadius={4}
          ringPropagationSpeed={1.2}
          ringRepeatPeriod={900}
          arcsData={ARCS}
          arcColor={() => ["rgba(249,115,22,0.9)", "rgba(239,68,68,0.9)"]}
          arcAltitude={0.2}
          arcStroke={0.6}
          arcDashLength={0.4}
          arcDashGap={0.2}
          arcDashAnimateTime={2500}
          arcLabel={(d) => d.label}
          atmosphereColor="#1d4ed8"
          atmosphereAltitude={0.1}
          rendererConfig={{ antialias: false, alpha: false, powerPreference: "high-performance" }}
          animateIn={false}
        />
      )}
    </div>
  );
}