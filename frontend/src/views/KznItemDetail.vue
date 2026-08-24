<template>
  <div class="detail-page">
    <LoadingSpinner v-if="!item" message="Loading..." />

    <template v-else>
      <div class="detail-hero" :style="{ backgroundImage: `url(${item.image})` }">
        <div class="detail-hero-overlay"></div>
        <div class="detail-hero-content">
          <button class="back-link" @click="goBack">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
            </svg>
            Back
          </button>
          <span class="cat-badge">{{ item.category }}</span>
          <h1>{{ item.name }}</h1>
          <div class="hero-meta">
            <span class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
              </svg>
              {{ item.location }}
            </span>
            <span class="meta-item" v-if="item.rating">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              {{ item.rating }} / 5
            </span>
            <span class="meta-item" v-if="item.priceRange">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
              {{ item.priceRange }}
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
          <div class="info-grid">
            <div class="info-card" v-if="item.hours">
              <div class="info-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <div class="info-text">
                <span class="info-label">Operating Hours</span>
                <span class="info-value">{{ item.hours }}</span>
              </div>
            </div>

            <div class="info-card" v-if="item.contact">
              <div class="info-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                </svg>
              </div>
              <div class="info-text">
                <span class="info-label">Contact</span>
                <span class="info-value">{{ item.contact }}</span>
              </div>
            </div>

            <div class="info-card" v-if="item.website">
              <div class="info-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                </svg>
              </div>
              <div class="info-text">
                <span class="info-label">Website</span>
                <a :href="item.website" target="_blank" rel="noopener" class="info-value link">{{ item.website }}</a>
              </div>
            </div>

            <div class="info-card" v-if="item.priceRange">
              <div class="info-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                </svg>
              </div>
              <div class="info-text">
                <span class="info-label">Price Range</span>
                <span class="info-value">{{ item.priceRange }}</span>
              </div>
            </div>

            <div class="info-card" v-if="item.rating">
              <div class="info-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
              </div>
              <div class="info-text">
                <span class="info-label">Rating</span>
                <span class="info-value stars">{{ 'â˜…'.repeat(Math.round(item.rating)) }}{{ 'â˜†'.repeat(5 - Math.round(item.rating)) }} {{ item.rating }}</span>
              </div>
            </div>
          </div>

          <div class="desc-section">
            <h2>About</h2>
            <p>{{ item.description }}</p>
          </div>

          <div class="services-section" v-if="item.services && item.services.length">
            <h2>Services</h2>
            <ul class="services-list">
              <li v-for="(s, si) in item.services" :key="si">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                {{ s }}
              </li>
            </ul>
          </div>

          <div class="loc-section" v-if="mapQuery">
            <h2>Location</h2>
            <div class="location-detail">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
              </svg>
              <div>
                <span class="loc-main">{{ item.location }}</span>
                <span class="loc-province">KwaZulu-Natal, South Africa</span>
              </div>
            </div>
            <div class="map-container">
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
        </div>

        <div class="sidebar">
          <div class="sidebar-card sticky">
            <div class="sidebar-price">
              <span class="price-val">{{ item.priceRange || 'Price Varies' }}</span>
            </div>
            <div class="sidebar-details">
              <div class="detail-row">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                </svg>
                <span>{{ item.hours || 'Hours not specified' }}</span>
              </div>
              <div class="detail-row">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                </svg>
                <span>{{ item.location }}</span>
              </div>
              <div class="detail-row" v-if="item.contact">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                </svg>
                <span>{{ item.contact }}</span>
              </div>
              <div class="detail-row" v-if="item.rating">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
                <span>{{ item.rating }} / 5</span>
              </div>
            </div>

            <button v-if="auth.isTourist" class="btn-trip-full" @click="openItineraryFor(item)">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
              </svg>
              Add to Itinerary
            </button>

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

    <AddToItineraryModal
      :experience="selectedForItinerary"
      :visible="showItineraryModal"
      @close="showItineraryModal = false"
      @success="handleItinerarySuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getAllKznItems } from '../data/kznCulturalData'
import { itemImages } from '../data/kznImages'
import { useAuthStore } from '../stores/auth'
import AddToItineraryModal from '../components/AddToItineraryModal.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const allItems = getAllKznItems()
const showItineraryModal = ref(false)
const selectedForItinerary = ref(null)
const currentTripInfo = ref(null)

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/kzn-directory')
  }
}

function slugify(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
}

const item = computed(() => {
  const slug = route.params.slug
  const found = allItems.find(i => slugify(i.name) === slug)
  if (found) {
    return { ...found, image: itemImages[found.name] || found.image }
  }
  return null
})

const mapQuery = computed(() => {
  if (!item.value || !item.value.location) return ''
  const parts = [item.value.location, 'KwaZulu-Natal', 'South Africa'].filter(Boolean)
  return encodeURIComponent(parts.join(', '))
})

function handleItinerarySuccess(tripInfo) {
  if (tripInfo) currentTripInfo.value = tripInfo
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-ZA', { year: 'numeric', month: 'short', day: 'numeric' })
}

function openItineraryFor(kznItem) {
  selectedForItinerary.value = {
    title: kznItem.name,
    location: kznItem.location,
    province: 'KwaZulu-Natal',
    description: kznItem.description || '',
    price: kznItem.priceRange ? parseFloat(kznItem.priceRange.replace(/[^0-9.]/g, '')) || 0 : 0,
    duration_hours: null,
    id: null,
  }
  showItineraryModal.value = true
}
</script>

<style scoped>
.detail-page { background: url('/img/cultures/woman.jpeg') no-repeat center top fixed; background-size: cover; position: relative; min-height: 100vh; }
.detail-page::before { content: ""; position: fixed; inset: 0; background: rgba(0, 0, 0, 0.15); z-index: 0; }
.detail-page > * { position: relative; z-index: 1; }
.loading-state { display: flex; justify-content: center; align-items: center; min-height: 60vh; color: rgba(255, 255, 255, 0.88); font-size: 1.1rem; }
.detail-hero { position: relative; height: 400px; background-size: cover; background-position: center; }
.detail-hero-overlay { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.8)); }
.detail-hero-content { position: relative; z-index: 1; max-width: 1000px; margin: 0 auto; padding: 100px 24px 40px; display: flex; flex-direction: column; justify-content: flex-end; height: 100%; }
.back-link { display: inline-flex; align-items: center; gap: 6px; background: rgba(255, 255, 255, 0.26); border: 1px solid rgba(255, 255, 255, 0.38); color: rgba(255, 255, 255, 0.97); padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; font-family: inherit; cursor: pointer; transition: all 0.2s; width: fit-content; margin-bottom: 20px; }
.back-link:hover { background: rgba(255, 255, 255, 0.36); color: #fff; }
.cat-badge { display: inline-block; background: var(--accent-fill); color: #1a1a1a; padding: 4px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; width: fit-content; margin-bottom: 12px; }
.detail-hero-content h1 { font-family: 'Poppins', sans-serif; font-size: 2.5rem; font-weight: 800; color: #fff; margin: 0 0 8px; text-shadow: 0 2px 8px rgba(0,0,0,0.3); }
.hero-meta { display: flex; gap: 20px; flex-wrap: wrap; }
.meta-item { display: flex; align-items: center; gap: 6px; color: rgba(255, 255, 255, 0.97); font-size: 0.88rem; }
.meta-item svg { flex-shrink: 0; }
.detail-body { max-width: 1000px; margin: 0 auto; padding: 40px 24px 60px; }
.info-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; margin-bottom: 32px; }
.info-card { background: rgba(255, 255, 255, 0.22); border: 1px solid rgba(255, 255, 255, 0.28); border-radius: 12px; padding: 18px; display: flex; align-items: flex-start; gap: 14px; }
.info-icon { width: 42px; height: 42px; border-radius: 10px; background: rgba(255,182,18,0.15); display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: var(--accent); }
.info-text { display: flex; flex-direction: column; gap: 2px; }
.info-label { font-size: 0.72rem; color: rgba(255, 255, 255, 0.80); text-transform: uppercase; letter-spacing: 0.5px; }
.info-value { font-size: 0.92rem; color: #fff; line-height: 1.4; word-break: break-word; }
.info-value.link { color: var(--accent); text-decoration: none; font-size: 0.82rem; }
.info-value.link:hover { text-decoration: underline; }
.info-value.stars { color: var(--accent); }
.desc-section { margin-bottom: 32px; }
.desc-section h2 { font-family: 'Poppins', sans-serif; font-size: 1.3rem; color: #fff; margin-bottom: 14px; }
.desc-section p { color: rgba(255, 255, 255, 0.97); line-height: 1.8; font-size: 0.95rem; }
.services-section h2 { font-family: 'Poppins', sans-serif; font-size: 1.3rem; color: #fff; margin-bottom: 14px; }
.services-list { list-style: none; padding: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.services-list li { display: flex; align-items: flex-start; gap: 8px; color: rgba(255, 255, 255, 0.97); font-size: 0.88rem; line-height: 1.5; }
.services-list li svg { margin-top: 3px; flex-shrink: 0; }
.loc-section { margin-bottom: 32px; }
.loc-section h2 { font-family: 'Poppins', sans-serif; font-size: 1.3rem; color: #fff; margin-bottom: 14px; }
.location-detail { display: flex; align-items: flex-start; gap: 0.75rem; color: rgba(255, 255, 255, 0.97); margin-bottom: 14px; }
.location-detail svg { flex-shrink: 0; color: var(--accent); }
.loc-main { display: block; font-weight: 600; color: #fff; }
.loc-province { display: block; font-size: 0.9rem; color: rgba(255, 255, 255, 0.88); }
.map-container { background: rgba(255, 255, 255, 0.28); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); border: 1px solid rgba(255, 255, 255, 0.45); border-radius: 12px; padding: 0.75rem; }
.map-container iframe { width: 100%; height: 320px; border: none; border-radius: 10px; display: block; background: #dde3e8; }
.map-open-link { display: inline-flex; align-items: center; gap: 0.4rem; margin-top: 0.75rem; font-size: 0.9rem; font-weight: 600; color: var(--accent); text-decoration: none; }
.map-open-link:hover { color: var(--accent-hover); }

/* Itinerary Banner */
.itinerary-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1100px;
  margin: 0 auto;
  padding: 10px 20px;
  background: rgba(232, 162, 0, 0.12);
  border: 1px solid rgba(232, 162, 0, 0.25);
  border-radius: 10px;
  animation: fadeIn 0.35s ease;
}
.banner-left { display: flex; align-items: center; gap: 10px; color: var(--accent); }
.banner-left svg { flex-shrink: 0; }
.banner-title { display: block; font-size: 0.88rem; font-weight: 600; color: #fff; }
.banner-meta { font-size: 0.75rem; color: rgba(255, 255, 255, 0.80); }
.banner-link { font-size: 0.82rem; color: var(--accent); text-decoration: none; font-weight: 600; white-space: nowrap; transition: opacity 0.2s; }
.banner-link:hover { opacity: 0.8; }

/* Mini Itinerary Card */
.mini-itinerary {
  margin-top: 12px;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.30);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.20);
  animation: fadeIn 0.35s ease;
}
.mini-itinerary-header { display: flex; align-items: center; gap: 6px; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--accent); font-weight: 600; margin-bottom: 8px; }
.mini-itinerary-body { margin-bottom: 8px; }
.mini-trip-name { font-size: 0.9rem; font-weight: 600; color: #fff; }
.mini-trip-dates { font-size: 0.75rem; color: rgba(255, 255, 255, 0.80); margin-top: 1px; }
.mini-trip-entries { font-size: 0.75rem; color: var(--accent); margin-top: 3px; }
.mini-itinerary-link { display: block; text-align: center; font-size: 0.8rem; color: var(--accent); text-decoration: none; padding: 6px 0; border-top: 1px solid rgba(255, 255, 255, 0.24); margin-top: 6px; font-weight: 500; transition: opacity 0.2s; }
.mini-itinerary-link:hover { opacity: 0.8; }

.sidebar { position: sticky; top: 90px; }
.sidebar-card { background: rgba(255, 255, 255, 0.28); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); border: 1px solid rgba(255, 255, 255, 0.45); border-radius: 12px; padding: 1.5rem; }
.sidebar-price { text-align: center; margin-bottom: 1.25rem; padding-bottom: 1.25rem; border-bottom: 1px solid rgba(255, 255, 255, 0.28); }
.price-val { display: block; font-size: 1.3rem; font-weight: 700; font-family: 'Poppins', sans-serif; color: var(--accent); }
.sidebar-details { margin-bottom: 1.25rem; }
.detail-row { display: flex; align-items: center; gap: 0.6rem; padding: 0.6rem 0; color: rgba(255, 255, 255, 0.97); font-size: 0.9rem; border-bottom: 1px solid rgba(255, 255, 255, 0.20); }
.detail-row:last-child { border-bottom: none; }
.detail-row svg { color: var(--accent); flex-shrink: 0; width: 16px; height: 16px; }
.btn-trip-full { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; padding: 0.75rem; border-radius: 8px; font-size: 0.9rem; font-weight: 600; text-decoration: none; transition: all 0.2s; border: 1px solid var(--accent-fill); background: var(--accent-fill); color: #1a1a1a; cursor: pointer; font-family: inherit; }
.btn-trip-full:hover { background: var(--accent-fill-hover); color: #1a1a1a; border-color: var(--accent-fill-hover); }
.detail-body { display: grid; grid-template-columns: 1fr 300px; gap: 2rem; align-items: start; }
@media (max-width: 768px) { .detail-hero { height: 280px; } .detail-hero-content h1 { font-size: 1.6rem; } .info-grid { grid-template-columns: 1fr; } .services-list { grid-template-columns: 1fr; } .hero-meta { flex-direction: column; gap: 8px; } .detail-body { grid-template-columns: 1fr; } }
</style>
