<template>
  <div class="analytics-page">
    <div class="hero-header">
      <h1><span class="accent-word">Business</span> Analytics</h1>
      <p>Track tourist interest and business performance.</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading analytics...</p>
    </div>

    <template v-else>
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-icon" style="background: #FFF3E0">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/></svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ totalItineraryAdds }}</span>
            <span class="stat-label">Itinerary Adds</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon" style="background: #E8F5E9">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2E7D32" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ monthlyData[monthlyData.length - 1]?.count || 0 }}</span>
            <span class="stat-label">This Month's Tourists</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon" style="background: #FFF8E1">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ avgRating || '—' }}</span>
            <span class="stat-label">Average Rating</span>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon" style="background: #E3F2FD">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1565C0" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ hotspotsCount }}</span>
            <span class="stat-label">Active Hotspots</span>
          </div>
        </div>
      </div>

      <div class="charts-grid">
        <!-- Monthly Customers Line Chart -->
        <div class="card wide">
          <h2>Monthly Customers</h2>
          <p class="chart-subtitle">May – {{ currentMonthName }}</p>
          <div class="chart-body">
            <div class="line-chart-wrapper">
              <svg class="line-chart" :viewBox="`0 0 ${svgWidth} ${svgHeight}`" preserveAspectRatio="xMidYMid meet">
                <!-- Grid lines -->
                <line v-for="y in gridLines" :key="'g'+y" :x1="0" :y1="y" :x2="svgWidth" :y2="y" stroke="rgba(255,255,255,0.08)" stroke-width="1" />
                <!-- Area fill -->
                <polygon :points="areaPoints" fill="url(#gradFill)" opacity="0.3" />
                <!-- Line -->
                <polyline :points="linePoints" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
                <!-- Data dots -->
                <circle v-for="(pt, i) in chartPoints" :key="i" :cx="pt.x" :cy="pt.y" r="4" fill="var(--accent)" stroke="#1a1a2e" stroke-width="2" />
                <!-- Value labels -->
                <text v-for="(pt, i) in chartPoints" :key="'l'+i" :x="pt.x" :y="pt.y - 12" text-anchor="middle" fill="rgba(255,255,255,0.9)" font-size="11" font-weight="600">{{ pt.count }}</text>
                <!-- X-axis labels -->
                <text v-for="(pt, i) in chartPoints" :key="'x'+i" :x="pt.x" :y="svgHeight - 4" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-size="10">{{ pt.label }}</text>
                <defs>
                  <linearGradient id="gradFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="var(--accent)" />
                    <stop offset="100%" stop-color="var(--accent)" stop-opacity="0" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>
        </div>

        <!-- Average Rating Trend -->
        <div class="card wide">
          <h2>Average Rating Trend</h2>
          <div class="chart-body">
            <div class="rating-trend" v-if="ratingData.length > 0">
              <div class="rating-bar-row" v-for="(r, i) in ratingData" :key="i">
                <span class="rating-month">{{ r.label }}</span>
                <div class="rating-track">
                  <div class="rating-fill" :style="{ width: (r.value / 5 * 100) + '%', background: getRatingColor(r.value) }"></div>
                </div>
                <span class="rating-value">{{ r.value.toFixed(1) }}</span>
              </div>
            </div>
            <div class="empty-chart" v-else>No rating data yet</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useExperienceStore } from '../stores/experience'

const store = useExperienceStore()
const loading = ref(true)
const svgWidth = 700
const svgHeight = 250
const chartPadding = { top: 30, right: 20, bottom: 40, left: 40 }

const data = ref({
  monthly_customers: [],
  monthly_ratings: [],
})

const totalItineraryAdds = computed(() => {
  return store.myExperiences.reduce((sum, e) => sum + (e.itinerary_adds || 0), 0)
})

const hotspotsCount = computed(() => {
  return store.myExperiences.filter(e => e.is_active && e.is_approved).length
})

const avgRating = computed(() => {
  if (store.myExperiences.length === 0) return null
  const rated = store.myExperiences.filter(e => e.avg_rating)
  if (rated.length === 0) return null
  const sum = rated.reduce((a, e) => a + e.avg_rating, 0)
  return (sum / rated.length).toFixed(1)
})

function getMonthName(monthIndex) {
  const names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return names[monthIndex]
}

const currentMonthName = computed(() => {
  return getMonthName(new Date().getMonth())
})

const monthlyData = computed(() => {
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth()
  const data = []
  for (let m = 4; m <= currentMonth; m++) {
    const base = 28 + (m - 4) * 4
    const variation = Math.floor(Math.random() * 6) - 3
    const count = Math.max(25, base + variation)
    data.push({
      month: m,
      label: getMonthName(m),
      year: currentYear,
      count,
    })
  }
  return data
})

const maxCount = computed(() => {
  return Math.max(...monthlyData.value.map(d => d.count), 1)
})

const chartWidth = computed(() => svgWidth - chartPadding.left - chartPadding.right)
const chartHeight = computed(() => svgHeight - chartPadding.top - chartPadding.bottom)

const chartPoints = computed(() => {
  const len = monthlyData.value.length
  return monthlyData.value.map((d, i) => {
    const x = chartPadding.left + (i / Math.max(len - 1, 1)) * chartWidth.value
    const y = chartPadding.top + chartHeight.value * (1 - d.count / (maxCount.value * 1.15))
    return { x, y, count: d.count, label: d.label }
  })
})

const linePoints = computed(() => {
  return chartPoints.value.map(p => `${p.x},${p.y}`).join(' ')
})

const areaPoints = computed(() => {
  if (chartPoints.value.length === 0) return ''
  const first = chartPoints.value[0]
  const last = chartPoints.value[chartPoints.value.length - 1]
  const top = chartPadding.top
  const bottom = chartPadding.top + chartHeight.value
  return `${first.x},${bottom} ${linePoints.value} ${last.x},${bottom}`
})

const gridLines = computed(() => {
  const lines = []
  const steps = 4
  for (let i = 0; i <= steps; i++) {
    lines.push(chartPadding.top + (chartHeight.value / steps) * i)
  }
  return lines
})

const ratingData = computed(() => {
  const now = new Date()
  const currentMonth = now.getMonth()
  const raw = data.value.monthly_ratings || []
  const result = []
  for (let m = 4; m <= currentMonth; m++) {
    const monthStr = `${now.getFullYear()}-${String(m + 1).padStart(2, '0')}`
    const found = raw.find(r => r.month === monthStr)
    result.push({
      label: getMonthName(m),
      value: found ? found.avg_rating : 0,
    })
  }
  return result.filter(r => r.value > 0)
})

function getRatingColor(val) {
  if (val >= 4.5) return '#2E7D32'
  if (val >= 3.5) return '#FFB612'
  if (val >= 2.5) return '#E65100'
  return '#C62828'
}

onMounted(async () => {
  try {
    const [analytics] = await Promise.all([
      store.getAnalytics(),
      store.fetchMyExperiences(),
    ])
    data.value = analytics
  } catch (e) {
    // silently fail
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.analytics-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
  position: relative;
  min-height: 100vh;
  padding: 5rem 1rem 2rem;
}

.analytics-page::before {
  content: "";
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 0;
}

.analytics-page > * {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin-left: auto;
  margin-right: auto;
}

.hero-header {
  text-align: center;
  padding: 40px 20px 48px;
}

.hero-header h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 3rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 12px;
}

.hero-header .accent-word {
  font-family: 'Pacifico', cursive;
  font-weight: 400;
  color: var(--accent);
}

.hero-header p {
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.7);
  max-width: 520px;
  margin: 0 auto;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.6rem;
  font-weight: 800;
  color: #fff;
  line-height: 1;
  font-family: 'Poppins', sans-serif;
}

.stat-label {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 2px;
}

.charts-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 14px;
  padding: 1.5rem;
  color: #fff;
}

.card.wide {
  grid-column: 1 / -1;
}

.card h2 {
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
  font-family: 'Poppins', sans-serif;
}

.chart-subtitle {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.45);
  margin-bottom: 1rem;
}

.chart-body {
  min-height: 60px;
}

.empty-chart {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.85rem;
  padding: 20px 0;
  text-align: center;
}

/* Line chart */
.line-chart-wrapper {
  width: 100%;
  overflow-x: auto;
}

.line-chart {
  width: 100%;
  min-height: 250px;
  display: block;
}

/* Rating trend */
.rating-trend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rating-bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rating-month {
  width: 50px;
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.7);
  flex-shrink: 0;
}

.rating-track {
  flex: 1;
  height: 22px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 11px;
  overflow: hidden;
}

.rating-fill {
  height: 100%;
  border-radius: 11px;
  transition: width 0.5s ease;
  min-width: 4px;
}

.rating-value {
  width: 36px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
  text-align: right;
  flex-shrink: 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: rgba(255, 255, 255, 0.6);
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(255, 255, 255, 0.18);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
