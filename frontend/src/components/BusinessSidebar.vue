<template>
  <aside class="sidebar" v-if="auth.isBusinessOwner || auth.isAdmin">
    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="sidebar-link"
        :class="{ active: isActive(item.path) }"
      >
        <span class="sidebar-icon" v-html="item.icon"></span>
        <span class="sidebar-label">{{ item.label }}</span>
        <span v-if="item.badge && item.badge > 0" class="sidebar-badge">{{ item.badge > 99 ? '99+' : item.badge }}</span>
      </router-link>

      <button class="sidebar-link notif-link" @click="toggleNotifPanel">
        <span class="sidebar-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
        </span>
        <span class="sidebar-label">Notifications</span>
        <span v-if="notifStore.unreadCount > 0" class="sidebar-badge">{{ notifStore.unreadCount > 99 ? '99+' : notifStore.unreadCount }}</span>
      </button>
    </nav>

    <div class="sidebar-footer">
      <button @click="handleLogout" class="sidebar-link logout-link">
        <span class="sidebar-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </span>
        <span class="sidebar-label">Logout</span>
      </button>
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

const navItems = computed(() => {
  const items = []
  if (auth.isBusinessOwner) {
    items.push(
      {
        path: '/my-hotspots',
        label: 'My Hotspots',
        icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
      },
      {
        path: '/analytics',
        label: 'Analytics',
        icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
      },
    )
  }
  if (auth.isAdmin) {
    items.push(
      {
        path: '/admin/registered-hotspots',
        label: 'Registered Hotspots',
        icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
      },
      {
        path: '/admin',
        label: 'Admin Dashboard',
        icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
      },
    )
  }
  items.push({
    path: '/profile',
    label: 'Profile',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
  })
  return items
})

function isActive(path) {
  return route.path.startsWith(path)
}

function toggleNotifPanel() {
  document.querySelector('.notif-bell')?.click()
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
  width: 220px;
  height: 100vh;
  background: rgba(10, 10, 25, 0.95);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  z-index: 998;
  padding-top: 80px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  font-size: 0.88rem;
  font-weight: 500;
  transition: all 0.2s;
  font-family: 'Poppins', sans-serif;
  background: none;
  border: none;
  cursor: pointer;
  width: 100%;
  text-align: left;
}

.sidebar-link:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.sidebar-link.active {
  background: rgba(255, 182, 18, 0.12);
  color: var(--accent);
}

.sidebar-link.logout-link:hover {
  background: rgba(198, 40, 40, 0.15);
  color: #EF5350;
}

.notif-link {
  position: relative;
}

.sidebar-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.sidebar-label {
  white-space: nowrap;
  flex: 1;
}

.sidebar-badge {
  background: #FF5252;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
  line-height: 1;
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
}
</style>
