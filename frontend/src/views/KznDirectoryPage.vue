<template>
  <div class="kzn-page">
    <div class="kzn-dir-section">
      <button class="back-btn" @click="goBack">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        Back
      </button>
      <h2 class="dir-heading">KZN Cultural Tourism Directory</h2>
      <p class="dir-sub">Explore 68 cultural tourism entities across KwaZulu-Natal, from restaurants and museums to game reserves and cultural tours.</p>

      <div class="kzn-tabs">
        <button
          v-for="cat in kznCategories"
          :key="cat.slug"
          :class="['kzn-tab', { active: selectedKznCategory === cat.slug }]"
          @click="selectedKznCategory = cat.slug"
        >
          {{ cat.name }}
        </button>
      </div>

      <div class="kzn-grid" v-if="currentKznItems.length > 0">
        <router-link
          v-for="(item, idx) in currentKznItems"
          :key="idx"
          :to="'/kzn-directory/item/' + slugify(item.name)"
          class="kzn-flip-card"
        >
          <div class="kzn-flip-inner">
            <div class="kzn-flip-front" :style="{ backgroundImage: `url(${item.image})` }">
              <span class="exp-cat-badge">{{ item.category || selectedKznCategoryLabel }}</span>
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
              </div>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { kznCategories } from '../data/kznCulturalData'
import { itemImages } from '../data/kznImages'

const router = useRouter()

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/experiences')
  }
}

const selectedKznCategory = ref(kznCategories.length > 0 ? kznCategories[0].slug : '')

function slugify(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
}

const currentKznItems = computed(() => {
  const cat = kznCategories.find(c => c.slug === selectedKznCategory.value)
  return cat ? cat.items.map(item => ({ ...item, image: itemImages[item.name] || cat.image })) : []
})

const selectedKznCategoryLabel = computed(() => {
  const cat = kznCategories.find(c => c.slug === selectedKznCategory.value)
  return cat ? cat.name : ''
})
</script>

<style scoped>
.kzn-page { background: url('/img/cultures/woman.jpeg') no-repeat center center; background-size: cover; position: relative; min-height: 100vh; padding: 100px 20px 40px; }
.kzn-page::before { content: ""; position: absolute; inset: 0; background: rgba(0, 0, 0, 0.15); z-index: 0; }
.kzn-page > * { position: relative; z-index: 1; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; background: rgba(255, 255, 255, 0.26); border: 1px solid rgba(255, 255, 255, 0.38); color: rgba(255, 255, 255, 0.97); padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; font-family: inherit; cursor: pointer; transition: all 0.2s; margin-bottom: 20px; }
.back-btn:hover { background: rgba(255, 255, 255, 0.36); color: #fff; }
.kzn-dir-section { max-width: 1200px; margin: 0 auto; }
.dir-heading { text-align: center; font-size: 1.6rem; color: #fff; margin-bottom: 28px; font-family: 'Poppins', sans-serif; }
.dir-sub { text-align: center; color: rgba(255, 255, 255, 0.90); font-size: 0.95rem; margin: -16px auto 32px; max-width: 600px; line-height: 1.6; }
.exp-cat-badge { position: absolute; top: 12px; left: 12px; background: rgba(0, 0, 0, 0.5); color: #fff; font-size: 0.72rem; font-weight: 500; padding: 3px 10px; border-radius: 6px; }
.kzn-tabs { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 28px; }
.kzn-tab { padding: 8px 18px; border: 1px solid var(--border-strong); border-radius: 20px; background: var(--surface); color: var(--text-color); font-size: 0.82rem; font-family: inherit; cursor: pointer; transition: all 0.25s ease; white-space: nowrap; }
.kzn-tab:hover { background: var(--accent-light); color: var(--accent-text); border-color: var(--accent); }
.kzn-tab.active { background: var(--accent-fill); color: #1a1a1a; border-color: var(--accent-fill); font-weight: 600; }
.kzn-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.kzn-flip-card { display: block; text-decoration: none; color: inherit; perspective: 1000px; height: 280px; cursor: pointer; }
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
@media (max-width: 768px) { .kzn-grid { grid-template-columns: 1fr; } .kzn-tabs { flex-wrap: nowrap; overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 8px; justify-content: flex-start; } .kzn-tab { flex-shrink: 0; } }
</style>
