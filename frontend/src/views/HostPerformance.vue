<template>
  <div class="host-page">
    <div class="hero-header">
      <h1><span class="accent-word">Performance</span> Insights</h1>
      <p>See how each of your experiences is performing.</p>
    </div>

    <LoadingSpinner v-if="loading" message="Loading performance data..." />

    <div v-else-if="store.hostPerformance.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/>
      </svg>
      <p>No experiences to analyze yet.</p>
      <router-link to="/host/register" class="btn-primary">Register Your First Hotspot</router-link>
    </div>

    <template v-else>
      <div class="summary-row">
        <div class="summary-card">
          <span class="summary-val">{{ store.hostPerformance.length }}</span>
          <span class="summary-lbl">Experiences</span>
        </div>
        <div class="summary-card">
          <span class="summary-val">{{ overallAvg }}</span>
          <span class="summary-lbl">Overall Avg Rating</span>
        </div>
        <div class="summary-card">
          <span class="summary-val">{{ totalReviews }}</span>
          <span class="summary-lbl">Total Reviews</span>
        </div>
        <div class="summary-card">
          <span class="summary-val">{{ improvingCount }}</span>
          <span class="summary-lbl">Trending Up</span>
        </div>
      </div>

      <div class="perf-list">
        <div v-for="item in store.hostPerformance" :key="item.experience_id" class="perf-card">
          <div class="perf-header">
            <div class="perf-title-row">
              <h3>{{ item.title }}</h3>
              <span :class="['trend-badge', item.trend]">
                <template v-if="item.trend === 'improving'">↗ Improving</template>
                <template v-else-if="item.trend === 'declining'">↘ Declining</template>
                <template v-else>→ Stable</template>
              </span>
            </div>
            <div class="perf-meta">
              <span class="category-tag">{{ item.category }}</span>
              <span class="location-text">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
                {{ item.location }}
              </span>
            </div>
          </div>

          <div class="perf-body">
            <div class="rating-big">
              <span class="big-num">{{ item.avg_rating || 'N/A' }}</span>
              <div class="big-stars">
                <span v-for="s in 5" :key="s" class="star" :class="{ filled: s <= Math.round(item.avg_rating || 0) }">&#9733;</span>
              </div>
              <span class="review-count">{{ item.total_ratings }} reviews</span>
            </div>

            <div class="star-bars">
              <div v-for="s in [5,4,3,2,1]" :key="s" class="bar-row">
                <span class="bar-label">{{ s }}★</span>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: getBarWidth(item.star_distribution[s] || 0, item.total_ratings) }"></div>
                </div>
                <span class="bar-count">{{ item.star_distribution[s] || 0 }}</span>
              </div>
            </div>
          </div>

          <div class="perf-footer">
            <span class="footer-stat">{{ item.unique_reviewers }} unique guests</span>
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

const overallAvg = computed(() => {
  const items = store.hostPerformance.filter(i => i.avg_rating > 0)
  if (items.length === 0) return '0.0'
  const sum = items.reduce((a, i) => a + i.avg_rating, 0)
  return (sum / items.length).toFixed(1)
})

const totalReviews = computed(() => store.hostPerformance.reduce((a, i) => a + i.total_ratings, 0))

const improvingCount = computed(() => store.hostPerformance.filter(i => i.trend === 'improving').length)

function getBarWidth(count, total) {
  if (total === 0) return '0%'
  return `${(count / total) * 100}%`
}

onMounted(async () => {
  await store.fetchHostPerformance()
  loading.value = false
})
</script>

<style scoped>
.host-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
  position: relative;
  min-height: 100vh;
  padding: 5rem 1rem 2rem;
}

.host-page::before {
  content: "";
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.15);
  z-index: 0;
}

.host-page > * {
  position: relative;
  z-index: 1;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.hero-header {
  text-align: center;
  padding: 40px 20px 32px;
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
  color: rgba(255, 255, 255, 0.94);
  max-width: 520px;
  margin: 0 auto;
  line-height: 1.6;
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 12px;
  padding: 1.25rem;
  text-align: center;
}

.summary-val {
  display: block;
  font-size: 1.8rem;
  font-weight: 800;
  font-family: 'Poppins', sans-serif;
  color: var(--accent);
  line-height: 1;
}

.summary-lbl {
  display: block;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.88);
  margin-top: 4px;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: rgba(255, 255, 255, 0.88);
}

.btn-primary {
  margin-top: 1rem;
  padding: 0.6rem 1.25rem;
  background: var(--accent);
  color: #1a1a1a;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(255, 255, 255, 0.45);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

.perf-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.perf-card {
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 12px;
  padding: 1.25rem;
}

.perf-header {
  margin-bottom: 1rem;
}

.perf-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.4rem;
}

.perf-title-row h3 {
  margin: 0;
  color: #fff;
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
}

.trend-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.trend-badge.improving { background: rgba(129, 199, 132, 0.2); color: #81C784; }
.trend-badge.declining { background: rgba(239, 83, 80, 0.2); color: #EF9A9A; }
.trend-badge.stable { background: rgba(255, 255, 255, 0.26); color: rgba(255, 255, 255, 0.88); }

.perf-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.category-tag {
  padding: 0.2rem 0.6rem;
  background: rgba(255, 255, 255, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 6px;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.94);
}

.location-text {
  display: flex;
  align-items: center;
  gap: 4px;
  color: rgba(255, 255, 255, 0.88);
  font-size: 0.85rem;
}

.perf-body {
  display: flex;
  gap: 2rem;
  align-items: center;
  margin-bottom: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.20);
  border-radius: 10px;
}

.rating-big {
  text-align: center;
  min-width: 100px;
}

.big-num {
  display: block;
  font-size: 2.2rem;
  font-weight: 800;
  font-family: 'Poppins', sans-serif;
  color: var(--accent);
  line-height: 1;
}

.big-stars {
  display: flex;
  justify-content: center;
  gap: 2px;
  margin: 4px 0;
}

.star { color: rgba(255, 255, 255, 0.55); font-size: 1rem; }
.star.filled { color: var(--accent); }

.review-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.80);
}

.star-bars {
  flex: 1;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 4px;
}

.bar-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.88);
  min-width: 28px;
  text-align: right;
}

.bar-track {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.26);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 4px;
  transition: width 0.3s;
}

.bar-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.88);
  min-width: 20px;
}

.perf-footer {
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.28);
}

.footer-stat {
  color: rgba(255, 255, 255, 0.80);
  font-size: 0.85rem;
}
</style>
