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
          <div class="hero-actions" v-if="!auth.isLoggedIn">
            <router-link to="/login" class="btn-outline-light">Login</router-link>
          </div>
        </div>
      </div>

      <div class="floating-stats">
        <div class="stat-card">
          <h3>50+</h3>
          <p>Cultural Experiences</p>
        </div>
        <div class="stat-card">
          <h3>9</h3>
          <p>Provinces Covered</p>
        </div>
        <div class="stat-card">
          <h3>100%</h3>
          <p>Community Owned</p>
        </div>
      </div>
    </section>

    <section class="recommended-section">
      <div class="recommended-container">
        <div class="section-badge">
          <i class="bi bi-star-fill"></i>
          Handpicked for You
        </div>
        <h2 class="section-heading">
          <template v-if="auth.isLoggedIn && hasPreferences">Handpicked Experiences Just for You</template>
          <template v-else>Handpicked Experiences</template>
        </h2>

        <div v-if="loadingRecs" class="loading-rec">Loading experiences...</div>
        <div v-else-if="auth.isLoggedIn && recommended.length > 0" class="rec-grid">
          <router-link
            v-for="exp in recommended"
            :key="exp.id"
            :to="`/experience/${exp.id}`"
            class="rec-card"
          >
            <div class="rec-inner">
              <div class="rec-front" :style="{ backgroundImage: `url(${exp.image_url || '/img/cultures/Safari.jpg'})` }">
                <span class="rec-cat">{{ exp.category }}</span>
                <span class="rec-rating" v-if="exp.avg_rating">&#9733; {{ exp.avg_rating.toFixed(1) }}</span>
                <div class="rec-front-name-bar">
                  <h3>{{ exp.title }}</h3>
                  <p class="rec-loc">{{ exp.location || exp.province }}</p>
                </div>
              </div>
              <div class="rec-back">
                <div class="rec-back-body">
                  <div class="rec-card-meta">
                    <span class="rec-back-location">{{ exp.location || exp.province }}</span>
                    <span class="rec-back-rating" v-if="exp.avg_rating">&#9733; {{ exp.avg_rating.toFixed(1) }}</span>
                  </div>
                  <div class="rec-detail-row"><strong>Category:</strong> {{ exp.category }}</div>
                  <p class="rec-back-desc">{{ exp.description }}</p>
                  <div class="rec-back-footer">
                    <span v-if="exp.priceRange || exp.price" class="rec-back-price">{{ exp.priceRange || 'From R' + exp.price }}</span>
                  </div>
                </div>
              </div>
            </div>
          </router-link>
        </div>
        <div v-else class="rec-grid">
          <router-link
            v-for="(item, idx) in handpicked"
            :key="idx"
            :to="`/destination/${item.id}`"
            class="rec-card"
          >
            <div class="rec-inner">
              <div class="rec-front" :style="{ backgroundImage: `url(${item.image})` }">
                <span class="rec-cat">{{ item.category }}</span>
                <span class="rec-rating" v-if="item.rating">&#9733; {{ item.rating }}</span>
                <div class="rec-front-name-bar">
                  <h3>{{ item.name }}</h3>
                  <p class="rec-loc">{{ item.location }}</p>
                </div>
              </div>
              <div class="rec-back">
                <div class="rec-back-body">
                  <div class="rec-card-meta">
                    <span class="rec-back-location">{{ item.location }}</span>
                    <span class="rec-back-rating" v-if="item.rating">&#9733; {{ item.rating }}</span>
                  </div>
                  <div class="rec-detail-row"><strong>Category:</strong> {{ item.category }}</div>
                  <p class="rec-back-desc">{{ item.description }}</p>
                  <div class="rec-back-footer">
                    <span v-if="item.priceRange" class="rec-back-price">{{ item.priceRange }}</span>
                  </div>
                </div>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </section>

    <section class="provinces-section">
      <div class="provinces-container">
        <div class="section-badge">
          <i class="bi bi-geo-alt-fill"></i>
          Explore by Province
        </div>
        <h2 class="section-heading">Discover South Africa's <br>9 Beautiful Provinces</h2>

        <div class="provinces-grid">
          <router-link
            v-for="province in provinces"
            :key="province.slug"
            :to="province.slug === 'kwaZulu-natal' ? '/kzn-directory' : `/province/${province.slug}`"
            class="province-card"
          >
            <div class="province-img" :style="{ backgroundImage: `url(${province.image})` }">
              <div class="province-overlay">
                <h3>{{ province.name }}</h3>
              </div>
            </div>
            <div class="province-body">
              <p>{{ province.description }}</p>
              <div class="province-destinations">
                <span v-for="dest in province.destinations.slice(0, 3)" :key="dest.id" class="dest-tag">{{ dest.name }}</span>
                <span v-if="province.destinations.length > 3" class="dest-tag more">+{{ province.destinations.length - 3 }} more</span>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useExperienceStore } from '../stores/experience'
import { provinces } from '../data/provinces'
import api from '../services/api'

const auth = useAuthStore()
const expStore = useExperienceStore()

const recommended = ref([])
const loadingRecs = ref(false)
const hasPreferences = ref(false)
const handpicked = ref([])

function slugify(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
}

onMounted(async () => {
  // Build handpicked list from top destinations across provinces
  const topDests = []
  for (const p of provinces) {
    for (const d of p.destinations) {
      topDests.push({ ...d, province: p.name })
    }
  }
  topDests.sort((a, b) => (b.rating || 0) - (a.rating || 0))
  handpicked.value = topDests.slice(0, 9)

  if (auth.isLoggedIn) {
    loadingRecs.value = true
    try {
      const r = await api.get('/experiences/home')
      expStore.preferences = r.data.preferences
      hasPreferences.value = r.data.preferences.length > 0
      recommended.value = r.data.recommended
    } catch (e) {
      // silently fail
    } finally {
      loadingRecs.value = false
    }
  }
})
</script>

<style scoped>
.home-page {
  padding-top: 0;
  background: url('/img/cultures/woman.jpeg') no-repeat center center fixed;
  background-size: cover;
  position: relative;
  min-height: 100vh;
}

.home-page::before {
  content: "";
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 0;
  pointer-events: none;
}

.home-page > * {
  position: relative;
  z-index: 1;
}

/* Hero */
.hero {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
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
  color: rgba(255, 255, 255, 0.85);
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

.floating-stats {
  position: absolute;
  bottom: 50px;
  left: 7%;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  z-index: 1;
}

.stat-card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 18px 24px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  min-width: 160px;
}

.stat-card h3 {
  font-size: 1.5rem;
  color: var(--accent);
  margin-bottom: 6px;
}

.stat-card p {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.82);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(25px); }
  to { opacity: 1; transform: translateY(0); }
}

.section-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 50px;
  font-size: 0.85rem;
  color: var(--accent);
  background: rgba(255, 182, 18, 0.15);
  margin-bottom: 16px;
}

.section-heading {
  font-size: 2.2rem;
  margin-bottom: 50px;
  line-height: 1.2;
  color: #fff;
}

/* Recommended Section */
.recommended-section {
  padding: 80px 20px;
}
.recommended-container {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}
.loading-rec {
  color: rgba(255, 255, 255, 0.6);
  padding: 40px 0;
}
.no-prefs {
  color: rgba(255, 255, 255, 0.7);
  padding: 40px 0;
}
.no-prefs p {
  margin-bottom: 16px;
}
.btn-sm {
  display: inline-block;
  padding: 8px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  text-decoration: none;
}
.rec-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 20px;
}
.rec-card {
  perspective: 1000px;
  height: 280px;
  cursor: pointer;
  text-decoration: none;
  color: inherit;
  display: block;
}
.rec-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.5s;
  transform-style: preserve-3d;
}
.rec-card:hover .rec-inner {
  transform: rotateY(180deg);
}
.rec-front, .rec-back {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.rec-front {
  background-size: cover;
  background-position: center;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}
.rec-cat {
  position: absolute;
  top: 12px;
  left: 12px;
  font-size: 0.7rem;
  padding: 3px 10px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-weight: 500;
}
.rec-rating {
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 0.75rem;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
}
.rec-front-name-bar {
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  padding: 30px 14px 14px;
}
.rec-front-name-bar h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  margin: 0 0 2px;
  text-shadow: 0 1px 4px rgba(0,0,0,0.5);
}
.rec-loc {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}
.rec-back {
  transform: rotateY(180deg);
  background: rgba(30, 30, 50, 0.96);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  color: #fff;
}
.rec-back-body {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.rec-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.rec-back-location {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.6);
}
.rec-back-rating {
  font-size: 0.78rem;
  color: var(--accent);
}
.rec-detail-row {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.75);
  line-height: 1.5;
  margin-bottom: 6px;
}
.rec-detail-row strong {
  color: rgba(255, 255, 255, 0.9);
  margin-right: 4px;
}
.rec-back-desc {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  margin-bottom: 8px;
}
.rec-back-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.rec-back-price {
  font-size: 0.78rem;
  color: var(--accent);
  font-weight: 600;
}
/* Provinces Section */
.provinces-section {
  padding: 80px 20px;
}

.provinces-container {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.provinces-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-top: 20px;
}

.province-card {
  display: block;
  text-decoration: none;
  color: inherit;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  text-align: left;
}

.province-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
}

.province-img {
  height: 160px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.province-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
  display: flex;
  align-items: flex-end;
  padding: 16px;
}

.province-overlay h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.province-body {
  padding: 16px;
}

.province-body p {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
  margin-bottom: 14px;
}

.province-destinations {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.dest-tag {
  font-size: 0.72rem;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.75);
  white-space: nowrap;
}

.dest-tag.more {
  background: rgba(255, 182, 18, 0.15);
  color: var(--accent);
}

@media (max-width: 768px) {
  .rec-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .floating-stats {
    position: static;
    padding: 30px 20px;
    justify-content: center;
  }

  .provinces-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
</style>
