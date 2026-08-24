<template>
  <div class="admin-page">
    <div class="hero-header">
      <h1><span class="accent-word">Admin</span> Dashboard</h1>
      <p>Monitor platform activity, manage users, and oversee registered hotspots.</p>
    </div>

    <LoadingSpinner v-if="loading" message="Loading dashboard..." />

    <template v-else>
      <!-- Platform Growth Overview -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg></div>
          <div class="stat-info">
            <span class="stat-number">{{ admin.stats?.total_users || 0 }}</span>
            <span class="stat-label">Total Users</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg></div>
          <div class="stat-info">
            <span class="stat-number">{{ admin.stats?.total_experiences || 0 }}</span>
            <span class="stat-label">Total Hotspots</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></div>
          <div class="stat-info">
            <span class="stat-number">{{ admin.stats?.total_ratings || 0 }}</span>
            <span class="stat-label">Total Reviews</span>
          </div>
        </div>
      </div>

      <div class="charts-grid">
        <!-- User Analytics -->
        <div class="card">
          <h2>User Analytics</h2>
          <div class="card-body-content">
            <div class="metric-row">
              <span class="metric-lbl">Tourists</span>
              <span class="metric-val">{{ admin.stats?.total_tourists || 0 }}</span>
            </div>
            <div class="metric-row">
              <span class="metric-lbl">Business Owners</span>
              <span class="metric-val">{{ admin.stats?.total_hosts || 0 }}</span>
            </div>
            <div class="metric-row">
              <span class="metric-lbl">Admins</span>
              <span class="metric-val">{{ admin.stats?.total_admins || 0 }}</span>
            </div>
            <div class="metric-row total">
              <span class="metric-lbl">Total Users</span>
              <span class="metric-val">{{ admin.stats?.total_users || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- Hotspot Analytics -->
        <div class="card">
          <h2>Hotspot Analytics</h2>
          <div class="card-body-content">
            <div class="metric-row">
              <span class="metric-lbl">Approved</span>
              <span class="metric-val" style="color:#66BB6A">{{ admin.stats?.approved_experiences || 0 }}</span>
            </div>
            <div class="metric-row">
              <span class="metric-lbl">Pending Approval</span>
              <span class="metric-val" style="color:#FFB74D">{{ admin.stats?.pending_experiences || 0 }}</span>
            </div>
            <div class="metric-row">
              <span class="metric-lbl">Active</span>
              <span class="metric-val" style="color:#81C784">{{ activeHotspots }}</span>
            </div>
            <div class="metric-row total">
              <span class="metric-lbl">Total Hotspots</span>
              <span class="metric-val">{{ admin.stats?.total_experiences || 0 }}</span>
            </div>
          </div>
          <div class="status-bar">
            <div class="status-segment approved" :style="{ flex: approvedExps }"></div>
            <div class="status-segment pending" :style="{ flex: pendingExps }"></div>
          </div>
        </div>

        <!-- Engagement Analytics -->
        <div class="card">
          <h2>Engagement</h2>
          <div class="card-body-content">
            <div class="metric-row">
              <span class="metric-lbl">Planned Trips</span>
              <span class="metric-val">{{ admin.stats?.total_trips || 0 }}</span>
            </div>
            <div class="metric-row">
              <span class="metric-lbl">Reviews Submitted</span>
              <span class="metric-val">{{ admin.stats?.total_ratings || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- Review Analytics -->
        <div class="card">
          <h2>Review Analytics</h2>
          <div class="card-body-content">
            <div class="metric-row">
              <span class="metric-lbl">Total Reviews</span>
              <span class="metric-val">{{ admin.stats?.total_ratings || 0 }}</span>
            </div>
            <div class="metric-row">
              <span class="metric-lbl">Pending Moderation</span>
              <span class="metric-val" style="color:#FFB74D">{{ admin.stats?.pending_comments || 0 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Pending Reviews Alert -->
      <div class="pending-section" v-if="(admin.stats?.pending_experiences || 0) > 0 || (admin.stats?.pending_comments || 0) > 0">
        <h2>Pending Reviews</h2>
        <div class="pending-grid">
          <router-link to="/admin/hotspots" class="pending-card" v-if="admin.stats?.pending_experiences > 0">
            <div class="pending-count">{{ admin.stats.pending_experiences }}</div>
            <div class="pending-info">
              <span class="pending-title">Hotspots</span>
              <span class="pending-sub">Awaiting approval</span>
            </div>
          </router-link>
          <router-link to="/admin/comments" class="pending-card" v-if="admin.stats?.pending_comments > 0">
            <div class="pending-count">{{ admin.stats.pending_comments }}</div>
            <div class="pending-info">
              <span class="pending-title">Comments</span>
              <span class="pending-sub">Awaiting moderation</span>
            </div>
          </router-link>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '../stores/admin'
const admin = useAdminStore()
const loading = ref(true)

const totalItineraryAdds = computed(() => {
  return admin.hotspots.reduce((s, e) => s + (e.itinerary_adds || 0), 0)
})

const activeHotspots = computed(() => {
  return admin.hotspots.filter(e => e.is_active && e.is_approved).length
})

const approvedExps = computed(() => Math.max(admin.stats?.approved_experiences || 1, 1))
const pendingExps = computed(() => Math.max(admin.stats?.pending_experiences || 1, 1))

onMounted(async () => {
  try {
    await Promise.all([
      admin.fetchStats(),
      admin.fetchHotspots('all'),
    ])
  } catch (e) {
    console.error('Failed to load dashboard', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.admin-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center top;
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
  background: rgba(0, 0, 0, 0.15);
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
  color: rgba(255, 255, 255, 0.94);
  max-width: 520px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(232, 162, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
  flex-shrink: 0;
}

.stat-number {
  display: block;
  font-size: 1.6rem;
  font-weight: 800;
  color: #fff;
  line-height: 1;
  font-family: 'Poppins', sans-serif;
}

.stat-label {
  display: block;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.88);
  margin-top: 2px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.card {
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 14px;
  padding: 1.25rem;
  color: #fff;
}

.card h2 {
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 1rem;
  font-family: 'Poppins', sans-serif;
}

.card-body-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.18);
}

.metric-row.total {
  border-top: 1px solid rgba(255, 255, 255, 0.30);
  margin-top: 4px;
  padding-top: 10px;
  border-bottom: none;
}

.metric-lbl {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.94);
}

.metric-val {
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
}

.status-bar {
  display: flex;
  height: 6px;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 12px;
}

.status-segment.approved { background: #66BB6A; }
.status-segment.pending { background: #FFB74D; }

.pending-section {
  margin-bottom: 2.5rem;
}

.pending-section h2 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--heading-color);
  margin-bottom: 1rem;
}

.pending-grid {
  display: flex;
  gap: 1rem;
}

.pending-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(232, 162, 0, 0.08);
  border: 1px solid rgba(232, 162, 0, 0.25);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  text-decoration: none;
  transition: all 0.25s;
  flex: 1;
}

.pending-card:hover {
  background: rgba(232, 162, 0, 0.15);
  border-color: var(--accent);
}

.pending-count {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--accent);
  font-family: 'Poppins', sans-serif;
  line-height: 1;
  min-width: 40px;
  text-align: center;
}

.pending-title {
  display: block;
  font-weight: 600;
  color: #fff;
}

.pending-sub {
  display: block;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.88);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: rgba(255, 255, 255, 0.88);
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(255, 255, 255, 0.45);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
