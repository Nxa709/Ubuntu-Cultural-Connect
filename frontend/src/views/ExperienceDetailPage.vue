<template>
  <div class="detail-page">
    <LoadingSpinner v-if="loading" message="Loading experience..." />

    <template v-else-if="exp">
      <div class="detail-hero" :style="{ backgroundImage: `url(${exp.image_url || getCategoryImage(exp.category)})` }">
        <div class="detail-hero-overlay"></div>
        <div class="detail-hero-content">
          <button class="back-link" @click="goBack">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
            </svg>
            Back
          </button>
          <span class="cat-badge">{{ exp.category }}</span>
          <h1>{{ exp.title }}</h1>
          <div class="hero-meta">
            <span class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
              </svg>
              {{ exp.location }}<template v-if="exp.province">, {{ exp.province }}</template>
            </span>
          </div>
        </div>
      </div>

      <!-- Itinerary Banner -->
      <div v-if="currentTripInfo" class="itinerary-banner">
        <div class="banner-left">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
          </svg>
          <div>
            <span class="banner-title">{{ currentTripInfo.title }}</span>
            <span class="banner-meta">{{ formatDate(currentTripInfo.start_date) }} â€“ {{ formatDate(currentTripInfo.end_date) }} &middot; {{ currentTripInfo.entryCount }} activit{{ currentTripInfo.entryCount === 1 ? 'y' : 'ies' }}</span>
          </div>
        </div>
        <router-link :to="`/plan-trip?trip=${currentTripInfo.id}`" class="banner-link">
          View Itinerary &rarr;
        </router-link>
      </div>

      <div class="detail-body">
        <div class="main-content">
          <div class="section">
            <h2>About This Experience</h2>
            <div class="description-full">
              <p>{{ exp.description }}</p>
            </div>
          </div>

          <div class="section" v-if="exp.location">
            <h2>Location</h2>
            <div class="location-detail">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
              </svg>
              <div>
                <span class="loc-main">{{ exp.location }}</span>
                <span class="loc-province">{{ exp.province ? exp.province + ' Province' : 'South Africa' }}</span>
              </div>
            </div>
            <div class="map-container" v-if="mapQuery">
              <iframe
                :src="`https://www.google.com/maps?q=${mapQuery}&output=embed`"
                title="Google Map"
                loading="lazy"
                allowfullscreen
                referrerpolicy="no-referrer-when-downgrade"
              ></iframe>
              <a
                class="map-open-link"
                :href="`https://www.google.com/maps?q=${mapQuery}`"
                target="_blank"
                rel="noopener noreferrer"
              >
                Open in Google Maps
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
              </a>
            </div>
          </div>

          <div class="section">
            <h2>Hosted By</h2>
            <div class="host-card">
              <div class="host-avatar">{{ (exp.owner_name || 'H').charAt(0) }}</div>
              <div class="host-info">
                <span class="host-name">{{ exp.owner_name || 'Host' }}</span>
                <span class="host-label">Cultural Experience Host</span>
              </div>
            </div>
          </div>

          <div class="section">
            <h2>Guest Reviews ({{ reviews.length }})</h2>

            <div v-if="reviews.length === 0" class="no-reviews">
              <p>No reviews yet. Be the first to review this experience!</p>
            </div>

            <div v-else class="reviews-summary">
              <div class="summary-stats">
                <span class="big-rating">{{ exp.avg_rating }}</span>
                <div class="summary-stars">
                  <span v-for="s in 5" :key="s" class="star" :class="{ filled: s <= Math.round(exp.avg_rating || 0) }">&#9733;</span>
                </div>
                <span class="summary-count">Based on {{ exp.rating_count }} reviews</span>
              </div>

              <div class="star-breakdown">
                <div v-for="s in [5,4,3,2,1]" :key="s" class="bar-row">
                  <span class="bar-label">{{ s }}â˜…</span>
                  <div class="bar-track">
                    <div class="bar-fill" :style="{ width: getStarPercent(s) + '%' }"></div>
                  </div>
                  <span class="bar-count">{{ getStarCount(s) }}</span>
                </div>
              </div>
            </div>

            <div class="reviews-list">
              <div v-for="review in reviews" :key="review.id" class="review-card">
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

        <div class="sidebar">
          <div class="sidebar-card sticky">
            <div class="sidebar-price">
              <span class="price-val">{{ formatPrice(exp.price) }}</span>
              <span class="price-lbl" v-if="exp.price > 0">Our services range from this price</span>
            </div>

            <div class="sidebar-details">
              <div class="detail-row">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                </svg>
                <span>{{ exp.location }}</span>
              </div>
              <div class="detail-row" v-if="exp.province">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
                </svg>
                <span>{{ exp.province }} Province</span>
              </div>
            </div>

            <template v-if="auth.isBusinessOwner && auth.user?.id === exp.owner_id">
              <router-link :to="`/host/edit/${exp.id}`" class="btn-trip-full edit-btn">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                Edit Hotspot
              </router-link>
            </template>
            <template v-else-if="auth.isTourist">
              <button class="btn-trip-full" @click="openItineraryModal" :disabled="addingToTrip">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
                </svg>
                {{ addingToTrip ? 'Adding...' : 'Add to Itinerary' }}
              </button>
            </template>

            <!-- Mini Itinerary Card -->
            <div v-if="currentTripInfo" class="mini-itinerary">
              <div class="mini-itinerary-header">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
                </svg>
                Your Itinerary
              </div>
              <div class="mini-itinerary-body">
                <div class="mini-trip-name">{{ currentTripInfo.title }}</div>
                <div class="mini-trip-dates">{{ formatDate(currentTripInfo.start_date) }} â€“ {{ formatDate(currentTripInfo.end_date) }}</div>
                <div class="mini-trip-entries">{{ currentTripInfo.entryCount }} activit{{ currentTripInfo.entryCount === 1 ? 'y' : 'ies' }}</div>
              </div>
              <router-link :to="`/plan-trip?trip=${currentTripInfo.id}`" class="mini-itinerary-link">
                View Full Itinerary &rarr;
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="empty-state">
      <p>Experience not found.</p>
      <router-link to="/experiences" class="back-link">Browse Experiences</router-link>
    </div>

    <AddToItineraryModal
      v-if="auth.isTourist"
      :experience="exp"
      :visible="showItineraryModal"
      @close="showItineraryModal = false"
      @success="handleItinerarySuccess"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useExperienceStore } from '../stores/experience'
import { useAuthStore } from '../stores/auth'
import AddToItineraryModal from '../components/AddToItineraryModal.vue'
import { formatPrice } from '../utils/format'

const route = useRoute()
const router = useRouter()
const store = useExperienceStore()
const auth = useAuthStore()

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}
const exp = ref(null)
const reviews = ref([])
const loading = ref(true)
const addingToTrip = ref(false)
const currentTripInfo = ref(null)
const showItineraryModal = ref(false)

const mapQuery = computed(() => {
  if (!exp.value || !exp.value.location) return ''
  const parts = [exp.value.location, exp.value.province, 'South Africa'].filter(Boolean)
  return encodeURIComponent(parts.join(', '))
})

const categoryImages = {
  'Traditional Cooking': '/img/cultures/Rural.jpg',
  'Storytelling': '/img/cultures/KwaMaiMai.jpg',
  'Music & Dance': '/img/cultures/Rasta.jpeg',
  'Crafts & Art': '/img/cultures/Ndebele.jpg',
  'Heritage Tours': '/img/cultures/Jepe.jpg',
  'Township Life': '/img/cultures/KwaMaiMai.jpg',
  'Rural Heritage': '/img/cultures/Rural.jpg',
  'Traditional Healing': '/img/cultures/Xhosa.jpg',
  'Textile & Weaving': '/img/cultures/Vhenda.jpg',
  'Photography Tours': '/img/cultures/Safari.jpg',
  'Nature & Wildlife': '/img/cultures/Safari.jpg',
  'Accommodation & Lodging': '/img/cultures/Rural.jpg',
}

function getCategoryImage(cat) {
  return categoryImages[cat] || '/img/cultures/Safari.jpg'
}

function getStarCount(star) {
  const dist = reviews.value.reduce((acc, r) => {
    acc[r.score] = (acc[r.score] || 0) + 1
    return acc
  }, {})
  return dist[star] || 0
}

function getStarPercent(star) {
  if (reviews.value.length === 0) return 0
  return (getStarCount(star) / reviews.value.length) * 100
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-ZA', { year: 'numeric', month: 'short', day: 'numeric' })
}

function openItineraryModal() {
  if (!auth.isLoggedIn) { router.push('/login'); return }
  showItineraryModal.value = true
}

function handleItinerarySuccess(tripInfo) {
  if (tripInfo) {
    currentTripInfo.value = tripInfo
  }
}

onMounted(async () => {
  try {
    const id = parseInt(route.params.id)
    ;[exp.value, reviews.value] = await Promise.all([
      store.getExperience(id),
      store.getRatings(id),
    ])
  } catch (e) {
    exp.value = null
  }
  loading.value = false
})
</script>

<style scoped>
.detail-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center top;
  background-size: cover;
  background-attachment: fixed;
  position: relative;
  min-height: 100vh;
}

.detail-page::before {
  content: "";
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.15);
  z-index: 0;
}

.detail-page > * {
  position: relative;
  z-index: 1;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8rem 2rem;
  color: rgba(255, 255, 255, 0.88);
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

.detail-hero {
  position: relative;
  height: 400px;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: flex-end;
}

.detail-hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.1) 100%);
}

.detail-hero-content {
  position: relative;
  z-index: 1;
  padding: 2rem;
  max-width: 1100px;
  margin: 0 auto;
  width: 100%;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.28);
  border: 1px solid rgba(255, 255, 255, 0.55);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 1rem;
  padding: 8px 18px;
  border-radius: 50px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: all 0.25s ease;
  width: fit-content;
}

.back-link:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: #1a1a1a;
  transform: translateX(-3px);
  box-shadow: 0 4px 16px rgba(255, 182, 18, 0.35);
}

.back-link:active {
  transform: translateX(-1px) scale(0.97);
}

.cat-badge {
  display: inline-block;
  padding: 0.3rem 0.9rem;
  background: rgba(255, 182, 18, 0.2);
  border: 1px solid rgba(255, 182, 18, 0.4);
  border-radius: 20px;
  color: var(--accent);
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.75rem;
}

.detail-hero-content h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 2.5rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 0.75rem;
  line-height: 1.2;
}

.hero-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #fff;
  font-size: 0.95rem;
}

/* Itinerary Banner */
.itinerary-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1100px;
  margin: 0 auto;
  padding: 10px 20px;
  background: rgba(255, 182, 18, 0.12);
  border: 1px solid rgba(255, 182, 18, 0.25);
  border-radius: 10px;
  animation: fadeIn 0.35s ease;
}
.banner-left {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--accent);
}
.banner-left svg { flex-shrink: 0; }
.banner-title {
  display: block;
  font-size: 0.88rem;
  font-weight: 600;
  color: #fff;
}
.banner-meta {
  font-size: 0.75rem;
  color: #fff;
}
.banner-link {
  font-size: 0.82rem;
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
  white-space: nowrap;
  transition: opacity 0.2s;
}
.banner-link:hover { opacity: 0.8; }

.detail-body {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem;
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 2rem;
  align-items: start;
}

.section {
  margin-bottom: 2rem;
}

.section h2 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.3rem;
  font-weight: 700;
  color: #fff;
  margin: 0 0 1rem;
}

.description-full p {
  color: #fff;
  line-height: 1.8;
  font-size: 1rem;
}

.location-detail {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  color: #fff;
}

.loc-main {
  display: block;
  font-weight: 600;
  color: #fff;
}

.loc-province {
  display: block;
  font-size: 0.9rem;
  color: #fff;
}

.map-container {
  margin-top: 1.25rem;
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 12px;
  padding: 0.75rem;
}

.map-container iframe {
  width: 100%;
  height: 320px;
  border: none;
  border-radius: 10px;
  display: block;
  background: #dde3e8;
}

.map-open-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.75rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--accent);
  text-decoration: none;
}

.map-open-link:hover {
  color: var(--accent-hover);
}

.host-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 12px;
  padding: 1.25rem;
}

.host-avatar {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  background: rgba(255, 182, 18, 0.2);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  font-weight: 700;
  font-family: 'Poppins', sans-serif;
}

.host-name {
  display: block;
  font-weight: 600;
  color: #fff;
}

.host-label {
  display: block;
  font-size: 0.85rem;
  color: #fff;
}

.no-reviews p {
  color: #fff;
  font-style: italic;
}

.reviews-summary {
  display: flex;
  gap: 2rem;
  align-items: center;
  background: rgba(255, 255, 255, 0.22);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.summary-stats {
  text-align: center;
  min-width: 120px;
}

.big-rating {
  display: block;
  font-size: 2.5rem;
  font-weight: 800;
  font-family: 'Poppins', sans-serif;
  color: var(--accent);
  line-height: 1;
}

.summary-stars {
  display: flex;
  justify-content: center;
  gap: 2px;
  margin: 4px 0;
}

.summary-count {
  font-size: 0.8rem;
  color: #fff;
}

.star-breakdown { flex: 1; }

.bar-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 4px;
}

.bar-label {
  font-size: 0.8rem;
  color: #fff;
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
  color: #fff;
  min-width: 20px;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.review-card {
  background: rgba(255, 255, 255, 0.26);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.38);
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
  gap: 0.6rem;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(255, 182, 18, 0.2);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  font-family: 'Poppins', sans-serif;
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
  color: #fff;
}

.review-stars {
  display: flex;
  gap: 2px;
}

.star { color: rgba(255, 255, 255, 0.55); font-size: 1rem; }
.star.filled { color: var(--accent); }

.review-comment p {
  color: #fff;
  line-height: 1.6;
  margin: 0;
  font-size: 0.95rem;
}

.sidebar {
  position: sticky;
  top: 90px;
}

.sidebar-card {
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 12px;
  padding: 1.5rem;
}

.sidebar-price {
  text-align: center;
  margin-bottom: 1.25rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.28);
}

.price-val {
  display: block;
  font-size: 2rem;
  font-weight: 800;
  font-family: 'Poppins', sans-serif;
  color: var(--accent);
}

.price-lbl {
  color: #fff;
  font-size: 0.9rem;
}

.sidebar-details {
  margin-bottom: 1.25rem;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0;
  color: #fff;
  font-size: 0.95rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.20);
}

.detail-row:last-child { border-bottom: none; }

.detail-row svg {
  color: var(--accent);
  flex-shrink: 0;
}

/* Mini Itinerary Card */
.mini-itinerary {
  margin-top: 12px;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.30);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.20);
  animation: fadeIn 0.35s ease;
}
.mini-itinerary-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 8px;
}
.mini-itinerary-body {
  margin-bottom: 8px;
}
.mini-trip-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
}
.mini-trip-dates {
  font-size: 0.75rem;
  color: #fff;
  margin-top: 1px;
}
.mini-trip-entries {
  font-size: 0.75rem;
  color: var(--accent);
  margin-top: 3px;
}
.mini-itinerary-link {
  display: block;
  text-align: center;
  font-size: 0.8rem;
  color: var(--accent);
  text-decoration: none;
  padding: 6px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.24);
  margin-top: 6px;
  font-weight: 500;
  transition: opacity 0.2s;
}
.mini-itinerary-link:hover {
  opacity: 0.8;
}

.btn-rate-full, .btn-trip-full {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  margin-bottom: 0.75rem;
}

.btn-rate-full {
  background: var(--accent);
  color: #1a1a1a;
}

.btn-rate-full:hover {
  background: #fff;
}

.btn-trip-full {
  background: var(--accent);
  color: #1a1a1a;
  border: 1px solid var(--accent);
}

.btn-trip-full:hover {
  background: #fff;
  color: #1a1a1a;
  border-color: #fff;
}

.btn-trip-full.edit-btn {
  background: var(--accent);
  color: #1a1a1a;
  border-color: var(--accent);
}
.btn-trip-full.edit-btn:hover {
  background: #fff;
  border-color: #fff;
}

@media (max-width: 900px) {
  .detail-body {
    grid-template-columns: 1fr;
  }
  .detail-hero-content h1 {
    font-size: 1.8rem;
  }
}

</style>
