<template>
  <div class="admin-page">
    <div class="hero-header">
      <h1><span class="accent-word">Registered</span> Hotspots</h1>
      <p>All cultural hotspots registered across the platform.</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading hotspots...</p>
    </div>

    <div v-else class="hotspots-grid">
      <div v-for="h in hotspots" :key="h.id" class="hs-card">
        <div class="hc-hero" :style="{ backgroundImage: `url(${h.image_url || '/img/cultures/Safari.jpg'})` }">
          <div class="hc-hero-overlay"></div>
          <div class="hc-hero-content">
            <div class="hc-badges">
              <span :class="['hc-status', h.is_approved ? 'approved' : 'pending']">{{ h.is_approved ? 'Approved' : 'Pending' }}</span>
              <span v-if="!h.is_active" class="hc-status inactive">Inactive</span>
            </div>
            <h3>{{ h.title }}</h3>
            <span class="hc-location">{{ h.location }}{{ h.province ? ', ' + h.province : '' }}</span>
          </div>
        </div>

        <div class="hc-body">
          <div class="hc-stats">
            <div class="hc-stat">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              <span>{{ h.avg_rating && h.rating_count > 0 ? h.avg_rating + ' (' + h.rating_count + ')' : 'No ratings' }}</span>
            </div>
            <div class="hc-stat">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
              <span>R{{ h.price }}</span>
            </div>
            <div class="hc-stat">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <span>{{ h.duration_hours ? h.duration_hours + 'h' : '—' }}</span>
            </div>
            <div class="hc-stat">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
              <span>{{ h.owner_name || 'Unknown' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../stores/admin'

const admin = useAdminStore()
const hotspots = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    await admin.fetchHotspots('all')
    hotspots.value = admin.hotspots
  } catch (e) {
    console.error('Failed to load hotspots', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.admin-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
  position: relative;
  min-height: 100vh;
  padding: 5rem 1rem 2rem;
}

.admin-page::before {
  content: "";
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 0;
}

.admin-page > * {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin-left: auto;
  margin-right: auto;
}

.hero-header {
  text-align: center;
  padding: 40px 20px 48px;
}

.hero-header h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 3rem;
  font-weight: 800;
  color: #fff;
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
  margin: 0 auto;
}

.hotspots-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .hotspots-grid { grid-template-columns: 1fr; }
}

.hs-card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 16px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.hs-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.hc-hero {
  height: 160px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.hc-hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 60%, rgba(0,0,0,0.1) 100%);
}

.hc-hero-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 16px;
}

.hc-hero-content h3 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #fff;
  margin: 6px 0 2px;
  font-family: 'Poppins', sans-serif;
  text-shadow: 0 2px 8px rgba(0,0,0,0.5);
}

.hc-location {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.75);
  text-shadow: 0 1px 4px rgba(0,0,0,0.5);
}

.hc-badges {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.hc-status {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hc-status.approved { background: #43A047; color: #fff; }
.hc-status.pending { background: #FF8F00; color: #fff; }
.hc-status.inactive { background: #7B1FA2; color: #fff; }

.hc-body {
  padding: 16px;
}

.hc-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.hc-stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.8);
}

.hc-stat svg {
  flex-shrink: 0;
  color: var(--accent);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: rgba(255, 255, 255, 0.6);
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(255, 255, 255, 0.18);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
