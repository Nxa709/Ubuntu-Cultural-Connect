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
        <div class="search-bar">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input v-model="search" type="text" placeholder="what are you looking for ?" class="search-input" @keyup.enter="performSearch" />
          <button class="search-btn" @click="performSearch">Search</button>
        </div>
      </div>
    </div>

    <section class="search-results-section" v-if="hasActiveFilters" ref="resultsSection">
      <div class="search-results-container">
        <div class="search-results-header">
          <h2 class="search-results-heading">
            Search Results <span class="results-count">{{ filteredExperiences.length }} {{ filteredExperiences.length === 1 ? 'result' : 'results' }}</span>
          </h2>
        </div>
        <p v-if="filteredExperiences.length === 0" class="no-results">
          No experiences match your search. Try a different keyword.
        </p>
        <div class="search-results-grid" v-else>
          <div
            class="search-result-card"
            v-for="exp in filteredExperiences"
            :key="exp.id"
            @click="$router.push(`/experience/${exp.id}`)"
            style="cursor: pointer;"
          >
            <div class="search-result-img" :style="{ backgroundImage: `url(${exp.image_url || getCategoryImage(exp.category)})` }">
              <span class="search-result-cat">{{ exp.category }}</span>
            </div>
            <div class="search-result-body">
              <h3>{{ exp.title }}</h3>
              <p class="search-result-loc">{{ exp.location }}{{ exp.province ? ', ' + exp.province : '' }}</p>
              <div class="search-result-meta">
                <span class="search-result-rating" v-if="exp.avg_rating">&#9733; {{ exp.avg_rating }}</span>
                <span class="search-result-owner" v-if="exp.owner_name">{{ exp.owner_name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="featured-section">
      <div class="featured-container">
        <div class="featured-header">
          <h2 class="featured-heading">Featured Experiences</h2>
          <button class="view-all-link view-all-btn" @click="showAll = !showAll">
            {{ showAll ? 'Show less' : 'View all hotspots' }}
            <i :class="showAll ? 'bi bi-arrow-up' : 'bi bi-arrow-right'"></i>
          </button>
        </div>

        <div class="featured-grid" v-if="!showAll">
          <div
            class="featured-card"
            v-for="exp in featuredExperiences"
            :key="exp.id"
            @click="$router.push(`/experience/${exp.id}`)"
            style="cursor: pointer;"
          >
            <div class="featured-img" :style="{ backgroundImage: `url(${exp.image_url || getCategoryImage(exp.category)})` }">
              <span class="featured-cat">{{ exp.category }}</span>
              <div class="featured-overlay">
                <h3>{{ exp.title }}</h3>
              </div>
            </div>
          </div>
        </div>

        <div class="featured-grid" v-else>
          <div
            class="featured-card"
            v-for="exp in experiences"
            :key="exp.id"
            @click="$router.push(`/experience/${exp.id}`)"
            style="cursor: pointer;"
          >
            <div class="featured-img" :style="{ backgroundImage: `url(${exp.image_url || getCategoryImage(exp.category)})` }">
              <span class="featured-cat">{{ exp.category }}</span>
              <div class="featured-overlay">
                <h3>{{ exp.title }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="province-explore">
      <div class="province-explore-container">
        <div class="province-explore-header">
          <h2 class="province-explore-heading">Explore by province</h2>
          <router-link to="/" class="view-all-link">
            View all provinces <i class="bi bi-arrow-right"></i>
          </router-link>
        </div>
        <div class="province-row">
          <router-link
            v-for="p in provinceData"
            :key="p.slug"
            :to="p.slug === 'kwaZulu-natal' ? '/kzn-directory' : `/province/${p.slug}`"
            class="province-square"
            :style="{ backgroundImage: `url(${p.image})` }"
          >
            <div class="province-square-overlay">
              <h3>{{ p.name }}</h3>
            </div>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useExperienceStore } from '../stores/experience'
import { provinces as provinceData } from '../data/provinces'

const route = useRoute()
const router = useRouter()
const store = useExperienceStore()

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

const experiences = ref([])
const search = ref('')
const showAll = ref(false)

const hasActiveFilters = computed(() => search.value.trim() !== '')

const filteredExperiences = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return experiences.value
  return experiences.value.filter((exp) => {
    const haystack = [
      exp.title, exp.description, exp.category, exp.location, exp.province, exp.owner_name,
    ].filter(Boolean).join(' ').toLowerCase()
    return haystack.includes(q)
  })
})

const featuredExperiences = computed(() => {
  return experiences.value.slice(0, 4)
})

const resultsSection = ref(null)

function performSearch() {
  if (resultsSection.value) {
    resultsSection.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

onMounted(async () => {
  search.value = (route.query.q || '').toString()
  await loadExperiences()
})

function loadExperiences() {
  store.fetchExperiences()
    .then(() => {
      experiences.value = store.experiences
    })
    .catch(e => {
      console.error('Failed to load experiences:', e)
      experiences.value = []
    })
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
  background: var(--glass-bg);
  position: relative;
  min-height: 100vh;
}

.hero-header {
  background: url('/img/cultures/woman.jpeg') no-repeat center top;
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

.back-btn {
  position: absolute;
  top: 96px;
  left: 20px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.26);
  border: 1px solid rgba(255, 255, 255, 0.45);
  color: rgba(255, 255, 255, 0.97);
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.82rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.36);
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
  color: rgba(255, 255, 255, 0.94);
  max-width: 520px;
  margin: 0 auto 32px;
  line-height: 1.6;
}

.filters {
  display: flex;
  justify-content: center;
  align-items: stretch;
  gap: 12px;
  max-width: 700px;
  margin: 0 auto;
  flex-wrap: wrap;
}

.search-bar {
  flex: 1;
  min-width: 260px;
  max-width: 600px;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 50px;
  padding: 6px 6px 6px 18px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  gap: 8px;
  transition: box-shadow 0.3s ease;
}

.search-bar:focus-within {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25), 0 0 0 3px rgba(232, 162, 0, 0.2);
}

.search-icon {
  flex-shrink: 0;
  color: var(--accent);
  pointer-events: none;
}

.search-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  outline: none;
  font-family: inherit;
  font-size: 0.95rem;
  color: #333;
  padding: 10px 0;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-btn {
  flex-shrink: 0;
  border: none;
  background: var(--accent-fill);
  color: #1a1a1a;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  font-size: 0.95rem;
  padding: 12px 28px;
  border-radius: 50px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.search-btn:hover {
  background: var(--accent-fill-hover);
  color: #1a1a1a;
}

/* Explore by province */
.province-explore {
  padding: 60px 20px;
}

.province-explore-container {
  max-width: 1200px;
  margin: 0 auto;
}

.province-explore-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 16px;
}

.province-explore-heading {
  font-size: 2rem;
  color: #1a1a1a;
  font-weight: 600;
  margin: 0;
}

.view-all-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--accent);
  white-space: nowrap;
}

.view-all-link:hover {
  color: var(--accent-hover);
}

.province-row {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding-bottom: 8px;
  scrollbar-width: thin;
}

.province-square {
  flex: 0 0 auto;
  width: 170px;
  height: 170px;
  position: relative;
  display: block;
  background-size: cover;
  background-position: center;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s, box-shadow 0.3s;
}

.province-square:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.province-square-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.75), transparent);
  display: flex;
  align-items: flex-end;
  padding: 14px;
}

.province-square-overlay h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
  font-family: 'Poppins', sans-serif;
}

/* Search Results */
.search-results-section {
  padding: 60px 20px 0;
}

.search-results-container {
  max-width: 1200px;
  margin: 0 auto;
}

.search-results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 16px;
}

.search-results-heading {
  font-size: 2rem;
  color: #1a1a1a;
  font-weight: 600;
  margin: 0;
}

.results-count {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  background: rgba(232, 162, 0, 0.15);
  padding: 3px 12px;
  border-radius: 20px;
  margin-left: 10px;
  vertical-align: middle;
}

.search-results-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.search-result-card {
  display: block;
  text-decoration: none;
  color: inherit;
  background: var(--glass-bg);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s, box-shadow 0.3s;
}

.search-result-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.search-result-img {
  height: 160px;
  position: relative;
  background-size: cover;
  background-position: center;
}

.search-result-cat {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.7rem;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  color: #1a1a1a;
  background: var(--accent-fill);
}

.search-result-body {
  padding: 16px;
}

.search-result-body h3 {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 6px;
}

.search-result-loc {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 0 0 12px;
}

.search-result-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.search-result-rating {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #f5a623;
}

.search-result-owner {
  font-size: 0.78rem;
  color: var(--text-secondary);
}

.no-results {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

/* Featured Experiences */
.featured-section {
  padding: 60px 20px;
}

.featured-container {
  max-width: 1200px;
  margin: 0 auto;
}

.featured-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 16px;
}

.view-all-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.featured-heading {
  font-size: 2rem;
  color: #1a1a1a;
  font-weight: 600;
  margin: 0;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.featured-card {
  display: block;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s, box-shadow 0.3s;
}

.featured-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.featured-img {
  height: 200px;
  position: relative;
  background-size: cover;
  background-position: center;
}

.featured-cat {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.7rem;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  color: #1a1a1a;
  background: var(--accent-fill);
}

.featured-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.75), transparent);
  display: flex;
  align-items: flex-end;
  padding: 16px;
  pointer-events: none;
}

.featured-overlay h3 {
  font-size: 1.15rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
  font-family: 'Poppins', sans-serif;
}

@media (max-width: 1024px) {
  .featured-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .search-results-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .filters {
    flex-direction: column;
  }
  .search-bar {
    flex-direction: column;
    align-items: stretch;
    border-radius: 20px;
    padding: 12px;
  }
  .search-btn {
    width: 100%;
    justify-content: center;
  }
  .featured-grid,
  .search-results-grid {
    grid-template-columns: 1fr;
  }
}
</style>
