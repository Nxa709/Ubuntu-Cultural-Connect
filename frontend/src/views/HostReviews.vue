<template>
  <div class="host-page">
    <div class="hero-header">
      <h1><span class="accent-word">Guest</span> Reviews</h1>
      <p>See what guests are saying about each of your hotspots.</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading reviews...</p>
    </div>

    <template v-else>
      <div class="stats-bar">
        <div class="stat">
          <span class="stat-val">{{ totalReviews }}</span>
          <span class="stat-lbl">Total Reviews</span>
        </div>
        <div class="stat">
          <span class="stat-val">{{ averageRating }}</span>
          <span class="stat-lbl">Average Rating</span>
        </div>
        <div class="stat">
          <span class="stat-val">{{ hotspotCount }}</span>
          <span class="stat-lbl">Hotspots</span>
        </div>
        <div class="stat">
          <span class="stat-val">{{ uniqueGuests }}</span>
          <span class="stat-lbl">Unique Guests</span>
        </div>
      </div>

      <div v-if="hotspotGroups.length === 0" class="empty-state">
        <p>No reviews yet.</p>
      </div>

      <div v-else class="hotspot-reviews">
        <div v-for="group in hotspotGroups" :key="group.experience_id" class="hotspot-group">
          <div class="hotspot-group-header">
            <div class="hotspot-group-title">
              <h2>{{ group.title }}</h2>
              <span class="hs-rating" v-if="group.avgRating">
                &#9733; {{ group.avgRating }} ({{ group.reviews.length }})
              </span>
            </div>
          </div>

          <div v-if="group.reviews.length === 0" class="no-reviews">
            No reviews for this hotspot yet.
          </div>

          <div v-else class="reviews-list">
            <div v-for="review in group.reviews" :key="review.id" class="review-card">
              <div class="review-header">
                <div class="review-user">
                  <div class="user-avatar">{{ (review.user_name || 'A').charAt(0) }}</div>
                  <div>
                    <span class="user-name">{{ review.user_name || 'Anonymous' }}</span>
                    <span class="review-date">{{ formatDate(review.created_at) }}</span>
                  </div>
                </div>
                <div class="review-stars">
                  <span v-for="s in 5" :key="s" class="star" :class="{ filled: s <= review.score }">&#9733;</span>
                </div>
              </div>
              <div class="review-comment" v-if="review.comment">
                <p>{{ review.comment }}</p>
              </div>
            </div>
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

const hotspotGroups = computed(() => {
  const groups = {}
  for (const review of store.hostReviews) {
    const key = review.experience_id
    if (!groups[key]) {
      groups[key] = {
        experience_id: key,
        title: review.experience_title || 'Unknown Hotspot',
        reviews: [],
      }
    }
    groups[key].reviews.push(review)
  }
  const result = Object.values(groups)
  for (const group of result) {
    if (group.reviews.length > 0) {
      const sum = group.reviews.reduce((a, r) => a + r.score, 0)
      group.avgRating = (sum / group.reviews.length).toFixed(1)
    }
  }
  return result
})

const totalReviews = computed(() => store.hostReviews.length)
const hotspotCount = computed(() => hotspotGroups.value.length)

const averageRating = computed(() => {
  if (store.hostReviews.length === 0) return '0.0'
  const sum = store.hostReviews.reduce((a, r) => a + r.score, 0)
  return (sum / store.hostReviews.length).toFixed(1)
})

const uniqueGuests = computed(() => new Set(store.hostReviews.map(r => r.user_name)).size)

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-ZA', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(async () => {
  await Promise.all([
    store.fetchHostReviews(),
  ])
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
  background: rgba(0, 0, 0, 0.55);
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
  color: rgba(255, 255, 255, 0.7);
  max-width: 520px;
  margin: 0 auto;
  line-height: 1.6;
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

.hotspot-reviews {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.hotspot-group {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  padding: 1.25rem;
}

.hotspot-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.hotspot-group-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hotspot-group-title h2 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
  margin: 0;
  font-family: 'Poppins', sans-serif;
}

.hs-rating {
  font-size: 0.85rem;
  color: var(--accent);
}

.no-reviews {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  font-style: italic;
  padding: 8px 0;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.review-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1rem;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.review-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255, 182, 18, 0.2);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-family: 'Poppins', sans-serif;
  flex-shrink: 0;
}

.user-name {
  display: block;
  font-weight: 600;
  color: #fff;
  font-size: 0.9rem;
}

.review-date {
  display: block;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

.review-stars {
  display: flex;
  gap: 2px;
}

.star { color: rgba(255, 255, 255, 0.25); font-size: 1rem; }
.star.filled { color: var(--accent); }

.review-comment p {
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.6;
  margin: 0;
  font-size: 0.88rem;
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
</style>
