<template>
  <div class="hotspot-analytics">
    <div class="ana-header">
      <button class="back-link" @click="goBack">
        <i class="bi bi-arrow-left"></i> Back
      </button>
      <h1>{{ title || 'Hotspot Analytics' }}</h1>
      <p v-if="title">Monitoring itinerary adds, visitors &amp; activity for this hotspot</p>
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
        <!-- Visitor type pie -->
        <div class="chart-card">
          <h3>Visitor Type</h3>
          <div class="chart-box"><canvas ref="visitorEl"></canvas></div>
        </div>

        <!-- Views per star rating -->
        <div class="chart-card">
          <h3>Views by Star Rating</h3>
          <div class="chart-box"><canvas ref="ratingEl"></canvas></div>
        </div>

        <!-- Most active days -->
        <div class="chart-card">
          <h3>Most Active Days</h3>
          <div class="chart-box"><canvas ref="daysEl"></canvas></div>
        </div>

        <!-- Peak times -->
        <div class="chart-card">
          <h3>Peak Times</h3>
          <div class="chart-box"><canvas ref="peakEl"></canvas></div>
        </div>

        <!-- Hourly activity -->
        <div class="chart-card wide">
          <h3>Hourly Activity</h3>
          <div class="chart-box"><canvas ref="hourlyEl"></canvas></div>
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

const visitorEl = ref(null)
const ratingEl = ref(null)
const daysEl = ref(null)
const peakEl = ref(null)
const hourlyEl = ref(null)

const PALETTE = {
  gold: '#FFB612',
  brown: '#8B5A2B',
  brownDark: '#5C3A21',
  brownMid: '#A67C52',
  tan: '#C9A227',
}
const STAR_COLORS = ['#5C3A21', '#8B5A2B', '#A67C52', '#C9A227', '#FFB612']

const localCount = ref(0)
const internationalCount = ref(0)

let charts = []

function destroyCharts() {
  charts.forEach(c => c.destroy())
  charts = []
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
  const local = (vt.find(v => v.type === 'Local') || {}).count || 0
  const intr = (vt.find(v => v.type === 'International') || {}).count || 0
  localCount.value = local
  internationalCount.value = intr

  // Visitor type pie
  if (visitorEl.value) {
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

  // Views by star rating
  if (ratingEl.value) {
    const vr = data.value.views_by_rating || []
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

  // Most active days
  if (daysEl.value) {
    const ad = data.value.active_days || []
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

  // Peak times (Morning / Afternoon / Evening)
  if (peakEl.value) {
    const pt = data.value.peak_times || []
    charts.push(new Chart(peakEl.value, {
      type: 'bar',
      data: {
        labels: pt.map(p => p.period),
        datasets: [{
          label: 'Adds',
          data: pt.map(p => p.count),
          backgroundColor: ['#C9A227', '#A67C52', '#5C3A21'],
          borderRadius: 5,
          maxBarThickness: 40,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, ticks: { color: '#6b6150', precision: 0, font: { size: 11 } }, grid: { color: 'rgba(0,0,0,0.06)' } },
          y: { grid: { display: false }, ticks: { color: '#6b6150', font: { size: 12 } } },
        },
      },
    }))
  }

  // Hourly activity (times on x axis, colored by period)
  if (hourlyEl.value) {
    const hourly = data.value.hourly || []
    const colors = hourly.map(h => {
      if (h.hour >= 6 && h.hour < 12) return '#C9A227' // Morning
      if (h.hour >= 12 && h.hour < 18) return '#A67C52' // Afternoon
      return '#5C3A21' // Evening
    })
    charts.push(new Chart(hourlyEl.value, {
      type: 'bar',
      data: {
        labels: hourly.map(h => (h.hour < 10 ? `0${h.hour}` : `${h.hour}`) + ':00'),
        datasets: [{
          label: 'Adds',
          data: hourly.map(h => h.count),
          backgroundColor: colors,
          borderRadius: 2,
          maxBarThickness: 14,
        }],
      },
      options: baseOptions('Time of day'),
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
.chart-card.wide .chart-box { height: 240px; }

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: var(--text-secondary);
}
</style>
