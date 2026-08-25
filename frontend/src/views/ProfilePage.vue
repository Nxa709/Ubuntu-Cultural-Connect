<template>
  <div class="profile-page">
    <div class="hero-header">
      <h1><span class="accent-word">My</span> Profile</h1>
      <p>{{ auth.isBusinessOwner ? 'Manage your business account, view performance metrics, and keep your information up to date.' : auth.isAdmin ? 'Your administration center. Monitor platform activity, manage users, and oversee registered hotspots.' : 'Your personal travel hub. Manage preferences, view your travel history, and review experiences.' }}</p>
    </div>

    <div v-if="success" class="alert alert-success">{{ success }}</div>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="profile-layout" :class="{ 'single-col': auth.isBusinessOwner || auth.isAdmin }">

      <!-- â”€â”€ LEFT COLUMN â”€â”€ -->
      <div class="left-col">

        <!-- User Information -->
        <div class="card">
          <div class="user-info-header">
            <div class="user-avatar-large">{{ initials }}</div>
            <div class="user-info-text">
              <h2>{{ auth.user?.full_name }}</h2>
              <span class="user-role-badge">{{ auth.userRole?.replace('_', ' ') }}</span>
            </div>
          </div>
          <div class="user-details">
            <div class="detail-row">
              <span class="detail-label">Email</span>
              <span class="detail-value">{{ auth.user?.email }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Phone</span>
              <span class="detail-value">{{ auth.user?.phone_number || 'Not provided' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Member Since</span>
              <span class="detail-value">{{ formatDate(auth.user?.created_at) }}</span>
            </div>
          </div>
          <button class="btn btn-primary" @click="showEditModal = true">Edit Profile</button>
        </div>

        <!-- Your Preferences -->
        <div class="card" v-if="auth.isTourist">
          <div class="section-header">
            <h2>Your Preferences</h2>
            <router-link to="/preferences" class="btn-link">Update</router-link>
          </div>
          <div v-if="preferences.length > 0" class="pref-tags">
            <span class="pref-tag" v-for="p in preferences" :key="p">{{ p }}</span>
          </div>
          <p v-else class="empty-text">No preferences set yet. <router-link to="/preferences">Tell us what you love</router-link> to get personalized recommendations.</p>
        </div>

        <!-- Business Summary (Business Owner only) -->
        <div class="card" v-if="auth.isBusinessOwner && ownerStats">
          <h2>Business Summary</h2>
          <div class="business-summary-grid">
            <div class="bs-item">
              <span class="bs-value">{{ ownerStats.total_hotspots }}</span>
              <span class="bs-label">Total Hotspots</span>
            </div>
            <div class="bs-item">
              <span class="bs-value active-v">{{ ownerStats.active_hotspots }}</span>
              <span class="bs-label">Active</span>
            </div>
            <div class="bs-item">
              <span class="bs-value pending-v">{{ ownerStats.pending_approval }}</span>
              <span class="bs-label">Pending Approval</span>
            </div>
            <div class="bs-item">
              <span class="bs-value">{{ ownerStats.total_ratings }}</span>
              <span class="bs-label">Total Reviews</span>
            </div>
            <div class="bs-item">
              <span class="bs-value">{{ ownerStats.avg_rating || '—' }}</span>
              <span class="bs-label">Avg Rating</span>
            </div>
            <div class="bs-item">
              <span class="bs-value">{{ ownerStats.total_categories }}</span>
              <span class="bs-label">Categories</span>
            </div>
          </div>
        </div>

        <!-- My Favorites -->
        <div class="card" v-if="auth.isTourist">
          <div class="section-header">
            <h2>My Favorites</h2>
            <span class="history-count">{{ favorites.length }} {{ favorites.length === 1 ? 'hotspot' : 'hotspots' }}</span>
          </div>
          <p v-if="favorites.length === 0" class="empty-text">No favorites yet. Tap the heart on any hotspot to save it here.</p>
          <div v-else class="favorites-grid">
            <router-link v-for="fav in favorites" :key="fav.id" :to="`/destination/${fav.id}`" class="favorite-card">
              <div class="favorite-img" :style="{ backgroundImage: `url(${fav.image})` }">
                <span class="favorite-badge">{{ fav.category }}</span>
                <button
                  class="favorite-remove"
                  :aria-label="'Remove from favorites'"
                  @click.prevent.stop="toggleFavorite(fav.id)"
                >
                  <i class="bi bi-heart-fill"></i>
                </button>
              </div>
              <div class="favorite-body">
                <h4>{{ fav.name }}</h4>
                <p class="favorite-loc">{{ fav.location }}</p>
                <span class="favorite-rating" v-if="fav.rating">&#9733; {{ fav.rating }}</span>
              </div>
            </router-link>
          </div>
        </div>

      </div>

      <!-- â”€â”€ RIGHT COLUMN â”€â”€ -->
      <div class="right-col" v-if="auth.isTourist">

        <!-- Travel History -->
        <div ref="historySection" class="card travel-history-card" v-if="!auth.isBusinessOwner">
          <div class="section-header">
            <h2>Travel History</h2>
            <span class="history-count">{{ travelHistory.length }} {{ travelHistory.length === 1 ? 'experience' : 'experiences' }}</span>
          </div>
          <p class="card-desc">Every experience you've added to your itinerary appears here. Only visited experiences can be reviewed.</p>

          <LoadingSpinner v-if="loadingHistory" size="sm" />

          <div v-else-if="travelHistory.length === 0" class="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
            </svg>
            <p>No travel history yet.</p>
            <router-link to="/experiences" class="btn-browse">Browse Experiences</router-link>
          </div>

          <div v-else class="history-list">
            <div v-for="(item, idx) in travelHistory" :key="idx" class="history-item">
              <div class="history-img" :style="{ backgroundImage: `url(${item.image || getCategoryImage(item.category)})` }">
                <span class="history-cat">{{ item.category }}</span>
              </div>
              <div class="history-body">
                <div class="history-top-row">
                  <h3>{{ item.name }}</h3>
                  <span class="history-province">{{ item.province || item.location }}</span>
                </div>
                <div class="history-meta">
                  <span class="history-date" v-if="item.addedDate">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/></svg>
                    Added: {{ item.addedDate }}
                  </span>
                  <span class="history-date" v-if="item.visitDate">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    Visit: {{ item.visitDate }}
                  </span>
                </div>

                <!-- Review Section -->
                <div class="history-review" v-if="item.experience_id">
                  <div v-if="submittingReview === item.experience_id" class="review-form">
                    <div class="star-rating">
                      <button v-for="n in 5" :key="n" type="button" class="star-btn" :class="{ filled: n <= (reviewForm.score) }" @click="reviewForm.score = n">
                        <svg width="20" height="20" viewBox="0 0 24 24" :fill="n <= reviewForm.score ? 'var(--accent)' : 'none'" :stroke="n <= reviewForm.score ? 'var(--accent)' : '#E8E2DC'" stroke-width="2">
                          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                        </svg>
                      </button>
                    </div>
                    <textarea v-model="reviewForm.comment" rows="2" maxlength="500" placeholder="Share your experience..." class="review-textarea"></textarea>
                    <div class="review-actions">
                      <button class="btn btn-primary btn-sm" @click="submitReview(item.experience_id)" :disabled="reviewForm.score === 0 || savingReview">Submit Review</button>
                      <button class="btn btn-outline btn-sm" @click="cancelReview">Cancel</button>
                    </div>
                  </div>

                  <div v-else-if="existingReview(item.experience_id)" class="existing-review">
                    <div class="existing-stars">
                      <span v-for="n in 5" :key="n" class="star" :class="{ filled: n <= existingReview(item.experience_id).score }">&#9733;</span>
                      <span class="existing-score">{{ existingReview(item.experience_id).score }}/5</span>
                    </div>
                    <p class="existing-comment" v-if="existingReview(item.experience_id).comment">{{ existingReview(item.experience_id).comment }}</p>
                    <button class="btn btn-link btn-xs" @click="editReview(item.experience_id)">Edit Review</button>
                  </div>

                  <div v-else>
                    <button class="btn btn-outline btn-sm" @click="startReview(item.experience_id)">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                      Rate &amp; Review
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal-card">
        <h3>Edit Profile</h3>
        <form @submit.prevent="handleUpdate">
          <div class="form-group">
            <label>Full Name</label>
            <input v-model="form.full_name" type="text" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input :value="auth.user?.email" type="email" disabled class="disabled-input" />
            <span class="field-note">Email cannot be changed</span>
          </div>
          <div class="form-group">
            <label>Phone Number</label>
            <input v-model="form.phone_number" type="tel" />
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? 'Saving...' : 'Save Changes' }}</button>
            <button type="button" class="btn btn-outline" @click="showEditModal = false">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useExperienceStore } from '../stores/experience'
import { getAllDestinations } from '../data/provinces'

const auth = useAuthStore()
const expStore = useExperienceStore()
const router = useRouter()

const form = reactive({
  full_name: '',
  phone_number: '',
})

const loading = ref(false)
const showEditModal = ref(false)
const success = ref('')
const error = ref('')

const preferences = ref([])

const favorites = ref([])

const travelHistory = ref([])
const loadingHistory = ref(false)
const ownerStats = ref(null)

const submittingReview = ref(null)
const savingReview = ref(false)
const reviewForm = reactive({ score: 0, comment: '' })

const historySection = ref(null)
const initials = computed(() => {
  const name = auth.user?.full_name || 'U'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
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

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-ZA', { year: 'numeric', month: 'short', day: 'numeric' })
}

function formatShortDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-ZA', { month: 'short', day: 'numeric' })
}

function loadFavorites() {
  let ids = []
  try {
    ids = JSON.parse(localStorage.getItem('ucc_wishlist') || '[]')
  } catch (e) { /* ignore */ }
  const all = getAllDestinations()
  favorites.value = ids
    .map(id => all.find(d => d.id === id))
    .filter(Boolean)
}

function toggleFavorite(id) {
  let ids = []
  try {
    ids = JSON.parse(localStorage.getItem('ucc_wishlist') || '[]')
  } catch (e) { /* ignore */ }
  ids = ids.filter(i => i !== id)
  try {
    localStorage.setItem('ucc_wishlist', JSON.stringify(ids))
  } catch (e) { /* ignore */ }
  loadFavorites()
}

function existingReview(expId) {
  return expStore.myReviews.find(r => r.experience_id === expId)
}

function startReview(expId) {
  if (!expId) return
  reviewForm.score = 0
  reviewForm.comment = ''
  submittingReview.value = expId
}

function editReview(expId) {
  const existing = existingReview(expId)
  if (existing) {
    reviewForm.score = existing.score
    reviewForm.comment = existing.comment || ''
    submittingReview.value = expId
  }
}

function cancelReview() {
  submittingReview.value = null
  reviewForm.score = 0
  reviewForm.comment = ''
}

async function submitReview(expId) {
  if (!expId || reviewForm.score === 0) return
  savingReview.value = true
  try {
    await expStore.submitRating(expId, {
      score: reviewForm.score,
      comment: reviewForm.comment || null,
    })
    await expStore.fetchMyReviews()
    submittingReview.value = null
    reviewForm.score = 0
    reviewForm.comment = ''
    success.value = 'Review submitted!'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to submit review'
    setTimeout(() => { error.value = '' }, 3000)
  } finally {
    savingReview.value = false
  }
}

async function loadTravelHistory() {
  loadingHistory.value = true
  try {
    // Authoritative list: every experience the tourist added to an itinerary
    // (from the ItineraryAdd records). Guarantees anything added shows up here.
    const rows = await expStore.fetchTravelHistory()
    travelHistory.value = (rows || []).map(r => ({
      name: r.title,
      location: r.location || '',
      province: r.province || '',
      category: r.category || 'Cultural Experience',
      image: r.image_url || null,
      experience_id: r.experience_id,
      tripTitle: r.trip_title || '',
      addedDate: r.added_at ? formatDate(r.added_at) : '',
      visitDate: '',
    }))
  } catch (e) {
    // silently fail
  } finally {
    loadingHistory.value = false
  }
}

onMounted(async () => {
  form.full_name = auth.user?.full_name || ''
  form.phone_number = auth.user?.phone_number || ''

  loadFavorites()

  try {
    await expStore.fetchPreferences()
    preferences.value = expStore.preferences
  } catch (e) { /* silently fail */ }

  if (auth.isBusinessOwner) {
    try {
      await expStore.fetchOwnerStats()
      ownerStats.value = expStore.ownerStats
    } catch (e) { /* silently fail */ }
  }

  await Promise.all([
    loadTravelHistory(),
    expStore.fetchMyReviews(),
  ])
})

async function handleUpdate() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await auth.updateProfile(form)
    success.value = 'Profile updated successfully!'
    showEditModal.value = false
    setTimeout(() => { success.value = '' }, 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Update failed.'
    setTimeout(() => { error.value = '' }, 3000)
  } finally {
    loading.value = false
  }
}

</script>

<style scoped>
.profile-page {
  position: relative;
  min-height: 100vh;
  padding: 0;
}

.profile-page > * {
  position: relative;
  z-index: 1;
}

.hero-header {
  text-align: center;
}

.hero-header h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 2.8rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 8px;
}

.hero-header .accent-word {
  font-family: 'Pacifico', cursive;
  font-weight: 400;
  color: var(--accent);
}

.hero-header p {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.94);
  max-width: 560px;
  margin: 0 auto;
  line-height: 1.6;
}

.alert {
  padding: 10px 14px;
  border-radius: 8px;
  margin: 16px auto;
  font-size: 0.88rem;
  max-width: 1100px;
}

.alert-error {
  background: rgba(255, 77, 77, 0.2);
  color: #ff6b6b;
  border: 1px solid rgba(255, 77, 77, 0.3);
}

.alert-success {
  background: rgba(76, 175, 80, 0.2);
  color: #81c784;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

/* Layout */
.profile-layout {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 20px 48px;
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 24px;
  align-items: start;
}

.profile-layout.single-col {
  grid-template-columns: 1fr;
  max-width: 600px;
}

.left-col, .right-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Card */
.card {
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 16px;
  padding: 24px;
  color: #fff;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.card h2 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.15rem;
  color: #fff;
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.section-header h2 {
  margin-bottom: 0;
}

/* User Info */
.user-info-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.user-avatar-large {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: rgba(232, 162, 0, 0.2);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  font-weight: 700;
  font-family: 'Poppins', sans-serif;
  flex-shrink: 0;
}

.user-info-text h2 {
  margin: 0 0 4px;
  font-size: 1.2rem;
}

.user-role-badge {
  display: inline-block;
  background: rgba(232, 162, 0, 0.2);
  color: var(--accent);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 0.72rem;
  text-transform: capitalize;
  font-weight: 500;
}

.user-details {
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.24);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 0.78rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 0.88rem;
  color: var(--text-color);
  text-align: right;
}

/* Preferences */
.pref-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.pref-tag {
  background: rgba(232, 162, 0, 0.2);
  color: var(--accent);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

/* Favorites */
.favorites-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
}

.favorite-card {
  background: var(--surface-secondary);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  text-decoration: none;
  color: var(--text-color);
  transition: transform 0.2s, box-shadow 0.2s;
}

.favorite-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.favorite-img {
  height: 90px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.favorite-badge {
  position: absolute;
  top: 6px;
  left: 6px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 0.65rem;
  padding: 2px 7px;
  border-radius: 4px;
  font-weight: 500;
}

.favorite-remove {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.55);
  border: none;
  border-radius: 50%;
  color: #ff4d4f;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.favorite-remove:hover {
  background: #ff4d4f;
  color: #fff;
  transform: scale(1.1);
}

.favorite-body {
  padding: 10px 12px;
}

.favorite-body h4 {
  font-size: 0.82rem;
  font-weight: 600;
  margin: 0 0 2px;
  color: var(--heading-color);
}

.favorite-loc {
  font-size: 0.72rem;
  color: var(--text-secondary);
  margin: 0 0 6px;
}

.favorite-rating {
  font-size: 0.72rem;
  color: var(--accent);
}

/* Business Summary */
.business-summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 8px;
}

.bs-item {
  background: var(--surface-secondary);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 10px;
  text-align: center;
}

.bs-value {
  display: block;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--heading-color);
  font-family: 'Poppins', sans-serif;
  line-height: 1;
}

.bs-value.active-v { color: var(--success); }
.bs-value.pending-v { color: var(--warning); }

.bs-label {
  display: block;
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

/* Travel History */
.travel-history-card .section-header {
  margin-bottom: 4px;
}

.history-count {
  font-size: 0.78rem;
  color: var(--text-secondary);
  background: var(--surface-secondary);
  border: 1px solid var(--border);
  padding: 2px 10px;
  border-radius: 20px;
}

.card-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin-bottom: 16px;
  line-height: 1.5;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.history-item {
  display: flex;
  gap: 14px;
  background: var(--surface-secondary);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  transition: border-color 0.2s;
}

.history-item:hover {
  border-color: var(--accent);
}

.history-img {
  width: 120px;
  min-height: 120px;
  background-size: cover;
  background-position: center;
  position: relative;
  flex-shrink: 0;
}

.history-cat {
  position: absolute;
  top: 6px;
  left: 6px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 0.6rem;
  padding: 2px 7px;
  border-radius: 4px;
  font-weight: 500;
}

.history-body {
  flex: 1;
  padding: 14px 14px 14px 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.history-top-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.history-top-row h3 {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--heading-color);
  margin: 0;
}

.history-province {
  font-size: 0.75rem;
  color: var(--text-secondary);
  white-space: nowrap;
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 1px 8px;
  border-radius: 4px;
}

.history-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.history-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.72rem;
  color: var(--text-secondary);
}

.history-date svg {
  flex-shrink: 0;
}

/* Review */
.history-review {
  margin-top: 4px;
}

.review-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.star-rating {
  display: flex;
  gap: 2px;
}

.star-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px;
  transition: transform 0.15s;
}

.star-btn:hover {
  transform: scale(1.2);
}

.review-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  background: var(--surface);
  color: var(--text-color);
  font-size: 0.82rem;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}

.review-textarea:focus {
  outline: none;
  border-color: var(--accent);
}

.review-actions {
  display: flex;
  gap: 8px;
}

.existing-review {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.existing-stars {
  display: flex;
  align-items: center;
  gap: 3px;
}

.star {
  color: #d1d5db;
  font-size: 0.95rem;
}

.star.filled {
  color: var(--accent);
}

.existing-score {
  font-size: 0.78rem;
  color: var(--text-secondary);
  margin-left: 4px;
}

.existing-comment {
  font-size: 0.82rem;
  color: var(--text-color);
  line-height: 1.5;
  margin: 0;
}

/* Buttons */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 600;
  transition: all 0.2s;
  font-family: inherit;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--accent-fill);
  color: #1a1a1a;
  width: 100%;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--accent-fill-hover);
}

.btn-outline {
  background: var(--surface);
  border: 1px solid var(--border-strong);
  color: var(--text-color);
}

.btn-outline:hover {
  border-color: var(--accent);
  color: var(--accent-text);
  background: var(--accent-light);
}

.btn-sm {
  padding: 6px 14px;
  font-size: 0.8rem;
}

.btn-xs {
  padding: 4px 10px;
  font-size: 0.72rem;
  background: none;
  border: none;
  color: var(--accent);
  cursor: pointer;
  font-family: inherit;
  font-weight: 500;
  width: fit-content;
}

.btn-xs:hover {
  text-decoration: underline;
}

.btn-link {
  font-size: 0.82rem;
  color: var(--accent);
  font-weight: 500;
  text-decoration: none;
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-browse {
  margin-top: 12px;
  display: inline-block;
  padding: 8px 18px;
  background: var(--accent-fill);
  color: #1a1a1a;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  width: 440px;
  max-width: 95vw;
  background: rgba(25, 25, 45, 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.38);
  border-radius: 16px;
  padding: 28px;
  color: #fff;
}

.modal-card h3 {
  font-size: 1.15rem;
  margin-bottom: 18px;
  font-family: 'Poppins', sans-serif;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.88);
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.38);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.22);
  color: #fff;
  font-size: 0.88rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-group input:focus {
  border-color: var(--accent);
}

.disabled-input {
  opacity: 0.6;
  cursor: not-allowed;
}

.field-note {
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.70);
  margin-top: 4px;
  display: block;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 6px;
}

.modal-actions .btn {
  flex: 1;
}

/* Empty / Loading */
.empty-text {
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.5;
}

.empty-text a {
  color: var(--accent);
  font-weight: 500;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px;
  color: rgba(255, 255, 255, 0.80);
  text-align: center;
}

.empty-state p {
  margin: 12px 0 0;
  font-size: 0.88rem;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(255, 255, 255, 0.38);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 900px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }

  .hero-header h1 {
    font-size: 2rem;
  }

  .history-img {
    width: 80px;
    min-height: 80px;
  }

  .favorites-grid {
    grid-template-columns: 1fr;
  }
}
</style>
