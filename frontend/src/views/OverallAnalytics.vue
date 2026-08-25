<template>
  <div class="ana-page">
    <LoadingSpinner v-if="loading" message="Loading overall analytics..." />

    <template v-else>
      <!-- Header -->
      <header class="ana-header">
        <div class="ana-head-left">
          <h1>Overall Analytics</h1>
          <p>Comprehensive insights across all your hotspots.</p>
        </div>
      </header>

      <!-- No hotspots -->
      <div class="empty-state" v-if="!hasData">
        <i class="bi bi-graph-up"></i>
        <h2>No analytics data yet</h2>
        <p>Once visitors interact with your hotspots, insights will appear here.</p>
      </div>

      <!-- Overall analytics -->
      <template v-else>
        <!-- KPI row -->
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-icon kpi-gold"><i class="bi bi-trophy"></i></span>
              <span class="kpi-label">Top Performing Hotspot</span>
            </div>
            <div class="kpi-value">{{ topHotspot?.title || 'N/A' }}</div>
            <span class="kpi-hint">{{ topHotspot?.views || 0 }} total views</span>
          </div>
          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-icon kpi-brown"><i class="bi bi-eye"></i></span>
              <span class="kpi-label">Total Profile Views</span>
            </div>
            <div class="kpi-value">{{ totalViews }}</div>
            <span class="kpi-hint">Itinerary adds</span>
          </div>
          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-icon kpi-tan"><i class="bi bi-people"></i></span>
              <span class="kpi-label">Unique Visitors</span>
            </div>
            <div class="kpi-value">{{ uniqueVisitors }}</div>
            <span class="kpi-hint">Distinct travellers</span>
          </div>
          <div class="kpi-card">
            <div class="kpi-top">
              <span class="kpi-icon kpi-brownDark"><i class="bi bi-star-fill"></i></span>
              <span class="kpi-label">Average Rating</span>
            </div>
            <div class="kpi-value">{{ avgRating }}</div>
            <span class="kpi-hint">Across all hotspots</span>
          </div>
        </div>

        <div class="chart-grid">
          <!-- Profile views over time: line -->
          <div class="chart-card wide">
            <div class="card-head">
              <h3>Profile Views Over Time</h3>
              <span class="card-sub">All hotspots combined</span>
            </div>
            <div class="chart-box"><canvas ref="timeEl"></canvas></div>
          </div>

          <!-- Visitor type: pie -->
          <div class="chart-card">
            <div class="card-head">
              <h3>Visitor Types</h3>
              <span class="card-sub">Local vs International</span>
            </div>
            <div class="chart-box"><canvas ref="visitorTypeEl"></canvas></div>
          </div>

          <!-- Top countries: horizontal bar -->
          <div class="chart-card">
            <div class="card-head">
              <h3>Top Countries</h3>
              <span class="card-sub">Where your visitors come from</span>
            </div>
            <div class="chart-box"><canvas ref="countriesEl"></canvas></div>
          </div>

          <!-- Most active days: bar -->
          <div class="chart-card">
            <div class="card-head">
              <h3>Most Active Days</h3>
              <span class="card-sub">Weekday activity</span>
            </div>
            <div class="chart-box"><canvas ref="daysEl"></canvas></div>
          </div>

          <!-- Visitor Types Heatmap -->
          <div class="chart-card wide">
            <div class="card-head">
              <h3>Visitor Activity Heatmap</h3>
              <span class="card-sub">Hourly activity across Morning, Afternoon &amp; Evening</span>
            </div>
            <div class="heatmap-wrap" v-if="heatmapData && heatmapData.length">
              <div class="hm-y-labels">
                <span v-for="row in heatmapData" :key="row.period" class="hm-y-label">{{ row.period }}</span>
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
                  <div class="hm-row" v-for="row in heatmapData" :key="row.period">
                    <div
                      v-for="(v, i) in row.values"
                      :key="i"
                      class="hm-cell"
                      :style="cellStyle(v)"
                      :title="row.period + ' ' + hourLabel(i) + ': ' + v + ' view' + (v === 1 ? '' : 's')"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="hm-legend">
              <span class="hm-legend-label">Low</span>
              <span v-for="s in 5" :key="s" class="hm-legend-cell" :style="cellStyle((maxHeatmapValue / 5) * s, true)"></span>
              <span class="hm-legend-label">High</span>
            </div>
          </div>

          <!-- Top Performing Hotspots -->
          <div class="chart-card wide">
            <div class="card-head">
              <h3>Top Performing Hotspots</h3>
              <span class="card-sub">Your hotspots ranked by total views</span>
            </div>
            <div class="chart-box"><canvas ref="hotspotsEl"></canvas></div>
          </div>
        </div>

        <!-- Business Insights Section -->
        <div class="insights-section">
          <div class="card-head insights-head">
            <h3><i class="bi bi-lightbulb"></i> Business Insights</h3>
            <span class="card-sub">Smart suggestions based on your data</span>
          </div>
          <div class="insights-grid">
            <div v-for="(insight, idx) in insights" :key="idx" class="insight-card" :class="'insight-' + insight.type">
              <div class="insight-icon">
                <i :class="['bi', insight.icon]"></i>
              </div>
              <div class="insight-content">
                <h4>{{ insight.title }}</h4>
                <p>{{ insight.message }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>

      <p class="note-foot">
        Profile views are measured as itinerary adds — how many times a traveller added your hotspots to their trip plan.
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
const overallData = ref(null)
const hotspotAnalyticsList = ref([])

const timeEl = ref(null)
const visitorTypeEl = ref(null)
const countriesEl = ref(null)
const daysEl = ref(null)
const hotspotsEl = ref(null)

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

const totalViews = ref(0)
const uniqueVisitors = ref(0)
const avgRating = ref(0)
const topHotspot = ref(null)
const heatmapData = ref([])
const maxHeatmapValue = ref(1)
const hasData = ref(false)

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

function cellStyle(v, legend = false) {
  const ratio = Math.max(0, Math.min(1, v / Math.max(1, maxHeatmapValue.value)))
  if (ratio <= 0.001) return { backgroundColor: 'rgba(139, 90, 43, 0.08)' }
  const base = [181, 121, 18]
  const light = [248, 228, 180]
  const r = Math.round(light[0] + (base[0] - light[0]) * ratio)
  const g = Math.round(light[1] + (base[1] - light[1]) * ratio)
  const b = Math.round(light[2] + (base[2] - light[2]) * ratio)
  return { backgroundColor: `rgb(${r},${g},${b})` }
}

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
        ticks: { color: TEXT_COLOR, font: { size: 10 } },
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

function aggregateData() {
  const allViews = []
  const allVisitorTypes = {}
  const allCountries = {}
  const allActiveDays = {}
  const allHeatmap = []
  const hotspotPerformance = []
  let totalRatings = 0
  let totalRatingSum = 0

  for (const ha of hotspotAnalyticsList.value) {
    // Views over time
    if (ha.views_over_time) {
      allViews.push(...ha.views_over_time)
    }

    // Visitor types
    if (ha.visitor_types) {
      for (const vt of ha.visitor_types) {
        allVisitorTypes[vt.type] = (allVisitorTypes[vt.type] || 0) + vt.count
      }
    }

    // Top countries
    if (ha.top_countries) {
      for (const tc of ha.top_countries) {
        allCountries[tc.country] = (allCountries[tc.country] || 0) + tc.count
      }
    }

    // Active days
    if (ha.active_days) {
      for (const ad of ha.active_days) {
        allActiveDays[ad.day] = (allActiveDays[ad.day] || 0) + ad.count
      }
    }

    // Heatmap
    if (ha.peak_heatmap) {
      for (const row of ha.peak_heatmap) {
        const existing = allHeatmap.find(h => h.period === row.period)
        if (existing) {
          existing.values = existing.values.map((v, i) => v + (row.values[i] || 0))
        } else {
          allHeatmap.push({ period: row.period, values: [...row.values] })
        }
      }
    }

    // Hotspot performance
    hotspotPerformance.push({
      title: ha.title,
      views: ha.total_itinerary_adds || 0,
    })
  }

  // Aggregate views over time
  const viewsByDate = {}
  for (const v of allViews) {
    viewsByDate[v.date] = (viewsByDate[v.date] || 0) + v.count
  }
  const aggregatedViewsOverTime = Object.entries(viewsByDate)
    .map(([date, count]) => ({ date, count }))
    .sort((a, b) => a.date.localeCompare(b.date))

  // Convert visitor types to array
  const aggregatedVisitorTypes = Object.entries(allVisitorTypes)
    .map(([type, count]) => ({ type, count }))

  // Convert countries to array and sort
  const aggregatedCountries = Object.entries(allCountries)
    .map(([country, count]) => ({ country, count }))
    .sort((a, b) => b.count - a.count)

  // Convert active days to array
  const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  const aggregatedActiveDays = dayOrder
    .filter(day => allActiveDays[day])
    .map(day => ({ day, count: allActiveDays[day] }))

  // Sort hotspot performance
  hotspotPerformance.sort((a, b) => b.views - a.views)

  return {
    views_over_time: aggregatedViewsOverTime,
    visitor_types: aggregatedVisitorTypes,
    top_countries: aggregatedCountries,
    active_days: aggregatedActiveDays,
    peak_heatmap: allHeatmap,
    hotspot_performance: hotspotPerformance,
    total_views: hotspotPerformance.reduce((sum, h) => sum + h.views, 0),
    unique_visitors: 0,
  }
}

function generateInsights() {
  const insights = []

  // Top performing hotspot insight
  if (topHotspot.value && topHotspot.value.views > 0) {
    insights.push({
      type: 'success',
      icon: 'bi-trophy-fill',
      title: 'Star Performer',
      message: `"${topHotspot.value.title}" is your top performing hotspot with ${topHotspot.value.views} views. Consider promoting it more to attract even more visitors.`,
    })
  }

  // Visitor mix insight
  const localCount = hotspotAnalyticsList.value.reduce((sum, ha) => {
    const local = (ha.visitor_types || []).find(v => v.type === 'Local')
    return sum + (local?.count || 0)
  }, 0)
  const intlCount = hotspotAnalyticsList.value.reduce((sum, ha) => {
    const intl = (ha.visitor_types || []).find(v => v.type === 'International')
    return sum + (intl?.count || 0)
  }, 0)

  if (localCount > 0 && intlCount > 0) {
    const localPct = Math.round((localCount / (localCount + intlCount)) * 100)
    if (localPct > 70) {
      insights.push({
        type: 'warning',
        icon: 'bi-globe',
        title: 'Expand International Reach',
        message: `${localPct}% of your visitors are local. Consider marketing to international tourists to diversify your visitor base.`,
      })
    } else if (localPct < 30) {
      insights.push({
        type: 'info',
        icon: 'bi-house-heart',
        title: 'Strong International Appeal',
        message: 'Your international visitor percentage is high! Consider adding content in multiple languages to enhance their experience.',
      })
    }
  }

  // Active days insight
  const allDays = hotspotAnalyticsList.value.flatMap(ha => ha.active_days || [])
  const dayCounts = {}
  for (const d of allDays) {
    dayCounts[d.day] = (dayCounts[d.day] || 0) + d.count
  }
  const sortedDays = Object.entries(dayCounts).sort((a, b) => b[1] - a[1])
  if (sortedDays.length > 0) {
    const busiestDay = sortedDays[0][0]
    const quietestDay = sortedDays[sortedDays.length - 1][0]
    insights.push({
      type: 'info',
      icon: 'bi-calendar-event',
      title: 'Peak Activity Day',
      message: `${busiestDay} is your busiest day. Consider running special promotions or events on ${quietestDay}s to boost activity.`,
    })
  }

  // Rating insight
  if (avgRating.value >= 4.5) {
    insights.push({
      type: 'success',
      icon: 'bi-star-fill',
      title: 'Excellent Ratings',
      message: `Your average rating of ${avgRating.value} stars is outstanding! Keep delivering quality experiences to maintain this standard.`,
    })
  } else if (avgRating.value < 3.5 && avgRating.value > 0) {
    insights.push({
      type: 'warning',
      icon: 'bi-exclamation-triangle',
      title: 'Improve Guest Experience',
      message: `Your average rating is ${avgRating.value} stars. Focus on improving service quality and gathering more positive reviews.`,
    })
  }

  // Heatmap insight
  if (heatmapData.value && heatmapData.value.length > 0) {
    let maxVal = 0
    let peakPeriod = ''
    let peakHour = 0
    for (const row of heatmapData.value) {
      for (let i = 0; i < row.values.length; i++) {
        if (row.values[i] > maxVal) {
          maxVal = row.values[i]
          peakPeriod = row.period
          peakHour = i
        }
      }
    }
    if (maxVal > 0) {
      insights.push({
        type: 'info',
        icon: 'bi-clock-history',
        title: 'Peak Viewing Time',
        message: `Most visitors view your hotspots during ${peakPeriod} around ${hourLabel(peakHour)}. Schedule updates and promotions during this window.`,
      })
    }
  }

  // Generic improvement suggestions
  if (totalViews.value < 10) {
    insights.push({
      type: 'warning',
      icon: 'bi-megaphone',
      title: 'Boost Visibility',
      message: 'Your total views are low. Share your hotspots on social media, add high-quality photos, and write compelling descriptions.',
    })
  }

  // Add at least 3 insights
  if (insights.length < 3) {
    insights.push({
      type: 'info',
      icon: 'bi-plus-circle',
      title: 'Add More Hotspots',
      message: 'Register more hotspots to increase your visibility and reach a wider audience of cultural tourists.',
    })
  }
  if (insights.length < 4) {
    insights.push({
      type: 'info',
      icon: 'bi-chat-dots',
      title: 'Engage With Reviews',
      message: 'Respond to guest reviews to show you value feedback. This builds trust and encourages more bookings.',
    })
  }

  return insights
}

const insights = computed(() => generateInsights())

function renderCharts() {
  destroyCharts()
  if (!overallData.value) return

  // 1. Profile views over time (line)
  if (timeEl.value && (overallData.value.views_over_time || []).length) {
    const mb = monthBuckets(overallData.value.views_over_time)
    charts.push(new Chart(timeEl.value, {
      type: 'line',
      data: {
        labels: mb.map(d => d.label),
        datasets: [{
          label: 'Profile Views',
          data: mb.map(d => d.count),
          borderColor: PALETTE.gold,
          backgroundColor: 'rgba(232,162,0,0.15)',
          fill: true,
          tension: 0.35,
          pointBackgroundColor: PALETTE.goldDark,
          pointBorderColor: PALETTE.cream,
          pointRadius: mb.length > 30 ? 2 : 4,
          pointHoverRadius: 6,
          borderWidth: 2.5,
        }],
      },
      options: baseOptions('Month', 'Views'),
    }))
  }

  // 2. Visitor type (pie)
  const vt = overallData.value.visitor_types || []
  if (visitorTypeEl.value && vt.length) {
    charts.push(new Chart(visitorTypeEl.value, {
      type: 'pie',
      data: {
        labels: vt.map(v => v.type),
        datasets: [{
          data: vt.map(v => v.count),
          backgroundColor: [PALETTE.gold, PALETTE.brownMid],
          borderColor: PALETTE.cream,
          borderWidth: 3,
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

  // 3. Top countries (horizontal bar)
  const tc = overallData.value.top_countries || []
  if (countriesEl.value && tc.length) {
    charts.push(new Chart(countriesEl.value, {
      type: 'bar',
      data: {
        labels: tc.map(c => c.country),
        datasets: [{
          label: 'Views',
          data: tc.map(c => c.count),
          backgroundColor: tc.map((_, i) => (i === 0 ? PALETTE.gold : i === 1 ? PALETTE.tan : PALETTE.brownMid)),
          borderRadius: 5,
          maxBarThickness: 24,
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
          x: { beginAtZero: true, title: { display: true, text: 'Views', color: TEXT_COLOR, font: { size: 11, weight: 600 } }, ticks: { color: TEXT_COLOR, precision: 0, font: { size: 11 } }, grid: { color: GRID_COLOR } },
          y: { grid: { display: false }, ticks: { color: TEXT_COLOR, font: { size: 11 } } },
        },
      },
    }))
  }

  // 4. Most active days (bar)
  const ad = (overallData.value.active_days || []).filter(d => d && d.day && d.count > 0)
  if (daysEl.value && ad.length) {
    charts.push(new Chart(daysEl.value, {
      type: 'bar',
      data: {
        labels: ad.map(d => d.day.slice(0, 3)),
        datasets: [{
          label: 'Views',
          data: ad.map(d => d.count),
          backgroundColor: ad.map((_, i) => [PALETTE.gold, PALETTE.tan, PALETTE.brownMid, PALETTE.brown, PALETTE.goldDark, PALETTE.brownDark, PALETTE.tan][i % 7]),
          borderRadius: 5,
          maxBarThickness: 32,
        }],
      },
      options: baseOptions('Day of Week', 'Views'),
    }))
  }

  // 5. Top performing hotspots (horizontal bar)
  const hp = overallData.value.hotspot_performance || []
  if (hotspotsEl.value && hp.length) {
    charts.push(new Chart(hotspotsEl.value, {
      type: 'bar',
      data: {
        labels: hp.map(h => h.title.length > 24 ? h.title.slice(0, 24) + '...' : h.title),
        datasets: [{
          label: 'Views',
          data: hp.map(h => h.views),
          backgroundColor: hp.map((_, i) => (i === 0 ? PALETTE.gold : i === 1 ? PALETTE.tan : PALETTE.brownMid)),
          borderRadius: 5,
          maxBarThickness: 24,
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
          x: { beginAtZero: true, title: { display: true, text: 'Views', color: TEXT_COLOR, font: { size: 11, weight: 600 } }, ticks: { color: TEXT_COLOR, precision: 0, font: { size: 11 } }, grid: { color: GRID_COLOR } },
          y: { grid: { display: false }, ticks: { color: TEXT_COLOR, font: { size: 10 } } },
        },
      },
    }))
  }
}

async function loadOverallAnalytics() {
  try {
    const myExperiences = await store.fetchMyExperiences()
    if (!myExperiences || myExperiences.length === 0) {
      hasData.value = false
      loading.value = false
      return
    }

    // Fetch analytics for each hotspot
    const analyticsPromises = myExperiences.map(exp => store.getHotspotAnalytics(exp.id))
    hotspotAnalyticsList.value = await Promise.all(analyticsPromises)

    // Aggregate data
    overallData.value = aggregateData()

    // Update KPIs
    totalViews.value = overallData.value.total_views
    uniqueVisitors.value = new Set(
      hotspotAnalyticsList.value.flatMap(ha =>
        (ha.visitor_types || []).map(v => v.count)
      )
    ).size || 0

    // Calculate average rating from experience performance
    const perfRes = await store.fetchHostPerformance()
    if (perfRes && perfRes.length) {
      const ratingsSum = perfRes.reduce((sum, p) => sum + (p.avg_rating || 0), 0)
      const ratedCount = perfRes.filter(p => p.avg_rating).length
      avgRating.value = ratedCount > 0 ? (ratingsSum / ratedCount).toFixed(1) : '0.0'
    }

    // Top hotspot
    if (overallData.value.hotspot_performance && overallData.value.hotspot_performance.length > 0) {
      topHotspot.value = overallData.value.hotspot_performance[0]
    }

    // Heatmap
    heatmapData.value = overallData.value.peak_heatmap || []
    maxHeatmapValue.value = Math.max(1, ...heatmapData.value.flatMap(r => r.values || []))

    hasData.value = totalViews.value > 0 || hotspotAnalyticsList.value.length > 0

    await nextTick()
    renderCharts()
  } catch (e) {
    console.error('Failed to load overall analytics', e)
    hasData.value = false
  }
}

onMounted(async () => {
  await loadOverallAnalytics()
  loading.value = false
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

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px;
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
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--heading-color);
  line-height: 1.1;
  margin-bottom: 6px;
}

.kpi-hint {
  margin-top: auto;
  font-size: 0.72rem;
  color: var(--text-muted);
  padding-top: 8px;
  border-top: 1px dashed var(--border);
}

.kpi-gold { color: var(--accent-fill); background: var(--accent-light); }
.kpi-brown { color: #8B5A2B; background: rgba(139, 90, 43, 0.13); }
.kpi-brownDark { color: #5C3A21; background: rgba(92, 58, 33, 0.13); }
.kpi-tan { color: #C9A227; background: rgba(201, 162, 39, 0.14); }

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
  align-items: baseline;
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

.card-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.chart-box { height: 280px; position: relative; }
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

/* Insights Section */
.insights-section {
  margin-top: 24px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px;
  box-shadow: var(--shadow-sm);
}

.insights-head {
  margin-bottom: 16px;
}

.insights-head h3 {
  display: flex;
  align-items: center;
  gap: 8px;
}

.insights-head h3 i {
  color: var(--accent);
  font-size: 1.1rem;
}

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

.insight-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

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
.insight-info .insight-icon { color: #1976d2; background: rgba(25, 118, 210, 0.12); }

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

.note-foot {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: center;
  margin: 24px 0 0;
}

@media (max-width: 1280px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 1024px) {
  .chart-grid { grid-template-columns: 1fr; }
  .chart-card.wide { grid-column: span 1; }
}

@media (max-width: 640px) {
  .ana-page { padding: 96px 14px 40px; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .ana-header { align-items: flex-start; flex-direction: column; }
  .insights-grid { grid-template-columns: 1fr; }
}

@media (max-width: 420px) {
  .kpi-grid { grid-template-columns: 1fr; }
}
</style>
