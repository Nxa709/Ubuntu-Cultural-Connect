<template>
  <div class="notif-wrapper" ref="wrapperRef">
    <button class="notif-bell" @click="togglePanel" aria-label="Notifications">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
      </svg>
      <span v-if="store.unreadCount > 0" class="notif-badge">{{ store.unreadCount > 99 ? '99+' : store.unreadCount }}</span>
    </button>

    <Transition name="panel">
      <div v-if="store.showPanel" class="notif-panel">
        <div class="notif-panel-header">
          <h4>Notifications</h4>
          <button v-if="store.unreadCount > 0" class="mark-all-btn" @click="handleMarkAllRead">Mark all read</button>
        </div>
        <div class="notif-list" v-if="store.notifications.length > 0">
          <div
            v-for="n in store.notifications"
            :key="n.id"
            class="notif-item"
            :class="{ unread: !n.is_read }"
            @click="handleClick(n)"
          >
            <div class="notif-dot" v-if="!n.is_read"></div>
            <div class="notif-content">
              <p class="notif-message">{{ n.message }}</p>
              <span class="notif-time">{{ formatTime(n.created_at) }}</span>
            </div>
            <span class="notif-view">View &rarr;</span>
          </div>
        </div>
        <div class="notif-empty" v-else>
          <p v-if="store.loadError">{{ store.loadError }} — check console</p>
          <p v-else-if="store.unreadCount > 0">Loading notifications...</p>
          <p v-else>No notifications yet</p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '../stores/notification'

const router = useRouter()
const store = useNotificationStore()
const wrapperRef = ref(null)

function togglePanel() {
  store.togglePanel()
}

function handleClick(n) {
  if (!n.is_read) {
    store.markAsRead(n.id)
  }
  store.closePanel()

  if (n.type === 'hotspot_rejected' && n.experience_id) {
    router.push(`/host/edit/${n.experience_id}`)
  } else if (n.experience_id) {
    router.push(`/experience/${n.experience_id}`)
  }
}

function handleMarkAllRead() {
  store.markAllAsRead()
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diffMs = now - d
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHrs = Math.floor(diffMins / 60)
  if (diffHrs < 24) return `${diffHrs}h ago`
  const diffDays = Math.floor(diffHrs / 24)
  if (diffDays < 7) return `${diffDays}d ago`
  return d.toLocaleDateString('en-ZA', { month: 'short', day: 'numeric' })
}

function onClickOutside(e) {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target)) {
    store.closePanel()
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
  store.fetchNotifications()
  store.fetchUnreadCount()
})

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside)
})
</script>

<style scoped>
.notif-wrapper {
  position: relative;
  display: inline-flex;
}

.notif-bell {
  position: relative;
  background: none;
  border: none;
  color: #ffffff;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: color 0.3s;
  display: flex;
  align-items: center;
}

.notif-bell:hover {
  color: var(--accent);
}

.notif-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 18px;
  height: 18px;
  background: #ff6b6b;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  line-height: 1;
}

.notif-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 360px;
  max-width: 90vw;
  max-height: 420px;
  background: rgba(20, 20, 35, 0.98);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.notif-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.notif-panel-header h4 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: #fff;
  font-family: 'Poppins', sans-serif;
}

.mark-all-btn {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 0.78rem;
  cursor: pointer;
  font-family: inherit;
  padding: 2px 6px;
  border-radius: 4px;
  transition: background 0.2s;
}

.mark-all-btn:hover {
  background: rgba(255, 182, 18, 0.12);
}

.notif-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.notif-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.notif-item.unread {
  background: rgba(255, 182, 18, 0.06);
}

.notif-dot {
  width: 8px;
  height: 8px;
  min-width: 8px;
  border-radius: 50%;
  background: var(--accent);
  margin-top: 5px;
}

.notif-content {
  flex: 1;
  min-width: 0;
}

.notif-message {
  margin: 0;
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.4;
  word-wrap: break-word;
  white-space: pre-line;
}

.notif-time {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 3px;
  display: block;
}

.notif-view {
  align-self: center;
  font-size: 0.72rem;
  color: var(--accent);
  white-space: nowrap;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s;
}

.notif-item:hover .notif-view {
  opacity: 1;
}

.notif-empty {
  padding: 32px 16px;
  text-align: center;
}

.notif-empty p {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.85rem;
  margin: 0;
}

.panel-enter-active,
.panel-leave-active {
  transition: all 0.2s ease;
}

.panel-enter-from,
.panel-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.notif-list::-webkit-scrollbar {
  width: 4px;
}

.notif-list::-webkit-scrollbar-track {
  background: transparent;
}

.notif-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 4px;
}
</style>
