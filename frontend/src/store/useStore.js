import { create } from 'zustand'
import { MOCK_TICKER } from '../data/mockData'
import { fetchGTI, fetchSignals, fetchNarratives } from '../services/api'

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
  tickerEvents: MOCK_TICKER,

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

  // Bootstrap — call once on app load
  bootstrap: async () => {
    try {
      const [gtiList, signals, narratives] = await Promise.all([
        fetchGTI(),
        fetchSignals(),
        fetchNarratives(),
      ])
      // Convert GTI array to map keyed by ISO
      const gtiMap = {}
      gtiList.forEach(g => { gtiMap[g.iso] = g })
      set({ gtiMap, signals, narratives })
    } catch (e) {
      console.warn('API offline, staying on mock data', e)
    }
  },
}))