<template>
  <aside class="sidebar" v-if="auth.isBusinessOwner || auth.isAdmin">
    <div class="sidebar-brand">
      <div class="brand-icon">
        <img src="/img/Ubuntu_logo/Ubuntu-logo.png" alt="Ubuntu Cultural Connect" />
      </div>
      <div class="brand-text">
        <span class="brand-name">Ubuntu</span>
        <span class="brand-sub">Cultural Connect</span>
      </div>
    </div>

    <div class="account-selector">
      <span class="account-avatar">{{ initials }}</span>
      <div class="account-meta">
        <span class="account-name">{{ auth.user?.full_name || 'My Business' }}</span>
        <span class="account-role">{{ roleLabel }}</span>
      </div>
      <i class="bi bi-chevron-down account-caret"></i>
    </div>

    <nav class="sidebar-nav">
      <template v-for="item in navItems" :key="item.label">
        <router-link
          v-if="item.path"
          :to="item.path"
          class="sidebar-link"
          :class="{ active: isActive(item.path) }"
        >
          <i :class="['bi', item.icon]"></i>
          <span class="sidebar-label">{{ item.label }}</span>
        </router-link>
        <button v-else type="button" class="sidebar-link sidebar-link--muted">
          <i :class="['bi', item.icon]"></i>
          <span class="sidebar-label">{{ item.label }}</span>
        </button>
      </template>
    </nav>

    <div class="sidebar-bottom">
      <div class="user-card">
        <span class="user-avatar">{{ initials }}</span>
        <div class="user-meta">
          <span class="user-name">{{ auth.user?.full_name || 'Account' }}</span>
          <span class="user-role">{{ roleLabel }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout" title="Logout">
          <i class="bi bi-box-arrow-right"></i>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notification'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const notifStore = useNotificationStore()

const initials = computed(() => {
  const name = auth.user?.full_name || 'U'
  return name.trim().charAt(0).toUpperCase()
})

const roleLabel = computed(() => {
  if (auth.isAdmin) return 'Administrator'
  return 'Business Owner'
})

const navItems = computed(() => {
  if (auth.isAdmin) {
    return [
      { path: '/admin', label: 'Dashboard', icon: 'bi-grid-1x2' },
      { path: '/admin/hotspots', label: 'Listings', icon: 'bi-briefcase' },
      { path: '/admin/comments', label: 'Reviews', icon: 'bi-chat-square-text' },
      { path: '/analytics', label: 'Analytics', icon: 'bi-bar-chart-line' },
      { path: '/profile', label: 'Profile', icon: 'bi-person' },
      { path: null, label: 'Settings', icon: 'bi-gear' },
    ]
  }
  return [
    { path: '/host/dashboard', label: 'Dashboard', icon: 'bi-grid-1x2' },
    { path: '/my-hotspots', label: 'My Hotspots', icon: 'bi-briefcase' },
    { path: '/host/reviews', label: 'Reviews', icon: 'bi-chat-square-text' },
    { path: '/analytics', label: 'Analytics', icon: 'bi-bar-chart-line' },
    { path: '/profile', label: 'Profile', icon: 'bi-person' },
  ]
})

function isActive(path) {
  return route.path === path || route.path.startsWith(path + '/')
}

function handleLogout() {
  auth.logout()
  notifStore.stopPolling()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 232px;
  height: 100vh;
  background: #16212f;
  display: flex;
  flex-direction: column;
  z-index: 998;
  padding: 20px 14px 16px;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 8px;
  margin-bottom: 18px;
}

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--glass-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.brand-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.brand-name {
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 1.05rem;
  color: #ffffff;
}

.brand-sub {
  font-size: 0.7rem;
  color: #9fb0c3;
  letter-spacing: 0.04em;
}

.account-selector {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 12px;
  padding: 10px 12px;
  margin-bottom: 18px;
}

.account-avatar {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: var(--accent-fill);
  color: #1a1a1a;
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.account-meta {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.account-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.account-role {
  font-size: 0.7rem;
  color: #9fb0c3;
}

.account-caret {
  color: #9fb0c3;
  font-size: 0.8rem;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  overflow-y: auto;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 9px;
  color: #c3cfdd;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.18s;
  font-family: 'Poppins', sans-serif;
  background: none;
  border: none;
  cursor: pointer;
  width: 100%;
  text-align: left;
}

.sidebar-link i {
  font-size: 1.05rem;
  width: 20px;
  text-align: center;
}

.sidebar-link:hover {
  background: rgba(255, 255, 255, 0.07);
  color: #ffffff;
}

.sidebar-link.active {
  background: var(--accent-fill);
  color: #1a1a1a;
  font-weight: 600;
}

.sidebar-link--muted {
  cursor: default;
  opacity: 0.6;
}

.sidebar-bottom {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #2d465e;
  color: #ffffff;
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-meta {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
  line-height: 1.2;
}

.user-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 0.7rem;
  color: #9fb0c3;
}

.logout-btn {
  background: none;
  border: none;
  color: #9fb0c3;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  transition: all 0.18s;
}

.logout-btn:hover {
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
}
</style>
