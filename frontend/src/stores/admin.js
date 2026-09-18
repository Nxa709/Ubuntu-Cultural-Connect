import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useAdminStore = defineStore('admin', () => {
  const comments = ref([])
  const hotspots = ref([])
  const users = ref([])
  const pendingCommentCount = ref(0)
  const pendingHotspotCount = ref(0)
  const stats = ref(null)
  const analytics = ref(null)

  async function fetchStats() {
    const r = await api.get('/admin/stats')
    stats.value = r.data
    return r.data
  }

  async function fetchAnalyticsOverview() {
    const r = await api.get('/admin/analytics/overview')
    analytics.value = r.data
    return r.data
  }

  async function fetchComments(statusFilter = 'pending') {
    const r = await api.get('/admin/comments', { params: { status_filter: statusFilter } })
    comments.value = r.data
    return r.data
  }

  async function fetchPendingCommentCount() {
    const r = await api.get('/admin/comments/pending/count')
    pendingCommentCount.value = r.data.count
    return r.data.count
  }

  async function approveComment(id) {
    const r = await api.put(`/admin/comments/${id}/approve`)
    return r.data
  }

  async function rejectComment(id) {
    const r = await api.put(`/admin/comments/${id}/reject`)
    return r.data
  }

  async function fetchHotspots(statusFilter = 'pending') {
    const r = await api.get('/admin/hotspots', { params: { status_filter: statusFilter } })
    hotspots.value = r.data
    return r.data
  }

  async function fetchPendingHotspotCount() {
    const r = await api.get('/admin/hotspots/pending/count')
    pendingHotspotCount.value = r.data.count
    return r.data.count
  }

  async function approveHotspot(id) {
    const r = await api.put(`/admin/hotspots/${id}/approve`)
    return r.data
  }

  async function rejectHotspot(id, reason) {
    const r = await api.put(`/admin/hotspots/${id}/reject`, { reason })
    return r.data
  }

  /* Remove a hotspot from the current list after it leaves the pending queue. */
  function removeHotspot(id) {
    hotspots.value = hotspots.value.filter(h => h.id !== id)
    if (pendingHotspotCount.value > 0) pendingHotspotCount.value -= 1
  }

  async function fetchUsers(roleFilter = 'all', search = '') {
    const r = await api.get('/admin/users', { params: { role_filter: roleFilter, search } })
    users.value = r.data
    return r.data
  }

  async function changeUserRole(id, role) {
    const r = await api.put(`/admin/users/${id}/role`, { role })
    return r.data
  }

  async function toggleUserActive(id) {
    const r = await api.put(`/admin/users/${id}/toggle-active`)
    return r.data
  }

  async function deleteUser(id) {
    const r = await api.delete(`/admin/users/${id}`)
    return r.data
  }

  return {
    comments, hotspots, users, pendingCommentCount, pendingHotspotCount, stats, analytics,
    fetchStats, fetchAnalyticsOverview, fetchComments, fetchPendingCommentCount, approveComment, rejectComment,
    fetchHotspots, fetchPendingHotspotCount, approveHotspot, rejectHotspot, removeHotspot,
    fetchUsers, changeUserRole, toggleUserActive, deleteUser,
  }
})
