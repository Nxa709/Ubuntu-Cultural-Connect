<template>
  <div class="hotspot-analytics">
    <div class="ana-header">
      <button class="back-link" @click="goBack">
        <i class="bi bi-arrow-left"></i> Back
      </button>
      <h1>{{ title || 'Hotspot Analytics' }}</h1>
      <p v-if="title">Itinerary adds, visitors &amp; activity for this hotspot</p>
      <p v-else class="muted">Loading analytics…</p>
    </div>

    <div class="ana-body" v-if="data">
      <!-- KPIs -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <span class="kpi-value">{{ data.total_itinerary_adds }}</span>
          <span class="kpi-label">Itinerary Adds</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-value">{{ data.unique_visitors }}</span>
          <span class="kpi-label">Unique Visitors</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-value">{{ localCount }}</span>
          <span class="kpi-label">Local</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-value">{{ internationalCount }}</span>
          <span class="kpi-label">International</span>
        </div>
      </div>

      <div class="chart-grid">
        <!-- Views over time: line -->
        <div class="chart-card wide">
          <h3>Profile Views Over Time</h3>
          <div class="chart-box"><canvas ref="timeEl"></canvas></div>
        </div>

        <!-- Visitor type: pie -->
        <div class="chart-card">
          <h3>Visitor Type</h3>
          <div class="chart-box"><canvas ref="visitorEl"></canvas></div>
        </div>

        <!-- Top countries: horizontal bar -->
        <div class="chart-card">
          <h3>Top Countries</h3>
          <div class="chart-box"><canvas ref="countriesEl"></canvas></div>
        </div>

        <!-- Views by star rating -->
        <div class="chart-card">
          <h3>Views by Star Rating</h3>
          <div class="chart-box"><canvas ref="ratingEl"></canvas></div>
        </div>

        <!-- Most active days: bar -->
        <div class="chart-card">
          <h3>Most Active Days</h3>
          <div class="chart-box"><canvas ref="daysEl"></canvas></div>
        </div>

        <!-- Peak times: heatmap -->
        <div class="chart-card wide">
          <h3>Peak Times — Heatmap</h3>
          <div class="heatmap-wrap">
            <div class="hm-y-labels">
              <span v-for="row in data.peak_heatmap" :key="row.period" class="hm-y-label">{{ row.period }}</span>
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
                <div class="hm-row" v-for="row in data.peak_heatmap" :key="row.period">
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
          <div class="hm-legend">
            <span class="hm-legend-label">Low</span>
            <span v-for="s in 5" :key="s" class="hm-legend-cell" :style="cellStyle(Math.max(0, maxAdds - ((5 - s) * (maxAdds / 5))), true)"></span>
            <span class="hm-legend-label">High</span>
          </div>
        </div>

        <!-- Top performing services: horizontal bar -->
        <div class="chart-card wide">
          <h3>Top Performing Services</h3>
          <div class="chart-box"><canvas ref="topEl"></canvas></div>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else-if="!loading">
      <p>No analytics available yet.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Chart from 'chart.js/auto'
import { useExperienceStore } from '../stores/experience'

const route = useRoute()
const router = useRouter()
const store = useExperienceStore()

const title = ref('')
const data = ref(null)
const loading = ref(true)

const timeEl = ref(null)
const visitorEl = ref(null)
const countriesEl = ref(null)
const ratingEl = ref(null)
const daysEl = ref(null)
const topEl = ref(null)

const PALETTE = {
  gold: '#E8A200',
  goldLight: '#F5C453',
  brown: '#8B5A2B',
  brownDark: '#5C3A21',
  brownMid: '#A67C52',
  tan: '#C9A227',
}
const STAR_COLORS = ['#5C3A21', '#8B5A2B', '#A67C52', '#C9A227', '#E8A200']

const localCount = ref(0)
const internationalCount = ref(0)

let charts = []

function destroyCharts() {
  charts.forEach(c => c.destroy())
  charts = []
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

function shortDate(d) {
  const parts = d.split('-')
  return parts.length === 3 ? `${parts[1]}/${parts[2]}` : d
}

function monthBuckets(series) {
  const byMonth = {}
  for (const p of series || []) {
    const key = String(p.date || p.period || '').slice(0, 7)
    if (!key) continue
    byMonth[key] = (byMonth[key] || 0) + (p.count || 0)
  }
  return Object.entries(byMonth)
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([key, count]) => {
      const [y, m] = key.split('-').map(Number)
      return { label: new Date(y, m - 1, 1).toLocaleString('en-US', { month: 'long' }), count }
    })
}

function hourLabel(h) {
  return h === 0 ? '12am' : h < 12 ? `${h}am` : h === 12 ? '12pm' : `${h - 12}pm`
}

const maxAdds = ref(0)

function cellStyle(v, legend = false) {
  const max = Math.max(1, legend ? maxAdds.value : maxAdds.value)
  const ratio = max > 0 ? v / max : 0
  if (ratio <= 0) return { backgroundColor: 'rgba(0,0,0,0.05)' }
  // warm gold scale: low -> pale tan, high -> deep gold
  const base = [232, 162, 0]
  const light = [248, 228, 180]
  const r = Math.round(light[0] + (base[0] - light[0]) * ratio)
  const g = Math.round(light[1] + (base[1] - light[1]) * ratio)
  const b = Math.round(light[2] + (base[2] - light[2]) * ratio)
  return { backgroundColor: `rgb(${r},${g},${b})` }
}

function baseOptions(xTitle = '') {
  const textColor = '#6b6150'
  const gridColor = 'rgba(0,0,0,0.06)'
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { color: textColor, font: { size: 11 } } } },
    scales: {
      x: { title: { display: !!xTitle, text: xTitle, color: textColor }, ticks: { color: textColor, font: { size: 10 } }, grid: { color: gridColor } },
      y: { beginAtZero: true, ticks: { color: textColor, precision: 0, font: { size: 10 } }, grid: { color: gridColor } },
    },
  }
}

function renderCharts() {
  destroyCharts()
  if (!data.value) return

  const vt = data.value.visitor_types || []
  localCount.value = (vt.find(v => v.type === 'Local') || {}).count || 0
  internationalCount.value = (vt.find(v => v.type === 'International') || {}).count || 0

  // Views over time (line)
  if (timeEl.value && (data.value.views_over_time || []).length) {
    const mb = monthBuckets(data.value.views_over_time)
    charts.push(new Chart(timeEl.value, {
      type: 'line',
      data: {
        labels: mb.map(d => d.label),
        datasets: [{
          label: 'Itinerary Adds',
          data: mb.map(d => d.count),
          borderColor: PALETTE.gold,
          backgroundColor: 'rgba(232,162,0,0.15)',
          fill: true,
          tension: 0.35,
          pointBackgroundColor: PALETTE.brownDark,
          pointRadius: mb.length > 30 ? 2 : 4,
          pointHoverRadius: 6,
          borderWidth: 2.5,
        }],
      },
      options: baseOptions('Month'),
    }))
  }

  // Visitor type (pie)
  if (visitorEl.value && vt.length) {
    charts.push(new Chart(visitorEl.value, {
      type: 'pie',
      data: {
        labels: vt.map(v => v.type),
        datasets: [{
          data: vt.map(v => v.count),
          backgroundColor: [PALETTE.gold, PALETTE.brownMid],
          borderColor: '#fff',
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { color: '#6b6150', font: { size: 12 } } } },
      },
    }))
  }

  // Top countries (horizontal bar)
  if (countriesEl.value && (data.value.top_countries || []).length) {
    const tc = data.value.top_countries
    charts.push(new Chart(countriesEl.value, {
      type: 'bar',
      data: {
        labels: tc.map(c => c.country),
        datasets: [{
          label: 'Adds',
          data: tc.map(c => c.count),
          backgroundColor: tc.map((_, i) => (i === 0 ? PALETTE.gold : i === 1 ? PALETTE.tan : PALETTE.brownMid)),
          borderRadius: 5,
          maxBarThickness: 22,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, ticks: { color: '#6b6150', precision: 0, font: { size: 11 } }, grid: { color: 'rgba(0,0,0,0.06)' } },
          y: { grid: { display: false }, ticks: { color: '#6b6150', font: { size: 11 } } },
        },
      },
    }))
  }

  // Views by star rating
  if (ratingEl.value && (data.value.views_by_rating || []).length) {
    const vr = data.value.views_by_rating
    charts.push(new Chart(ratingEl.value, {
      type: 'bar',
      data: {
        labels: vr.map(v => `${v.rating}★`),
        datasets: [{
          label: 'Views',
          data: vr.map(v => v.views),
          backgroundColor: STAR_COLORS,
          borderRadius: 5,
          maxBarThickness: 34,
        }],
      },
      options: baseOptions('Rating'),
    }))
  }

  // Most active days (bar)
  const ad = (data.value.active_days || []).filter(d => d && d.day && d.count > 0)
  if (daysEl.value && ad.length) {
    charts.push(new Chart(daysEl.value, {
      type: 'bar',
      data: {
        labels: ad.map(d => d.day.slice(0, 3)),
        datasets: [{
          label: 'Itinerary Adds',
          data: ad.map(d => d.count),
          backgroundColor: PALETTE.brownMid,
          borderRadius: 4,
          maxBarThickness: 26,
        }],
      },
      options: baseOptions('Day'),
    }))
  }

  // Top performing services (horizontal bar)
  if (topEl.value && (data.value.top_services || []).length) {
    const ts = data.value.top_services
    charts.push(new Chart(topEl.value, {
      type: 'bar',
      data: {
        labels: ts.map(s => s.title.length > 22 ? s.title.slice(0, 22) + '…' : s.title),
        datasets: [{
          label: 'Itinerary Adds',
          data: ts.map(s => s.views),
          backgroundColor: ts.map((_, i) => (i === 0 ? PALETTE.gold : i === 1 ? PALETTE.tan : PALETTE.brownMid)),
          borderRadius: 5,
          maxBarThickness: 20,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, ticks: { color: '#6b6150', precision: 0, font: { size: 11 } }, grid: { color: 'rgba(0,0,0,0.06)' } },
          y: { grid: { display: false }, ticks: { color: '#6b6150', font: { size: 10 } } },
        },
      },
    }))
  }
}

function goBack() {
  router.back()
}

onMounted(async () => {
  const id = route.params.id
  try {
    const res = await store.getHotspotAnalytics(id)
    data.value = res
    title.value = res.title || ''
    maxAdds.value = Math.max(1, ...(res.peak_heatmap || []).flatMap(r => r.values || []))
    renderCharts()
  } catch (e) {
    console.error('Failed to load hotspot analytics', e)
  } finally {
    loading.value = false
  }
})

onUnmounted(destroyCharts)
</script>

<style scoped>
.hotspot-analytics {
  min-height: 100vh;
  background: var(--bg-color);
  color: var(--text-color);
}

.ana-header {
  text-align: center;
  padding: 60px 20px 40px;
  background: linear-gradient(rgba(40, 32, 20, 0.6), rgba(40, 32, 20, 0.6)), url('/img/cultures/woman.jpeg') no-repeat center center / cover;
  color: #fff;
  position: relative;
}

.ana-header h1 {
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  color: #fff;
  font-size: clamp(1.6rem, 4vw, 2.2rem);
  margin: 0 0 8px;
}
.ana-header p { color: rgba(255, 255, 255, 0.9); margin: 0; }
.ana-header .muted { color: rgba(255, 255, 255, 0.7); }

.back-link {
  position: absolute;
  top: 18px;
  left: 18px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.35);
  color: #fff;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.82rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}
.back-link:hover { background: var(--accent-fill); color: #1a1a1a; }

.ana-body {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 20px 60px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  text-align: center;
  box-shadow: var(--shadow-sm);
}
.kpi-value {
  display: block;
  font-family: 'Poppins', sans-serif;
  font-size: 2rem;
  font-weight: 800;
  color: var(--accent);
  line-height: 1.1;
}
.kpi-label {
  display: block;
  margin-top: 6px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 20px;
}
.chart-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}
.chart-card.wide { grid-column: 1 / -1; }
.chart-card h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: var(--heading-color);
  margin: 0 0 14px;
}
.chart-box { height: 280px; }
.chart-card.wide .chart-box { height: 260px; }

/* Heatmap */
.heatmap-wrap {
  display: flex;
  gap: 10px;
  align-items: stretch;
}
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
  font-size: 0.8rem;
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
.hm-cell:hover { transform: scale(1.08); }
.hm-legend {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 3px;
  margin-top: 10px;
}
.hm-legend-label { font-size: 0.7rem; color: var(--text-muted); }
.hm-legend-cell { width: 22px; height: 14px; border-radius: 3px; }

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: var(--text-secondary);
}
</style>
