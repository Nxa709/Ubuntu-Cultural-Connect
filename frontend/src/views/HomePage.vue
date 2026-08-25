<template>
  <div class="home-page">
    <section class="hero">
      <div class="hero-content">
        <div class="content-box">
          <p class="subtitle">Welcome to</p>
          <h1>Ubuntu <span class="heartbeat">Cultural</span> Connect</h1>
          <p class="hero-text">
            Discover authentic South African cultural experiences. Connect with local community hosts
            and immerse yourself in indigenous traditions, township life, and rural heritage.
          </p>
        </div>
      </div>
    </section>

    <section class="categories-section">
      <div class="categories-container">
        <div class="categories-header">
          <h2 class="categories-heading">Explore by category</h2>
          <router-link to="/experiences" class="view-all-link">
            View all categories <i class="bi bi-arrow-right"></i>
          </router-link>
        </div>
        <div class="categories-row">
          <button
            type="button"
            v-for="c in categories"
            :key="c.name"
            class="category-box"
            :class="{ active: selectedCategory === c.name }"
            @click="selectCategory(c.name)"
          >
            <div class="category-icon"><i :class="['bi', c.icon]"></i></div>
            <span class="category-name">{{ c.name }}</span>
            <span class="category-desc">{{ c.desc }}</span>
          </button>
        </div>
      </div>
    </section>

    <section class="popular-section">
      <div class="popular-container">
        <div class="popular-header">
          <h2 class="popular-heading">
            {{ sectionTitle }}
          </h2>
          <div class="popular-actions">
            <button
              v-if="hasFilters"
              class="view-all-link view-all-btn"
              @click="clearFilters"
            >
              Clear filter <i class="bi bi-x-circle"></i>
            </button>
            <router-link v-else to="/experiences" class="view-all-link">
              View all <i class="bi bi-arrow-right"></i>
            </router-link>
          </div>
        </div>
        <div class="popular-grid">
          <router-link class="hotspot-card" :to="`/destination/${h.id}`" v-for="(h, i) in popularHotspots" :key="h.id">
            <div class="hotspot-img" :style="{ backgroundImage: `url(${h.image})` }">
              <button
                class="wishlist-btn"
                :class="{ active: isWishlisted(h.id) }"
                :aria-label="isWishlisted(h.id) ? 'Remove from wishlist' : 'Add to wishlist'"
                @click.stop.prevent="toggleWishlist(h.id)"
              >
                <i :class="isWishlisted(h.id) ? 'bi-heart-fill' : 'bi-heart'"></i>
              </button>
              <span class="hotspot-badge" :class="badgeClass(h, i)">{{ getBadge(h, i) }}</span>
              <div class="hotspot-overlay">
                <h3 class="hotspot-name">{{ h.name }}</h3>
              </div>
            </div>
            <div class="hotspot-body">
              <p class="hotspot-desc">{{ h.category }}</p>
              <div class="hotspot-meta">
                <span class="hotspot-rating"><i class="bi bi-star-fill"></i> {{ h.rating }}</span>
                <span class="hotspot-location"><i class="bi bi-geo-alt-fill"></i> {{ h.location }}</span>
              </div>
            </div>
          </router-link>
        </div>
        <p v-if="popularHotspots.length === 0" class="no-results">No hotspots match your filters. Try a different location or category.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { provinces } from '../data/provinces'

const auth = useAuthStore()

const selectedCategory = ref('')

function selectCategory(name) {
  selectedCategory.value = selectedCategory.value === name ? '' : name
}

function normalizeCategory(c) {
  return (c || '').trim().toLowerCase().replace(/s$/, '')
}

const categories = [
  { name: 'Museums', icon: 'bi-bank', desc: 'Art & heritage' },
  { name: 'Game Reserves', icon: 'bi-tree', desc: 'Big Five safaris' },
  { name: 'Nature Reserves', icon: 'bi-flower1', desc: 'Scenic outdoors' },
  { name: 'Lodges', icon: 'bi-house-heart', desc: 'Luxury stays' },
  { name: 'Cultural Theatre', icon: 'bi-mic', desc: 'Live performances' },
  { name: 'Local Restaurants', icon: 'bi-cup-hot', desc: 'African cuisine' },
  { name: 'Cultural Storytelling', icon: 'bi-chat-quote', desc: 'Heritage stories' },
  { name: 'Cultural Tours', icon: 'bi-map', desc: 'Guided tours' },
  { name: 'Historical Landmarks', icon: 'bi-bank2', desc: 'Heritage sites' },
  { name: 'Cultural Attire Market', icon: 'bi-bag', desc: 'Traditional fashion' },
  { name: 'Traditional Healing', icon: 'bi-heart-pulse', desc: 'Ancestral wellness' },
  { name: 'Cultural Experience', icon: 'bi-stars', desc: 'Immersive culture' },
]

function loadWishlist() {
  try {
    return JSON.parse(localStorage.getItem('ucc_wishlist') || '[]')
  } catch (e) {
    return []
  }
}

const wishlist = ref(loadWishlist())

const hasFilters = computed(() => selectedCategory.value !== '')

const sectionTitle = computed(() => {
  const cat = selectedCategory.value
  if (cat) return cat
  return 'Popular near you'
})

function clearFilters() {
  selectedCategory.value = ''
}

const popularHotspots = computed(() => {
  const all = provinces.flatMap((p) =>
    p.destinations.map((d) => ({ ...d, provinceSlug: p.slug, provinceName: p.name }))
  )
  let result = all
  if (selectedCategory.value) {
    const target = normalizeCategory(selectedCategory.value)
    result = result.filter((d) => normalizeCategory(d.category) === target)
  }
  if (!hasFilters.value) {
    result = result.filter((d) => d.rating >= 4.5)
  }
  return result
    .sort((a, b) => b.rating - a.rating)
    .slice(0, 8)
})

function getBadge(h, index) {
  if (index === 0) return 'Top Rated'
  return ['Popular', 'Trending', 'New'][(index - 1) % 3]
}

function badgeClass(h, index) {
  const badge = getBadge(h, index)
  return {
    'Top Rated': 'badge-top',
    Popular: 'badge-popular',
    Trending: 'badge-trending',
    New: 'badge-new',
  }[badge]
}

function isWishlisted(id) {
  return wishlist.value.includes(id)
}

function toggleWishlist(id) {
  const index = wishlist.value.indexOf(id)
  if (index >= 0) {
    wishlist.value.splice(index, 1)
  } else {
    wishlist.value.push(id)
  }
  try {
    localStorage.setItem('ucc_wishlist', JSON.stringify(wishlist.value))
  } catch (e) {}
}
</script>

<style scoped>
.home-page {
  padding-top: 0;
  background: var(--glass-bg);
  position: relative;
  min-height: 100vh;
}

/* Hero */
.hero {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  background: url('/img/cultures/woman.jpeg') no-repeat center top;
  background-size: cover;
}

.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.22);
  z-index: 0;
  pointer-events: none;
}

.hero-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 80px 20px;
  position: relative;
  z-index: 1;
}

.content-box {
  max-width: 900px;
  animation: fadeIn 1.3s ease;
}

.subtitle {
  letter-spacing: 4px;
  text-transform: uppercase;
  font-size: 0.9rem;
  margin-bottom: 18px;
  color: rgba(255, 255, 255, 0.98);
}

.hero h1 {
  font-size: clamp(3rem, 7vw, 5.5rem);
  line-height: 1.05;
  font-weight: 700;
  margin-bottom: 20px;
  color: #ffffff;
  font-family: 'Poppins', sans-serif;
}

.heartbeat {
  color: var(--accent);
  font-family: 'Pacifico', cursive;
  font-weight: 400;
}

.hero-text {
  font-size: 1.1rem;
  line-height: 1.8;
  max-width: 700px;
  margin: 0 auto 30px;
  color: rgba(255, 255, 255, 0.88);
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Search bar */
.search-bar {
  display: flex;
  align-items: stretch;
  max-width: 820px;
  margin: 0 auto 28px;
  background: var(--glass-bg);
  border-radius: 50px;
  padding: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.search-field {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  padding: 0 16px;
  border-right: 1px solid #eaeaea;
}

.search-field i {
  color: var(--accent);
  font-size: 1rem;
}

.search-field input,
.search-field select {
  width: 100%;
  border: none;
  background: transparent;
  outline: none;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
  color: #333;
  padding: 10px 0;
}

.search-field select {
  cursor: pointer;
  appearance: auto;
  -webkit-appearance: auto;
}

.search-field input::placeholder {
  color: var(--text-muted);
}

.search-btn {
  border: none;
  background: var(--accent);
  color: #1a1a1a;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  font-size: 0.95rem;
  padding: 0 32px;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.search-btn:hover {
  background: var(--accent-fill-hover);
  color: #1a1a1a;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(25px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Categories Section */
.categories-section {
  padding: 60px 20px 20px;
}

.categories-container {
  max-width: 1200px;
  margin: 0 auto;
}

.categories-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 16px;
}

.categories-heading {
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

.view-all-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.popular-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.categories-row {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding-bottom: 8px;
  scrollbar-width: thin;
}

.category-box {
  flex: 0 0 auto;
  width: 165px;
  height: 165px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
  background: var(--glass-bg);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s;
  text-align: center;
  padding: 16px;
  cursor: pointer;
  font-family: inherit;
}

.category-box:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
  border-color: var(--accent);
}

.category-box.active {
  border-color: var(--accent);
  background: rgba(232, 162, 0, 0.08);
  box-shadow: 0 6px 20px rgba(232, 162, 0, 0.2);
}

.category-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(232, 162, 0, 0.15);
  color: var(--accent);
  font-size: 1.35rem;
}

.category-name {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  color: #333;
  line-height: 1.25;
}

.category-desc {
  font-size: 0.72rem;
  color: var(--text-secondary);
  line-height: 1.3;
}

/* Popular Section */
.popular-section {
  padding: 20px 20px 60px;
}

.popular-container {
  max-width: 1200px;
  margin: 0 auto;
}

.popular-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 16px;
}

.popular-heading {
  font-size: 2rem;
  color: #1a1a1a;
  font-weight: 600;
  margin: 0;
}

.popular-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.hotspot-card {
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

.hotspot-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.hotspot-img {
  height: 180px;
  position: relative;
  background-size: cover;
  background-position: center;
}

.hotspot-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.7rem;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  color: #1a1a1a;
  background: var(--accent);
}

.hotspot-badge.badge-top,
.hotspot-badge.badge-popular,
.hotspot-badge.badge-trending,
.hotspot-badge.badge-new {
  background: var(--accent-fill);
  color: #1a1a1a;
}

.wishlist-btn {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 50%;
  color: var(--accent-fill);
  font-size: 1.15rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.wishlist-btn:hover {
  color: var(--accent-fill);
  transform: scale(1.1);
}

.wishlist-btn.active {
  color: var(--accent-fill);
}

.hotspot-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.75), transparent);
  display: flex;
  align-items: flex-end;
  padding: 14px;
  pointer-events: none;
}

.hotspot-body {
  padding: 16px;
}

.hotspot-name {
  font-family: 'Poppins', sans-serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.hotspot-desc {
  font-size: 0.78rem;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.hotspot-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.hotspot-rating {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #f5a623;
}

.hotspot-location {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.no-results {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

@media (max-width: 768px) {
  .popular-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}
</style>
