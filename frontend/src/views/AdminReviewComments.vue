<template>
  <div class="admin-page">
    <div class="hero-header">
      <h1><span class="accent-word">Review</span> Comments</h1>
      <p>Moderate user reviews and comments on experiences.</p>
    </div>

    <div class="filter-bar">
      <button
        v-for="f in filters"
        :key="f.value"
        :class="['filter-btn', { active: activeFilter === f.value }]"
        @click="setFilter(f.value)"
      >
        {{ f.label }}
        <span v-if="f.value === 'pending' && admin.pendingCommentCount > 0" class="badge">
          {{ admin.pendingCommentCount }}
        </span>
      </button>
    </div>

    <LoadingSpinner v-if="loading" message="Loading comments..." />

    <div v-else-if="admin.comments.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      <p>No {{ activeFilter }} comments found.</p>
    </div>

    <div v-else class="comments-list">
      <div v-for="comment in admin.comments" :key="comment.id" class="comment-card">
        <div class="comment-header">
          <div class="comment-meta">
            <span class="user-name">{{ comment.user_name || 'Anonymous' }}</span>
            <span class="separator">on</span>
            <span class="exp-title">{{ comment.experience_title || 'Unknown Experience' }}</span>
          </div>
          <div class="comment-date">{{ formatDate(comment.created_at) }}</div>
        </div>

        <div class="comment-score">
          <span v-for="s in 5" :key="s" class="star" :class="{ filled: s <= comment.score }">&#9733;</span>
        </div>

        <div class="comment-body">
          <p>{{ comment.comment }}</p>
        </div>

        <div class="comment-actions" v-if="activeFilter === 'pending'">
          <button @click="handleApprove(comment.id)" class="btn btn-approve" :disabled="processing">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            Approve
          </button>
          <button @click="handleReject(comment.id)" class="btn btn-reject" :disabled="processing">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
            Reject
          </button>
        </div>

        <div class="comment-status" v-else>
          <span v-if="comment.rejected_at" class="status-badge rejected">Rejected</span>
          <span v-else class="status-badge approved">Approved</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAdminStore } from '../stores/admin'

const admin = useAdminStore()
const loading = ref(true)
const processing = ref(false)
const activeFilter = ref('pending')

const filters = [
  { value: 'pending', label: 'Pending Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'all', label: 'All Comments' },
]

async function setFilter(f) {
  activeFilter.value = f
  loading.value = true
  await admin.fetchComments(f)
  loading.value = false
}

async function handleApprove(id) {
  processing.value = true
  await admin.approveComment(id)
  await admin.fetchComments(activeFilter.value)
  await admin.fetchPendingCommentCount()
  processing.value = false
}

async function handleReject(id) {
  processing.value = true
  await admin.rejectComment(id)
  await admin.fetchComments(activeFilter.value)
  await admin.fetchPendingCommentCount()
  processing.value = false
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-ZA', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

onMounted(async () => {
  await Promise.all([
    admin.fetchComments('pending'),
    admin.fetchPendingCommentCount(),
  ])
  loading.value = false
})
</script>

<style scoped>
.admin-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  position: relative;
  min-height: 100vh;
  padding: 5rem 1rem 2rem;
}

.admin-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.15);
  z-index: 0;
}

.admin-page > * {
  position: relative;
  z-index: 1;
  max-width: 900px;
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

.subtitle {
  color: rgba(255, 255, 255, 0.94);
}

.filter-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
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

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: var(--accent);
  color: #fff;
  font-size: 0.75rem;
  margin-left: 6px;
}

.loading-state, .empty-state {
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.comment-card {
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 12px;
  padding: 1.25rem;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  gap: 1rem;
}

.comment-meta {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.user-name {
  font-weight: 600;
  color: #fff;
}

.separator {
  color: rgba(255, 255, 255, 0.80);
}

.exp-title {
  color: var(--accent);
  font-weight: 500;
}

.comment-date {
  color: rgba(255, 255, 255, 0.80);
  font-size: 0.85rem;
  white-space: nowrap;
}

.comment-score {
  margin-bottom: 0.5rem;
}

.star {
  color: rgba(255, 255, 255, 0.55);
  font-size: 1.1rem;
}

.star.filled {
  color: var(--accent);
}

.comment-body p {
  color: #fff;
  line-height: 1.6;
  margin: 0 0 1rem;
}

.comment-actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-approve {
  background: #2E7D32;
  color: #fff;
}

.btn-approve:hover:not(:disabled) {
  background: #1B5E20;
}

.btn-reject {
  background: #C62828;
  color: #fff;
}

.btn-reject:hover:not(:disabled) {
  background: #B71C1C;
}

.status-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.approved {
  background: rgba(46, 125, 50, 0.25);
  color: #81C784;
}

.status-badge.rejected {
  background: rgba(198, 40, 40, 0.25);
  color: #EF9A9A;
}
</style>
