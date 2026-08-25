<template>
  <div class="preferences-page">
    <div class="hero-header">
      <button class="back-btn" @click="goBack">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Back
      </button>
      <h1><span class="accent-word">Cultural</span> Preferences</h1>
      <p>Select the cultural experiences that interest you. We'll personalize your recommendations.</p>
    </div>

    <div v-if="success" class="alert alert-success">{{ success }}</div>
    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="card">
      <h2>What interests you?</h2>
      <p class="card-sub">Select one or more cultural categories</p>

      <div class="categories-grid">
        <button
          v-for="cat in allCategories"
          :key="cat.value"
          class="cat-btn"
          :class="{ selected: selected.includes(cat.value) }"
          @click="toggle(cat.value)"
        >
          <span class="cat-icon" v-html="getIcon(cat.value)"></span>
          <span class="cat-label">{{ cat.value }}</span>
        </button>
      </div>

      <div class="card-actions">
        <button @click="save" class="btn btn-primary" :disabled="saving || selected.length === 0">
          {{ saving ? 'Saving...' : 'Save Preferences' }}
        </button>
        <span class="hint" v-if="selected.length === 0">Select at least one category</span>
        <span class="hint" v-else>{{ selected.length }} selected</span>
      </div>
    </div>

    <div class="card" v-if="recommended.length > 0">
      <h2>Handpicked Experiences Just for You</h2>
      <p class="card-sub">Based on your preferences</p>
      <div class="rec-grid">
        <div class="rec-card" v-for="exp in recommended" :key="exp.id" @click="$router.push(`/experience/${exp.id}`)" style="cursor: pointer;">
          <div class="rec-cat-badge">{{ exp.category }}</div>
          <h4>{{ exp.title }}</h4>
          <p class="rec-loc">{{ exp.location }}{{ exp.province ? ', ' + exp.province : '' }}</p>
          <div class="rec-meta">
            <span class="rec-rating" v-if="exp.avg_rating">
              {{ exp.avg_rating }} ({{ exp.rating_count }})
            </span>
          </div>
        </div>
      </div>
      <div class="browse-actions">
        <router-link to="/experiences" class="btn btn-primary browse-btn">Browse all experiences</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useExperienceStore } from '../stores/experience'

const router = useRouter()
const store = useExperienceStore()

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}
const allCategories = ref([])
const selected = ref([])
const saving = ref(false)
const success = ref('')
const error = ref('')
const recommended = ref([])

onMounted(async () => {
  try {
    await Promise.all([
      store.fetchCategories(),
      store.fetchPreferences(),
    ])
    allCategories.value = store.categories
    selected.value = [...store.preferences]
    await store.fetchRecommended()
    recommended.value = store.recommended
  } catch (e) {
    error.value = 'Failed to load data'
  }
})

function toggle(cat) {
  const idx = selected.value.indexOf(cat)
  if (idx >= 0) {
    selected.value.splice(idx, 1)
  } else {
    selected.value.push(cat)
  }
}

async function save() {
  if (selected.value.length === 0) {
    error.value = 'Please select at least one category'
    return
  }
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await store.savePreferences(selected.value)
    await store.fetchRecommended()
    recommended.value = store.recommended
    success.value = 'Preferences saved! Here are your handpicked experiences.'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save preferences'
  } finally {
    saving.value = false
  }
}

function getIcon(cat) {
  const icons = {
    'Traditional Cooking': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2C6.48 2 2 6 2 10c0 2 1 3 2 4v4h16v-4c1-1 2-2 2-4 0-4-4.48-8-10-8z"/><line x1="7" y1="22" x2="17" y2="22"/></svg>',
    'Storytelling': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
    'Music & Dance': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>',
    'Crafts & Art': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>',
    'Heritage Tours': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    'Township Life': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    'Rural Heritage': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>',
    'Traditional Healing': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    'Textile & Weaving': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>',
    'Photography Tours': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>',
  }
  return icons[cat] || '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>'
}
</script>

<style scoped>
.preferences-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center top;
  background-size: cover;
  position: relative;
  min-height: 100vh;
  padding: 0;
}

.preferences-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.15);
  z-index: 0;
}

.preferences-page > * {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin-left: auto;
  margin-right: auto;
}

.preferences-page > .hero-header {
  max-width: none;
  margin: 0;
  padding: 120px 20px 60px;
}

.hero-header {
  text-align: center;
  position: relative;
}

.back-btn {
  position: absolute;
  top: 96px;
  left: 20px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--surface);
  border: 1px solid var(--border-strong);
  color: var(--text-color);
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.82rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--accent-light);
  border-color: var(--accent);
  color: var(--accent-text);
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

.card {
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.24);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  margin-bottom: 24px;
  color: #fff;
}

.card::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--accent), #EC407A, #29B6F6);
}

.card h2 {
  color: #fff;
  font-size: 1.15rem;
  margin-bottom: 4px;
}

.card-sub {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-bottom: 20px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.cat-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 12px;
  border: 2px solid var(--accent);
  border-radius: 12px;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  color: var(--accent);
}

.cat-btn:hover {
  background: var(--accent-light);
  color: var(--accent-text);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.cat-btn.selected {
  border-color: var(--accent-fill);
  background: var(--accent-fill);
  color: #1a1a1a;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
}

.cat-icon {
  color: inherit;
}

.cat-btn:hover .cat-icon {
  color: inherit;
}

.cat-btn.selected .cat-icon {
  color: inherit;
}

.cat-label {
  font-size: 0.78rem;
  font-weight: 500;
  text-align: center;
  color: inherit;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  font-family: inherit;
  transition: opacity 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--accent-fill);
  color: #1a1a1a;
}

.btn-primary:hover:not(:disabled) { background-color: var(--accent-fill-hover); }

.hint {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.alert {
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 0.88rem;
}

.alert-error { background: rgba(255, 77, 77, 0.2); color: #ff6b6b; border: 1px solid rgba(255, 77, 77, 0.3); }
.alert-success { background: rgba(76, 175, 80, 0.2); color: #81c784; border: 1px solid rgba(76, 175, 80, 0.3); }

.rec-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.rec-card {
  background: var(--accent-fill);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid var(--accent);
  border-radius: 10px;
  padding: 18px;
  color: #1a1a1a;
  transition: transform 0.2s;
}

.rec-card:hover {
  transform: translateY(-4px);
}

.browse-actions {
  margin-top: 22px;
  text-align: center;
}

.browse-btn {
  text-decoration: none;
}

.rec-cat-badge {
  display: inline-block;
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 600;
  margin-bottom: 10px;
  background: #1a1a1a;
  color: var(--accent);
}

.rec-card h4 {
  font-size: 0.92rem;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.rec-loc {
  font-size: 0.8rem;
  color: rgba(0, 0, 0, 0.72);
  margin-bottom: 10px;
}

.rec-meta {
  display: flex;
  justify-content: flex-end;
}

.rec-rating {
  font-size: 0.8rem;
  color: #1a1a1a;
}

@media (max-width: 900px) {
  .categories-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .rec-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .preferences-page {
    padding: 0;
  }
  .hero-header {
    padding: 90px 12px 36px;
  }
  .hero-header h1 {
    font-size: 2rem;
  }
  .back-btn {
    top: 70px;
    left: 12px;
  }
  .card {
    padding: 20px 16px;
  }
  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  .rec-grid {
    grid-template-columns: 1fr;
  }
  .card-actions {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
