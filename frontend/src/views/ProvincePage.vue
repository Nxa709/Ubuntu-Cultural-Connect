<template>
  <div class="province-page">
    <div class="province-dir-section" v-if="province.name">
      <button class="back-btn" @click="goBack">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        Back
      </button>
      <h2 class="dir-heading">{{ province.name }} Cultural Tourism Directory</h2>
      <p class="dir-sub">{{ province.description }}</p>

      <div class="kzn-tabs">
        <button
          v-for="cat in categories"
          :key="cat.slug"
          :class="['kzn-tab', { active: selectedCategorySlug === cat.slug }]"
          @click="selectedCategorySlug = cat.slug"
        >
          {{ cat.name }} <span class="tab-count">({{ cat.items.length }})</span>
        </button>
      </div>

      <div class="kzn-grid" v-if="currentItems.length > 0">
        <div
          v-for="(item, idx) in currentItems"
          :key="idx"
          class="kzn-flip-card"
          @click="goToItem(item)"
        >
          <div class="kzn-flip-inner">
            <div class="kzn-flip-front" :style="{ backgroundImage: `url(${item.image})` }">
              <span class="exp-cat-badge">{{ item.category }}</span>
              <div class="front-name-bar">
                <h3>{{ item.name }}</h3>
              </div>
            </div>
            <div class="kzn-flip-back">
              <div class="kzn-flip-back-body">
                <div class="kzn-card-meta">
                  <span class="kzn-location">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                    {{ item.location }}
                  </span>
                  <span class="kzn-rating" v-if="item.rating">&#9733; {{ item.rating }}</span>
                </div>
                <div class="kzn-detail-row" v-if="item.hours"><strong>Hours:</strong> {{ item.hours }}</div>
                <div class="kzn-detail-row" v-if="item.contact"><strong>Contact:</strong> {{ item.contact }}</div>
                <div class="kzn-detail-row" v-if="item.priceRange"><strong>Price:</strong> {{ item.priceRange }}</div>
                <div class="kzn-detail-row" v-if="item.website"><strong>Web:</strong> <a :href="item.website" target="_blank" rel="noopener" class="kzn-link" @click.stop>{{ item.website }}</a></div>
                <div class="kzn-services" v-if="item.services && item.services.length">
                  <strong>Services:</strong>
                  <ul>
                    <li v-for="(s, si) in item.services.slice(0, 3)" :key="si">{{ s }}</li>
                    <li v-if="item.services.length > 3">+{{ item.services.length - 3 }} more</li>
                  </ul>
                </div>
                <button
                  v-if="auth.isTourist"
                  class="kzn-itinerary-btn"
                  @click.stop="openItineraryFor(item)"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
                  </svg>
                  Add to Itinerary
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <LoadingSpinner v-else message="Loading directory..." />
    </div>

    <AddToItineraryModal
      :experience="selectedForItinerary"
      :visible="showItineraryModal"
      @close="showItineraryModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { provinces } from '../data/provinces'
import { kznCategories } from '../data/kznCulturalData'
import { provinceImages } from '../data/provinceImages'
import { useAuthStore } from '../stores/auth'
import AddToItineraryModal from '../components/AddToItineraryModal.vue'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/experiences')
  }
}

const selectedCategorySlug = ref('')
const apiExperiences = ref([])
const loading = ref(true)
const showItineraryModal = ref(false)
const selectedForItinerary = ref(null)

const province = computed(() => {
  return provinces.find(p => p.slug === route.params.slug) || {}
})

const CATEGORY_SLUGS = [
  { name: 'Local Restaurants', slug: 'local-restaurants' },
  { name: 'Museums', slug: 'museums' },
  { name: 'Nature Reserves', slug: 'nature-reserves' },
  { name: 'Game Reserves', slug: 'game-reserves' },
  { name: 'Lodges', slug: 'lodges' },
  { name: 'Cultural Storytelling', slug: 'cultural-storytelling' },
  { name: 'Cultural Attire Market', slug: 'cultural-attire-market' },
  { name: 'Traditional Healing', slug: 'traditional-healing' },
  { name: 'Historical Landmarks', slug: 'historical-landmarks' },
  { name: 'Cultural Theatre', slug: 'cultural-theatre' },
  { name: 'Cultural Tours', slug: 'cultural-tours' },
]

const categoryImages = {
  'Local Restaurants': '/img/blog/blog-post-4.webp',
  'Museums': '/img/cultures/KwaMaiMai.jpg',
  'Nature Reserves': '/img/blog/blog-post-2.webp',
  'Game Reserves': '/img/cultures/Safari.jpg',
  'Lodges': '/img/blog/blog-post-1.webp',
  'Cultural Storytelling': '/img/cultures/Xhosa.jpg',
  'Cultural Attire Market': '/img/cultures/Ndebele.jpg',
  'Traditional Healing': '/img/cultures/Rural.jpg',
  'Historical Landmarks': '/img/cultures/Jepe.jpg',
  'Cultural Theatre': '/img/cultures/Rasta.jpeg',
  'Cultural Tours': '/img/cultures/Rural.jpg',
}

const categoryMap = {
  'Local Restaurants': 'local-restaurants',
  'Museums': 'museums',
  'Nature Reserves': 'nature-reserves',
  'Game Reserves': 'game-reserves',
  'Lodges': 'lodges',
  'Cultural Storytelling': 'cultural-storytelling',
  'Cultural Attire Market': 'cultural-attire-market',
  'Traditional Healing': 'traditional-healing',
  'Historical Landmarks': 'historical-landmarks',
  'Cultural Theatre': 'cultural-theatre',
  'Cultural Tours': 'cultural-tours',
  'Cultural Experience': 'cultural-tours',
  'Nature Reserve': 'nature-reserves',
  'Game Reserve': 'game-reserves',
  'Restaurants': 'local-restaurants',
}

function slugify(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
}

function goToItem(item) {
  if (item.id) {
    router.push(`/destination/${item.id}`)
  } else if (item.name) {
    router.push(`/kzn-directory/item/${slugify(item.name)}`)
  }
}

function buildCategory(name) {
  const slug = categoryMap[name]
  let kznItems = []
  if (province.value.slug === 'kwaZulu-natal') {
    const kznCat = kznCategories.find(c => c.slug === slug)
    if (kznCat) {
      kznItems = kznCat.items.map(item => ({ ...item, category: name, image: kznCat.image }))
    }
  }

  const staticItems = (province.value.destinations || [])
    .filter(d => d.category === name)
    .map(d => ({ ...d, category: name }))

  const apiItems = apiExperiences.value
    .filter(e => e.category === name)
    .map(e => ({
      name: e.title,
      location: e.location,
      rating: e.avg_rating,
      hours: null,
      contact: null,
      website: null,
      services: e.description ? [e.description.slice(0, 100)] : [],
      image: e.image_url,
      category: name,
    }))

  const seen = new Set()
  const merged = [...kznItems, ...staticItems, ...apiItems].filter(item => {
    if (seen.has(item.name)) return false
    seen.add(item.name)
    return true
  })

  return merged
}

const categories = computed(() => {
  return CATEGORY_SLUGS
    .map(c => ({
      slug: c.slug,
      name: c.name,
      items: buildCategory(c.name),
    }))
    .filter(c => c.items.length > 0)
})

const currentItems = computed(() => {
  const cat = categories.value.find(c => c.slug === selectedCategorySlug.value)
  if (!cat) return []
  return cat.items.map(item => ({
    ...item,
    image: provinceImages[item.name] || item.image || categoryImages[item.category] || '/img/cultures/Safari.jpg',
  }))
})

function openItineraryFor(item) {
  selectedForItinerary.value = {
    title: item.name,
    location: item.location,
    province: province.value.name || '',
    description: item.services ? item.services.join(', ') : '',
    price: item.priceRange ? parseFloat(item.priceRange.replace(/[^0-9.]/g, '')) || 0 : 0,
    duration_hours: null,
    id: null,
  }
  showItineraryModal.value = true
}

onMounted(async () => {
  if (!province.value.name) {
    router.push('/experiences')
    return
  }
  try {
    const r = await api.get('/experiences/', { params: { province: province.value.name } })
    apiExperiences.value = r.data
  } catch (e) {
    console.error('Failed to load experiences:', e)
  } finally {
    loading.value = false
    if (categories.value.length > 0 && !selectedCategorySlug.value) {
      selectedCategorySlug.value = categories.value[0].slug
    }
  }
})
</script>

<style scoped>
.province-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  position: relative;
  min-height: 100vh;
  padding: 100px 20px 40px;
}

.province-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.15);
  z-index: 0;
}

.province-page > * {
  position: relative;
  z-index: 1;
}

.province-dir-section {
  max-width: 1200px;
  margin: 0 auto;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.26);
  border: 1px solid rgba(255, 255, 255, 0.38);
  color: rgba(255, 255, 255, 0.97);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 20px;
}
.back-btn:hover { background: rgba(255, 255, 255, 0.36); color: #fff; }
.dir-heading { text-align: center; font-size: 1.6rem; color: #fff; margin-bottom: 28px; font-family: 'Poppins', sans-serif; }
.dir-sub { text-align: center; color: rgba(255, 255, 255, 0.90); font-size: 0.95rem; margin: -16px auto 32px; max-width: 600px; line-height: 1.6; }
.exp-cat-badge { position: absolute; top: 12px; left: 12px; background: rgba(0, 0, 0, 0.5); color: #fff; font-size: 0.72rem; font-weight: 500; padding: 3px 10px; border-radius: 6px; }
.kzn-tabs { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 28px; }
.kzn-tab { padding: 8px 18px; border: 1px solid rgba(255, 255, 255, 0.38); border-radius: 20px; background: rgba(255, 255, 255, 0.22); color: rgba(255, 255, 255, 0.94); font-size: 0.82rem; font-family: inherit; cursor: pointer; transition: all 0.25s ease; white-space: nowrap; }
.kzn-tab:hover { background: rgba(255, 255, 255, 0.30); color: #fff; }
.kzn-tab.active { background: var(--accent); color: #1a1a1a; border-color: var(--accent); font-weight: 600; }
.tab-count { opacity: 0.6; font-size: 0.75rem; }
.kzn-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.kzn-flip-card { perspective: 1000px; height: 320px; cursor: pointer; }
.kzn-flip-inner { position: relative; width: 100%; height: 100%; transition: transform 0.5s; transform-style: preserve-3d; }
.kzn-flip-card:hover .kzn-flip-inner { transform: rotateY(180deg); }
.kzn-flip-front, .kzn-flip-back { position: absolute; inset: 0; backface-visibility: hidden; -webkit-backface-visibility: hidden; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.45); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); }
.kzn-flip-front { background-size: cover; background-position: center; display: flex; flex-direction: column; justify-content: flex-end; }
.front-name-bar { background: linear-gradient(transparent, rgba(0,0,0,0.8)); padding: 30px 14px 14px; }
.front-name-bar h3 { font-size: 1rem; font-weight: 600; color: #fff; margin: 0; text-shadow: 0 1px 4px rgba(0,0,0,0.5); }
.kzn-flip-back { transform: rotateY(180deg); background: rgba(30, 30, 50, 0.96); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); color: #fff; }
.kzn-flip-back-body { padding: 16px; height: 100%; overflow-y: auto; }
.kzn-card-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.kzn-location { display: flex; align-items: center; gap: 4px; font-size: 0.78rem; color: rgba(255, 255, 255, 0.88); }
.kzn-rating { font-size: 0.78rem; color: var(--accent); }
.kzn-detail-row { font-size: 0.78rem; color: rgba(255, 255, 255, 0.95); line-height: 1.5; margin-bottom: 4px; }
.kzn-detail-row strong { color: rgba(255, 255, 255, 0.9); margin-right: 4px; }
.kzn-link { color: var(--accent); text-decoration: none; word-break: break-all; font-size: 0.75rem; }
.kzn-link:hover { text-decoration: underline; }
.kzn-services { font-size: 0.78rem; margin-top: 4px; }
.kzn-services strong { color: rgba(255, 255, 255, 0.9); }
.kzn-services ul { margin: 2px 0 0; padding-left: 14px; }
.kzn-services li { color: rgba(255, 255, 255, 0.94); line-height: 1.4; font-size: 0.75rem; }
.loading-state { text-align: center; color: rgba(255, 255, 255, 0.94); padding: 40px 0; font-size: 0.95rem; }
.kzn-itinerary-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
  margin-top: 6px;
  padding: 5px 10px;
  border: 1px solid var(--accent);
  border-radius: 6px;
  background: rgba(255, 182, 18, 0.12);
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}
.kzn-itinerary-btn:hover {
  background: var(--accent);
  color: #1a1a1a;
  border-color: var(--accent);
}
.kzn-itinerary-btn svg {
  width: 12px;
  height: 12px;
}
@media (max-width: 768px) { .kzn-grid { grid-template-columns: 1fr; } .kzn-tabs { flex-wrap: nowrap; overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 8px; justify-content: flex-start; } .kzn-tab { flex-shrink: 0; } }
</style>
