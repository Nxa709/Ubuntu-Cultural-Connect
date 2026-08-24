<template>
  <div class="owner-dash">
    <div class="dash-content">
      <div class="welcome">
        <h1>Welcome, <span class="accent-word">{{ auth.user?.full_name || 'Owner' }}</span></h1>
        <p>Manage your cultural tourism business from one place.</p>
      </div>

      <div class="quick-grid">
        <router-link to="/host" class="quick-card">
          <div class="qc-icon" style="background: #E3F2FD">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1565C0" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
            </svg>
          </div>
          <h3>My Hotspots</h3>
          <p>View and manage your registered cultural experiences</p>
        </router-link>

        <router-link to="/host/register" class="quick-card">
          <div class="qc-icon" style="background: #E8F5E9">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2E7D32" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </div>
          <h3>Register New Hotspot</h3>
          <p>Add a new cultural experience to your portfolio</p>
        </router-link>

        <router-link to="/analytics" class="quick-card">
          <div class="qc-icon" style="background: #FFF8E1">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </div>
          <h3>Analytics</h3>
          <p>Track performance, ratings, and customer feedback</p>
        </router-link>

        <router-link to="/host/reviews" class="quick-card">
          <div class="qc-icon" style="background: #F3E5F5">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#7B1FA2" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <h3>Reviews</h3>
          <p>See what your guests are saying about your hotspots</p>
        </router-link>
      </div>

      <div class="stats-preview" v-if="stats || store.myExperiences.length">
        <h2>At a Glance</h2>
        <div class="stats-row">
          <div class="s-card highlight-card">
            <span class="s-value">{{ stats?.registered_hotspots ?? registeredCount }}</span>
            <span class="s-label">Registered Hotspots</span>
          </div>
          <div class="s-card">
            <span class="s-value active-v">{{ stats?.active_hotspots ?? activeCount }}</span>
            <span class="s-label">Active</span>
          </div>
          <div class="s-card">
            <span class="s-value pending-v">{{ stats?.pending_approval ?? 0 }}</span>
            <span class="s-label">Pending</span>
          </div>
          <div class="s-card">
            <span class="s-value">{{ stats?.total_ratings ?? 0 }}</span>
            <span class="s-label">Total Reviews</span>
          </div>
          <div class="s-card">
            <span class="s-value">{{ stats?.avg_rating || 'â€”' }}</span>
            <span class="s-label">Avg Rating</span>
          </div>
          <div class="s-card">
            <span class="s-value">{{ stats?.total_itinerary_adds ?? totalAdds }}</span>
            <span class="s-label">Total Itinerary Adds</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useExperienceStore } from '../stores/experience'

const auth = useAuthStore()
const store = useExperienceStore()
const stats = ref(null)

const registeredCount = computed(() => store.myExperiences.length)
const activeCount = computed(() => store.myExperiences.filter(e => e.is_active && e.is_approved).length)
const totalAdds = computed(() => store.myExperiences.reduce((sum, e) => sum + (e.itinerary_adds || 0), 0))

onMounted(async () => {
  try {
    await Promise.all([store.fetchOwnerStats(), store.fetchMyExperiences()])
    stats.value = store.ownerStats
  } catch (e) {
    console.error('Failed to load stats', e)
  }
})
</script>

<style scoped>
.owner-dash { background: #0a0c12; position: relative; min-height: 100vh; padding: 100px 20px 40px; }
.owner-dash::before { content: ""; position: fixed; inset: -32px; z-index: 0; background: url('/img/cultures/woman.jpeg') no-repeat center top; background-size: cover; filter: blur(14px); transform: scale(1.08); }
.owner-dash::after { content: ""; position: fixed; inset: 0; z-index: 0; background: rgba(0, 0, 0, 0.45); }
.dash-content { position: relative; z-index: 1; max-width: 1100px; margin: 0 auto; }
.welcome { text-align: center; padding: 40px 20px 48px; }
.welcome h1 { font-family: 'Poppins', sans-serif; font-size: 2.5rem; font-weight: 800; color: #fff; margin-bottom: 12px; }
.welcome .accent-word { font-family: 'Pacifico', cursive; font-weight: 400; color: var(--accent); }
.welcome p { font-size: 1.05rem; color: rgba(255, 255, 255, 0.94); max-width: 520px; margin: 0 auto; line-height: 1.6; }
.quick-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 32px; }
.quick-card { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 32px 24px; background: rgba(255, 255, 255, 0.28); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); border: 1px solid rgba(255, 255, 255, 0.45); border-radius: 14px; text-decoration: none; transition: all 0.3s ease; }
.quick-card:hover { transform: translateY(-4px); background: rgba(255, 255, 255, 0.36); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); }
.qc-icon { width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; }
.quick-card h3 { color: #fff; font-family: 'Poppins', sans-serif; font-size: 1.1rem; margin-bottom: 8px; }
.quick-card p { color: rgba(255, 255, 255, 0.90); font-size: 0.85rem; line-height: 1.5; max-width: 220px; }
.stats-preview h2 { text-align: center; font-size: 1.3rem; color: #fff; font-family: 'Poppins', sans-serif; margin-bottom: 20px; }
.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.s-card { background: rgba(255, 255, 255, 0.38); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); border: 1px solid rgba(255, 255, 255, 0.42); border-radius: 12px; padding: 20px; text-align: center; }
.s-card.highlight-card { background: rgba(232, 162, 0, 0.22); border-color: rgba(232, 162, 0, 0.5); }
.s-value { display: block; font-size: 1.8rem; font-weight: 700; color: #fff; font-family: 'Poppins', sans-serif; }
.s-value.active-v { color: var(--success); }
.s-value.pending-v { color: var(--warning); }
.s-label { display: block; color: rgba(255, 255, 255, 0.9); font-size: 0.85rem; margin-top: 4px; }

@media (max-width: 768px) {
  .quick-grid { grid-template-columns: 1fr; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
  .stats-row { grid-template-columns: 1fr; }
}
</style>
