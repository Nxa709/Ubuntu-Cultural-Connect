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
          class="featured-card"
          @click="goToItem(item)"
        >
          <div class="featured-img" :style="{ backgroundImage: `url(${item.image})` }">
            <span class="featured-cat">{{ item.category }}</span>
            <div class="featured-overlay">
              <h3>{{ item.name }}</h3>
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
import { useAuthStore } from '../stores/auth'
import AddToItineraryModal from '../components/AddToItineraryModal.vue'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

/* Allows this component to be reused for a fixed province (e.g. the KZN
   directory route passes slug="kwaZulu-natal"). Falls back to the route param. */
const props = defineProps({
  slug: { type: String, default: '' },
})

const provinceSlug = computed(() => props.slug || route.params.slug)

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/experiences')
  }
}

function normalizeCategory(c) {
  return (c || '').trim().toLowerCase().replace(/s$/, '')
}

/* The tabs use display names; map them to the database categories. */
const dbCategoryMap = {
  'Local Restaurants': ['Traditional Cooking'],
  'Museums': ['Heritage Tours'],
  'Nature Reserves': ['Nature & Wildlife'],
  'Game Reserves': ['Nature & Wildlife'],
  'Lodges': ['Accommodation & Lodging'],
  'Cultural Storytelling': ['Storytelling'],
  'Cultural Attire Market': ['Textile & Weaving'],
  'Traditional Healing': ['Traditional Healing'],
  'Historical Landmarks': ['Heritage Tours'],
  'Cultural Theatre': ['Music & Dance'],
  'Cultural Tours': ['Crafts & Art', 'Township Life', 'Rural Heritage', 'Photography Tours'],
}

const selectedCategorySlug = ref('')
const apiExperiences = ref([])
const loading = ref(true)
const showItineraryModal = ref(false)
const selectedForItinerary = ref(null)

const provinceMeta = ref(null)
const staticProvince = computed(() => provinces.find(p => p.slug === provinceSlug.value) || {})
const province = computed(() => provinceMeta.value || staticProvince.value)

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
  if (item.experience?.id) {
    router.push(`/experience/${item.experience.id}`)
  } else if (item.id) {
    router.push(`/destination/${item.id}`)
  }
}

function buildCategory(name) {
  const targets = (dbCategoryMap[name] || [name]).map(normalizeCategory)
  return apiExperiences.value
    .filter(e => targets.includes(normalizeCategory(e.category)))
    .map(e => ({
      name: e.title,
      location: e.location,
      rating: e.avg_rating,
      hours: null,
      contact: null,
      website: null,
      services: e.description ? [e.description.slice(0, 100)] : [],
      image: e.image_url || categoryImages[name] || '/img/cultures/Safari.jpg',
      category: name,
      experience: e,
    }))
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
  return cat.items
})

function openItineraryFor(item) {
  selectedForItinerary.value = item.experience || {
    title: item.name,
    location: item.location,
    province: province.value.name || '',
    description: item.services ? item.services.join(', ') : '',
    price: 0,
    duration_hours: null,
    id: item.id || null,
  }
  showItineraryModal.value = true
}

onMounted(async () => {
  // Province metadata from the database (falls back to static config if unavailable).
  try {
    const r = await api.get(`/provinces/${provinceSlug.value}`)
    provinceMeta.value = r.data
  } catch (e) {
    provinceMeta.value = null
  }

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
  background: url('/img/cultures/woman.jpeg') no-repeat center top;
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
.kzn-tab { padding: 8px 18px; border: 1px solid var(--border-strong); border-radius: 20px; background: var(--surface); color: var(--text-color); font-size: 0.82rem; font-family: inherit; cursor: pointer; transition: all 0.25s ease; white-space: nowrap; }
.kzn-tab:hover { background: var(--accent-light); color: var(--accent-text); border-color: var(--accent); }
.kzn-tab.active { background: var(--accent-fill); color: #1a1a1a; border-color: var(--accent-fill); font-weight: 600; }
.tab-count { opacity: 0.6; font-size: 0.75rem; }
.kzn-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.featured-card { display: block; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08); transition: transform 0.3s, box-shadow 0.3s; cursor: pointer; }
.featured-card:hover { transform: translateY(-6px); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12); }
.featured-img { height: 200px; position: relative; background-size: cover; background-position: center; }
.featured-cat { position: absolute; top: 12px; left: 12px; padding: 4px 12px; border-radius: 50px; font-size: 0.7rem; font-weight: 600; font-family: 'Poppins', sans-serif; color: #1a1a1a; background: var(--accent-fill); }
.featured-overlay { position: absolute; inset: 0; background: linear-gradient(to top, rgba(0, 0, 0, 0.75), transparent); display: flex; align-items: flex-end; padding: 16px; pointer-events: none; }
.featured-overlay h3 { font-size: 1.15rem; font-weight: 600; color: #fff; margin: 0; font-family: 'Poppins', sans-serif; }
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
  background: rgba(232, 162, 0, 0.12);
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}
.kzn-itinerary-btn:hover {
  background: var(--accent-fill);
  color: #1a1a1a;
  border-color: var(--accent);
}
.kzn-itinerary-btn svg {
  width: 12px;
  height: 12px;
}
@media (max-width: 768px) { .kzn-grid { grid-template-columns: 1fr; } .kzn-tabs { flex-wrap: nowrap; overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 8px; justify-content: flex-start; } .kzn-tab { flex-shrink: 0; } }
</style>
