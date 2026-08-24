<template>
  <div class="admin-page">
    <div class="hero-header">
      <h1><span class="accent-word">Manage</span> Users</h1>
      <p>View, edit, and manage all platform user accounts.</p>
    </div>

    <div class="controls-bar">
      <div class="filter-bar">
        <button
          v-for="f in filters"
          :key="f.value"
          :class="['filter-btn', { active: activeFilter === f.value }]"
          @click="setFilter(f.value)"
        >
          {{ f.label }}
        </button>
      </div>

      <div class="search-bar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input v-model="searchQuery" @input="debouncedSearch" placeholder="Search by name or email..." />
      </div>
    </div>

    <LoadingSpinner v-if="loading" message="Loading users..." />

    <div v-else-if="admin.users.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
      </svg>
      <p>No users found.</p>
    </div>

    <div v-else class="users-list">
      <div v-for="user in admin.users" :key="user.id" class="user-card">
        <div class="user-main">
          <div class="user-avatar">
            {{ (user.full_name || 'U').charAt(0).toUpperCase() }}
          </div>

          <div class="user-details">
            <div class="user-name-row">
              <h3>{{ user.full_name }}</h3>
              <span :class="['role-badge', user.role]">{{ formatRole(user.role) }}</span>
              <span v-if="!user.is_active" class="status-badge inactive">Inactive</span>
            </div>
            <div class="user-meta">
              <span class="meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                  <polyline points="22,6 12,13 2,6"/>
                </svg>
                {{ user.email }}
              </span>
              <span class="meta-item" v-if="user.phone_number">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>
                </svg>
                {{ user.phone_number }}
              </span>
              <span class="meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                  <line x1="16" y1="2" x2="16" y2="6"/>
                  <line x1="8" y1="2" x2="8" y2="6"/>
                  <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
                Joined {{ formatDate(user.created_at) }}
              </span>
            </div>
          </div>
        </div>

        <div class="user-actions">
          <div class="action-group">
            <label class="action-label">Role</label>
            <select
              :value="user.role"
              @change="handleRoleChange(user.id, $event.target.value)"
              :disabled="user.id === currentUserId"
              class="role-select"
            >
              <option value="tourist">Tourist</option>
              <option value="business_owner">Host</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <button
            @click="handleToggleActive(user)"
            :disabled="user.id === currentUserId"
            :class="['btn', user.is_active ? 'btn-deactivate' : 'btn-activate']"
          >
            {{ user.is_active ? 'Deactivate' : 'Activate' }}
          </button>

          <button
            @click="handleDelete(user)"
            :disabled="user.id === currentUserId"
            class="btn btn-delete"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../stores/admin'
import { useAuthStore } from '../stores/auth'

const admin = useAdminStore()
const auth = useAuthStore()
const loading = ref(true)
const processing = ref(false)
const activeFilter = ref('all')
const searchQuery = ref('')
const currentUserId = ref(auth.user?.id)
let searchTimeout = null

const filters = [
  { value: 'all', label: 'All Users' },
  { value: 'tourist', label: 'Tourists' },
  { value: 'business_owner', label: 'Hosts' },
  { value: 'admin', label: 'Admins' },
]

async function setFilter(f) {
  activeFilter.value = f
  loading.value = true
  await admin.fetchUsers(f, searchQuery.value)
  loading.value = false
}

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(async () => {
    loading.value = true
    await admin.fetchUsers(activeFilter.value, searchQuery.value)
    loading.value = false
  }, 300)
}

async function handleRoleChange(userId, newRole) {
  if (processing.value) return
  processing.value = true
  try {
    await admin.changeUserRole(userId, newRole)
    await admin.fetchUsers(activeFilter.value, searchQuery.value)
  } finally {
    processing.value = false
  }
}

async function handleToggleActive(user) {
  if (processing.value) return
  processing.value = true
  try {
    await admin.toggleUserActive(user.id)
    await admin.fetchUsers(activeFilter.value, searchQuery.value)
  } finally {
    processing.value = false
  }
}

async function handleDelete(user) {
  if (!confirm(`Are you sure you want to delete ${user.full_name}? This action cannot be undone.`)) return
  if (processing.value) return
  processing.value = true
  try {
    await admin.deleteUser(user.id)
    await admin.fetchUsers(activeFilter.value, searchQuery.value)
  } finally {
    processing.value = false
  }
}

function formatRole(role) {
  return role.replace('_', ' ')
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-ZA', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

onMounted(async () => {
  await admin.fetchUsers('all')
  loading.value = false
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
  max-width: 1000px;
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
  letter-spacing: -0.5px;
  line-height: 1.15;
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
  line-height: 1.6;
}

.controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-bar {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  color: rgba(255, 255, 255, 0.97);
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.filter-btn.active {
  background: var(--heading-color);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.60);
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  min-width: 250px;
}

.search-bar svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.search-bar input {
  background: none;
  border: none;
  color: var(--text-color);
  font-size: 0.9rem;
  width: 100%;
  outline: none;
}

.search-bar input::placeholder {
  color: var(--text-muted);
}

.search-bar:focus-within {
  border-color: var(--accent);
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--text-secondary);
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem;
}

.user-main {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(232, 162, 0, 0.2);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 700;
  font-family: 'Poppins', sans-serif;
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.4rem;
  flex-wrap: wrap;
}

.user-name-row h3 {
  margin: 0;
  color: var(--heading-color);
  font-family: 'Poppins', sans-serif;
  font-size: 1.05rem;
}

.role-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.role-badge.tourist {
  background: rgba(100, 181, 246, 0.2);
  color: #1976D2;
}

.role-badge.business_owner {
  background: rgba(232, 162, 0, 0.2);
  color: var(--accent-dark);
}

.role-badge.admin {
  background: rgba(206, 147, 216, 0.2);
  color: #8E24AA;
}

.status-badge.inactive {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(239, 83, 80, 0.2);
  color: var(--error);
}

.user-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.meta-item svg {
  opacity: 0.6;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border);
  flex-wrap: wrap;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.action-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.role-select {
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--border-strong);
  border-radius: 6px;
  background: var(--glass-bg);
  color: var(--text-color);
  font-size: 0.85rem;
  cursor: pointer;
}

.role-select option {
  background: var(--glass-bg);
  color: var(--text-color);
}

.role-select:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn {
  padding: 0.4rem 0.9rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-deactivate {
  background: rgba(255, 183, 77, 0.2);
  color: #B45309;
}

.btn-deactivate:hover:not(:disabled) {
  background: rgba(255, 183, 77, 0.35);
}

.btn-activate {
  background: rgba(22, 163, 74, 0.2);
  color: var(--success);
}

.btn-activate:hover:not(:disabled) {
  background: rgba(22, 163, 74, 0.35);
}

.btn-delete {
  background: rgba(239, 83, 80, 0.2);
  color: var(--error);
}

.btn-delete:hover:not(:disabled) {
  background: rgba(239, 83, 80, 0.35);
}
</style>
