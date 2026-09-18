<template>
  <div class="ana-page">
    <LoadingSpinner v-if="loading" message="Putting your numbers together..." />

    <template v-else-if="error">
      <div class="empty-state">
        <i class="bi bi-exclamation-triangle"></i>
        <h2>Couldn't load your analytics</h2>
        <p>Something went wrong while fetching your data. Please try again.</p>
        <button class="btn-gold retry-btn" @click="load">Try again</button>
      </div>
    </template>

    <template v-else-if="!hotspots.length">
      <div class="empty-state">
        <i class="bi bi-bar-chart-line"></i>
        <h2>No hotspots yet</h2>
        <p>Register a hotspot to unlock business analytics.</p>
        <router-link to="/host/register" class="btn-gold retry-btn">Register a Hotspot</router-link>
      </div>
    </template>

    <template v-else>
      <!-- Header -->
      <header class="ana-header">
        <div class="ana-head-left">
          <h1>Business Analytics</h1>
          <p>What's happening with your hotspots, why it matters, and what to do next.</p>
        </div>
        <div class="ana-head-right">
          <div class="range-tabs" v-if="isOwner && selectedId === 'all'" role="tablist" aria-label="Time range">
            <button
              v-for="r in ranges"
              :key="r.value"
              class="range-tab"
              :class="{ active: range === r.value }"
              @click="setRange(r.value)"
            >{{ r.label }}</button>
          </div>
          <div class="hotspot-select">
            <i class="bi bi-geo-alt-fill"></i>
            <select v-model="selectedId" aria-label="Select hotspot" @change="onSelectHotspot">
              <option v-if="isOwner || auth.isAdmin" value="all">All hotspots</option>
              <option v-for="h in hotspots" :key="h.id" :value="h.id">{{ h.title }}</option>
            </select>
            <i class="bi bi-chevron-down"></i>
          </div>
        </div>
      </header>

      <template v-if="data">
        <!-- KPI row -->
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-icon kpi-gold"><i class="bi bi-eye"></i></span>
              <span class="kpi-label">Profile Views</span>
            </div>
            <div class="kpi-value">{{ fmt(data.kpis.profileViews) }}</div>
            <div class="kpi-delta-row">
              <span v-if="data.prev.profileViews != null" class="kpi-delta" :class="deltaClass(data.prev.profileViews, data.kpis.profileViews)">
                <i :class="deltaIcon(data.prev.profileViews, data.kpis.profileViews)"></i> {{ deltaText(data.prev.profileViews, data.kpis.profileViews) }}
              </span>
              <span v-else class="kpi-delta muted">—</span>
              <span class="kpi-hint">Travellers who opened your profile</span>
            </div>
          </div>

          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-icon kpi-brown"><i class="bi bi-search"></i></span>
              <span class="kpi-label">Search Appearances</span>
            </div>
            <div class="kpi-value">{{ data.kpis.searches != null ? fmt(data.kpis.searches) : '—' }}</div>
            <div class="kpi-delta-row">
              <span v-if="data.prev.searches != null" class="kpi-delta" :class="deltaClass(data.prev.searches, data.kpis.searches)">
                <i :class="deltaIcon(data.prev.searches, data.kpis.searches)"></i> {{ deltaText(data.prev.searches, data.kpis.searches) }}
              </span>
              <span v-else class="kpi-delta muted">{{ data.kpis.searches != null ? '—' : 'Portfolio level' }}</span>
              <span class="kpi-hint">Times listed in search results</span>
            </div>
          </div>

          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-icon kpi-tan"><i class="bi bi-telephone"></i></span>
              <span class="kpi-label">Contact / Clicks</span>
            </div>
            <div class="kpi-value">{{ data.kpis.contacts != null ? fmt(data.kpis.contacts) : '—' }}</div>
            <div class="kpi-delta-row">
              <span v-if="data.prev.contacts != null" class="kpi-delta" :class="deltaClass(data.prev.contacts, data.kpis.contacts)">
                <i :class="deltaIcon(data.prev.contacts, data.kpis.contacts)"></i> {{ deltaText(data.prev.contacts, data.kpis.contacts) }}
              </span>
              <span v-else class="kpi-delta muted">{{ data.kpis.contacts != null ? '—' : 'Portfolio level' }}</span>
              <span class="kpi-hint">Direct contact / booking requests</span>
            </div>
          </div>

          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-icon kpi-brownDark"><i class="bi bi-calendar-plus"></i></span>
              <span class="kpi-label">Itinerary Adds</span>
            </div>
            <div class="kpi-value">{{ fmt(data.kpis.adds) }}</div>
            <div class="kpi-delta-row">
              <span v-if="data.prev.adds != null" class="kpi-delta" :class="deltaClass(data.prev.adds, data.kpis.adds)">
                <i :class="deltaIcon(data.prev.adds, data.kpis.adds)"></i> {{ deltaText(data.prev.adds, data.kpis.adds) }}
              </span>
              <span v-else class="kpi-delta muted">—</span>
              <span class="kpi-hint">Saved to a traveller's trip plan</span>
            </div>
          </div>

          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-icon kpi-gold"><i class="bi bi-star-fill"></i></span>
              <span class="kpi-label">Average Rating</span>
            </div>
            <div class="kpi-value">{{ data.kpis.rating != null ? data.kpis.rating.toFixed(1) : '—' }}</div>
            <div class="kpi-delta-row">
              <span v-if="data.prev.rating != null && data.kpis.rating != null" class="kpi-delta" :class="deltaClass(data.prev.rating, data.kpis.rating)">
                <i :class="deltaIcon(data.prev.rating, data.kpis.rating)"></i> {{ ratingDeltaText(data.prev.rating, data.kpis.rating) }}
              </span>
              <span v-else class="kpi-delta muted">{{ data.kpis.rating != null ? `${data.kpis.reviews} review${data.kpis.reviews === 1 ? '' : 's'}` : 'No reviews yet' }}</span>
              <span class="kpi-hint">Across {{ data.kpis.reviews }} review{{ data.kpis.reviews === 1 ? '' : 's' }}</span>
            </div>
          </div>

          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-icon kpi-brown"><i class="bi bi-people"></i></span>
              <span class="kpi-label">Unique Visitors</span>
            </div>
            <div class="kpi-value">{{ fmt(data.kpis.visitors) }}</div>
            <div class="kpi-delta-row">
              <span v-if="data.prev.visitors != null" class="kpi-delta" :class="deltaClass(data.prev.visitors, data.kpis.visitors)">
                <i :class="deltaIcon(data.prev.visitors, data.kpis.visitors)"></i> {{ deltaText(data.prev.visitors, data.kpis.visitors) }}
              </span>
              <span v-else class="kpi-delta muted">—</span>
              <span class="kpi-hint">Distinct travellers</span>
            </div>
          </div>
        </div>

        <div class="chart-grid">
          <!-- Profile views over time: line -->
          <div class="chart-card wide">
            <div class="card-head">
              <h3>Profile Views Over Time</h3>
              <span class="card-sub">Monthly views</span>
            </div>
            <div class="chart-box"><canvas ref="timeEl"></canvas></div>
            <p class="chart-note" v-if="!hasLineData">No tracked views in this period yet. Views begin accumulating as visitors open your profiles.</p>
          </div>

          <!-- Visitor type: donut -->
          <div class="chart-card">
            <div class="card-head">
              <h3>Visitor Types</h3>
              <span class="card-sub">Local vs International</span>
            </div>
            <div class="chart-box" v-if="hasVisitorData"><canvas ref="visitorEl"></canvas></div>
            <div class="chart-empty" v-else>No visitor data yet</div>
          </div>

          <!-- Top countries: thin horizontal bar -->
          <div class="chart-card">
            <div class="card-head">
              <h3>Top Visitor Countries</h3>
              <span class="card-sub">Where visitors come from</span>
            </div>
            <div class="chart-box" v-if="hasCountryData"><canvas ref="countriesEl"></canvas></div>
            <div class="chart-empty" v-else>No country data yet</div>
          </div>

          <!-- Most active days: bar -->
          <div class="chart-card">
            <div class="card-head">
              <h3>Most Active Days</h3>
              <span class="card-sub">Weekday activity</span>
            </div>
            <div class="chart-box" v-if="hasDayData"><canvas ref="daysEl"></canvas></div>
            <div class="chart-empty" v-else>No activity data yet</div>
          </div>

          <!-- Star distribution -->
          <div class="chart-card">
            <div class="card-head">
              <h3>Rating Breakdown</h3>
              <span class="card-sub">Star distribution</span>
            </div>
            <div class="star-dist" v-if="starTotal > 0">
              <div v-for="s in [5,4,3,2,1]" :key="s" class="sd-row">
                <span class="sd-label">{{ s }}<i class="bi bi-star-fill"></i></span>
                <div class="sd-track">
                  <div class="sd-fill" :style="{ width: starPct(s) + '%' }"></div>
                </div>
                <span class="sd-count">{{ data.starDist[s] || 0 }}</span>
              </div>
            </div>
            <div class="chart-empty" v-else>No ratings yet</div>
          </div>

          <!-- Peak times: heatmap -->
          <div class="chart-card wide">
            <div class="card-head">
              <h3>Peak Visitor Times</h3>
              <span class="card-sub">Hourly activity across Morning, Afternoon &amp; Evening</span>
            </div>
            <div class="heatmap-wrap" v-if="hasHeatmap">
              <div class="hm-y-labels">
                <span v-for="row in data.heatmap" :key="row.period" class="hm-y-label">{{ row.period }}</span>
              </div>
              <div class="heatmap">
                <div class="hm-x-labels">
                  <span
                    v-for="h in 24"
                    :key="h"
                    class="hm-x-label"
                    :class="{ 'hm-x-label--major': [1, 10, 13, 19, 22].includes(h) }"
                  >{{ hourLabel(h - 1) }}</span>
                </div>
                <div class="hm-body">
                  <div class="hm-row" v-for="row in data.heatmap" :key="row.period">
                    <div
                      v-for="(v, i) in row.values"
                      :key="i"
                      class="hm-cell"
                      :style="cellStyle(v)"
                      :title="row.period + ' ' + hourLabel(i) + ': ' + v"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="chart-empty" v-else>No time-of-day data yet</div>
            <div class="hm-legend" v-if="hasHeatmap">
              <span class="hm-legend-label">Low</span>
              <span v-for="s in 5" :key="s" class="hm-legend-cell" :style="cellStyle((maxAdds / 5) * s, true)"></span>
              <span class="hm-legend-label">High</span>
            </div>
          </div>

          <!-- Top performing hotspots -->
          <div class="chart-card wide">
            <div class="card-head">
              <h3>Top Performing Hotspots</h3>
              <span class="card-sub">Your experiences ranked by engagement</span>
            </div>
            <div class="perf-list" v-if="ranked.length">
              <div v-for="(p, i) in ranked" :key="i" class="perf-row">
                <span class="perf-rank" :class="'rank-' + (i + 1)">{{ i + 1 }}</span>
                <div class="perf-main">
                  <span class="perf-title">{{ p.title }}</span>
                  <span class="perf-cat">{{ p.category }}</span>
                </div>
                <div class="perf-bar-wrap">
                  <div class="perf-bar" :style="{ width: perfWidth(p) + '%' }"></div>
                </div>
                <div class="perf-metrics">
                  <span class="perf-metric"><i class="bi bi-eye"></i>{{ fmt(p.views) }}</span>
                  <span class="perf-metric" v-if="p.searches != null"><i class="bi bi-search"></i>{{ fmt(p.searches) }}</span>
                  <span class="perf-metric"><i class="bi bi-star-fill"></i>{{ p.avg_rating != null ? p.avg_rating.toFixed(1) : '—' }}</span>
                </div>
                <span class="perf-trend" :class="trendClass(p)">{{ trendLabel(p) }}</span>
              </div>
            </div>
            <div class="chart-empty" v-else>No engagement data yet</div>
          </div>

          <!-- Recent reviews -->
          <div class="chart-card wide">
            <div class="card-head">
              <h3>Recent Reviews</h3>
              <span class="card-sub">Latest feedback from travellers</span>
            </div>
            <div class="review-list" v-if="data.recentReviews.length">
              <div v-for="r in data.recentReviews" :key="r.id" class="review-item">
                <div class="review-avatar">{{ (r.user_name || '?').charAt(0) }}</div>
                <div class="review-main">
                  <div class="review-top">
                    <span class="review-name">{{ r.user_name || 'Anonymous' }}</span>
                    <span class="review-stars">
                      <i v-for="s in 5" :key="s" class="bi bi-star-fill" :class="{ filled: s <= r.score, empty: s > r.score }"></i>
                    </span>
                  </div>
                  <span class="review-exp">{{ r.experience_title }}</span>
                  <p class="review-comment" v-if="r.comment">{{ r.comment }}</p>
                </div>
                <span class="review-date">{{ formatDate(r.created_at) }}</span>
              </div>
            </div>
            <div class="chart-empty" v-else>No reviews yet — travellers who add your hotspots can leave ratings.</div>
          </div>
        </div>

        <!-- Business insights -->
        <section class="insights-section" v-if="insights.length">
          <div class="card-head insights-head">
            <h3><i class="bi bi-graph-up"></i> Business Insights</h3>
            <span class="card-sub">Why it matters — auto-detected from your data</span>
          </div>
          <div class="insights-grid">
            <div v-for="(insight, idx) in insights" :key="idx" class="insight-card" :class="'insight-' + insight.type">
              <div class="insight-icon"><i :class="['bi', insight.icon]"></i></div>
              <div class="insight-content">
                <h4>{{ insight.title }}</h4>
                <p>{{ insight.message }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Recommendations -->
        <section class="rec-section" ref="recSection" v-if="recommendations.length">
          <div class="card-head rec-head">
            <h3><i class="bi bi-lightbulb"></i> What to do next</h3>
            <span class="card-sub">{{ recommendations.length }} recommendation{{ recommendations.length === 1 ? '' : 's' }} · based on your current data</span>
          </div>
          <div class="rec-grid">
            <div v-for="(rec, idx) in recommendations" :key="idx" class="rec-card" :class="'rec-' + rec.type">
              <div class="rec-icon"><i :class="['bi', rec.icon]"></i></div>
              <div class="rec-body">
                <h4>{{ rec.title }}</h4>
                <p class="rec-action">{{ rec.action }}</p>
                <div class="rec-why">
                  <span class="rec-why-label"><i class="bi bi-info-circle"></i> Why this recommendation</span>
                  <p>{{ rec.why }}</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </template>

      <p class="note-foot" v-if="data">
        Profile views, search appearances and contact clicks are tracked from visitor activity. Itinerary adds measure how often travellers save your hotspots to a trip plan.
      </p>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import { useExperienceStore } from '../stores/experience'
import { useAuthStore } from '../stores/auth'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const store = useExperienceStore()
const auth = useAuthStore()

const loading = ref(true)
const error = ref(false)
const hotspots = ref([])
const selectedId = ref(null)
const range = ref('all')
const data = ref(null)
const recommendations = ref([])
const recSection = ref(null)
const maxAdds = ref(1)

const timeEl = ref(null)
const visitorEl = ref(null)
const countriesEl = ref(null)
const daysEl = ref(null)

const PALETTE = {
  gold: '#E8A200',
  goldDark: '#B57912',
  brown: '#8B5A2B',
  brownDark: '#5C3A21',
  brownMid: '#A67C52',
  tan: '#C9A227',
  cream: '#F6F0E3',
}
const TEXT_COLOR = '#6B6150'
const GRID_COLOR = 'rgba(139, 90, 43, 0.12)'
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

function normalizeActiveDays(raw) {
  const counts = {}
  for (const d of raw || []) {
    if (d && typeof d === 'object' && d.day && typeof d.count === 'number') {
      counts[d.day] = (counts[d.day] || 0) + d.count
    }
  }
  return DAY_NAMES.map(day => ({ day, count: counts[day] || 0 }))
}

const isOwner = computed(() => auth.isBusinessOwner)
const ranges = [
  { value: '7d', label: '7D' },
  { value: '30d', label: '30D' },
  { value: '90d', label: '90D' },
  { value: '180d', label: '6M' },
  { value: '365d', label: '12M' },
  { value: 'all', label: 'All' },
]

let charts = []

function destroyCharts() {
  charts.forEach(c => c.destroy())
  charts = []
}

function fmt(n) {
  if (n == null) return '—'
  return Number(n).toLocaleString('en-ZA')
}

function hourLabel(h) {
  return h === 0 ? '12am' : h < 12 ? `${h}am` : h === 12 ? '12pm' : `${h - 12}pm`
}

function shortDate(d) {
  const parts = d.split('-')
  return parts.length === 3 ? `${parts[1]}/${parts[2]}` : d
}

function formatDate(d) {
  if (!d) return ''
  const date = new Date(d)
  return date.toLocaleDateString('en-ZA', { day: 'numeric', month: 'short', year: 'numeric' })
}

function cellStyle(v, legend = false) {
  const ratio = Math.max(0, Math.min(1, v / Math.max(1, maxAdds.value)))
  if (ratio <= 0.001) return { backgroundColor: 'rgba(139, 90, 43, 0.08)' }
  const base = [181, 121, 18]
  const light = [248, 228, 180]
  const r = Math.round(light[0] + (base[0] - light[0]) * ratio)
  const g = Math.round(light[1] + (base[1] - light[1]) * ratio)
  const b = Math.round(light[2] + (base[2] - light[2]) * ratio)
  return { backgroundColor: `rgb(${r},${g},${b})` }
}

/* ── KPI helpers ─────────────────────────────── */
function deltaInfo(prev, cur) {
  if (prev == null || cur == null || prev === 0) return null
  const diff = cur - prev
  const pct = Math.round((diff / Math.abs(prev)) * 100)
  return { up: diff >= 0, diff, pct: Math.abs(pct) }
}
function deltaText(prev, cur) {
  const d = deltaInfo(prev, cur)
  if (!d) return ''
  return `${d.up ? '+' : '−'}${d.pct}%`
}
function ratingDeltaText(prev, cur) {
  const d = deltaInfo(prev, cur)
  if (!d) return ''
  return `${d.up ? '+' : '−'}${Math.abs(d.diff).toFixed(1)}`
}
function deltaIcon(prev, cur) {
  const d = deltaInfo(prev, cur)
  return d ? (d.up ? 'bi-arrow-up-short' : 'bi-arrow-down-short') : ''
}
function deltaClass(prev, cur) {
  const d = deltaInfo(prev, cur)
  if (!d) return 'muted'
  return d.up ? 'up' : 'down'
}

/* ── Trend / performance helpers ─────────────── */
function trendLabel(p) {
  if (!p) return '—'
  if (p.trend === 'improving') return 'Improving'
  if (p.trend === 'declining') return 'Declining'
  if (p.trend === 'no ratings') return 'No ratings'
  return 'Stable'
}
function trendClass(p) {
  if (!p) return ''
  if (p.trend === 'improving') return 'up'
  if (p.trend === 'declining') return 'down'
  if (p.trend === 'no ratings') return 'muted'
  return 'stable'
}
function perfWidth(p) {
  const max = Math.max(1, ...(data.value.performance || []).map(x => x.views || 0))
  return Math.max(4, Math.round((p.views / max) * 100))
}

const ranked = computed(() => (data.value?.performance || []).filter(p => p.views > 0 || p.reviews > 0))
const starTotal = computed(() => {
  const d = data.value?.starDist || {}
  return Object.values(d).reduce((a, b) => a + b, 0)
})
function starPct(s) {
  if (starTotal.value === 0) return 0
  return Math.round(((data.value.starDist[s] || 0) / starTotal.value) * 100)
}

const hasLineData = computed(() => (data.value?.line || []).length > 0)
const hasVisitorData = computed(() => (data.value?.visitorTypes || []).some(v => v.count > 0))
const hasCountryData = computed(() => (data.value?.topCountries || []).length > 0)
const hasDayData = computed(() => (data.value?.activeDays || []).some(d => d.count > 0))
const hasHeatmap = computed(() => (data.value?.heatmap || []).length > 0)

/* ── Data loading ────────────────────────────── */
async function load() {
  loading.value = true
  error.value = false
  recommendations.value = []
  try {
    if (isOwner.value) {
      hotspots.value = (await store.fetchMyExperiences()) || []
      selectedId.value = hotspots.value.length ? 'all' : null
    } else if (auth.isAdmin) {
      hotspots.value = (await store.fetchExperiences()) || []
      selectedId.value = hotspots.value.length ? 'all' : null
    } else {
      hotspots.value = (await store.fetchExperiences()) || []
      selectedId.value = hotspots.value.length ? hotspots.value[0].id : null
    }
    if (hotspots.value.length) await loadPortfolio()
  } catch (e) {
    console.error('Failed to load analytics', e)
    error.value = true
  }
  loading.value = false
}

async function loadPortfolio() {
  try {
    if (selectedId.value === 'all') {
      const ids = hotspots.value.map(h => h.id)
      const analyticsList = await Promise.all(ids.map(id => store.getHotspotAnalytics(id)))
      const agg = aggregateVisitor(analyticsList)
      if (isOwner.value) {
        const ov = await store.getAnalytics(range.value)
        data.value = buildFromOverview(ov, agg)
      } else {
        data.value = buildFromAggregate(agg, analyticsList, hotspots.value)
      }
    } else {
      const id = selectedId.value
      const [ha, ratings] = await Promise.all([
        store.getHotspotAnalytics(id),
        store.getRatings(id),
      ])
      data.value = buildFromHotspot(ha, ratings)
    }
    maxAdds.value = Math.max(1, ...(data.value.heatmap || []).flatMap(r => r.values || []))
    recommendations.value = buildRecommendations()
    await nextTick()
    renderCharts()
  } catch (e) {
    console.error('Failed to load analytics portfolio', e)
    error.value = true
  }
}

function aggregateVisitor(analyticsList) {
  const visitorTypes = {}
  const countries = {}
  const heatmapMap = {}
  const viewsOverTime = {}

  for (const ha of analyticsList) {
    for (const vt of ha.visitor_types || []) {
      visitorTypes[vt.type] = (visitorTypes[vt.type] || 0) + vt.count
    }
    for (const tc of ha.top_countries || []) {
      countries[tc.country] = (countries[tc.country] || 0) + tc.count
    }
    for (const row of ha.peak_heatmap || []) {
      if (!heatmapMap[row.period]) heatmapMap[row.period] = new Array(24).fill(0)
      heatmapMap[row.period] = heatmapMap[row.period].map((v, i) => v + (row.values[i] || 0))
    }
    for (const v of ha.views_over_time || []) {
      const date = v.date || v.period
      if (!date) continue
      viewsOverTime[date] = (viewsOverTime[date] || 0) + (v.count || 0)
    }
  }

  return {
    visitorTypes: Object.entries(visitorTypes).map(([type, count]) => ({ type, count })),
    topCountries: Object.entries(countries).map(([country, count]) => ({ country, count })).sort((a, b) => b.count - a.count),
    activeDays: normalizeActiveDays(analyticsList.flatMap(ha => ha.active_days || [])),
    heatmap: Object.entries(heatmapMap).map(([period, values]) => ({ period, values })),
    viewsOverTime: Object.entries(viewsOverTime)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => a.date.localeCompare(b.date)),
  }
}

function buildFromOverview(ov, agg) {
  return {
    kpis: {
      profileViews: ov.total_profile_views,
      searches: ov.total_searches,
      contacts: ov.total_contacts,
      adds: ov.total_views,
      visitors: ov.unique_visitors,
      rating: ov.avg_rating || null,
      reviews: ov.total_reviews,
    },
    prev: {
      profileViews: ov.prev_total_profile_views,
      searches: ov.prev_total_searches,
      contacts: ov.prev_total_contacts,
      adds: ov.prev_total_views,
      visitors: ov.prev_unique_visitors,
      rating: ov.prev_avg_rating || null,
    },
    line: (ov.profile_views_over_time || []).length ? ov.profile_views_over_time : ov.interest_over_time,
    lineLabel: (ov.profile_views_over_time || []).length ? 'Profile views' : 'Itinerary adds',
    visitorTypes: agg.visitorTypes,
    topCountries: agg.topCountries,
    activeDays: agg.activeDays,
    heatmap: agg.heatmap,
    performance: ov.experience_performance || [],
    recentReviews: ov.recent_reviews || [],
    starDist: ov.star_distribution || {},
  }
}

function buildFromAggregate(agg, analyticsList, hotspotList) {
  const meta = {}
  for (const h of hotspotList || []) meta[h.id] = h
  const adds = analyticsList.reduce((s, ha) => s + (ha.total_itinerary_adds || 0), 0)
  const visitors = analyticsList.reduce((s, ha) => s + (ha.unique_visitors || 0), 0)
  const performance = analyticsList
    .map(ha => ({
      id: ha.experience_id,
      title: ha.title,
      category: (meta[ha.experience_id] && meta[ha.experience_id].category) || 'Hotspot',
      views: ha.total_itinerary_adds || 0,
      searches: null,
      contacts: null,
      reviews: 0,
      avg_rating: null,
      trend: 'stable',
    }))
    .sort((a, b) => b.views - a.views)
  return {
    kpis: { profileViews: adds, searches: null, contacts: null, adds, visitors, rating: null, reviews: 0 },
    prev: { profileViews: null, searches: null, contacts: null, adds: null, visitors: null, rating: null },
    line: (agg.viewsOverTime || []).map(v => ({ period: v.date, count: v.count })),
    lineLabel: 'Itinerary adds',
    visitorTypes: agg.visitorTypes,
    topCountries: agg.topCountries,
    activeDays: agg.activeDays,
    heatmap: agg.heatmap,
    performance,
    recentReviews: [],
    starDist: {},
  }
}

function buildFromHotspot(ha, ratings) {
  const count = ratings.length
  const avg = count ? Math.round((ratings.reduce((s, r) => s + r.score, 0) / count) * 10) / 10 : null
  const starDist = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }
  ratings.forEach(r => { starDist[r.score] = (starDist[r.score] || 0) + 1 })
  const performance = (ha.top_services || []).map(s => ({
    id: s.id,
    title: s.title,
    category: 'Hotspot',
    views: s.views || 0,
    searches: null,
    contacts: null,
    reviews: 0,
    avg_rating: null,
    trend: 'stable',
  }))
  if (performance.length === 0) {
    performance.push({ id: ha.experience_id, title: ha.title, category: 'Hotspot', views: ha.total_itinerary_adds || 0, searches: null, contacts: null, reviews: count, avg_rating: avg, trend: 'stable' })
  }
  return {
    kpis: { profileViews: null, searches: null, contacts: null, adds: ha.total_itinerary_adds || 0, visitors: ha.unique_visitors || 0, rating: avg, reviews: count },
    prev: { profileViews: null, searches: null, contacts: null, adds: null, visitors: null, rating: null },
    line: (ha.views_over_time || []).map(v => ({ period: v.date || v.period, count: v.count })),
    lineLabel: 'Itinerary adds',
    visitorTypes: ha.visitor_types || [],
    topCountries: ha.top_countries || [],
    activeDays: normalizeActiveDays(ha.active_days),
    heatmap: ha.peak_heatmap || [],
    performance,
    recentReviews: ratings.slice(0, 10).map(r => ({
      id: r.id,
      user_name: r.user_name,
      experience_title: ha.title,
      score: r.score,
      comment: r.comment,
      created_at: r.created_at,
    })),
    starDist,
  }
}

/* ── Line series bucketing (Day / Week / Month) ── */
function bucketSeries(series, mode) {
  const map = new Map()
  for (const p of series) {
    const parts = String(p.period || p.date || '').split('-').map(Number)
    if (parts.length < 3 || parts.some(Number.isNaN)) continue
    const [y, m, d] = parts
    const date = new Date(y, m - 1, d)
    let key
    let label
    if (mode === 'day') {
      key = p.period || p.date
      label = `${m}/${d}`
    } else if (mode === 'week') {
      const monday = new Date(date)
      monday.setDate(date.getDate() - ((date.getDay() + 6) % 7))
      key = `${monday.getFullYear()}-${monday.getMonth() + 1}-${monday.getDate()}`
      label = `w/c ${monday.getDate()} ${MONTHS[monday.getMonth()]}`
    } else {
      key = p.period.slice(0, 7)
      label = new Date(y, m - 1, 1).toLocaleString('en-US', { month: 'long' })
    }
    const cur = map.get(key) || { label, count: 0 }
    cur.count += p.count
    map.set(key, cur)
  }
  const items = [...map.values()]
  return { labels: items.map(v => v.label), counts: items.map(v => v.count) }
}

/* ── Charts ─────────────────────────────────── */
function baseOptions(xTitle = '', yTitle = '') {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: TEXT_COLOR, font: { size: 11 } } },
      tooltip: { backgroundColor: '#2C2416', titleColor: '#F6F0E3', bodyColor: '#F6F0E3' },
    },
    scales: {
      x: {
        title: { display: !!xTitle, text: xTitle, color: TEXT_COLOR, font: { size: 11, weight: 600 } },
        ticks: { color: TEXT_COLOR, font: { size: 10 }, maxTicksLimit: 12 },
        grid: { color: GRID_COLOR },
      },
      y: {
        beginAtZero: true,
        title: { display: !!yTitle, text: yTitle, color: TEXT_COLOR, font: { size: 11, weight: 600 } },
        ticks: { color: TEXT_COLOR, precision: 0, font: { size: 10 } },
        grid: { color: GRID_COLOR },
      },
    },
  }
}

function renderCharts() {
  destroyCharts()
  if (!data.value) return

  // 1. Profile views over time (line)
  if (timeEl.value && (data.value.line || []).length) {
    const { labels, counts } = bucketSeries(data.value.line, 'month')
    charts.push(new Chart(timeEl.value, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: data.value.lineLabel,
          data: counts,
          borderColor: PALETTE.gold,
          backgroundColor: 'rgba(232,162,0,0.15)',
          fill: true,
          tension: 0.35,
          pointBackgroundColor: PALETTE.goldDark,
          pointBorderColor: PALETTE.cream,
          pointRadius: labels.length > 30 ? 2 : 4,
          pointHoverRadius: 6,
          borderWidth: 2.5,
        }],
      },
      options: baseOptions('', data.value.lineLabel),
    }))
  }

  // 2. Visitor type (donut)
  const vt = (data.value.visitorTypes || []).filter(v => v.count > 0)
  if (visitorEl.value && vt.length) {
    charts.push(new Chart(visitorEl.value, {
      type: 'doughnut',
      data: {
        labels: vt.map(v => v.type),
        datasets: [{
          data: vt.map(v => v.count),
          backgroundColor: [PALETTE.gold, PALETTE.brownMid],
          borderColor: PALETTE.cream,
          borderWidth: 3,
          hoverOffset: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: TEXT_COLOR, font: { size: 12 }, padding: 14, boxWidth: 14, boxHeight: 14 } },
          tooltip: { backgroundColor: '#2C2416', titleColor: '#F6F0E3', bodyColor: '#F6F0E3' },
        },
      },
    }))
  }

  // 3. Top countries (thin horizontal bar)
  const tc = data.value.topCountries || []
  if (countriesEl.value && tc.length) {
    charts.push(new Chart(countriesEl.value, {
      type: 'bar',
      data: {
        labels: tc.map(c => c.country),
        datasets: [{
          data: tc.map(c => c.count),
          backgroundColor: tc.map((_, i) => (i === 0 ? PALETTE.gold : i === 1 ? PALETTE.tan : PALETTE.brownMid)),
          borderRadius: 5,
          maxBarThickness: 14,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { backgroundColor: '#2C2416', titleColor: '#F6F0E3', bodyColor: '#F6F0E3' },
        },
        scales: {
          x: { beginAtZero: true, ticks: { color: TEXT_COLOR, precision: 0, font: { size: 10 } }, grid: { color: GRID_COLOR } },
          y: { grid: { display: false }, ticks: { color: TEXT_COLOR, font: { size: 11 } } },
        },
      },
    }))
  }

  // 4. Most active days (bar)
  const ad = (data.value.activeDays || []).filter(d => d && d.day && d.count > 0)
  if (daysEl.value && ad.length) {
    charts.push(new Chart(daysEl.value, {
      type: 'bar',
      data: {
        labels: ad.map(d => d.day.slice(0, 3)),
        datasets: [{
          label: 'Activity',
          data: ad.map(d => d.count),
          backgroundColor: [PALETTE.gold, PALETTE.tan, PALETTE.brownMid, PALETTE.brown, PALETTE.goldDark, PALETTE.brownDark, PALETTE.tan],
          borderRadius: 5,
          maxBarThickness: 32,
        }],
      },
      options: baseOptions('Day of week', 'Views'),
    }))
  }
}

/* ── Insights (auto, why it matters) ─────────── */
function buildInsights() {
  const out = []
  const d = data.value
  if (!d) return out
  const push = (type, icon, title, message) => { if (out.length < 6) out.push({ type, icon, title, message }) }

  const perf = (d.performance || []).filter(p => p.views > 0)
  const series = d.line || []

  // Strength: top performer
  if (perf.length) {
    const top = perf[0]
    push('success', 'bi-trophy-fill', 'Your star performer',
      `"${top.title}" is your most-engaged hotspot with ${fmt(top.views)} itinerary adds${top.avg_rating ? ` and a ${top.avg_rating.toFixed(1)}★ rating` : ''}.`)
  }

  // Strength/weakness: rating health
  if (d.kpis.rating != null && d.kpis.reviews > 0) {
    if (d.kpis.rating >= 4.5) {
      push('success', 'bi-star-fill', 'Excellent guest ratings',
        `Your average rating of ${d.kpis.rating.toFixed(1)}★ across ${d.kpis.reviews} reviews is outstanding — keep delivering what you're doing.`)
    } else if (d.kpis.rating < 3.5) {
      push('danger', 'bi-exclamation-triangle', 'Ratings need attention',
        `Your average rating is ${d.kpis.rating.toFixed(1)}★. Address the recurring feedback in your recent reviews to protect bookings.`)
    }
  }

  // Conversion gap (owner-level data only)
  if (d.kpis.profileViews != null && d.kpis.profileViews > 0 && d.kpis.adds != null) {
    const conv = Math.round((d.kpis.adds / d.kpis.profileViews) * 100)
    if (conv < 35) {
      push('warning', 'bi-arrow-down-right-circle', "Visitors look but don't save",
        `${fmt(d.kpis.profileViews)} profile views produced only ${fmt(d.kpis.adds)} itinerary adds (${conv}% conversion). Your listing or offer isn't compelling enough at the decision point.`)
    }
  }

  // Trend
  if (series.length >= 4) {
    const half = Math.floor(series.length / 2)
    const first = series.slice(0, half).reduce((s, p) => s + p.count, 0) / half
    const second = series.slice(half).reduce((s, p) => s + p.count, 0) / (series.length - half)
    if (second > first * 1.25) {
      push('opportunity', 'bi-graph-up-arrow', 'Interest is rising',
        `Average daily engagement grew from ${Math.round(first)} to ${Math.round(second)} — momentum you can ride right now.`)
    } else if (second < first * 0.75) {
      push('danger', 'bi-graph-down-arrow', 'Engagement is declining',
        `Average daily engagement fell from ${Math.round(first)} to ${Math.round(second)}. Investigate what changed recently.`)
    }
  }

  // Visitor mix (local vs international)
  const vt = (d.visitorTypes || []).filter(v => v.count > 0)
  const local = (vt.find(v => v.type === 'Local') || {}).count || 0
  const intl = (vt.find(v => v.type === 'International') || {}).count || 0
  if (local + intl > 0) {
    const intlPct = Math.round((intl / (local + intl)) * 100)
    if (intlPct < 25) {
      push('opportunity', 'bi-globe', 'Expand your international reach',
        `Only ${intlPct}% of visitors are international (${intl} of ${local + intl}). A mostly local audience leaves global tourism growth on the table.`)
    } else if (intlPct > 60) {
      push('info', 'bi-house-heart', 'Add multilingual content for international guests',
        `With ${intlPct}% international visitors, key phrases and welcome info in their languages can lift engagement.`)
    }
  }

  // Peak activity day
  const days = (d.activeDays || []).filter(x => x && x.count > 0)
  if (days.length) {
    const busiest = days.reduce((a, b) => (b.count > a.count ? b : a))
    const quietest = days.reduce((a, b) => (b.count < a.count ? b : a))
    push('info', 'bi-calendar-event', 'Peak activity day',
      `${busiest.day} is your busiest day. Consider running special promotions or events to spread activity across the week.`)
  }

  // Peak viewing time
  if ((d.heatmap || []).length) {
    let maxVal = 0
    let peakPeriod = ''
    let peakHour = 0
    for (const row of d.heatmap) {
      for (let i = 0; i < row.values.length; i++) {
        if (row.values[i] > maxVal) { maxVal = row.values[i]; peakPeriod = row.period; peakHour = i }
      }
    }
    if (maxVal > 0) {
      push('info', 'bi-clock-history', 'Peak viewing time',
        `Most visitors engage during ${peakPeriod} around ${hourLabel(peakHour)}. Schedule updates and promotions in that window.`)
    }
  }

  // Low ratings clustered
  if (starTotal.value > 0) {
    const low = (d.starDist[1] || 0) + (d.starDist[2] || 0)
    const lowPct = Math.round((low / starTotal.value) * 100)
    if (lowPct >= 25) {
      push('danger', 'bi-binoculars', 'Low ratings are clustered',
        `${lowPct}% of all reviews are 1–2 stars (${low} of ${starTotal.value}). Find the common thread in those comments.`)
    }
  }

  // Contact vs adds
  if (d.kpis.contacts != null && d.kpis.contacts > 0 && d.kpis.adds != null && d.kpis.contacts > d.kpis.adds) {
    push('info', 'bi-telephone', 'More contacts than saves',
      `${fmt(d.kpis.contacts)} travellers contacted you but only ${fmt(d.kpis.adds)} saved a trip plan — follow up while interest is hot.`)
  }

  // Generic, always-applicable guidance
  const hasEngagement = perf.length || series.length || starTotal.value > 0 || (d.kpis.rating != null && d.kpis.reviews > 0)
  if (!hasEngagement) {
    push('warning', 'bi-megaphone', 'Boost visibility',
      'Your hotspots have little activity yet. Share them on social media, add high-quality photos, and write compelling descriptions to attract visitors.')
  }
  if (d.kpis.reviews === 0 && !perf.length) {
    push('info', 'bi-chat-dots', 'Collect reviews early',
      'Encourage visitors to rate their experience after a visit — social proof helps other travellers choose your hotspot.')
  }

  return out
}
const insights = computed(() => buildInsights())

/* ── Recommendations (what to do next) ──────── */
function buildRecommendations() {
  const out = []
  const d = data.value
  if (!d) return out
  const push = (type, icon, title, action, why) => {
    if (out.length < 8) out.push({ type, icon, title, action, why })
  }

  const perf = (d.performance || []).filter(p => p.views > 0)
  const series = d.line || []

  // 1. Conversion
  if (d.kpis.profileViews != null && d.kpis.profileViews > 0 && d.kpis.adds != null) {
    const conv = Math.round((d.kpis.adds / d.kpis.profileViews) * 100)
    if (conv < 35) {
      push('warning', 'bi-arrow-down-right-circle',
        "Improve conversion — visitors look but don't save",
        'Refresh the profile photos, description and pricing for your most-viewed hotspots.',
        `Data: ${fmt(d.kpis.profileViews)} profile views but only ${fmt(d.kpis.adds)} itinerary adds (${conv}% conversion). High views with low saves usually means the profile isn't convincing at the point of decision.`)
    }
  }

  // 2. Rising trend
  if (series.length >= 4) {
    const half = Math.floor(series.length / 2)
    const first = series.slice(0, half).reduce((s, p) => s + p.count, 0) / half
    const second = series.slice(half).reduce((s, p) => s + p.count, 0) / (series.length - half)
    if (second > first * 1.25) {
      const top = perf[0]
      push('success', 'bi-megaphone',
        'Ride the momentum — promote your top experience',
        top ? `Boost visibility of "${top.title}" while interest is climbing.` : 'Boost your most-viewed experience while interest is climbing.',
        `Data: average daily engagement rose from ${Math.round(first)} to ${Math.round(second)} (${Math.round(((second - first) / first) * 100)}% increase). Promoting now capitalises on existing demand.`)
    } else if (second < first * 0.75) {
      push('danger', 'bi-search',
        'Investigate the decline before it deepens',
        'Check recent reviews, listing status, and whether a hotspot went inactive or lost approval.',
        `Data: average daily engagement fell from ${Math.round(first)} to ${Math.round(second)} (${Math.round(((first - second) / first) * 100)}% drop). Declining engagement usually follows a change to the listing or market.`)
    }
  }

  // 3. Top performer
  if (perf.length) {
    const top = perf[0]
    push('success', 'bi-trophy-fill',
      'Promote your star performer',
      `Feature "${top.title}" on social media and in your profile links.`,
      `Data: "${top.title}" leads your portfolio with ${fmt(top.views)} itinerary adds${top.avg_rating ? ` and a ${top.avg_rating.toFixed(1)}★ average` : ''}. Proven demand makes it the safest thing to promote.`)
  }

  // 4. Category expansion
  const catViews = {}
  for (const p of perf) catViews[p.category] = (catViews[p.category] || 0) + p.views
  const sortedCats = Object.entries(catViews).sort((a, b) => b[1] - a[1])
  if (sortedCats.length && sortedCats[0][1] > 0 && perf.length >= 2) {
    const [cat, count] = sortedCats[0]
    const owned = perf.filter(p => p.category === cat)
    push('opportunity', 'bi-plus-circle',
      `Grow your ${cat} offering`,
      owned.length ? `Consider adding a new experience in ${cat} — your strongest category.` : `Create a new offering in ${cat}.`,
      `Data: ${count} itinerary adds belong to ${cat} experiences${owned.length ? ` (${owned.length} currently listed)` : ''} — the largest demand pool in your portfolio.`)
  }

  // 5. Weak performer
  const weak = (d.performance || []).find(p => p.avg_rating != null && p.avg_rating < 3.5 && p.reviews > 0)
  if (weak) {
    push('warning', 'bi-exclamation-triangle',
      `Fix "${weak.title}" before it drags your average down`,
      'Read its recent reviews, address the common complaint, then update the listing.',
      `Data: "${weak.title}" averages ${weak.avg_rating.toFixed(1)}★ from ${weak.reviews} reviews. Low-rated hotspots discourage saves and hurt your overall average.`)
  }

  // 6. Review coverage
  const noReviews = (d.performance || []).find(p => p.views > 0 && (p.reviews || 0) === 0)
  if (noReviews) {
    push('info', 'bi-chat-dots',
      'Turn views into reviews',
      `Ask visitors of "${noReviews.title}" to leave a rating after their visit.`,
      `Data: "${noReviews.title}" has ${fmt(noReviews.views)} itinerary adds but zero reviews — visible demand with no social proof.`)
  }

  // 7. International mix
  const vt = (d.visitorTypes || []).filter(v => v.count > 0)
  const local = (vt.find(v => v.type === 'Local') || {}).count || 0
  const intl = (vt.find(v => v.type === 'International') || {}).count || 0
  if (local + intl > 0) {
    const intlPct = Math.round((intl / (local + intl)) * 100)
    if (intlPct < 25) {
      push('opportunity', 'bi-globe',
        'Expand your international reach',
        'Add English + your language(s), mention flight/transit access, and highlight what makes the experience uniquely South African.',
        `Data: only ${intlPct}% of visitors are international (${intl} of ${local + intl}). A mostly local audience leaves global tourism growth on the table.`)
    } else if (intlPct > 60) {
      push('info', 'bi-house-heart',
        'Add multilingual content for international guests',
        "Add key phrases and welcome info in your visitors' languages.",
        `Data: ${intlPct}% of visitors are international (${intl} of ${local + intl}) — a diverse audience benefits from multilingual touchpoints.`)
    }
  }

  // 8. Peak time scheduling
  if (hasHeatmap.value) {
    let maxVal = 0
    let peakPeriod = ''
    let peakHour = 0
    for (const row of data.value.heatmap) {
      for (let i = 0; i < row.values.length; i++) {
        if (row.values[i] > maxVal) { maxVal = row.values[i]; peakPeriod = row.period; peakHour = i }
      }
    }
    if (maxVal > 0) {
      push('info', 'bi-clock-history',
        'Schedule promotions around peak times',
        `Publish updates and run offers during ${peakPeriod} (around ${hourLabel(peakHour)}) when visitors are most active.`,
        `Data: your busiest window is ${peakPeriod} at ${hourLabel(peakHour)} (${maxVal} events). Timing marketing to when people are already engaged lifts response rates.`)
    }
  }

  // 9. Contact follow-up
  if (d.kpis.contacts != null && d.kpis.contacts > 0 && d.kpis.adds != null && d.kpis.contacts > d.kpis.adds) {
    push('warning', 'bi-telephone',
      "Follow up with contacts who didn't save",
      'Reach out within 48 hours to convert contact requests into confirmed plans.',
      `Data: ${fmt(d.kpis.contacts)} contact requests vs ${fmt(d.kpis.adds)} itinerary adds. Unconverted contacts are warm leads going cold.`)
  }

  return out
}

/* ── Events ─────────────────────────────────── */
function setRange(r) {
  range.value = r
  recommendations.value = []
  if (selectedId.value === 'all') {
    loadPortfolio()
  }
}
async function onSelectHotspot() {
  recommendations.value = []
  await loadPortfolio()
}

onMounted(() => {
  load()
})

onUnmounted(() => {
  destroyCharts()
})
</script>

<style scoped>
.ana-page {
  min-height: 100vh;
  background: var(--bg-color);
  padding: 96px 28px 40px;
  color: var(--text-color);
  font-family: 'Roboto', sans-serif;
  min-width: 0;
  overflow-x: hidden;
}

/* Header */
.ana-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.ana-head-left h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--heading-color);
  margin: 0 0 4px;
}

.ana-head-left p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0;
}

.ana-head-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

/* Range tabs */
.range-tabs {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 4px;
}

.range-tab {
  padding: 6px 12px;
  border: none;
  border-radius: 7px;
  background: transparent;
  font-family: 'Poppins', sans-serif;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.18s;
}

.range-tab:hover { color: var(--accent); }
.range-tab.active {
  background: var(--accent-fill);
  color: #1a1a1a;
}

/* Hotspot select */
.hotspot-select {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 9px 14px;
  color: var(--text-secondary);
  min-width: 240px;
}

.hotspot-select select {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-family: 'Poppins', sans-serif;
  font-size: 0.85rem;
  color: var(--heading-color);
  cursor: pointer;
  appearance: none;
  padding-right: 6px;
}

.hotspot-select i:first-child { color: var(--accent); font-size: 0.9rem; }
.hotspot-select i:last-child { color: var(--text-muted); font-size: 0.8rem; }

/* CTA banner */
.cta-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  background: linear-gradient(120deg, rgba(232, 162, 0, 0.16), rgba(139, 90, 43, 0.10));
  border: 1px solid rgba(232, 162, 0, 0.4);
  border-radius: 14px;
  padding: 18px 22px;
  margin-bottom: 20px;
}

.cta-copy { display: flex; align-items: center; gap: 14px; min-width: 260px; flex: 1; }

.cta-icon {
  width: 44px;
  height: 44px;
  border-radius: 11px;
  background: var(--accent-fill);
  color: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.cta-copy h2 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--heading-color);
  margin: 0 0 2px;
}

.cta-copy p { font-size: 0.82rem; color: var(--text-secondary); margin: 0; }

.cta-btn { font-size: 0.88rem; padding: 12px 22px; }
.cta-btn i { font-size: 1rem; }

/* KPI grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 18px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
}

.kpi-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.kpi-icon {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.kpi-label {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.kpi-value {
  font-family: 'Poppins', sans-serif;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--heading-color);
  line-height: 1.1;
  margin-bottom: 8px;
}

.kpi-delta-row {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 8px;
  border-top: 1px dashed var(--border);
}

.kpi-delta {
  font-size: 0.78rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.kpi-delta.up { color: var(--success); }
.kpi-delta.down { color: var(--error); }
.kpi-delta.muted { color: var(--text-muted); font-weight: 400; }

.kpi-hint {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.kpi-gold { color: var(--accent-fill); background: var(--accent-light); }
.kpi-brown { color: #8B5A2B; background: rgba(139, 90, 43, 0.13); }
.kpi-brownDark { color: #5C3A21; background: rgba(92, 58, 33, 0.13); }
.kpi-tan { color: #C9A227; background: rgba(201, 162, 39, 0.14); }

/* Chart grid */
.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px;
  box-shadow: var(--shadow-sm);
}

.chart-card.wide { grid-column: 1 / -1; }

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 14px;
}

.card-head h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--heading-color);
  margin: 0;
}

.card-sub { font-size: 0.75rem; color: var(--text-muted); }

.chart-box { height: 280px; position: relative; }
.chart-card.wide .chart-box { height: 260px; }

.chart-note {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 8px 0 0;
  text-align: center;
}

.chart-empty {
  height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 0.85rem;
}

/* Segmented control */
.seg-control {
  display: flex;
  align-items: center;
  gap: 3px;
  background: var(--surface-secondary);
  border-radius: 8px;
  padding: 3px;
}

.seg-btn {
  padding: 5px 14px;
  border: none;
  border-radius: 6px;
  background: transparent;
  font-family: 'Poppins', sans-serif;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.16s;
}

.seg-btn:hover { color: var(--accent); }
.seg-btn.active { background: var(--accent-fill); color: #1a1a1a; }

/* Star distribution */
.star-dist { display: flex; flex-direction: column; gap: 8px; padding-top: 6px; }

.sd-row { display: flex; align-items: center; gap: 10px; }

.sd-label {
  font-size: 0.82rem;
  color: var(--text-secondary);
  min-width: 30px;
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.sd-label i { color: var(--accent); font-size: 0.7rem; }

.sd-track {
  flex: 1;
  height: 9px;
  background: var(--surface-secondary);
  border-radius: 5px;
  overflow: hidden;
}

.sd-fill { height: 100%; background: var(--accent-fill); border-radius: 5px; transition: width 0.3s; }
.sd-count { font-size: 0.8rem; color: var(--text-secondary); min-width: 22px; text-align: right; }

/* Heatmap */
.heatmap-wrap { display: flex; gap: 10px; align-items: stretch; }

.hm-y-labels {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 22px;
  flex-shrink: 0;
}

.hm-y-label {
  height: 34px;
  display: flex;
  align-items: center;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.heatmap { flex: 1; min-width: 0; }

.hm-x-labels {
  display: grid;
  grid-template-columns: repeat(24, 1fr);
  margin-bottom: 4px;
}

.hm-x-label {
  font-size: 0.62rem;
  color: var(--text-muted);
  text-align: center;
  white-space: nowrap;
}

.hm-x-label--major {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.hm-body { display: flex; flex-direction: column; gap: 4px; }
.hm-row { display: grid; grid-template-columns: repeat(24, 1fr); gap: 3px; }

.hm-cell {
  height: 30px;
  border-radius: 4px;
  transition: transform 0.1s;
}

.hm-cell:hover { transform: scale(1.1); }

.hm-legend {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  margin-top: 10px;
}

.hm-legend-label { font-size: 0.72rem; color: var(--text-muted); }
.hm-legend-cell { width: 24px; height: 14px; border-radius: 3px; }

/* Performance list */
.perf-list { display: flex; flex-direction: column; gap: 8px; }

.perf-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--surface-secondary);
}

.perf-rank {
  width: 26px;
  height: 26px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Poppins', sans-serif;
  font-size: 0.78rem;
  font-weight: 700;
  background: var(--accent-light);
  color: var(--accent-dark);
  flex-shrink: 0;
}

.perf-rank.rank-1 { background: var(--accent-fill); color: #1a1a1a; }
.perf-rank.rank-2 { background: rgba(139, 90, 43, 0.18); color: #5C3A21; }
.perf-rank.rank-3 { background: rgba(201, 162, 39, 0.18); color: #7A4E00; }

.perf-main { min-width: 0; flex: 0 0 220px; }

.perf-title {
  display: block;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--heading-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.perf-cat { font-size: 0.72rem; color: var(--text-muted); }

.perf-bar-wrap { flex: 1; height: 10px; background: rgba(139, 90, 43, 0.1); border-radius: 5px; overflow: hidden; min-width: 60px; }
.perf-bar { height: 100%; background: linear-gradient(90deg, var(--accent-fill), #b57912); border-radius: 5px; }

.perf-metrics { display: flex; gap: 14px; flex-shrink: 0; }

.perf-metric {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.perf-metric i { color: var(--accent); font-size: 0.75rem; }

.perf-trend {
  flex-shrink: 0;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
}

.perf-trend.up { background: var(--success-light); color: var(--success); }
.perf-trend.down { background: var(--error-light); color: var(--error); }
.perf-trend.stable { background: rgba(139, 90, 43, 0.12); color: var(--text-secondary); }
.perf-trend.muted { background: var(--surface-secondary); color: var(--text-muted); }

/* Reviews */
.review-list { display: flex; flex-direction: column; gap: 10px; }

.review-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface-secondary);
}

.review-avatar {
  width: 38px;
  height: 38px;
  border-radius: 9px;
  background: var(--accent-light);
  color: var(--accent-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.95rem;
  font-family: 'Poppins', sans-serif;
  flex-shrink: 0;
}

.review-main { flex: 1; min-width: 0; }

.review-top { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }

.review-name { font-size: 0.85rem; font-weight: 600; color: var(--heading-color); }

.review-stars { display: inline-flex; gap: 1px; }
.review-stars .bi { font-size: 0.75rem; }
.review-stars .filled { color: var(--accent); }
.review-stars .empty { color: #d1d5db; }

.review-exp { display: block; font-size: 0.72rem; color: var(--text-muted); margin-top: 1px; }

.review-comment { font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5; margin: 6px 0 0; }

.review-date { flex-shrink: 0; font-size: 0.72rem; color: var(--text-muted); white-space: nowrap; }

/* Insights */
.insights-section {
  margin-top: 24px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px;
  box-shadow: var(--shadow-sm);
}

.insights-head { margin-bottom: 16px; }
.insights-head h3 { display: flex; align-items: center; gap: 8px; }
.insights-head h3 i { color: var(--accent); font-size: 1.05rem; }

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 14px;
}

.insight-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  border-radius: 10px;
  border: 1px solid var(--border);
  transition: transform 0.15s, box-shadow 0.15s;
}

.insight-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }

.insight-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1rem;
}

.insight-success .insight-icon { color: #2e7d32; background: rgba(46, 125, 50, 0.12); }
.insight-warning .insight-icon { color: #f57c00; background: rgba(245, 124, 0, 0.12); }
.insight-danger .insight-icon { color: #d32f2f; background: rgba(211, 47, 47, 0.12); }
.insight-info .insight-icon { color: #1976d2; background: rgba(25, 118, 210, 0.12); }
.insight-opportunity .insight-icon { color: #7B1FA2; background: rgba(123, 31, 162, 0.12); }

.insight-content h4 {
  font-family: 'Poppins', sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--heading-color);
  margin: 0 0 4px;
}

.insight-content p {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* Recommendations */
.rec-section {
  margin-top: 24px;
  background: linear-gradient(180deg, rgba(232, 162, 0, 0.07), rgba(232, 162, 0, 0.02));
  border: 1px solid rgba(232, 162, 0, 0.35);
  border-radius: 14px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
  scroll-margin-top: 90px;
}

.rec-head { margin-bottom: 16px; }
.rec-head h3 { display: flex; align-items: center; gap: 8px; }
.rec-head h3 i { color: var(--accent); font-size: 1.05rem; }

.rec-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 14px;
}

.rec-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  transition: transform 0.15s, box-shadow 0.15s;
}

.rec-card:hover { transform: translateY(-2px); box-shadow: var(--shadow); }

.rec-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.05rem;
}

.rec-success .rec-icon { color: #2e7d32; background: rgba(46, 125, 50, 0.12); }
.rec-warning .rec-icon { color: #f57c00; background: rgba(245, 124, 0, 0.12); }
.rec-danger .rec-icon { color: #d32f2f; background: rgba(211, 47, 47, 0.12); }
.rec-info .rec-icon { color: #1976d2; background: rgba(25, 118, 210, 0.12); }
.rec-opportunity .rec-icon { color: #7B1FA2; background: rgba(123, 31, 162, 0.12); }

.rec-body h4 {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--heading-color);
  margin: 0 0 4px;
}

.rec-action {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--accent-dark);
  margin: 0 0 10px;
  line-height: 1.5;
}

.rec-why {
  background: var(--surface-secondary);
  border-radius: 8px;
  padding: 10px 12px;
}

.rec-why-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.rec-why-label i { color: var(--accent); }

.rec-why p { font-size: 0.78rem; color: var(--text-secondary); line-height: 1.55; margin: 0; }

/* Empty & error */
.empty-state {
  min-height: 40vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--text-secondary);
  text-align: center;
}

.empty-state i { font-size: 2.4rem; color: var(--accent); }
.empty-state h2 { font-size: 1.2rem; margin: 0; }
.empty-state p { font-size: 0.9rem; margin: 0; color: var(--text-muted); }

.retry-btn { margin-top: 10px; }

.note-foot {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: center;
  margin: 24px 0 0;
}

/* Responsive */
@media (max-width: 1280px) {
  .kpi-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 1024px) {
  .chart-grid { grid-template-columns: 1fr; }
  .chart-card.wide { grid-column: span 1; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 760px) {
  .perf-row { flex-wrap: wrap; }
  .perf-main { flex: 1 1 100%; }
  .perf-bar-wrap { order: 3; flex-basis: 100%; }
  .perf-metrics { order: 2; }
  .perf-trend { order: 2; }
  .cta-banner { flex-direction: column; align-items: stretch; }
  .cta-btn { width: 100%; }
}

@media (max-width: 640px) {
  .ana-page { padding: 96px 14px 40px; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .ana-header { align-items: flex-start; flex-direction: column; }
  .hotspot-select { width: 100%; min-width: 0; }
  .range-tabs { width: 100%; justify-content: space-between; }
}

@media (max-width: 420px) {
  .kpi-grid { grid-template-columns: 1fr; }
}
</style>
