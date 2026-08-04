<template>
  <div class="experiences-page">
    <div class="hero-header">
      <button class="back-btn" @click="goBack">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Back
      </button>
      <h1><span class="accent-word">Cultural</span> Experiences</h1>
      <p>Browse authentic South African cultural experiences from verified local hosts.</p>
      <div class="filters">
        <div class="search-wrapper">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input v-model="search" type="text" placeholder="Search experiences..." class="search-input" @input="debounceSearch" />
        </div>
        <div class="select-wrapper">
          <select v-model="selectedCategory" @change="loadExperiences" class="filter-select">
            <option value="">All Categories</option>
            <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.value }}</option>
          </select>
          <svg class="select-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
      </div>
    </div>

    <div class="exp-grid" v-if="experiences.length > 0">
      <div class="exp-card" v-for="exp in experiences" :key="exp.id" @click="$router.push(`/experience/${exp.id}`)" style="cursor: pointer;">
        <div class="exp-img" :style="{ backgroundImage: `url(${exp.image_url || getCategoryImage(exp.category)})` }">
          <span class="exp-cat-badge">{{ exp.category }}</span>
        </div>
        <div class="exp-body">
          <h3>{{ exp.title }}</h3>
          <p class="exp-desc">{{ exp.description }}</p>
          <div class="exp-details">
            <span class="exp-location">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
              {{ exp.location }}
            </span>
          </div>
          <div class="exp-footer">
            <span class="exp-rating" v-if="exp.avg_rating">
              &#9733; {{ exp.avg_rating }} ({{ exp.rating_count }})
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else-if="!loading">
      <p>No experiences found. Try a different search or category.</p>
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
  router.push('/')
}
const experiences = ref([])
const categories = ref([])
const selectedCategory = ref('')
const search = ref('')
const loading = ref(false)
let debounceTimer = null

onMounted(async () => {
  loading.value = true
  await Promise.all([
    store.fetchCategories(),
    store.fetchExperiences(),
  ])
  categories.value = store.categories
  experiences.value = store.experiences
  loading.value = false
})

function debounceSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadExperiences, 300)
}

async function loadExperiences() {
  loading.value = true
  const params = {}
  if (selectedCategory.value) params.category = selectedCategory.value
  if (search.value) params.search = search.value
  await store.fetchExperiences(params)
  experiences.value = store.experiences
  loading.value = false
}

function getCategoryColor(cat) {
  const colors = {
    'Traditional Cooking': 'var(--accent)',
    'Storytelling': '#6B2A2A',
    'Music & Dance': 'var(--heading-color)',
    'Crafts & Art': '#5C4033',
    'Heritage Tours': '#4A3228',
    'Township Life': '#1a1a1a',
    'Rural Heritage': '#8B6914',
    'Traditional Healing': '#2E7D32',
    'Textile & Weaving': '#7B5B3A',
    'Photography Tours': '#5D4037',
    'Nature & Wildlife': '#2E7D32',
    'Accommodation & Lodging': '#6B4F3A',
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
.experiences-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
  position: relative;
  min-height: 100vh;
  padding: 100px 20px 40px;
}

.experiences-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 0;
}

.experiences-page > * {
  position: relative;
  z-index: 1;
}

.hero-header {
  text-align: center;
  padding: 40px 20px 48px;
  position: relative;
}

.back-btn {
  position: absolute;
  top: 40px;
  left: 20px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.8);
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.82rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
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
  margin: 0 auto 32px;
  line-height: 1.6;
}

.filters {
  display: flex;
  justify-content: center;
  gap: 12px;
  max-width: 600px;
  margin: 0 auto;
}

.search-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 16px;
  color: rgba(255, 255, 255, 0.5);
  pointer-events: none;
  transition: color 0.3s;
}

.search-input {
  width: 100%;
  padding: 14px 16px 14px 46px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 14px;
  font-size: 0.95rem;
  font-family: inherit;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #fff;
  transition: all 0.3s ease;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.45);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.18);
  box-shadow: 0 0 0 3px rgba(255, 182, 18, 0.15);
}

.search-wrapper:focus-within .search-icon {
  color: var(--accent);
}

.select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-select {
  padding: 14px 40px 14px 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 14px;
  font-size: 0.95rem;
  font-family: inherit;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #fff;
  min-width: 200px;
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-select option {
  background: #1a1a2e;
  color: #fff;
  padding: 8px;
}

.filter-select:focus {
  outline: none;
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.18);
  box-shadow: 0 0 0 3px rgba(255, 182, 18, 0.15);
}

.select-arrow {
  position: absolute;
  right: 14px;
  color: rgba(255, 255, 255, 0.5);
  pointer-events: none;
}

.exp-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.exp-card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s;
  color: #fff;
}

.exp-card:hover {
  transform: translateY(-3px);
}

.exp-img {
  height: 140px;
  position: relative;
  background-size: cover;
  background-position: center;
}

.exp-cat-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 6px;
}

.exp-body {
  padding: 18px;
}

.exp-body h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  margin-bottom: 6px;
}

.exp-desc {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.exp-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.exp-location {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.exp-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.exp-rating {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.btn-rate {
  font-size: 0.8rem;
  padding: 5px 12px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  text-decoration: none;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.2s;
}

.btn-rate:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.95rem;
}
</style>
