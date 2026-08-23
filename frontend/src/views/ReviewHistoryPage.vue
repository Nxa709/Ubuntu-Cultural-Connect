<template>
  <div class="review-page">
    <div class="hero-header">
      <h1><span class="accent-word">Review</span> History</h1>
      <p>All your ratings and reviews in one place.</p>
    </div>

    <div class="review-content">
      <LoadingSpinner v-if="loading" message="Loading reviews..." />

      <div v-else-if="store.myReviews.length === 0" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
        <p>You haven't reviewed any experiences yet.</p>
        <router-link to="/experiences" class="btn-browse">Browse Experiences</router-link>
      </div>

      <template v-else>
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
          <div v-for="review in store.myReviews" :key="review.id" class="review-card">
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useExperienceStore } from '../stores/experience'

const store = useExperienceStore()
const loading = ref(true)

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
  background: #ffffff;
  position: relative;
  min-height: 100vh;
}

.hero-header {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  position: relative;
  text-align: center;
  padding: 120px 20px 60px;
}

.hero-header::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 0;
}

.hero-header > * {
  position: relative;
  z-index: 1;
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
  color: rgba(255, 255, 255, 0.94);
  max-width: 520px;
  margin: 0 auto;
  line-height: 1.6;
}

.review-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #888;
}

.empty-state svg {
  color: var(--accent);
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(0, 0, 0, 0.1);
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

.stats-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  padding: 1.25rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
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
  color: #666;
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.review-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s, box-shadow 0.3s;
}

.review-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
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
  color: #1a1a1a;
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
  color: #2E7D32;
}

.status-badge.pending {
  background: rgba(255, 183, 77, 0.2);
  color: #B26A00;
}

.status-badge.rejected {
  background: rgba(239, 83, 80, 0.2);
  color: #C62828;
}

.review-location {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 0.85rem;
}

.review-stars {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 4px;
}

.star {
  color: #ddd;
  font-size: 1.1rem;
}

.star.filled {
  color: var(--accent);
}

.score-text {
  color: #666;
  font-size: 0.85rem;
  margin-left: 6px;
}

.review-comment p {
  color: #333;
  line-height: 1.6;
  margin: 0 0 0.75rem;
}

.review-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid #eaeaea;
}

.review-date {
  color: #888;
  font-size: 0.8rem;
}

.btn-view {
  padding: 0.35rem 0.75rem;
  background: rgba(255, 182, 18, 0.15);
  color: var(--accent);
  text-decoration: none;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-view:hover {
  background: var(--accent);
  color: #1a1a1a;
}

@media (max-width: 768px) {
  .hero-header h1 {
    font-size: 2rem;
  }
  .hero-header {
    padding: 100px 20px 40px;
  }
  .stats-bar {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
