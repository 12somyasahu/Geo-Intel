// GTI levels: CRITICAL (75-100) | HIGH (50-74) | MEDIUM (25-49) | LOW (0-24)
// Keyed by ISO-A2 country code → used to match GeoJSON properties

export const MOCK_GTI = {
  // CRITICAL
  RU: { score: 94, level: 'CRITICAL', label: 'Russia' },
  UA: { score: 91, level: 'CRITICAL', label: 'Ukraine' },
  SD: { score: 88, level: 'CRITICAL', label: 'Sudan' },
  MM: { score: 85, level: 'CRITICAL', label: 'Myanmar' },
  YE: { score: 83, level: 'CRITICAL', label: 'Yemen' },
  SY: { score: 82, level: 'CRITICAL', label: 'Syria' },
  SS: { score: 80, level: 'CRITICAL', label: 'South Sudan' },
  AF: { score: 79, level: 'CRITICAL', label: 'Afghanistan' },
  IL: { score: 78, level: 'CRITICAL', label: 'Israel' },
  PS: { score: 78, level: 'CRITICAL', label: 'Palestine' },
  IQ: { score: 76, level: 'CRITICAL', label: 'Iraq' },

  // HIGH
  CN: { score: 72, level: 'HIGH', label: 'China' },
  IR: { score: 70, level: 'HIGH', label: 'Iran' },
  KP: { score: 68, level: 'HIGH', label: 'North Korea' },
  PK: { score: 65, level: 'HIGH', label: 'Pakistan' },
  ET: { score: 63, level: 'HIGH', label: 'Ethiopia' },
  LY: { score: 61, level: 'HIGH', label: 'Libya' },
  SO: { score: 60, level: 'HIGH', label: 'Somalia' },
  ML: { score: 58, level: 'HIGH', label: 'Mali' },
  CF: { score: 57, level: 'HIGH', label: 'Central African Republic' },
  MX: { score: 54, level: 'HIGH', label: 'Mexico' },
  VE: { score: 52, level: 'HIGH', label: 'Venezuela' },
  TW: { score: 51, level: 'HIGH', label: 'Taiwan' },
  KZ: { score: 50, level: 'HIGH', label: 'Kazakhstan' },

  // MEDIUM
  TR: { score: 48, level: 'MEDIUM', label: 'Turkey' },
  IN: { score: 46, level: 'MEDIUM', label: 'India' },
  SA: { score: 44, level: 'MEDIUM', label: 'Saudi Arabia' },
  EG: { score: 42, level: 'MEDIUM', label: 'Egypt' },
  NG: { score: 41, level: 'MEDIUM', label: 'Nigeria' },
  ZA: { score: 39, level: 'MEDIUM', label: 'South Africa' },
  AR: { score: 38, level: 'MEDIUM', label: 'Argentina' },
  BD: { score: 36, level: 'MEDIUM', label: 'Bangladesh' },
  KE: { score: 34, level: 'MEDIUM', label: 'Kenya' },
  TH: { score: 33, level: 'MEDIUM', label: 'Thailand' },
  PH: { score: 32, level: 'MEDIUM', label: 'Philippines' },
  BR: { score: 30, level: 'MEDIUM', label: 'Brazil' },
  CO: { score: 29, level: 'MEDIUM', label: 'Colombia' },
  ID: { score: 27, level: 'MEDIUM', label: 'Indonesia' },

  // LOW
  US: { score: 22, level: 'LOW', label: 'United States' },
  GB: { score: 18, level: 'LOW', label: 'United Kingdom' },
  FR: { score: 16, level: 'LOW', label: 'France' },
  DE: { score: 14, level: 'LOW', label: 'Germany' },
  JP: { score: 12, level: 'LOW', label: 'Japan' },
  CA: { score: 10, level: 'LOW', label: 'Canada' },
  AU: { score: 9,  level: 'LOW', label: 'Australia' },
  SE: { score: 8,  level: 'LOW', label: 'Sweden' },
  NO: { score: 7,  level: 'LOW', label: 'Norway' },
  CH: { score: 6,  level: 'LOW', label: 'Switzerland' },
  NZ: { score: 5,  level: 'LOW', label: 'New Zealand' },
}

export const GTI_COLORS = {
  CRITICAL: { fill: '#e84040', fillOpacity: 0.75, border: '#ff6b6b' },
  HIGH:     { fill: '#f4a261', fillOpacity: 0.65, border: '#ffd166' },
  MEDIUM:   { fill: '#457b9d', fillOpacity: 0.55, border: '#74b3ce' },
  LOW:      { fill: '#2d6a4f', fillOpacity: 0.45, border: '#52b788' },
  UNKNOWN: { fill: '#1e3a5f', fillOpacity: 0.6, border: '#2d5a8e' },
}

export const MOCK_SIGNALS = [
  {
    id: 's1',
    asset: 'WTI Crude',
    ticker: 'WTI',
    assetClass: 'Commodity',
    direction: 'BUY',
    confidence: 0.87,
    cluster: 'Energy Supply Squeeze',
    trigger: 'Russia-Ukraine pipeline disruption signals',
    affectedCountries: ['RU', 'UA', 'DE'],
    timestamp: new Date(Date.now() - 12 * 60000).toISOString(),
    cot: {
      step1: 'Fresh shelling reported near Sudzha gas transit hub, disrupting ~15% of EU gas flow.',
      step2: 'Historically, transit disruptions in 2006 and 2009 caused WTI to spike 8-12% within 72hrs.',
      step3: 'Reduced EU supply → emergency LNG procurement → elevated oil demand as substitution fuel.',
      step4: ['WTI_OIL', 'XLE', 'TTF_GAS'],
      step5: 'BUY',
      step6: 0.87,
      step7: ['Ceasefire announcement could reverse signal within hours', 'US strategic reserve release would dampen upside'],
    },
    sources: [
      { id: 'a1', title: 'Russia intensifies strikes near Ukrainian gas transit hub', source: 'Reuters', sentiment: -0.82, finbert: 'negative' },
      { id: 'a2', title: 'EU emergency energy ministers meeting called for Thursday', source: 'FT', sentiment: -0.61, finbert: 'negative' },
      { id: 'a3', title: 'LNG spot prices surge as winter storage concerns mount', source: 'Bloomberg', sentiment: -0.54, finbert: 'negative' },
    ]
  },
  {
    id: 's2',
    asset: 'Gold',
    ticker: 'XAUUSD',
    assetClass: 'Commodity',
    direction: 'BUY',
    confidence: 0.81,
    cluster: 'Middle East Escalation Arc',
    trigger: 'Multi-front regional escalation signals',
    affectedCountries: ['IL', 'IR', 'SA'],
    timestamp: new Date(Date.now() - 28 * 60000).toISOString(),
    cot: {
      step1: 'Iran-linked groups attacked Saudi Aramco facilities via drone; Israel conducted pre-dawn airstrikes in southern Lebanon.',
      step2: 'Dual-front escalation mirrors 2019 Abqaiq attack pattern — gold surged 2.3% in 48hrs post-event.',
      step3: 'Flight-to-safety capital rotation → gold, CHF, JPY. Equity risk-off pressure.',
      step4: ['XAUUSD', 'CHF_USD', 'XAGUSD'],
      step5: 'BUY',
      step6: 0.81,
      step7: ['US-brokered de-escalation', 'Dollar strengthening on rate hike expectations could cap gold upside'],
    },
    sources: [
      { id: 'a4', title: 'Drone swarm targets Aramco facility in Eastern Province', source: 'Al Jazeera', sentiment: -0.79, finbert: 'negative' },
      { id: 'a5', title: 'IDF confirms overnight strikes on Hezbollah weapons depots', source: 'Haaretz', sentiment: -0.71, finbert: 'negative' },
    ]
  },
  {
    id: 's3',
    asset: 'USD/CNH',
    ticker: 'USDCNH',
    assetClass: 'Forex',
    direction: 'BUY',
    confidence: 0.74,
    cluster: 'USD Weaponization Wave',
    trigger: 'US-China tariff escalation signals',
    affectedCountries: ['US', 'CN', 'TW'],
    timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
    cot: {
      step1: 'US Treasury announced 45% tariff on Chinese EVs; China retaliated with rare earth export curbs.',
      step2: 'Dollar weaponization pattern (sanctions/tariffs) historically strengthens USD vs CNH 1.5-3% over 2-week horizon.',
      step3: 'Capital flight from CNH → dollar-denominated assets. PBoC intervention risk caps extreme moves.',
      step4: ['USD_CNH', 'KRW_USD', 'TWD_USD'],
      step5: 'BUY',
      step6: 0.74,
      step7: ['PBoC could fix CNH stronger than expected daily', 'De-escalation talks could quickly reverse signal'],
    },
    sources: [
      { id: 'a6', title: 'Biden-era EV tariffs extended and expanded under new trade framework', source: 'WSJ', sentiment: -0.44, finbert: 'negative' },
      { id: 'a7', title: 'China restricts gallium and germanium exports in retaliatory move', source: 'SCMP', sentiment: -0.67, finbert: 'negative' },
    ]
  },
  {
    id: 's4',
    asset: 'MSCI EM',
    ticker: 'EEM',
    assetClass: 'Equity',
    direction: 'SELL',
    confidence: 0.69,
    cluster: 'USD Weaponization Wave',
    trigger: 'Dollar strength + EM capital outflow risk',
    affectedCountries: ['IN', 'BR', 'ID', 'MX'],
    timestamp: new Date(Date.now() - 67 * 60000).toISOString(),
    cot: {
      step1: 'Combined tariff escalation + hawkish Fed minutes signal prolonged dollar strength.',
      step2: 'Strong USD historically triggers 8-15% EM equity drawdown over 3-month periods (2018, 2022 analogues).',
      step3: 'Dollar strength → EM debt servicing costs rise → capital outflows → local currency depreciation → equity sell-off.',
      step4: ['EEM', 'VWO', 'IEMG'],
      step5: 'SELL',
      step6: 0.69,
      step7: ['Fed pivot could rapidly reverse EM outflows', 'Commodity-exporting EMs (Brazil) may decouple from tech-heavy EMs'],
    },
    sources: [
      { id: 'a8', title: 'Fed minutes reveal hawkish tilt, rate cuts pushed to 2026', source: 'FT', sentiment: -0.51, finbert: 'negative' },
    ]
  },
]

export const MOCK_NARRATIVES = [
  { id: 'n1', name: 'Energy Supply Squeeze',   articleCount: 14, strength: 0.91, direction: 'BEARISH_EQUITIES', countries: ['RU','UA','DE','PL'] },
  { id: 'n2', name: 'Middle East Escalation Arc', articleCount: 11, strength: 0.85, direction: 'BULLISH_GOLD',     countries: ['IL','IR','SA','LB'] },
  { id: 'n3', name: 'USD Weaponization Wave',  articleCount: 9,  strength: 0.78, direction: 'BULLISH_USD',      countries: ['US','CN','TW','KR'] },
]

export const MOCK_TICKER = [
  { id: 1, region: 'EUROPE',       severity: 'CRITICAL', text: 'Russian forces advance near Zaporizhzhia nuclear plant — IAEA monitoring elevated radiation alerts' },
  { id: 2, region: 'MIDDLE EAST',  severity: 'CRITICAL', text: 'IDF confirms overnight strikes on Hezbollah weapons depots in southern Lebanon — 3rd consecutive night' },
  { id: 3, region: 'ASIA PAC',     severity: 'HIGH',     text: 'PLA Navy conducts live-fire exercises in Taiwan Strait — 12 vessels detected in restricted zone' },
  { id: 4, region: 'S. ASIA',      severity: 'HIGH',     text: 'Pakistan-India LoC tensions: cross-border shelling reported in Kashmir sector for 2nd day' },
  { id: 5, region: 'AFRICA',       severity: 'HIGH',     text: 'Sudan RSF militia seizes Khartoum water infrastructure — UN warns of humanitarian crisis' },
  { id: 6, region: 'L. AMERICA',   severity: 'MEDIUM',   text: 'Venezuela mobilizes 15,000 troops to Guyana border amid Essequibo oil dispute' },
  { id: 7, region: 'N. AMERICA',   severity: 'MEDIUM',   text: 'US Treasury expands sanctions list targeting Russian energy sector with 34 new entities' },
  { id: 8, region: 'EUROPE',       severity: 'HIGH',     text: 'Poland activates NATO Article 4 consultation after drone incursion near Rzeszow airbase' },
  { id: 9, region: 'MIDDLE EAST',  severity: 'CRITICAL', text: 'Iran-linked drone swarm strikes Saudi Aramco facility — oil futures surge 4.2% in after-hours trading' },
  { id: 10, region: 'ASIA PAC',    severity: 'MEDIUM',   text: 'North Korea test-fires two ICBMs — trajectory indicates range capable of reaching continental US' },
]
