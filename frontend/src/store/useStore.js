import { create } from 'zustand'
import { fetchGTI, fetchSignals, fetchNarratives, fetchTicker } from '../services/api'

export const useStore = create((set, get) => ({
  // Map state
  gtiMap: {},
  selectedCountry: null,
  simulatedGTI: null,
  setSelectedCountry: (code) => set({ selectedCountry: code }),

  // Signals
  signals: [],
  narratives: [],
  activeSignal: null,
  setActiveSignal: (signal) => set({ activeSignal: signal }),

  // Ticker
  tickerEvents: [],

  // Filters
  filters: { region: 'ALL', assetClass: 'ALL' },
  setFilter: (key, val) => set(s => ({ filters: { ...s.filters, [key]: val } })),

  // What-If
  scenario: {
    energy_weight:   1.0,
    conflict_weight: 1.0,
    trade_weight:    1.0,
    cyber_weight:    1.0,
    monetary_weight: 1.0,
  },
  setScenarioSlider: (key, val) => set(s => ({
    scenario: { ...s.scenario, [key]: val }
  })),

  // UI
  activeTab: 'signals',
  setActiveTab: (tab) => set({ activeTab: tab }),
  sidebarOpen: true,
  toggleSidebar: () => set(s => ({ sidebarOpen: !s.sidebarOpen })),

  // Bootstrap — GTI loads first independently so map always has colors
  bootstrap: async () => {
    // Step 1: GTI first — map colors depend on this alone
    try {
      const gtiList = await fetchGTI()
      const gtiMap = {}
      gtiList.forEach(g => { gtiMap[g.iso] = g })
      set({ gtiMap })
    } catch (e) {
      console.warn('[bootstrap] GTI fetch failed', e)
    }

    // Step 2: Everything else — each fails silently, partial data is fine
    const [signalsResult, narrativesResult, tickerResult] = await Promise.allSettled([
      fetchSignals(),
      fetchNarratives(),
      fetchTicker(),
    ])

    if (signalsResult.status === 'fulfilled' && Array.isArray(signalsResult.value)) {
      set({ signals: signalsResult.value })
    }
    if (narrativesResult.status === 'fulfilled' && Array.isArray(narrativesResult.value)) {
      set({ narratives: narrativesResult.value })
    }
    if (tickerResult.status === 'fulfilled' && Array.isArray(tickerResult.value)) {
      set({ tickerEvents: tickerResult.value })
    }
  },
}))