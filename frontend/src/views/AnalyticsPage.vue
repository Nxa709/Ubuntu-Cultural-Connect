<template>
  <div class="ana-page">
    <LoadingSpinner v-if="loading" message="Putting your numbers together..." />

    <template v-else>
      <!-- Header -->
      <header class="ana-header">
        <div class="ana-head-left">
          <h1>Analytics</h1>
          <p>Understand how your hotspots are performing and make informed business decisions.</p>
        </div>
        <div class="ana-head-right">
          <div class="date-select">
            <i class="bi bi-calendar3"></i>
            <select v-model="range" aria-label="Analytics period">
              <option v-for="r in RANGE_OPTIONS" :key="r.value" :value="r.value">{{ r.label }}</option>
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
          <div class="kpi-delta" v-if="k.delta !== null && k.delta !== undefined">
            <span class="delta-pill" :class="k.delta >= 0 ? 'up' : 'down'">
              <i :class="k.delta >= 0 ? 'bi-arrow-up-short' : 'bi-arrow-down-short'"></i>
              {{ Math.abs(k.delta).toFixed(0) }}%
            </span>
            <span class="kpi-vs">vs previous period</span>
          </div>
          <div class="kpi-delta" v-else><span class="kpi-vs">all-time snapshot</span></div>
          <span class="kpi-hint">{{ k.hint }}</span>
        </div>
      </div>

      <!-- Performance table + Insights -->
      <div class="grid-wide">
        <div class="card table-card span-2">
          <div class="card-head">
            <h2>Experience Performance</h2>
            <span class="card-sub">{{ rangeLabel }}</span>
          </div>
          <div class="table-scroll" v-if="experiencePerformance.length">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Experience</th>
                  <th>Views</th>
                  <th>Avg Rating</th>
                  <th>Reviews</th>
                  <th>Status</th>
                  <th>Trend</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in experiencePerformance" :key="row.id">
                  <td>
                    <div class="listing-cell">
                      <span class="thumb" :style="{ backgroundImage: `url(${row.image_url || fallbackImage})` }"></span>
                      <div class="listing-info">
                        <span class="listing-name">{{ row.title }}</span>
                        <span class="listing-cat">{{ row.category }}</span>
                      </div>
                    </div>
                  </td>
                  <td><strong>{{ row.views }}</strong></td>
                  <td>{{ row.avg_rating ? row.avg_rating.toFixed(1) : '—' }}</td>
                  <td>{{ row.reviews }}</td>
                  <td><span class="status-pill" :class="statusClass(row.status)">{{ row.status }}</span></td>
                  <td><span class="trend-badge" :class="trendClass(row.trend)">{{ trendText(row.trend) }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="no-data">No experiences yet.</div>
        </div>

        <div class="card insights-card">
          <div class="card-head">
            <h2>Business Insights</h2>
          </div>
          <div class="insight-list">
            <div class="insight-item" v-for="(ins, i) in insights" :key="i">
              <span class="insight-icon" :class="'kpi-' + ins.color"><i :class="['bi', ins.icon]"></i></span>
              <p class="insight-text">{{ ins.pre }}<strong>{{ ins.strong }}</strong>{{ ins.post }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts row -->
      <div class="grid-2">
        <div class="card">
          <div class="card-head">
            <h2>Most Viewed Experiences</h2>
            <span class="card-sub">{{ rangeLabel }}</span>
          </div>
          <div class="chart-wrap-md">
            <canvas v-if="mostViewed.length" ref="viewsEl"></canvas>
            <div v-else class="no-data">No interest data yet.</div>
          </div>
        </div>
        <div class="card">
          <div class="card-head">
            <h2>Visitor Interest Over Time</h2>
            <span class="card-sub">{{ rangeLabel }}</span>
          </div>
          <div class="chart-wrap-md">
            <canvas v-if="interestOverTime.length" ref="interestEl"></canvas>
            <div v-else class="no-data">No interest data yet.</div>
          </div>
        </div>
      </div>

      <!-- Customer satisfaction -->
      <div class="grid-3">
        <div class="card sat-card">
          <div class="card-head">
            <h2>Customer Satisfaction</h2>
          </div>
          <div class="sat-stats">
            <div class="sat-stat">
              <span class="sat-val">{{ totalReviews ? avgRating.toFixed(1) : '—' }}</span>
              <span class="sat-lbl">Avg Rating</span>
            </div>
            <div class="sat-stat">
              <span class="sat-val">{{ totalReviews }}</span>
              <span class="sat-lbl">Reviews</span>
            </div>
            <div class="sat-stat">
              <span class="sat-val">{{ totalReviews ? positivePct + '%' : '—' }}</span>
              <span class="sat-lbl">Positive (4★+)</span>
            </div>
          </div>
          <div class="chart-wrap-sm">
            <canvas v-if="starCount" ref="starsEl"></canvas>
            <div v-else class="no-data">No ratings yet.</div>
          </div>
        </div>

        <div class="card">
          <div class="card-head">
            <h2>What Visitors Mention</h2>
          </div>
          <div class="bar-list" v-if="themes.length">
            <div class="bar-row" v-for="t in themes" :key="t.key">
              <div class="bar-label-row">
                <span class="bar-name">{{ t.key }}</span>
                <span class="bar-pct">{{ t.count }}</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill brown-fill" :style="{ width: themePct(t) + '%' }"></div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">No comments in this period.</div>
        </div>

        <div class="card reviews-card">
          <div class="card-head">
            <h2>Recent Reviews</h2>
          </div>
          <div class="review-list" v-if="recentReviews.length">
            <div class="review-item" v-for="r in recentReviews" :key="r.id">
              <div class="review-top">
                <span class="review-name">{{ r.user_name }}</span>
                <span class="review-stars">{{ filledStars(r.score) }}</span>
              </div>
              <p class="review-text">{{ r.comment || 'No comment left.' }}</p>
              <span class="review-meta">{{ r.experience_title }} · {{ formatDate(r.created_at) }}</span>
            </div>
          </div>
          <div v-else class="no-data">No reviews in this period.</div>
        </div>
      </div>

      <!-- Visitor profile -->
      <div class="grid-wide">
        <div class="card span-2 visitor-card">
          <div class="card-head">
            <h2>Visitor Profile</h2>
          </div>
          <p class="visitor-text">
            Our system does not yet collect visitor demographics (origin, age group, interests),
            so we can't show who your visitors are. This period we tracked
            <strong>{{ uniqueVisitors }} unique visitors</strong> across
            <strong>{{ totalViews }} views</strong>.
          </p>
        </div>
      </div>

      <p class="note-foot">
        Views are measured as itinerary adds — how many times a traveller added an experience to their trip plan.
        This is the closest interest signal our system tracks.
      </p>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import { useExperienceStore } from '../stores/experience'

const store = useExperienceStore()

const loading = ref(true)
const range = ref('30d')
const stats = ref(null)
const overview = ref({
  total_views: 0,
  prev_total_views: 0,
  unique_visitors: 0,
  prev_unique_visitors: 0,
  avg_rating: 0,
  prev_avg_rating: 0,
  total_reviews: 0,
  prev_total_reviews: 0,
  positive_review_pct: 0,
  prev_positive_review_pct: 0,
  star_distribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
  interest_over_time: [],
  interest_granularity: 'month',
  experience_performance: [],
  recent_reviews: [],
})

const fallbackImage = '/img/cultures/Safari.jpg'

const RANGE_OPTIONS = [
  { value: '7d', label: 'Last 7 days' },
  { value: '30d', label: 'Last 30 days' },
  { value: '90d', label: 'Last 3 months' },
  { value: '180d', label: 'Last 6 months' },
  { value: '365d', label: 'Last year' },
  { value: 'all', label: 'All time' },
]

const PALETTE = {
  gold: '#FFB612',
  brown: '#8B5A2B',
  brownDark: '#5C3A21',
  brownMid: '#A67C52',
  tan: '#C9A227',
  cream: '#F5EFE3',
}

const STAR_COLORS = { 1: '#5C3A21', 2: '#8B5A2B', 3: '#A67C52', 4: '#C9A227', 5: '#FFB612' }

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const rangeLabel = computed(() => RANGE_OPTIONS.find(r => r.value === range.value)?.label || 'All time')

/* ---------- KPIs ---------- */

const kpis = computed(() => {
  const o = overview.value
  const s = stats.value || {}
  const delta = (cur, prev) => (prev ? Math.round(((cur - prev) / prev) * 100) : null)
  return [
    { label: 'Total Views', value: o.total_views ?? 0, icon: 'bi-eye', color: 'brown', delta: delta(o.total_views, o.prev_total_views), hint: 'Itinerary adds' },
    { label: 'Unique Visitors', value: o.unique_visitors ?? 0, icon: 'bi-people', color: 'gold', delta: delta(o.unique_visitors, o.prev_unique_visitors), hint: 'Distinct travellers' },
    { label: 'Average Rating', value: o.total_reviews ? o.avg_rating : null, icon: 'bi-star-fill', color: 'tan', delta: delta(o.avg_rating, o.prev_avg_rating), hint: 'Out of 5' },
    { label: 'Total Reviews', value: o.total_reviews ?? 0, icon: 'bi-chat-square-text', color: 'brownMid', delta: delta(o.total_reviews, o.prev_total_reviews), hint: 'Ratings received' },
    { label: 'Active Experiences', value: s.active_hotspots ?? 0, icon: 'bi-check-circle', color: 'brownDark', delta: null, hint: 'Live & approved' },
    { label: 'Positive Reviews', value: o.total_reviews ? o.positive_review_pct + '%' : null, icon: 'bi-hand-thumbs-up', color: 'gold', delta: delta(o.positive_review_pct, o.prev_positive_review_pct), hint: '4★ and above' },
  ]
})

function formatValue(k) {
  if (k.value === null || k.value === undefined) return '—'
  return String(k.value)
}

/* ---------- Tables & charts data ---------- */

const experiencePerformance = computed(() => overview.value.experience_performance || [])
const mostViewed = computed(() => experiencePerformance.value.filter(e => e.views > 0).slice(0, 8))
const interestOverTime = computed(() => overview.value.interest_over_time || [])
const starDistribution = computed(() => overview.value.star_distribution || {})
const starCount = computed(() => Object.values(starDistribution.value).reduce((s, v) => s + (v || 0), 0))
const recentReviews = computed(() => overview.value.recent_reviews || [])

const totalReviews = computed(() => overview.value.total_reviews || 0)
const avgRating = computed(() => overview.value.avg_rating || 0)
const positivePct = computed(() => overview.value.positive_review_pct || 0)
const totalViews = computed(() => overview.value.total_views || 0)
const uniqueVisitors = computed(() => overview.value.unique_visitors || 0)

function statusClass(status) {
  const map = {
    Excellent: 's-excellent',
    Good: 's-good',
    'Needs attention': 's-warn',
    Critical: 's-critical',
    'No reviews': 's-none',
  }
  return map[status] || 's-none'
}

function trendText(trend) {
  if (trend === 'improving') return '↑ Improving'
  if (trend === 'declining') return '↓ Declining'
  if (trend === 'no ratings') return '— No prior ratings'
  return '→ Stable'
}

function trendClass(trend) {
  if (trend === 'improving') return 't-improving'
  if (trend === 'declining') return 't-declining'
  if (trend === 'no ratings') return 't-none'
  return 't-stable'
}

/* ---------- Review themes (keyword-based, real comments) ---------- */

const THEMES = [
  { key: 'Guides & hosts', words: ['guide', 'host', 'sangoma', 'healer', 'welcom', 'knowledgeable', 'friendly', 'passion'] },
  { key: 'Culture & heritage', words: ['culture', 'tradition', 'heritage', 'zulu', 'authentic', 'african'] },
  { key: 'Food & meals', words: ['food', 'meal', 'breakfast', 'lunch', 'dinner', 'cuisine', 'delicious', 'cook', 'eat'] },
  { key: 'Storytelling', words: ['story', 'tale', 'legend', 'folklore', 'narrat'] },
  { key: 'Music & dance', words: ['music', 'dance', 'drum', 'song', 'sing', 'perform'] },
  { key: 'Views & setting', words: ['view', 'scenic', 'beautiful', 'location', 'ocean', 'beach', 'setting'] },
  { key: 'Organisation', words: ['organi', 'arrang', 'well', 'smooth', 'professional', 'seamless'] },
  { key: 'Value for money', words: ['price', 'worth', 'value', 'expensive', 'cost', 'cheap'] },
]

const themes = computed(() => {
  const counts = {}
  for (const r of recentReviews.value) {
    const text = (r.comment || '').toLowerCase()
    if (!text) continue
    for (const t of THEMES) {
      if (t.words.some(w => text.includes(w))) counts[t.key] = (counts[t.key] || 0) + 1
    }
  }
  return Object.entries(counts)
    .map(([key, count]) => ({ key, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6)
})

function themePct(t) {
  const max = themes.value[0]?.count || 1
  return Math.round((t.count / max) * 100)
}

/* ---------- Actionable insights (real data only) ---------- */

const insights = computed(() => {
  const list = []
  const o = overview.value
  const perf = o.experience_performance || []

  if (perf.length && o.total_views > 0) {
    const top = [...perf].sort((a, b) => b.views - a.views)[0]
    if (top && top.views > 0) {
      list.push({
        icon: 'bi-eye', color: 'brown',
        pre: `"${top.title}" is your most viewed experience (${top.views} view${top.views === 1 ? '' : 's'} this period). `,
        strong: 'Promote it more prominently', post: ' to capitalise on existing interest.',
      })
    }
  }

  const lowInterest = perf.filter(p => p.views === 0)
  if (lowInterest.length && perf.length > lowInterest.length) {
    const names = lowInterest.slice(0, 3).map(p => `"${p.title}"`).join(', ')
    list.push({
      icon: 'bi-graph-down-arrow', color: 'tan',
      pre: `${lowInterest.length} experience(s) drew no interest this period (${names}). `,
      strong: 'Improve descriptions, images or positioning', post: ' to attract attention.',
    })
  }

  const needsAttention = perf.filter(p => p.status === 'Needs attention' || p.status === 'Critical')
  if (needsAttention.length) {
    const names = needsAttention.slice(0, 3).map(p => `"${p.title}"`).join(', ')
    list.push({
      icon: 'bi-exclamation-triangle', color: 'brownDark',
      pre: `${needsAttention.length} experience(s) have low ratings (${names}). `,
      strong: 'Review recent feedback', post: ' and address any recurring issues.',
    })
  }

  if (o.prev_total_reviews > 0 && o.prev_avg_rating > 0) {
    const diff = o.avg_rating - o.prev_avg_rating
    if (diff >= 0.2) {
      list.push({
        icon: 'bi-star-fill', color: 'gold',
        pre: `Average rating improved to ${o.avg_rating}★ from ${o.prev_avg_rating}★. `,
        strong: 'Keep doing what works', post: ' and repeat it across your experiences.',
      })
    } else if (diff <= -0.2) {
      list.push({
        icon: 'bi-star-half', color: 'brownDark',
        pre: `Average rating dropped to ${o.avg_rating}★ from ${o.prev_avg_rating}★. `,
        strong: 'Check recent feedback', post: ' to identify what changed.',
      })
    }
  }

  const it = o.interest_over_time || []
  if (it.length >= 2) {
    const first = it[0].count
    const last = it[it.length - 1].count
    if (last > first) {
      list.push({
        icon: 'bi-graph-up-arrow', color: 'brown',
        pre: `Interest is rising (${first} → ${last} per ${o.interest_granularity} over the period). `,
        strong: 'Scale up promotion', post: ' while momentum is high.',
      })
    } else if (last < first) {
      list.push({
        icon: 'bi-graph-down-arrow', color: 'tan',
        pre: `Interest has declined (${first} → ${last}). `,
        strong: 'Refresh your listings', post: ' or try new marketing to reverse the trend.',
      })
    }
  }

  const sd = o.star_distribution || {}
  const low = (sd[1] || 0) + (sd[2] || 0)
  if (low > 0 && o.total_reviews > 0) {
    list.push({
      icon: 'bi-chat-square-text', color: 'brownDark',
      pre: `${low} of your ${o.total_reviews} review(s) were 1-2★. `,
      strong: 'Read the low ratings', post: ' and act on recurring concerns.',
    })
  }

  if (!list.length) {
    list.push({
      icon: 'bi-lightbulb', color: 'gold',
      pre: 'Add experiences and collect reviews / itinerary adds to ',
      strong: 'unlock insights', post: ' about your business.',
    })
  }
  return list.slice(0, 5)
})

/* ---------- Export ---------- */

function exportReport() {
  const rows = [['Metric', 'Value', 'Period']]
  for (const k of kpis.value) rows.push([k.label, k.value === null || k.value === undefined ? '—' : String(k.value), rangeLabel.value])
  rows.push(['', '', ''])
  rows.push(['Experience', 'Views', 'Avg Rating', 'Reviews', 'Status'])
  for (const p of experiencePerformance.value) {
    rows.push([p.title, String(p.views), p.avg_rating ? String(p.avg_rating) : '—', String(p.reviews), p.status])
  }
  const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `analytics-report-${range.value}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/* ---------- Formatting ---------- */

function periodLabel(period, granularity) {
  if (granularity === 'day') {
    const [y, m, d] = period.split('-').map(Number)
    return `${MONTHS[m - 1]} ${d}`
  }
  const [y, m] = period.split('-').map(Number)
  return `${MONTHS[m - 1]} '${String(y).slice(2)}`
}

function shortTitle(t) {
  return t && t.length > 18 ? t.slice(0, 18) + '…' : t
}

function filledStars(score) {
  return '★'.repeat(score) + '☆'.repeat(5 - score)
}

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}`
}

/* ---------- Charts ---------- */

const viewsEl = ref(null)
const interestEl = ref(null)
const starsEl = ref(null)
let charts = []

function destroyCharts() {
  charts.forEach(c => c.destroy())
  charts = []
}

function renderCharts() {
  destroyCharts()

  const textColor = '#6c757d'
  const gridColor = 'rgba(0,0,0,0.06)'
  const axisColor = 'rgba(0,0,0,0.12)'

  if (viewsEl.value && mostViewed.value.length) {
    charts.push(new Chart(viewsEl.value, {
      type: 'bar',
      data: {
        labels: mostViewed.value.map(e => shortTitle(e.title)),
        datasets: [{
          label: 'Views',
          data: mostViewed.value.map(e => e.views),
          backgroundColor: mostViewed.value.map((e, i) => (i === 0 ? PALETTE.gold : PALETTE.brownMid)),
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
          x: { beginAtZero: true, grid: { color: gridColor }, ticks: { color: textColor, precision: 0, font: { size: 11 } }, border: { color: axisColor } },
          y: { grid: { display: false }, ticks: { color: textColor, font: { size: 10 } }, border: { color: axisColor } },
        },
      },
    }))
  }

  if (interestEl.value && interestOverTime.value.length) {
    charts.push(new Chart(interestEl.value, {
      type: 'line',
      data: {
        labels: interestOverTime.value.map(d => periodLabel(d.period, overview.value.interest_granularity)),
        datasets: [{
          label: 'Interest',
          data: interestOverTime.value.map(d => d.count),
          borderColor: PALETTE.gold,
          backgroundColor: 'rgba(139, 90, 43, 0.12)',
          fill: true,
          tension: 0.35,
          pointBackgroundColor: PALETTE.brown,
          pointRadius: 4,
          pointHoverRadius: 5,
          borderWidth: 2.5,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: textColor, font: { size: 10 }, maxRotation: 45, minRotation: 0 }, border: { color: axisColor } },
          y: { beginAtZero: true, grid: { color: gridColor }, ticks: { color: textColor, precision: 0, font: { size: 11 } }, border: { color: axisColor } },
        },
      },
    }))
  }

  if (starsEl.value && starCount.value > 0) {
    const sd = starDistribution.value
    const labels = []
    const data = []
    const colors = []
    for (let i = 5; i >= 1; i--) {
      if (sd[i]) {
        labels.push(`${i}★`)
        data.push(sd[i])
        colors.push(STAR_COLORS[i])
      }
    }
    charts.push(new Chart(starsEl.value, {
      type: 'doughnut',
      data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 2, borderColor: '#ffffff' }] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, boxHeight: 12, font: { size: 10 }, color: textColor, padding: 10 } },
        },
      },
    }))
  }
}

/* ---------- Data loading ---------- */

watch(range, async () => {
  try {
    overview.value = (await store.getAnalytics(range.value)) || overview.value
  } catch (e) {
    console.error('Failed to reload analytics', e)
  }
  await nextTick()
  renderCharts()
})

onMounted(async () => {
  const results = await Promise.allSettled([
    store.fetchOwnerStats(),
    store.getAnalytics(range.value),
  ])
  if (results[0].status === 'fulfilled') stats.value = results[0].value || store.ownerStats || null
  if (results[1].status === 'fulfilled' && results[1].value) overview.value = results[1].value
  loading.value = false
  await nextTick()
  renderCharts()
})

onUnmounted(() => {
  destroyCharts()
})
</script>

<style scoped>
.ana-page {
  min-height: 100vh;
  background: #f4f6f9;
  padding: 96px 28px 40px;
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
  margin-bottom: 6px;
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

.kpi-hint {
  margin-top: auto;
  font-size: 0.72rem;
  color: #98a2b3;
  padding-top: 8px;
  border-top: 1px dashed #eef1f5;
}

/* KPI color accents */
.kpi-gold { color: #FFB612; }
.kpi-brown { color: #8B5A2B; }
.kpi-brownDark { color: #5C3A21; }
.kpi-brownMid { color: #A67C52; }
.kpi-tan { color: #C9A227; }

.kpi-icon.kpi-gold { background: rgba(255, 182, 18, 0.14); }
.kpi-icon.kpi-brown { background: rgba(139, 90, 43, 0.13); }
.kpi-icon.kpi-brownDark { background: rgba(92, 58, 33, 0.13); }
.kpi-icon.kpi-brownMid { background: rgba(166, 124, 82, 0.14); }
.kpi-icon.kpi-tan { background: rgba(201, 162, 39, 0.14); }

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

/* Layout rows */
.grid-wide {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
  align-items: start;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
  align-items: start;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
  align-items: start;
}

.span-2 {
  grid-column: span 1;
}

.chart-wrap-md { height: 260px; position: relative; }
.chart-wrap-sm { height: 200px; position: relative; }

/* Table */
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
  min-width: 170px;
}

.thumb {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
}

.listing-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.listing-name {
  font-weight: 500;
  color: var(--heading-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.listing-cat {
  font-size: 0.72rem;
  color: #98a2b3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.status-pill {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 999px;
  white-space: nowrap;
}

.s-excellent { background: rgba(139, 90, 43, 0.12); color: #6B4423; }
.s-good { background: rgba(81, 207, 102, 0.14); color: #1f8a3c; }
.s-warn { background: rgba(201, 162, 39, 0.18); color: #8a6d1a; }
.s-critical { background: rgba(255, 107, 107, 0.15); color: #d64545; }
.s-none { background: rgba(108, 117, 125, 0.12); color: #6c757d; }

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
.trend-badge.t-improving { background: rgba(81, 207, 102, 0.15); color: #1f8a3c; }
.trend-badge.t-declining { background: rgba(255, 107, 107, 0.15); color: #d64545; }
.trend-badge.t-stable { background: rgba(77, 171, 247, 0.14); color: #2f7fc1; }
.trend-badge.t-none { background: rgba(108, 117, 125, 0.12); color: #6c757d; }

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

.insight-icon.kpi-gold { background: rgba(255, 182, 18, 0.14); }
.insight-icon.kpi-brown { background: rgba(139, 90, 43, 0.13); }
.insight-icon.kpi-brownDark { background: rgba(92, 58, 33, 0.13); }
.insight-icon.kpi-tan { background: rgba(201, 162, 39, 0.14); }

.insight-text {
  font-size: 0.8rem;
  color: #6c757d;
  line-height: 1.55;
  margin: 0;
}

.insight-text strong {
  color: var(--heading-color);
  font-weight: 700;
}

/* Satisfaction */
.sat-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 14px;
}

.sat-stat {
  text-align: center;
  background: #faf7f2;
  border: 1px solid #f0e9dd;
  border-radius: 10px;
  padding: 12px 8px;
}

.sat-val {
  display: block;
  font-family: 'Poppins', sans-serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: #16212f;
}

.sat-lbl {
  display: block;
  font-size: 0.7rem;
  color: #98a2b3;
  margin-top: 2px;
}

/* Bars */
.bar-list { display: flex; flex-direction: column; gap: 12px; }

.bar-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 5px;
}

.bar-name { font-size: 0.82rem; color: #495057; }
.bar-pct { font-size: 0.8rem; font-weight: 700; color: #16212f; }

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

.bar-fill.brown-fill {
  background: linear-gradient(90deg, #5C3A21, #C9A227);
}

/* Recent reviews */
.review-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 320px;
  overflow-y: auto;
}

.review-item {
  border-bottom: 1px solid #f2f4f7;
  padding-bottom: 12px;
}

.review-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.review-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
}

.review-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: #16212f;
}

.review-stars {
  font-size: 0.82rem;
  color: var(--accent);
  letter-spacing: 1px;
}

.review-text {
  font-size: 0.8rem;
  color: #495057;
  line-height: 1.5;
  margin: 0 0 4px;
}

.review-meta {
  font-size: 0.72rem;
  color: #98a2b3;
}

/* Visitor card */
.visitor-card { grid-column: span 2; }

.visitor-text {
  font-size: 0.85rem;
  color: #495057;
  line-height: 1.6;
  margin: 0;
}

.visitor-text strong {
  color: #16212f;
}

.note-foot {
  font-size: 0.75rem;
  color: #98a2b3;
  text-align: center;
  margin: 0;
  padding: 4px 0 8px;
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
  .grid-3 { grid-template-columns: 1fr; }
}

@media (max-width: 1024px) {
  .grid-wide { grid-template-columns: 1fr; }
  .grid-2 { grid-template-columns: 1fr; }
  .visitor-card { grid-column: span 1; }
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
