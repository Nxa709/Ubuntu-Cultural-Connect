<template>
  <div class="review-page">
    <div class="hero-header">
      <h1><span class="accent-word">Review</span> History</h1>
      <p>All your ratings and reviews in one place.</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading reviews...</p>
    </div>

    <div v-else-if="store.myReviews.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
      </svg>
      <p>You haven't reviewed any experiences yet.</p>
      <router-link to="/experiences" class="btn-browse">Browse Experiences</router-link>
    </div>

    <template v-else>
      <div class="search-box">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input v-model="searchQuery" placeholder="Search reviews by experience, location, or comment..." />
      </div>

      <div v-if="filteredReviews.length === 0" class="empty-state no-results">
        <p>No reviews match "{{ searchQuery }}".</p>
      </div>

      <div class="stats-bar">
        <div class="stat">
          <span class="stat-val">{{ store.myReviews.length }}</span>
          <span class="stat-lbl">Total Reviews</span>
        </div>
        <div class="stat">
          <span class="stat-val">{{ averageRating }}</span>
          <span class="stat-lbl">Average Rating</span>
        </div>
        <div class="stat">
          <span class="stat-val">{{ approvedCount }}</span>
          <span class="stat-lbl">Approved</span>
        </div>
        <div class="stat">
          <span class="stat-val">{{ pendingCount }}</span>
          <span class="stat-lbl">Pending</span>
        </div>
      </div>

      <div class="reviews-list">
        <div v-for="review in filteredReviews" :key="review.id" class="review-card">
          <div class="review-header">
            <div class="review-title-row">
              <h3>{{ review.experience_title || 'Unknown Experience' }}</h3>
              <span :class="['status-badge', reviewStatus(review)]">{{ reviewStatusText(review) }}</span>
            </div>
            <div class="review-location" v-if="review.experience_location">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
              {{ review.experience_location }}
            </div>
          </div>

          <div class="review-stars">
            <span v-for="s in 5" :key="s" class="star" :class="{ filled: s <= review.score }">&#9733;</span>
            <span class="score-text">{{ review.score }}/5</span>
          </div>

          <div class="review-comment" v-if="review.comment">
            <p>{{ review.comment }}</p>
          </div>

          <div class="review-footer">
            <span class="review-date">{{ formatDate(review.created_at) }}</span>
            <router-link
              :to="review.experience_id ? `/experience/${review.experience_id}` : `/experiences`"
              class="btn-view"
            >
              View Experience
            </router-link>
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
const searchQuery = ref('')

const filteredReviews = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return store.myReviews
  return store.myReviews.filter((r) => {
    return (
      (r.experience_title || '').toLowerCase().includes(q) ||
      (r.experience_location || '').toLowerCase().includes(q) ||
      (r.comment || '').toLowerCase().includes(q)
    )
  })
})

const averageRating = computed(() => {
  if (store.myReviews.length === 0) return '0.0'
  const sum = store.myReviews.reduce((acc, r) => acc + r.score, 0)
  return (sum / store.myReviews.length).toFixed(1)
})

const approvedCount = computed(() => {
  return store.myReviews.filter(r => r.is_approved && !r.rejected_at).length
})

const pendingCount = computed(() => {
  return store.myReviews.filter(r => !r.is_approved && !r.rejected_at).length
})

function reviewStatus(review) {
  if (review.rejected_at) return 'rejected'
  if (review.is_approved) return 'approved'
  return 'pending'
}

function reviewStatusText(review) {
  if (review.rejected_at) return 'Rejected'
  if (review.is_approved) return 'Approved'
  return 'Pending'
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-ZA', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

onMounted(async () => {
  await store.fetchMyReviews()
  loading.value = false
})
</script>

<style scoped>
.review-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
  position: relative;
  min-height: 100vh;
  padding: 5rem 1rem 2rem;
}

.review-page::before {
  content: "";
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 0;
}

.review-page > * {
  position: relative;
  z-index: 1;
  max-width: 800px;
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
  letter-spacing: -0.5px;
  line-height: 1.15;
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
  line-height: 1.6;
}

.loading-state, .empty-state {
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

.btn-browse {
  margin-top: 1rem;
  padding: 0.6rem 1.25rem;
  background: var(--accent);
  color: #1a1a1a;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.6rem 0.9rem;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 1.5rem;
}

.search-box input {
  width: 100%;
  background: none;
  border: none;
  outline: none;
  color: #fff;
  font-size: 0.95rem;
  font-family: inherit;
}

.search-box input::placeholder {
  color: rgba(255, 255, 255, 0.45);
}

.no-results {
  margin-bottom: 1.5rem;
}

.stats-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  padding: 1.25rem;
  text-align: center;
}

.stat-val {
  display: block;
  font-size: 1.8rem;
  font-weight: 800;
  font-family: 'Poppins', sans-serif;
  color: var(--accent);
  line-height: 1;
}

.stat-lbl {
  display: block;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.review-card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  padding: 1.25rem;
}

.review-header {
  margin-bottom: 0.5rem;
}

.review-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.3rem;
}

.review-title-row h3 {
  margin: 0;
  color: #fff;
  font-family: 'Poppins', sans-serif;
  font-size: 1.05rem;
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.status-badge.approved {
  background: rgba(129, 199, 132, 0.2);
  color: #81C784;
}

.status-badge.pending {
  background: rgba(255, 183, 77, 0.2);
  color: #FFB74D;
}

.status-badge.rejected {
  background: rgba(239, 83, 80, 0.2);
  color: #EF9A9A;
}

.review-location {
  display: flex;
  align-items: center;
  gap: 4px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
}

.review-stars {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 4px;
}

.star {
  color: rgba(255, 255, 255, 0.25);
  font-size: 1.1rem;
}

.star.filled {
  color: var(--accent);
}

.score-text {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  margin-left: 6px;
}

.review-comment p {
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.6;
  margin: 0 0 0.75rem;
}

.review-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.review-date {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.8rem;
}

.btn-view {
  padding: 0.35rem 0.75rem;
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  border-radius: 6px;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.btn-view:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}
</style>
