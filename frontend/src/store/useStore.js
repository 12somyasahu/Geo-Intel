import { create } from 'zustand'
import { MOCK_GTI, MOCK_SIGNALS, MOCK_NARRATIVES, MOCK_TICKER } from '../data/mockData'

export const useStore = create((set, get) => ({
  // ── Map state ─────────────────────────────────────────────────
  gtiMap: MOCK_GTI,
  selectedCountry: null,
  simulatedGTI: null,   // non-null when what-if is active
  setSelectedCountry: (code) => set({ selectedCountry: code }),

  // ── Signals ───────────────────────────────────────────────────
  signals: MOCK_SIGNALS,
  narratives: MOCK_NARRATIVES,
  activeSignal: null,
  setActiveSignal: (signal) => set({ activeSignal: signal }),

  // ── Ticker ────────────────────────────────────────────────────
  tickerEvents: MOCK_TICKER,

  // ── Filters ───────────────────────────────────────────────────
  filters: {
    region: 'ALL',
    assetClass: 'ALL',
  },
  setFilter: (key, val) => set(s => ({ filters: { ...s.filters, [key]: val } })),

  // ── What-If sliders ───────────────────────────────────────────
  scenario: {
    energy_weight:    1.0,
    conflict_weight:  1.0,
    trade_weight:     1.0,
    cyber_weight:     1.0,
    monetary_weight:  1.0,
  },
  setScenarioSlider: (key, val) => set(s => ({
    scenario: { ...s.scenario, [key]: val }
  })),

  // ── UI ────────────────────────────────────────────────────────
  activeTab: 'map',   // 'map' | 'signals' | 'whatif'
  setActiveTab: (tab) => set({ activeTab: tab }),
  sidebarOpen: true,
  toggleSidebar: () => set(s => ({ sidebarOpen: !s.sidebarOpen })),
}))
