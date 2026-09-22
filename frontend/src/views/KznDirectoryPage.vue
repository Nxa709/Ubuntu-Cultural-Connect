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
          class="featured-card"
        >
          <div class="featured-img" :style="{ backgroundImage: `url(${item.image})` }">
            <span class="featured-cat">{{ item.category || selectedKznCategoryLabel }}</span>
            <div class="featured-overlay">
              <h3>{{ item.name }}</h3>
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
.kzn-page { background: url('/img/cultures/woman.jpeg') no-repeat center top; background-size: cover; position: relative; min-height: 100vh; padding: 100px 20px 40px; }
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
.featured-card { display: block; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08); transition: transform 0.3s, box-shadow 0.3s; cursor: pointer; color: inherit; text-decoration: none; }
.featured-card:hover { transform: translateY(-6px); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12); }
.featured-img { height: 200px; position: relative; background-size: cover; background-position: center; }
.featured-cat { position: absolute; top: 12px; left: 12px; padding: 4px 12px; border-radius: 50px; font-size: 0.7rem; font-weight: 600; font-family: 'Poppins', sans-serif; color: #1a1a1a; background: var(--accent-fill); }
.featured-overlay { position: absolute; inset: 0; background: linear-gradient(to top, rgba(0, 0, 0, 0.75), transparent); display: flex; align-items: flex-end; padding: 16px; pointer-events: none; }
.featured-overlay h3 { font-size: 1.15rem; font-weight: 600; color: #fff; margin: 0; font-family: 'Poppins', sans-serif; }
@media (max-width: 768px) { .kzn-grid { grid-template-columns: 1fr; } .kzn-tabs { flex-wrap: nowrap; overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 8px; justify-content: flex-start; } .kzn-tab { flex-shrink: 0; } }
</style>
