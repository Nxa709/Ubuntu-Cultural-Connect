<template>
  <div class="host-page">
    <div class="hero-header">
      <h1><span class="accent-word">My</span> Hotspots</h1>
      <p>Manage your cultural experiences</p>
      <router-link to="/host/register" class="btn btn-primary hero-btn">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        Register New Hotspot
      </router-link>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading your hotspots...</p>
    </div>

    <template v-else>
      <div class="filter-bar">
        <button
          v-for="f in filters"
          :key="f.value"
          :class="['filter-btn', { active: activeFilter === f.value }]"
          @click="activeFilter = f.value"
        >
          {{ f.label }}
          <span v-if="f.count !== undefined" class="count">{{ f.count }}</span>
        </button>
      </div>

      <div class="search-bar">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input v-model="searchQuery" type="text" placeholder="Search your hotspots..." class="search-input" />
      </div>

      <div v-if="filteredExps.length === 0" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
          <circle cx="12" cy="10" r="3"/>
        </svg>
        <p v-if="activeFilter === 'all'">You haven't registered any hotspots yet.</p>
        <p v-else>No {{ activeFilter }} hotspots found.</p>
        <router-link to="/host/register" class="btn btn-primary" v-if="activeFilter === 'all'">
          Register Your First Hotspot
        </router-link>
      </div>

      <div v-else class="hotspots-grid">
        <div v-for="exp in filteredExps" :key="exp.id" class="hotspot-card">
          <div class="hc-hero" :style="{ backgroundImage: `url(${exp.image_url || getCategoryImage(exp.category)})` }" @click="$router.push(`/experience/${exp.id}`)" style="cursor: pointer;">
            <div class="hc-hero-overlay"></div>
            <div class="hc-hero-content">
              <span class="hc-status" :class="statusClass(exp)">{{ statusLabel(exp) }}</span>
              <h3>{{ exp.title }}</h3>
              <span class="hc-location">{{ exp.location }}{{ exp.province ? ', ' + exp.province : '' }}</span>
            </div>
          </div>

          <div class="hc-body">
            <div v-if="exp.rejection_reason" class="rejection-banner">
              <strong>Rejected:</strong> {{ exp.rejection_reason }}
            </div>
            <div class="hc-stats">
              <div class="hc-stat">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
                <span>{{ exp.avg_rating ? exp.avg_rating + ' (' + exp.rating_count + ')' : 'No ratings' }}</span>
              </div>
              <div class="hc-stat">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
                <span>R{{ exp.price }}</span>
              </div>
              <div class="hc-stat">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
                </svg>
                <span>{{ exp.itinerary_adds || 0 }} itinerary {{ exp.itinerary_adds === 1 ? 'add' : 'adds' }}</span>
              </div>
              <div class="hc-stat">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                </svg>
                <span>{{ exp.duration_hours ? exp.duration_hours + 'h' : '—' }}</span>
              </div>
            </div>
          </div>

          <div class="hc-actions">
            <router-link :to="`/host/edit/${exp.id}`" class="hc-btn" :class="exp.rejected_at ? 'hc-btn-appeal' : 'hc-btn-edit'">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              {{ exp.rejected_at ? 'Appeal' : 'Edit' }}
            </router-link>
            <button v-if="!exp.rejected_at" @click="handleToggle(exp)" class="hc-btn" :class="exp.is_active ? 'hc-btn-deactivate' : 'hc-btn-activate'" :disabled="toggling">
              {{ exp.is_active ? 'Deactivate' : 'Activate' }}
            </button>
            <button @click="handleDelete(exp)" class="hc-btn hc-btn-delete">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
              Delete
            </button>
          </div>

          <div class="hc-reviews" v-if="getReviews(exp.id).length > 0">
            <div class="hc-reviews-header" @click="toggleReviews(exp.id)">
              <span>Reviews ({{ getReviews(exp.id).length }})</span>
              <span class="hc-reviews-arrow" :class="{ open: openReviews[exp.id] }">&#9660;</span>
            </div>
            <div class="hc-reviews-body" v-if="openReviews[exp.id]">
              <div v-for="r in getReviews(exp.id)" :key="r.id" class="hc-review-item">
                <div class="hc-review-top">
                  <span class="hc-review-author">{{ r.user_name || 'Anonymous' }}</span>
                  <span class="hc-review-stars">
                    <span v-for="s in 5" :key="s" :class="['star', { filled: s <= r.score }]">&#9733;</span>
                  </span>
                </div>
                <p class="hc-review-text" v-if="r.comment">{{ r.comment }}</p>
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
const toggling = ref(false)
const activeFilter = ref('all')
const searchQuery = ref('')
const openReviews = ref({})

function toggleReviews(id) {
  openReviews.value[id] = !openReviews.value[id]
}

function getReviews(expId) {
  return store.hostReviews.filter(r => r.experience_id === expId)
}

const filters = computed(() => [
  { value: 'all', label: 'All', count: store.myExperiences.length },
  { value: 'active', label: 'Active', count: store.myExperiences.filter(e => e.is_active && e.is_approved).length },
  { value: 'inactive', label: 'Inactive', count: store.myExperiences.filter(e => !e.is_active && !e.rejected_at).length },
  { value: 'pending', label: 'Pending', count: store.myExperiences.filter(e => !e.is_approved && !e.rejected_at).length },
  { value: 'rejected', label: 'Rejected', count: store.myExperiences.filter(e => e.rejected_at).length },
])

const filteredExps = computed(() => {
  let exps = store.myExperiences
  if (activeFilter.value === 'active') exps = exps.filter(e => e.is_active && e.is_approved)
  else if (activeFilter.value === 'inactive') exps = exps.filter(e => !e.is_active && !e.rejected_at)
  else if (activeFilter.value === 'pending') exps = exps.filter(e => !e.is_approved && !e.rejected_at)
  else if (activeFilter.value === 'rejected') exps = exps.filter(e => e.rejected_at)
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    exps = exps.filter(e =>
      e.title.toLowerCase().includes(q) ||
      e.location.toLowerCase().includes(q) ||
      e.category.toLowerCase().includes(q) ||
      (e.description && e.description.toLowerCase().includes(q))
    )
  }
  return exps
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

function statusClass(exp) {
  if (exp.rejected_at) return 'rejected'
  if (!exp.is_approved) return 'pending'
  if (exp.is_active) return 'active'
  return 'inactive'
}

function statusLabel(exp) {
  if (exp.rejected_at) return 'Rejected'
  if (!exp.is_approved) return 'Pending Approval'
  if (exp.is_active) return 'Active'
  return 'Inactive'
}

async function handleToggle(exp) {
  toggling.value = true
  await store.toggleActive(exp.id)
  await store.fetchOwnerStats()
  toggling.value = false
}

async function handleDelete(exp) {
  if (!confirm(`Are you sure you want to permanently delete "${exp.title}"? This action cannot be undone.`)) return
  await store.deleteExperience(exp.id)
  await store.fetchOwnerStats()
}

onMounted(async () => {
  await Promise.all([
    store.fetchMyExperiences(),
    store.fetchHostReviews(),
  ])
  loading.value = false
})
</script>

<style scoped>
.host-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  position: relative;
  min-height: 100vh;
  padding: 5rem 1rem 2rem;
}

.host-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 0;
}

.host-page > * {
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
  margin: 0 auto 28px;
  line-height: 1.6;
}

.hero-btn {
  margin: 0 auto;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-primary { background: var(--accent); color: #fff; }
.btn-primary:hover { background: var(--accent-hover); }

.filter-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.4rem 0.9rem;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
  color: #666;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.filter-btn:hover { border-color: var(--accent); color: var(--accent); }
.filter-btn.active { background: rgba(255, 255, 255, 0.3); color: #fff; border-color: rgba(255, 255, 255, 0.3); }

.count {
  margin-left: 4px;
  opacity: 0.7;
  font-size: 0.8rem;
}

.search-bar {
  position: relative;
  margin-bottom: 1.5rem;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.4);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 10px 14px 10px 42px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  font-size: 0.88rem;
  font-family: inherit;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #fff;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.search-input:focus {
  border-color: var(--accent);
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #666;
}

.spinner {
  width: 36px; height: 36px;
  border: 3px solid rgba(255, 255, 255, 0.18);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

.hotspots-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .hotspots-grid {
    grid-template-columns: 1fr;
  }
}

.hotspot-card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 16px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.hotspot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.hc-hero {
  height: 160px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.hc-hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 60%, rgba(0,0,0,0.1) 100%);
}

.hc-hero-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 16px;
}

.hc-hero-content h3 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #fff;
  margin: 6px 0 2px;
  font-family: 'Poppins', sans-serif;
  text-shadow: 0 2px 8px rgba(0,0,0,0.5);
}

.hc-location {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.75);
  text-shadow: 0 1px 4px rgba(0,0,0,0.5);
}

.hc-status {
  display: inline-block;
  align-self: flex-start;
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hc-status.active { background: #43A047; color: #fff; }
.hc-status.inactive { background: #7B1FA2; color: #fff; }
.hc-status.pending { background: #FF8F00; color: #fff; }
.hc-status.rejected { background: #C62828; color: #fff; }

.rejection-banner {
  background: rgba(198, 40, 40, 0.18);
  border: 1px solid rgba(198, 40, 40, 0.35);
  border-radius: 8px;
  padding: 10px 12px;
  color: #fff;
  font-size: 0.82rem;
  line-height: 1.5;
  margin-bottom: 12px;
}

.rejection-banner strong {
  color: #EF9A9A;
}

.hc-body {
  padding: 16px;
}

.hc-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.hc-stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.8);
}

.hc-stat svg {
  flex-shrink: 0;
  color: var(--accent);
}

.hc-actions {
  display: flex;
  gap: 6px;
  padding: 0 16px 16px;
  flex-wrap: wrap;
}

.hc-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 10px;
  border: none;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  text-decoration: none;
  transition: all 0.2s;
  min-width: 0;
}

.hc-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.hc-btn-edit {
  background: #2196F3;
  color: #fff;
}
.hc-btn-edit:hover { background: #1976D2; }

.hc-btn-appeal {
  background: var(--accent);
  color: #1a1a1a;
  font-weight: 600;
}
.hc-btn-appeal:hover { background: #fff; }

.hc-btn-activate {
  background: #43A047;
  color: #fff;
}
.hc-btn-activate:hover:not(:disabled) { background: #2E7D32; }

.hc-btn-deactivate {
  background: #E53935;
  color: #fff;
}
.hc-btn-deactivate:hover:not(:disabled) { background: #C62828; }

.hc-btn-delete {
  background: #546E7A;
  color: #fff;
}
.hc-btn-delete:hover { background: #37474F; }

.hc-reviews {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: 12px 16px;
}

.hc-reviews-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  user-select: none;
}

.hc-reviews-header:hover { color: #fff; }

.hc-reviews-arrow {
  font-size: 0.6rem;
  transition: transform 0.2s;
}

.hc-reviews-arrow.open { transform: rotate(180deg); }

.hc-reviews-body {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hc-review-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 8px 10px;
}

.hc-review-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3px;
}

.hc-review-author {
  font-size: 0.78rem;
  font-weight: 600;
  color: #fff;
}

.hc-review-stars {
  display: flex;
  gap: 1px;
}

.hc-review-stars .star {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.2);
}

.hc-review-stars .star.filled {
  color: var(--accent);
}

.hc-review-text {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
  margin: 0;
}
</style>
