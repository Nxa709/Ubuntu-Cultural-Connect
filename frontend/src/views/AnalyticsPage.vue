<template>
  <div class="ana-page">
    <LoadingSpinner v-if="loading" message="Putting your numbers together..." />

    <template v-else>
      <!-- Header -->
      <header class="ana-header">
        <div class="ana-head-left">
          <h1>Analytics Overview</h1>
          <p>Track how your hotspots are performing through your analytics.</p>
        </div>
        <div class="ana-head-right">
          <div class="date-select">
            <i class="bi bi-calendar3"></i>
            <select v-model="range" aria-label="Date range">
              <option value="all">All time</option>
              <option value="12m">Last 12 months</option>
              <option value="30d">Last 30 days</option>
            </select>
            <i class="bi bi-chevron-down"></i>
          </div>
          <button class="export-btn" @click="exportReport">
            <i class="bi bi-download"></i>
            Export Report
          </button>
        </div>
      </header>

      <!-- KPI row -->
      <div class="kpi-grid">
        <div class="kpi-card" v-for="k in kpis" :key="k.label">
          <div class="kpi-top">
            <span class="kpi-icon" :class="'kpi-' + k.color"><i :class="['bi', k.icon]"></i></span>
            <span class="kpi-label">{{ k.label }}</span>
          </div>
          <div class="kpi-value">{{ formatValue(k) }}</div>
          <div class="kpi-delta" v-if="k.delta !== null">
            <span class="delta-pill" :class="k.delta >= 0 ? 'up' : 'down'">
              <i :class="k.delta >= 0 ? 'bi-arrow-up-short' : 'bi-arrow-down-short'"></i>
              {{ Math.abs(k.delta).toFixed(0) }}%
            </span>
            <span class="kpi-vs">vs previous period</span>
          </div>
          <div class="kpi-delta" v-else><span class="kpi-vs">no prior period</span></div>
          <svg
            v-if="k.spark && k.spark.length > 1"
            class="kpi-spark"
            :class="'kpi-' + k.color"
            viewBox="0 0 100 32"
            preserveAspectRatio="none"
          >
            <polyline :points="sparkPoints(k.spark)" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <div v-else class="kpi-spark kpi-spark--empty"></div>
        </div>
      </div>

      <!-- Row 3 -->
      <div class="row-triple">
        <div class="card">
          <div class="card-head">
            <h2>Top Categories</h2>
          </div>
          <div class="bar-list" v-if="topCategories.length">
            <div class="bar-row" v-for="c in topCategories" :key="c.name">
              <div class="bar-label-row">
                <span class="bar-name">{{ c.name }}</span>
                <span class="bar-pct">{{ c.pct }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: c.pct + '%' }"></div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">No category data yet.</div>
        </div>

        <div class="card">
          <div class="card-head">
            <h2>Top Listings by Itinerary Adds</h2>
          </div>
          <div class="chart-wrap-sm">
            <canvas v-if="topByAdds.length" ref="barEl"></canvas>
            <div v-else class="no-data">No itinerary adds yet.</div>
          </div>
        </div>
      </div>

      <!-- Row 4 -->
      <div class="row-bottom">
        <div class="card table-card">
          <div class="card-head">
            <h2>Top Performing Listings</h2>
          </div>
          <div class="table-scroll" v-if="topListings.length">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Listing</th>
                  <th>Itinerary Adds</th>
                  <th>Reviews</th>
                  <th>Avg Rating</th>
                  <th>Trend</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in topListings" :key="row.id">
                  <td>
                    <div class="listing-cell">
                      <span class="thumb" :style="{ backgroundImage: `url(${row.image_url || fallbackImage})` }"></span>
                      <span class="listing-name">{{ row.title }}</span>
                    </div>
                  </td>
                  <td>{{ row.itinerary_adds }}</td>
                  <td>{{ row.reviews }}</td>
                  <td><strong>{{ row.avg_rating ? row.avg_rating.toFixed(1) : '—' }}</strong></td>
                  <td>
                    <span :class="['trend-badge', row.trend]">
                      {{ row.trend === 'improving' ? '↑ Improving' : row.trend === 'declining' ? '↓ Declining' : '→ Stable' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="no-data">No listings yet.</div>
        </div>

        <div class="card insights-card">
          <div class="card-head">
            <h2>Insights</h2>
          </div>
          <div class="insight-list">
            <div class="insight-item" v-for="(ins, i) in insights" :key="i">
              <span class="insight-icon" :class="'kpi-' + ins.color"><i :class="['bi', ins.icon]"></i></span>
              <p class="insight-text">{{ ins.pre }}<strong>{{ ins.strong }}</strong>{{ ins.post }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import { useExperienceStore } from '../stores/experience'

const store = useExperienceStore()

const loading = ref(true)
const range = ref('all')
const stats = ref(null)
const overview = ref({
  total_customers: 0,
  total_reviews: 0,
  avg_rating: 0,
  star_distribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
  monthly_customers: [],
  monthly_ratings: [],
  recent_reviews: [],
})

const fallbackImage = '/img/cultures/Safari.jpg'

const COLORS = {
  gold: '#FFB612',
  navy: '#2d465e',
  blue: '#4dabf7',
  green: '#51cf66',
  purple: '#9b59b6',
  red: '#ff6b6b',
  gray: '#c2c9d1',
}

/* ---------- Derived data ---------- */

const myExperiences = computed(() => store.myExperiences || [])
const hostPerformance = computed(() => store.hostPerformance || [])

const kpis = computed(() => {
  const s = stats.value || {}
  const o = overview.value || {}
  return [
    { label: 'Registered Hotspots', value: s.registered_hotspots ?? myExperiences.value.length, icon: 'bi-building', color: 'navy', delta: null, spark: null },
    { label: 'Active Hotspots', value: s.active_hotspots ?? 0, icon: 'bi-check-circle', color: 'green', delta: null, spark: null },
    { label: 'Itinerary Adds', value: s.total_itinerary_adds ?? 0, icon: 'bi-map', color: 'red', delta: null, spark: null },
  ]
})

function formatValue(k) {
  const v = Number(k.value || 0)
  return v.toLocaleString()
}

function sparkPoints(data) {
  const w = 100
  const h = 32
  const max = Math.max(...data, 1)
  const min = Math.min(...data, 0)
  const range = max - min || 1
  const step = w / (data.length - 1)
  return data.map((v, i) => {
    const x = (i * step).toFixed(1)
    const y = (h - ((v - min) / range) * (h - 4) - 2).toFixed(1)
    return `${x},${y}`
  }).join(' ')
}

/* ---------- Rankings & listings ---------- */

const topCategories = computed(() => {
  let map = {}
  for (const p of hostPerformance.value) {
    const c = p.category || 'Other'
    map[c] = (map[c] || 0) + (p.total_ratings || 0)
  }
  let total = Object.values(map).reduce((s, v) => s + v, 0)
  if (!total) {
    map = {}
    for (const e of myExperiences.value) {
      const c = e.category || 'Other'
      map[c] = (map[c] || 0) + 1
    }
    total = Object.values(map).reduce((s, v) => s + v, 0)
  }
  const t = total || 1
  return Object.entries(map)
    .map(([name, count]) => ({ name, count, pct: Math.round((count / t) * 100) }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)
})

const topByAdds = computed(() => {
  return [...myExperiences.value]
    .filter(e => (e.itinerary_adds || 0) > 0)
    .sort((a, b) => (b.itinerary_adds || 0) - (a.itinerary_adds || 0))
    .slice(0, 7)
})

function trendFor(id) {
  const p = hostPerformance.value.find(i => i.experience_id === id)
  return p ? p.trend : 'stable'
}

const topListings = computed(() => {
  return [...myExperiences.value]
    .map(e => ({
      id: e.id,
      title: e.title,
      image_url: e.image_url,
      avg_rating: e.avg_rating,
      reviews: e.rating_count || 0,
      itinerary_adds: e.itinerary_adds || 0,
      trend: trendFor(e.id),
    }))
    .sort((a, b) => (b.avg_rating || 0) - (a.avg_rating || 0) || b.itinerary_adds - a.itinerary_adds)
    .slice(0, 6)
})

/* ---------- Insights ---------- */

const insights = computed(() => {
  const list = []
  const o = overview.value
  const s = stats.value || {}
  if (o.total_reviews > 0) {
    list.push({
      icon: 'bi-star-fill', color: 'gold',
      pre: 'Your average rating is ', strong: `${Number(o.avg_rating).toFixed(1)}★`, post: ` across ${o.total_reviews} reviews.`,
    })
  }
  const mv = s.most_visited_hotspot
  if (mv) {
    list.push({
      icon: 'bi-geo-alt-fill', color: 'blue',
      pre: 'Your most-visited hotspot is ', strong: mv.title, post: ` with ${mv.visits} itinerary add${mv.visits === 1 ? '' : 's'}.`,
    })
  }
  if (hostPerformance.value.length) {
    const improving = hostPerformance.value.filter(i => i.trend === 'improving').length
    list.push({
      icon: 'bi-graph-up-arrow', color: 'green',
      pre: `${improving} of ${hostPerformance.value.length} listings are `, strong: 'trending up', post: ' in rating.',
    })
  }
  const top = topCategories.value[0]
  if (top) {
    list.push({
      icon: 'bi-tags-fill', color: 'purple',
      pre: 'Your top category is ', strong: top.name, post: ` with ${top.count} entr${top.count === 1 ? 'y' : 'ies'}.`,
    })
  }
  if (!list.length) {
    list.push({
      icon: 'bi-info-circle', color: 'navy',
      pre: 'Add hotspots and collect reviews to ', strong: 'unlock insights', post: ' about your business.',
    })
  }
  return list.slice(0, 4)
})

/* ---------- Export ---------- */

function exportReport() {
  const rows = [['Metric', 'Value']]
  for (const k of kpis.value) rows.push([k.label, String(k.value)])
  const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'analytics-report.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/* ---------- Charts ---------- */

const barEl = ref(null)
let charts = []

function baseOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
  }
}

function createCharts() {
  charts.forEach(c => c.destroy())
  charts = []

  const textColor = '#6c757d'
  const gridColor = 'rgba(0,0,0,0.06)'
  const axisColor = 'rgba(0,0,0,0.12)'

  if (barEl.value && topByAdds.value.length) {
    charts.push(new Chart(barEl.value, {
      type: 'bar',
      data: {
        labels: topByAdds.value.map(e => e.title.length > 14 ? e.title.slice(0, 14) + '…' : e.title),
        datasets: [{
          label: 'Itinerary adds',
          data: topByAdds.value.map(e => e.itinerary_adds),
          backgroundColor: COLORS.gold,
          borderRadius: 6,
          maxBarThickness: 26,
        }],
      },
      options: {
        ...baseOptions(),
        scales: {
          x: { grid: { display: false }, ticks: { color: textColor, font: { size: 10 }, maxRotation: 45, minRotation: 45 }, border: { color: axisColor } },
          y: { beginAtZero: true, grid: { color: gridColor }, ticks: { color: textColor, precision: 0, font: { size: 11 } }, border: { color: axisColor } },
        },
      },
    }))
  }
}

onMounted(async () => {
  const results = await Promise.allSettled([
    store.fetchOwnerStats(),
    store.fetchMyExperiences(),
    store.fetchHostPerformance(),
    store.getAnalytics(),
  ])
  if (results[0].status === 'fulfilled') stats.value = results[0].value || store.ownerStats || null
  if (results[3].status === 'fulfilled' && results[3].value) overview.value = results[3].value
  loading.value = false
  await nextTick()
  createCharts()
})

onUnmounted(() => {
  charts.forEach(c => c.destroy())
  charts = []
})
</script>

<style scoped>
.ana-page {
  min-height: 100vh;
  background: var(--surface-secondary);
  padding: 96px 28px 48px;
  color: #212529;
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
  margin-bottom: 24px;
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
}

.date-select {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--glass-bg);
  border: 1px solid #e5e9ef;
  border-radius: 10px;
  padding: 9px 14px;
  color: #495057;
}

.date-select select {
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

.date-select i {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.export-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #16212f;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 10px 16px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.export-btn:hover {
  background: var(--accent-fill);
  color: #1a1a1a;
}

/* KPI grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.kpi-card {
  background: var(--glass-bg);
  border: 1px solid #e5e9ef;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
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
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--heading-color);
  line-height: 1.1;
  margin-bottom: 6px;
}

.kpi-delta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  min-height: 18px;
}

.delta-pill {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
}

.delta-pill.up { color: #1f8a3c; background: rgba(81, 207, 102, 0.14); }
.delta-pill.down { color: #d64545; background: rgba(255, 107, 107, 0.14); }

.kpi-vs {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.kpi-spark {
  width: 100%;
  height: 32px;
  margin-top: auto;
}

.kpi-spark--empty {
  height: 32px;
  margin-top: auto;
}

/* Color accents */
.kpi-gold { color: #FFB612; }
.kpi-navy { color: #2d465e; }
.kpi-blue { color: #4dabf7; }
.kpi-green { color: #51cf66; }
.kpi-purple { color: #9b59b6; }
.kpi-red { color: #ff6b6b; }

.kpi-icon.kpi-gold { background: rgba(232, 162, 0, 0.14); }
.kpi-icon.kpi-navy { background: rgba(45, 70, 94, 0.12); }
.kpi-icon.kpi-blue { background: rgba(77, 171, 247, 0.14); }
.kpi-icon.kpi-green { background: rgba(81, 207, 102, 0.14); }
.kpi-icon.kpi-purple { background: rgba(155, 89, 182, 0.14); }
.kpi-icon.kpi-red { background: rgba(255, 107, 107, 0.14); }

/* Cards */
.card {
  background: var(--glass-bg);
  border: 1px solid #e5e9ef;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}

.card-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 14px;
}

.card-head h2 {
  font-family: 'Poppins', sans-serif;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--heading-color);
  margin: 0;
}

.card-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Row 2 */
.row-main {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.chart-wrap-lg { height: 300px; position: relative; }
.chart-wrap-sm { height: 220px; position: relative; }

/* Donuts */
.donut-body {
  display: flex;
  align-items: center;
  gap: 16px;
}

.donut-wrap {
  width: 110px;
  height: 110px;
  flex-shrink: 0;
  position: relative;
  margin: 0 auto;
}

.legend {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.legend li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
  color: #495057;
}

.legend .dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}

.lg-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lg-val {
  color: var(--text-muted);
  font-weight: 600;
  white-space: nowrap;
}

/* Row 3 */
.row-triple {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.bar-list { display: flex; flex-direction: column; gap: 14px; }

.bar-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 5px;
}

.bar-name { font-size: 0.82rem; color: #495057; }
.bar-pct { font-size: 0.8rem; font-weight: 700; color: var(--heading-color); }

.bar-track {
  height: 8px;
  background: #eef1f5;
  border-radius: 5px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 5px;
  background: linear-gradient(90deg, #2d465e, var(--accent));
}

.trend-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.trend-box {
  border-radius: 10px;
  padding: 14px 10px;
  text-align: center;
  display: flex;
  flex-direction: column;
}

.trend-improving { background: rgba(81, 207, 102, 0.12); }
.trend-stable { background: rgba(77, 171, 247, 0.12); }
.trend-declining { background: rgba(255, 107, 107, 0.12); }

.trend-num {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--heading-color);
  line-height: 1;
}

.trend-lbl { font-size: 0.72rem; color: var(--text-secondary); margin-top: 4px; }

.trend-note {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 14px 0 0;
  line-height: 1.5;
}

/* Row 4 */
.row-bottom {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 16px;
  align-items: start;
}

.table-scroll { overflow-x: auto; }

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}

.data-table th {
  text-align: left;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--text-muted);
  padding: 8px 10px;
  border-bottom: 1px solid #eef1f5;
}

.data-table td {
  padding: 10px;
  border-bottom: 1px solid #f2f4f7;
  color: #495057;
}

.listing-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 160px;
}

.thumb {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
}

.listing-name {
  font-weight: 500;
  color: var(--heading-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}

.trend-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 999px;
  white-space: nowrap;
}

.trend-badge.improving { background: rgba(81, 207, 102, 0.15); color: #1f8a3c; }
.trend-badge.declining { background: rgba(255, 107, 107, 0.15); color: #d64545; }
.trend-badge.stable { background: rgba(77, 171, 247, 0.14); color: #2f7fc1; }

/* Insights */
.insight-list { display: flex; flex-direction: column; gap: 14px; }

.insight-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.insight-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.insight-icon.kpi-gold { background: rgba(232, 162, 0, 0.14); }
.insight-icon.kpi-navy { background: rgba(45, 70, 94, 0.12); }
.insight-icon.kpi-blue { background: rgba(77, 171, 247, 0.14); }
.insight-icon.kpi-green { background: rgba(81, 207, 102, 0.14); }
.insight-icon.kpi-purple { background: rgba(155, 89, 182, 0.14); }
.insight-icon.kpi-red { background: rgba(255, 107, 107, 0.14); }

.insight-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}

.insight-text strong {
  color: var(--heading-color);
  font-weight: 700;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 90px;
  color: var(--text-muted);
  font-size: 0.85rem;
  text-align: center;
  padding: 16px;
}

/* Responsive */
@media (max-width: 1280px) {
  .kpi-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 1024px) {
  .row-main { grid-template-columns: 1fr; }
  .row-triple { grid-template-columns: 1fr; }
  .row-bottom { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .ana-page { padding: 96px 14px 40px; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .ana-header { align-items: flex-start; flex-direction: column; }
}

@media (max-width: 420px) {
  .kpi-grid { grid-template-columns: 1fr; }
}
</style>
