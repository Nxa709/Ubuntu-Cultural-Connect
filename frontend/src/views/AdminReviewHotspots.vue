<template>
  <div class="admin-page">
    <div class="hero-header">
      <h1><span class="accent-word">Review</span> Hotspots</h1>
      <p>Approve or reject cultural hotspot submissions from hosts.</p>
    </div>

    <div class="filter-bar">
      <button
        v-for="f in filters"
        :key="f.value"
        :class="['filter-btn', { active: activeFilter === f.value }]"
        @click="setFilter(f.value)"
      >
        {{ f.label }}
        <span v-if="f.value === 'pending' && admin.pendingHotspotCount > 0" class="badge">
          {{ admin.pendingHotspotCount }}
        </span>
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading hotspots...</p>
    </div>

    <div v-else-if="admin.hotspots.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
        <circle cx="12" cy="10" r="3"/>
      </svg>
      <p>No {{ activeFilter }} hotspots found.</p>
    </div>

    <div v-else class="hotspots-list">
      <div v-for="hotspot in admin.hotspots" :key="hotspot.id" class="hotspot-card">
        <div class="hotspot-header">
          <div class="hotspot-title-row">
            <h3>{{ hotspot.title }}</h3>
            <span class="category-tag">{{ hotspot.category }}</span>
            <span v-if="hotspot.rejected_at" class="status-badge rejected">Rejected</span>
          </div>
          <div class="hotspot-location">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            {{ hotspot.location }}<span v-if="hotspot.province">, {{ hotspot.province }}</span>
          </div>
        </div>

        <div class="hotspot-image" v-if="hotspot.image_url">
          <img :src="hotspot.image_url" :alt="hotspot.title" />
        </div>

        <div class="hotspot-body">
          <p :class="{ 'full-desc': expanded === hotspot.id }">{{ hotspot.description }}</p>
        </div>

        <div class="detail-grid" v-if="expanded === hotspot.id">
          <div class="detail-item">
            <span class="detail-label">Price</span>
            <span class="detail-value">R {{ hotspot.price }}</span>
          </div>
          <div class="detail-item" v-if="hotspot.duration_hours">
            <span class="detail-label">Duration</span>
            <span class="detail-value">{{ hotspot.duration_hours }} hours</span>
          </div>
          <div class="detail-item" v-if="hotspot.max_participants">
            <span class="detail-label">Max Participants</span>
            <span class="detail-value">{{ hotspot.max_participants }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Category</span>
            <span class="detail-value">{{ hotspot.category }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Location</span>
            <span class="detail-value">{{ hotspot.location }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Reviews</span>
            <span class="detail-value">{{ hotspot.rating_count }} (avg {{ hotspot.avg_rating || '—' }})</span>
          </div>

          <div class="owner-section">
            <div class="owner-title">Owner Information</div>
            <div class="owner-info">
              <div class="detail-item">
                <span class="detail-label">Name</span>
                <span class="detail-value">{{ hotspot.owner_name || 'Unknown' }}</span>
              </div>
              <div class="detail-item" v-if="hotspot.owner_email">
                <span class="detail-label">Email</span>
                <span class="detail-value">{{ hotspot.owner_email }}</span>
              </div>
              <div class="detail-item" v-if="hotspot.owner_phone">
                <span class="detail-label">Phone</span>
                <span class="detail-value">{{ hotspot.owner_phone }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Owner ID</span>
                <span class="detail-value">#{{ hotspot.owner_id }}</span>
              </div>
            </div>
          </div>

          <div class="rejection-box" v-if="hotspot.rejection_reason">
            <div class="rejection-title">Rejection Reason</div>
            <p class="rejection-reason">{{ hotspot.rejection_reason }}</p>
          </div>
        </div>

        <div class="hotspot-footer">
          <div class="hotspot-info">
            <span class="info-item">Hosted by {{ hotspot.owner_name || 'Unknown' }}</span>
            <span class="info-item">{{ hotspot.rating_count }} reviews</span>
            <span class="info-item">Added {{ formatDate(hotspot.created_at) }}</span>
          </div>

          <div class="hotspot-actions">
            <button class="btn btn-details" @click="toggleExpand(hotspot.id)">
              {{ expanded === hotspot.id ? 'Hide Details' : 'View Details' }}
            </button>

            <template v-if="activeFilter === 'pending'">
              <button @click="handleApprove(hotspot.id)" class="btn btn-approve" :disabled="processing">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                Approve
              </button>
              <button @click="openRejectModal(hotspot)" class="btn btn-reject" :disabled="processing">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
                Reject
              </button>
            </template>

            <template v-else-if="activeFilter === 'approved'">
              <span class="status-badge approved">Approved</span>
            </template>
            <template v-else-if="activeFilter === 'rejected'">
              <span class="status-badge rejected">Rejected</span>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="modal-overlay" @click.self="closeRejectModal">
      <div class="modal-card">
        <h3>Reject Hotspot</h3>
        <p class="modal-subtitle">
          <strong>{{ rejectTarget?.title }}</strong><br>
          {{ rejectTarget?.owner_name || 'Unknown' }} · {{ rejectTarget?.category }}
        </p>

        <div class="form-group">
          <label>Reason for rejection <span class="required">*</span></label>
          <textarea
            v-model="rejectReason"
            rows="4"
            maxlength="500"
            placeholder="Explain why this hotspot is being rejected. The owner will be notified with this message."
          ></textarea>
          <span class="char-count">{{ rejectReason.length }}/500</span>
        </div>

        <div class="modal-actions">
          <button class="btn btn-outline" @click="closeRejectModal">Cancel</button>
          <button
            class="btn btn-reject"
            :disabled="!rejectReason.trim() || processing"
            @click="handleReject"
          >
            {{ processing ? 'Rejecting...' : 'Reject & Notify Owner' }}
          </button>
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
const expanded = ref(null)
const showRejectModal = ref(false)
const rejectTarget = ref(null)
const rejectReason = ref('')

const filters = [
  { value: 'pending', label: 'Pending Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'all', label: 'All Hotspots' },
]

async function setFilter(f) {
  activeFilter.value = f
  expanded.value = null
  loading.value = true
  await admin.fetchHotspots(f)
  loading.value = false
}

function toggleExpand(id) {
  expanded.value = expanded.value === id ? null : id
}

async function handleApprove(id) {
  if (!confirm('Approve this hotspot? It will become visible to tourists.')) return
  processing.value = true
  try {
    await admin.approveHotspot(id)
    await admin.fetchHotspots(activeFilter.value)
    await admin.fetchPendingHotspotCount()
  } finally {
    processing.value = false
  }
}

function openRejectModal(hotspot) {
  rejectTarget.value = hotspot
  rejectReason.value = ''
  showRejectModal.value = true
}

function closeRejectModal() {
  showRejectModal.value = false
  rejectTarget.value = null
  rejectReason.value = ''
}

async function handleReject() {
  if (!rejectTarget.value || !rejectReason.value.trim()) return
  processing.value = true
  try {
    await admin.rejectHotspot(rejectTarget.value.id, rejectReason.value.trim())
    closeRejectModal()
    await admin.fetchHotspots(activeFilter.value)
    await admin.fetchPendingHotspotCount()
  } finally {
    processing.value = false
  }
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-ZA', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

onMounted(async () => {
  await Promise.all([
    admin.fetchHotspots('pending'),
    admin.fetchPendingHotspotCount(),
  ])
  loading.value = false
})
</script>

<style scoped>
.admin-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
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
  background: rgba(0, 0, 0, 0.55);
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
  color: rgba(255, 255, 255, 0.7);
  max-width: 520px;
  margin: 0 auto;
  line-height: 1.6;
}

.filter-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  color: #ccc;
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
  color: #f9f9f9;
  border-color: rgba(255, 255, 255, 0.3);
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
  color: #ccc;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(255, 255, 255, 0.18);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.hotspots-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.hotspot-card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  padding: 1.25rem;
}

.hotspot-header {
  margin-bottom: 0.75rem;
}

.hotspot-title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
  flex-wrap: wrap;
}

.hotspot-title-row h3 {
  margin: 0;
  color: #fff;
  font-family: 'Poppins', sans-serif;
}

.category-tag {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 6px;
  font-size: 0.78rem;
  color: #ccc;
  white-space: nowrap;
}

.hotspot-location {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #bbb;
  font-size: 0.9rem;
}

.hotspot-image {
  margin-bottom: 0.75rem;
  border-radius: 10px;
  overflow: hidden;
  max-height: 220px;
}

.hotspot-image img {
  width: 100%;
  height: 220px;
  object-fit: cover;
  display: block;
}

.hotspot-body p {
  color: #fff;
  line-height: 1.6;
  margin: 0 0 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hotspot-body p.full-desc {
  display: block;
  -webkit-line-clamp: unset;
  overflow: visible;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: rgba(255, 255, 255, 0.5);
}

.detail-value {
  font-size: 0.9rem;
  color: #fff;
  word-break: break-word;
}

.owner-section {
  grid-column: 1 / -1;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  padding-top: 12px;
  margin-top: 4px;
}

.owner-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 8px;
}

.owner-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.rejection-box {
  grid-column: 1 / -1;
  background: rgba(198, 40, 40, 0.15);
  border: 1px solid rgba(198, 40, 40, 0.3);
  border-radius: 8px;
  padding: 12px;
}

.rejection-title {
  font-size: 0.78rem;
  font-weight: 600;
  color: #EF9A9A;
  margin-bottom: 4px;
}

.rejection-reason {
  margin: 0;
  color: #fff;
  font-size: 0.88rem;
  line-height: 1.5;
  white-space: pre-line;
}

.hotspot-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.hotspot-info {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.info-item {
  color: #bbb;
  font-size: 0.85rem;
}

.hotspot-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
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
  font-family: inherit;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-details {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.btn-details:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.25);
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

.btn-outline {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
}

.btn-outline:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.status-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.approved {
  background: rgba(46, 125, 50, 0.2);
  color: #81C784;
}

.status-badge.rejected {
  background: rgba(198, 40, 40, 0.2);
  color: #EF9A9A;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  width: 480px;
  max-width: 95vw;
  background: rgba(25, 25, 45, 0.98);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 28px;
  color: #fff;
}

.modal-card h3 {
  font-size: 1.15rem;
  margin-bottom: 8px;
  font-family: 'Poppins', sans-serif;
}

.modal-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.88rem;
  line-height: 1.5;
  margin-bottom: 18px;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.required {
  color: #EF9A9A;
}

.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  font-size: 0.88rem;
  font-family: inherit;
  outline: none;
  resize: vertical;
  box-sizing: border-box;
}

.form-group textarea:focus {
  border-color: var(--accent);
}

.char-count {
  display: block;
  text-align: right;
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 4px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 6px;
}

.modal-actions .btn {
  flex: 1;
  justify-content: center;
}
</style>
