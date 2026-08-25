<template>
  <div class="rate-page">
    <div class="hero-header">
      <h1><span class="accent-word">Rate</span> Your Experience</h1>
      <p>Share your feedback to help other tourists discover great cultural experiences.</p>
    </div>

    <LoadingSpinner v-if="loading" message="Loading experience..." />

    <div class="rate-layout" v-if="experience">
      <div class="card exp-info-card">
        <div class="exp-header" :style="{ backgroundImage: `url(${experience.image_url || getCategoryImage(experience.category)})` }">
          <span class="exp-cat">{{ experience.category }}</span>
        </div>
        <div class="exp-body">
          <h2>{{ experience.title }}</h2>
          <p class="exp-desc">{{ experience.description }}</p>
          <div class="exp-meta">
            <span>{{ experience.location }}</span>
            <span v-if="experience.duration_hours">{{ experience.duration_hours }}h</span>
          </div>
          <div class="exp-rating-summary" v-if="experience.avg_rating">
            <span class="avg-score">{{ experience.avg_rating }}</span>
            <span class="avg-label">Average from {{ experience.rating_count }} reviews</span>
          </div>
        </div>
      </div>

      <div class="card rate-form-card">
        <h2>Your Review</h2>

        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>

        <form @submit.prevent="handleSubmit" v-if="!submitted">
          <div class="form-group">
            <label>Rating</label>
            <div class="star-rating">
              <button
                v-for="n in 5"
                :key="n"
                type="button"
                class="star-btn"
                :class="{ filled: n <= score }"
                @click="score = n"
                @mouseenter="hoverScore = n"
                @mouseleave="hoverScore = 0"
              >
                <svg width="28" height="28" viewBox="0 0 24 24" :fill="n <= (hoverScore || score) ? 'var(--accent)' : 'none'" :stroke="n <= (hoverScore || score) ? 'var(--accent)' : '#E8E2DC'" stroke-width="2">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
              </button>
            </div>
            <span class="score-label" v-if="score">{{ scoreLabels[score - 1] }}</span>
          </div>

          <div class="form-group">
            <label>Comment (optional)</label>
            <textarea v-model="comment" rows="4" maxlength="500" placeholder="Tell us about your experience..."></textarea>
            <span class="char-count">{{ comment.length }}/500</span>
          </div>

          <button type="submit" class="btn btn-primary" :disabled="submitting || score === 0">
            {{ submitting ? 'Submitting...' : 'Submit Review' }}
          </button>
        </form>

        <div class="success-message" v-else>
          <div class="success-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#2E7D32" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <h3>Thank you for your feedback!</h3>
          <p>Your review helps other tourists discover great experiences.</p>
          <router-link to="/experiences" class="btn btn-outline">Back to Experiences</router-link>
        </div>
      </div>

      <div class="card reviews-card">
        <h3>Recent Reviews</h3>
        <div v-if="ratings.length === 0" class="no-reviews">
          <p>No reviews yet. Be the first to rate this experience!</p>
        </div>
        <div class="review-list" v-else>
          <div class="review-item" v-for="r in ratings" :key="r.id">
            <div class="review-header">
              <div class="review-avatar">{{ r.user_name?.charAt(0) || '?' }}</div>
              <div class="review-meta">
                <span class="review-name">{{ r.user_name || 'Anonymous' }}</span>
                <span class="review-date">{{ formatDate(r.created_at) }}</span>
              </div>
              <div class="review-score">
                <span v-for="n in 5" :key="n" class="mini-star" :class="{ filled: n <= r.score }">★</span>
              </div>
            </div>
            <p class="review-comment" v-if="r.comment">{{ r.comment }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else-if="!loading">
      <p>Experience not found.</p>
      <router-link to="/experiences" class="btn btn-outline">Browse Experiences</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useExperienceStore } from '../stores/experience'

const route = useRoute()
const store = useExperienceStore()

const experience = ref(null)
const ratings = ref([])
const score = ref(0)
const hoverScore = ref(0)
const comment = ref('')
const submitting = ref(false)
const submitted = ref(false)
const loading = ref(true)
const error = ref('')
const success = ref('')

const scoreLabels = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent']

onMounted(async () => {
  try {
    const id = route.params.id
    ;[experience.value, ratings.value] = await Promise.all([
      store.getExperience(id),
      store.getRatings(id),
    ])
  } catch (e) {
    error.value = 'Failed to load experience'
  } finally {
    loading.value = false
  }
})

async function handleSubmit() {
  if (score.value === 0) return
  submitting.value = true
  error.value = ''
  success.value = ''

  try {
    await store.submitRating(route.params.id, {
      score: score.value,
      comment: comment.value || null,
    })
    submitted.value = true
    success.value = 'Review submitted successfully!'
    ratings.value = await store.getRatings(route.params.id)
    experience.value = await store.getExperience(route.params.id)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to submit review'
  } finally {
    submitting.value = false
  }
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-ZA', { month: 'short', day: 'numeric', year: 'numeric' })
}

function getCategoryColor(cat) {
  const colors = {
    'Traditional Cooking': 'var(--accent)', 'Storytelling': '#6B2A2A', 'Music & Dance': 'var(--heading-color)',
    'Crafts & Art': '#5C4033', 'Heritage Tours': '#4A3228', 'Township Life': '#1a1a1a',
    'Rural Heritage': '#8B6914', 'Traditional Healing': '#2E7D32', 'Textile & Weaving': '#7B5B3A',
    'Photography Tours': '#5D4037', 'Nature & Wildlife': '#2E7D32', 'Accommodation & Lodging': '#6B4F3A',
  }
  return colors[cat] || 'var(--heading-color)'
}

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
</script>

<style scoped>
.rate-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center top;
  background-size: cover;
  position: relative;
  min-height: 100vh;
  padding: 100px 20px 40px;
}

.rate-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.15);
  z-index: 0;
}

.rate-page > * {
  position: relative;
  z-index: 1;
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

.rate-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  max-width: 1100px;
  margin: 0 auto;
}

@media (max-width: 900px) {
  .rate-layout {
    grid-template-columns: 1fr;
  }
  .exp-info-card {
    grid-row: auto;
  }
}

.card {
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.exp-info-card {
  padding: 0;
  overflow: hidden;
  grid-row: 1 / 3;
}

.exp-header {
  height: 120px;
  display: flex;
  align-items: flex-end;
  padding: 16px;
  background-size: cover;
  background-position: center;
}

.exp-cat {
  background: rgba(255, 255, 255, 0.9);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 6px;
}

.exp-body { padding: 20px; }
.exp-body h2 { color: var(--heading-color); font-size: 1.2rem; margin-bottom: 8px; }
.exp-desc { color: var(--text-secondary); font-size: 0.88rem; line-height: 1.5; margin-bottom: 14px; }

.exp-meta {
  display: flex;
  gap: 16px;
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.exp-rating-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.45);
}

.avg-score {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--accent);
}

.avg-label { font-size: 0.82rem; color: rgba(255, 255, 255, 0.88); }

.rate-form-card h2 { color: var(--heading-color); font-size: 1.1rem; margin-bottom: 20px; }

.form-group { margin-bottom: 18px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: #fff; font-size: 0.88rem; }

.star-rating { display: flex; gap: 4px; }

.star-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px;
  transition: transform 0.15s;
}

.star-btn:hover { transform: scale(1.2); }

.score-label {
  display: inline-block;
  margin-top: 6px;
  font-size: 0.85rem;
  color: var(--accent);
  font-weight: 500;
}

textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  resize: vertical;
}

textarea:focus { outline: none; border-color: rgba(255, 255, 255, 0.60); }

.char-count {
  display: block;
  text-align: right;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.88);
  margin-top: 4px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  font-family: inherit;
}

.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--accent-fill); color: #1a1a1a; }
.btn-primary:hover:not(:disabled) { background: var(--accent-fill-hover); }
.btn-outline { background: var(--surface); color: var(--text-color); border: 1px solid var(--border-strong); }

.alert { padding: 10px 14px; border-radius: 8px; margin-bottom: 16px; font-size: 0.88rem; }
.alert-error { background: #FDE8E8; color: #C0392B; }
.alert-success { background: #E8F5E9; color: #2E7D32; }

.success-message {
  text-align: center;
  padding: 30px 0;
}

.success-icon { margin-bottom: 16px; }
.success-message h3 { color: #2E7D32; margin-bottom: 8px; }
.success-message p { color: var(--text-secondary); margin-bottom: 20px; }

.reviews-card h3 { color: #fff; font-size: 1.05rem; margin-bottom: 16px; }
.no-reviews { color: rgba(255, 255, 255, 0.88); font-size: 0.88rem; }

.review-list { display: flex; flex-direction: column; gap: 14px; }

.review-item {
  padding: 14px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.45);
}

.review-item:last-child { border-bottom: none; }

.review-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.review-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #5C4033;
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.review-meta { flex: 1; }

.review-name { display: block; font-weight: 500; font-size: 0.88rem; color: #fff; }
.review-date { font-size: 0.75rem; color: rgba(255, 255, 255, 0.88); }

.review-score { display: flex; gap: 1px; }

.mini-star { color: #E8E2DC; font-size: 0.9rem; }
.mini-star.filled { color: var(--accent); }

.review-comment { font-size: 0.88rem; color: rgba(255, 255, 255, 0.94); line-height: 1.5; }

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.88);
}
</style>
