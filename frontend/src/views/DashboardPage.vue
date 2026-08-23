<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Dashboard</h1>
      <p class="role-label">Welcome back, {{ auth.user?.full_name }}</p>
    </div>

    <div class="dashboard-content">
      <div class="info-card">
        <h2>User Information</h2>
        <div class="info-grid">
          <div class="info-item">
            <label>Full Name</label>
            <p>{{ auth.user?.full_name }}</p>
          </div>
          <div class="info-item">
            <label>Email</label>
            <p>{{ auth.user?.email }}</p>
          </div>
          <div class="info-item">
            <label>Phone</label>
            <p>{{ auth.user?.phone_number || 'Not provided' }}</p>
          </div>
          <div class="info-item">
            <label>Role</label>
            <p class="role-text">{{ auth.userRole?.replace('_', ' ') }}</p>
          </div>
        </div>
      </div>

      <template v-if="auth.isTourist">
        <div class="info-card" v-if="preferences.length > 0">
          <div class="card-row">
            <div>
              <h2>Your Preferences</h2>
              <div class="pref-tags">
                <span class="pref-tag" v-for="p in preferences" :key="p">{{ p }}</span>
              </div>
            </div>
            <router-link to="/preferences" class="btn-link">Update</router-link>
          </div>
        </div>

        <div class="info-card" v-else>
          <div class="card-row">
            <div>
              <h2>Set Your Preferences</h2>
              <p class="card-desc">Tell us what cultural experiences interest you to get personalized recommendations.</p>
            </div>
            <router-link to="/preferences" class="btn btn-primary-sm">Get Started</router-link>
          </div>
        </div>

        <div class="info-card">
          <div class="card-row">
            <h2>Recommended Experiences</h2>
            <router-link to="/experiences" class="btn-link">View All</router-link>
          </div>
          <div class="rec-grid" v-if="recommended.length > 0">
            <div class="rec-card" v-for="exp in recommended" :key="exp.id">
              <div class="rec-img" :style="{ backgroundImage: `url(${exp.image_url || getCategoryImage(exp.category)})` }">
                <span class="rec-badge">{{ exp.category }}</span>
              </div>
              <div class="rec-body">
                <h4>{{ exp.title }}</h4>
                <p class="rec-loc">{{ exp.location }}</p>
                <div class="rec-footer">
                  <router-link :to="`/rate/${exp.id}`" class="rec-rate">Rate</router-link>
                </div>
              </div>
            </div>
          </div>
          <div class="empty-rec" v-else>
            <p>No recommendations yet. <router-link to="/preferences">Set your preferences</router-link> to get started.</p>
          </div>
        </div>

        <div class="info-card">
          <div class="card-row">
            <h2>Quick Actions</h2>
          </div>
          <div class="quick-grid">
            <router-link to="/experiences" class="quick-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
              <span>Browse Experiences</span>
            </router-link>
            <router-link to="/plan-trip" class="quick-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              <span>Plan a Trip</span>
            </router-link>
            <router-link to="/preferences" class="quick-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              <span>Set Preferences</span>
            </router-link>
          </div>
        </div>
      </template>

      <template v-if="auth.isBusinessOwner">
        <div class="info-card">
          <h2>Host Dashboard</h2>
          <p class="card-desc">Manage your cultural experiences and connect with tourists.</p>
          <div class="quick-grid">
            <router-link to="/host" class="quick-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              <span>My Hotspots</span>
            </router-link>
            <router-link to="/host/register" class="quick-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              <span>Register Hotspot</span>
            </router-link>
            <router-link to="/analytics" class="quick-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
              <span>Analytics</span>
            </router-link>
          </div>
        </div>
      </template>

      <template v-if="auth.isAdmin">
        <div class="info-card">
          <h2>Admin Panel</h2>
          <p class="card-desc">Manage users, verify hosts, and oversee platform operations.</p>
          <div class="quick-grid">
            <router-link to="/admin/comments" class="quick-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              <span>Review Comments</span>
            </router-link>
            <router-link to="/admin/hotspots" class="quick-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
              <span>Review Hotspots</span>
            </router-link>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useExperienceStore } from '../stores/experience'
import api from '../services/api'

const auth = useAuthStore()
const expStore = useExperienceStore()

const preferences = ref([])
const recommended = ref([])

onMounted(async () => {
  try {
    const r = await api.get('/experiences/home')
    preferences.value = r.data.preferences
    expStore.preferences = r.data.preferences
    recommended.value = r.data.recommended
  } catch (e) {
    // silently fail
  }
})

function getCategoryColor(cat) {
  const colors = {
    'Traditional Cooking': 'var(--accent)', 'Storytelling': '#6B2A2A', 'Music & Dance': 'var(--heading-color)',
    'Crafts & Art': '#5C4033', 'Heritage Tours': '#4A3228', 'Township Life': '#1a1a1a',
    'Rural Heritage': '#8B6914', 'Traditional Healing': '#2E7D32', 'Textile & Weaving': '#7B5B3A',
    'Photography Tours': '#5D4037', 'Nature & Wildlife': '#2E7D32', 'Accommodation & Lodging': '#6B4F3A',
  }
  return colors[cat] || 'var(--heading-color)'
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
.dashboard {
  background: url('/img/cultures/woman.jpeg') no-repeat center top;
  background-size: cover;
  background-attachment: fixed;
  position: relative;
  min-height: 100vh;
  padding: 5rem 1rem 2rem;
}

.dashboard::before {
  content: "";
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.15);
  z-index: 0;
}

.dashboard > * {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin-left: auto;
  margin-right: auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.dashboard-header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #fff;
}

.role-label {
  color: rgba(255, 255, 255, 0.94);
  font-size: 0.9rem;
}

.info-card {
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  margin-bottom: 20px;
  color: #fff;
}

.info-card h2 {
  color: #fff;
  margin-bottom: 16px;
  font-size: 1.2rem;
}

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.card-desc {
  color: rgba(255, 255, 255, 0.94);
  font-size: 0.88rem;
  margin-top: 4px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item label {
  display: block;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.80);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item p {
  font-size: 0.95rem;
  color: #fff;
}

.role-text {
  text-transform: capitalize;
}

.btn-link {
  font-size: 0.85rem;
  color: var(--accent);
  font-weight: 500;
}

.btn-primary-sm {
  padding: 8px 18px;
  background: var(--accent);
  color: #1a1a1a;
  border-radius: 50px;
  font-size: 0.88rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-primary-sm:hover {
  background: rgba(255, 255, 255, 0.38);
  color: #fff;
  transform: translateY(-1px);
}

.pref-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.pref-tag {
  background: rgba(255, 182, 18, 0.2);
  color: var(--accent);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.82rem;
  font-weight: 500;
}

.rec-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.rec-card {
  background: rgba(255, 255, 255, 0.26);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.38);
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.rec-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.rec-img {
  height: 80px;
  position: relative;
  background-size: cover;
  background-position: center;
}

.rec-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 0.68rem;
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 500;
}

.rec-body { padding: 14px; }
.rec-body h4 { font-size: 0.88rem; color: #fff; margin-bottom: 4px; }
.rec-loc { font-size: 0.78rem; color: rgba(255, 255, 255, 0.88); margin-bottom: 8px; }

.rec-footer {
  display: flex;
  justify-content: flex-end;
}

.rec-rate {
  font-size: 0.78rem;
  color: #fff;
  background: rgba(255, 255, 255, 0.30);
  padding: 4px 12px;
  border-radius: 50px;
  border: 1px solid rgba(255, 255, 255, 0.50);
  text-decoration: none;
  transition: all 0.2s;
}

.rec-rate:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.empty-rec {
  color: rgba(255, 255, 255, 0.80);
  font-size: 0.88rem;
  padding: 20px 0;
}

.empty-rec a { color: var(--accent); font-weight: 500; }

.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.quick-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  background: rgba(255, 255, 255, 0.26);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.38);
  border-radius: 12px;
  text-decoration: none;
  color: #fff;
  font-size: 0.82rem;
  font-weight: 500;
  transition: all 0.3s;
}

.quick-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
</style>
