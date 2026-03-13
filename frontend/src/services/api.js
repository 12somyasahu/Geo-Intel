const BASE = `${import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"}/api`;

export async function fetchGTI() {
  const r = await fetch(`${BASE}/gti`);
  return r.json();
}

export async function fetchSignals() {
  const r = await fetch(`${BASE}/signals`);
  return r.json();
}

export async function fetchNarratives() {
  const r = await fetch(`${BASE}/narratives`);
  return r.json();
}

export async function fetchCountryGTI(iso) {
  const r = await fetch(`${BASE}/gti/${iso}`);
  return r.json();
}

export const fetchTicker = () => fetch(`${BASE}/ticker`).then(r => r.json());

export async function fetchAnalysis(iso) {
  const r = await fetch(`${BASE}/analyze/${iso}`);
  return r.json();
}

export async function fetchPrices(ticker) {
  const r = await fetch(`${BASE}/prices/${ticker}`);
  return r.json();
}