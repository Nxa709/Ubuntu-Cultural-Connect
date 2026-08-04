import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])
  const unreadCount = ref(0)
  const showPanel = ref(false)
  const loadError = ref('')

  let pollTimer = null

  function togglePanel() {
    showPanel.value = !showPanel.value
    if (showPanel.value) {
      fetchNotifications()
    }
  }

  function closePanel() {
    showPanel.value = false
  }

  async function fetchNotifications() {
    try {
      const r = await api.get('/notifications')
      notifications.value = r.data || []
      loadError.value = ''
    } catch (e) {
      console.error('Failed to fetch notifications', e)
      loadError.value = e.response?.status ? `Error ${e.response.status}` : 'Network error'
    }
  }

  async function fetchUnreadCount() {
    try {
      const r = await api.get('/notifications/unread-count')
      unreadCount.value = r.data.count
    } catch (e) {
      console.error('Failed to fetch unread count', e)
    }
  }

  async function markAsRead(id) {
    try {
      await api.put(`/notifications/${id}/read`)
      const n = notifications.value.find(n => n.id === id)
      if (n) n.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (e) {
      console.error('Failed to mark notification as read', e)
    }
  }

  async function markAllAsRead() {
    try {
      await api.put('/notifications/read-all')
      notifications.value.forEach(n => { n.is_read = true })
      unreadCount.value = 0
    } catch (e) {
      console.error('Failed to mark all as read', e)
    }
  }

  function startPolling(intervalMs = 10000) {
    stopPolling()
    fetchUnreadCount()
    fetchNotifications()
    pollTimer = setInterval(() => {
      fetchUnreadCount()
      fetchNotifications()
    }, intervalMs)
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  return {
    notifications,
    unreadCount,
    showPanel,
    loadError,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    startPolling,
    stopPolling,
    togglePanel,
    closePanel,
  }
})
