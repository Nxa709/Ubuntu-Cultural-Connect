<template>
  <div class="journal-page">
    <div class="hero-header">
      <h1><span class="accent-word">Travel</span> Journal</h1>
      <p>Capture your cultural experiences and memories.</p>
    </div>

    <div class="journal-content">
      <div class="journal-controls">
        <div class="search-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input v-model="searchQuery" placeholder="Search by location, title, or story..." />
        </div>
        <button @click="showForm = !showForm" class="btn-new">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          {{ showForm ? 'Cancel' : 'New Entry' }}
        </button>
      </div>

      <div v-if="showForm" class="journal-form glass-card">
        <h2>{{ editingId ? 'Edit Entry' : 'New Journal Entry' }}</h2>
        <div class="form-group">
          <label>Title</label>
          <input v-model="form.title" placeholder="Give your entry a title..." />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Location</label>
            <input v-model="form.location" placeholder="Where were you?" />
          </div>
          <div class="form-group">
            <label>Visit Date</label>
            <input v-model="form.visit_date" type="date" />
          </div>
        </div>
        <div class="form-group">
          <label>Link to Experience (optional)</label>
          <div class="exp-combobox" ref="comboboxRef">
            <div class="combobox-input-wrap" @click="openDropdown">
              <input
                v-model="expSearch"
                @focus="openDropdown"
                @input="openDropdown"
                @keydown.esc="closeDropdown"
                placeholder="Search for an experience..."
              />
              <span class="combobox-chevron">▾</span>
              <button v-if="form.experience_id" @click.stop="clearExperience" class="combobox-clear" aria-label="Clear">✕</button>
            </div>

            <div v-if="expDropdownOpen" class="combobox-dropdown">
              <div v-if="filteredExperiences.length === 0" class="combobox-empty">
                No experiences match "{{ expSearch }}"
              </div>
              <div
                v-for="exp in filteredExperiences"
                :key="exp.id"
                class="combobox-option"
                :class="{ selected: form.experience_id === exp.id }"
                @click="selectExperience(exp)"
              >
                <div class="option-title">{{ exp.title }}</div>
                <div class="option-meta">
                  <span v-if="exp.location">{{ exp.location }}</span>
                  <span class="option-cat" v-if="exp.category">{{ exp.category }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="form-group">
          <label>Mood</label>
          <div class="mood-picker">
            <button
              v-for="m in moods"
              :key="m.value"
              :class="['mood-btn', { active: form.mood === m.value }]"
              @click="form.mood = form.mood === m.value ? null : m.value"
              type="button"
            >
              {{ m.icon }} {{ m.label }}
            </button>
          </div>
        </div>
        <div class="form-group">
          <label>Your Story</label>
          <textarea v-model="form.content" rows="6" placeholder="Write about your experience..."></textarea>
        </div>
        <div class="form-actions">
          <button @click="showForm = false" class="btn-cancel">Cancel</button>
          <button @click="handleSubmit" class="btn-submit" :disabled="!form.title || !form.content">
            {{ editingId ? 'Update Entry' : 'Save Entry' }}
          </button>
        </div>
      </div>

      <LoadingSpinner v-if="loading" message="Loading journal..." />

      <div v-else-if="store.myJournals.length === 0" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
        </svg>
        <p>No journal entries yet. Start writing!</p>
      </div>

      <div v-else-if="filteredJournals.length === 0" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <p>No entries match "{{ searchQuery }}".</p>
      </div>

      <div v-else class="journal-list">
        <div v-for="entry in filteredJournals" :key="entry.id" class="journal-card">
          <div class="journal-header">
            <div class="journal-title-row">
              <h3>{{ entry.title }}</h3>
              <span v-if="entry.mood" class="mood-tag">{{ getMoodIcon(entry.mood) }}</span>
            </div>
            <div class="journal-meta">
              <span v-if="entry.location">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
                {{ entry.location }}
              </span>
              <span v-if="entry.visit_date">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                  <line x1="16" y1="2" x2="16" y2="6"/>
                  <line x1="8" y1="2" x2="8" y2="6"/>
                </svg>
                {{ formatDate(entry.visit_date) }}
              </span>
              <span v-if="entry.experience_title" class="exp-link">
                Linked: {{ entry.experience_title }}
              </span>
            </div>
          </div>

          <div class="journal-body">
            <p>{{ entry.content }}</p>
          </div>

          <div class="journal-footer">
            <span class="journal-date">Written {{ formatDateTime(entry.created_at) }}</span>
            <div class="journal-actions">
              <button @click="startEdit(entry)" class="btn-sm btn-edit">Edit</button>
              <button @click="handleDelete(entry.id)" class="btn-sm btn-delete">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useExperienceStore } from '../stores/experience'

const store = useExperienceStore()
const loading = ref(true)
const showForm = ref(false)
const editingId = ref(null)
const experiences = ref([])
const searchQuery = ref('')

const comboboxRef = ref(null)
const expSearch = ref('')
const expDropdownOpen = ref(false)

const filteredExperiences = computed(() => {
  const q = expSearch.value.trim().toLowerCase()
  if (!q) return experiences.value
  return experiences.value.filter((exp) => {
    return (
      (exp.title || '').toLowerCase().includes(q) ||
      (exp.location || '').toLowerCase().includes(q) ||
      (exp.category || '').toLowerCase().includes(q)
    )
  })
})

function openDropdown() {
  expDropdownOpen.value = true
}

function closeDropdown() {
  expDropdownOpen.value = false
}

function selectExperience(exp) {
  form.value.experience_id = exp.id
  expSearch.value = exp.title
  expDropdownOpen.value = false
}

function clearExperience() {
  form.value.experience_id = null
  expSearch.value = ''
}

function onClickOutside(e) {
  if (comboboxRef.value && !comboboxRef.value.contains(e.target)) {
    expDropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside)
})

const filteredJournals = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return store.myJournals
  return store.myJournals.filter((j) => {
    return (
      (j.location || '').toLowerCase().includes(q) ||
      (j.title || '').toLowerCase().includes(q) ||
      (j.content || '').toLowerCase().includes(q) ||
      (j.experience_title || '').toLowerCase().includes(q)
    )
  })
})

const moods = [
  { value: 'amazed', icon: '🤩', label: 'Amazed' },
  { value: 'happy', icon: '😊', label: 'Happy' },
  { value: 'inspired', icon: '✨', label: 'Inspired' },
  { value: 'peaceful', icon: '😌', label: 'Peaceful' },
  { value: 'excited', icon: '🔥', label: 'Excited' },
  { value: 'nostalgic', icon: '🥹', label: 'Nostalgic' },
]

const form = ref({
  title: '',
  content: '',
  location: '',
  visit_date: null,
  experience_id: null,
  mood: null,
})

function getMoodIcon(mood) {
  return moods.find(m => m.value === mood)?.icon || ''
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-ZA', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

function formatDateTime(d) {
  return new Date(d).toLocaleDateString('en-ZA', {
    year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

function startEdit(entry) {
  editingId.value = entry.id
  form.value = {
    title: entry.title,
    content: entry.content,
    location: entry.location || '',
    visit_date: entry.visit_date || null,
    experience_id: entry.experience_id || null,
    mood: entry.mood || null,
  }
  const linked = experiences.value.find(e => e.id === entry.experience_id)
  expSearch.value = linked ? linked.title : ''
  showForm.value = true
}

async function handleSubmit() {
  if (editingId.value) {
    await store.updateJournal(editingId.value, form.value)
  } else {
    await store.createJournal(form.value)
  }
  resetForm()
}

function resetForm() {
  editingId.value = null
  form.value = { title: '', content: '', location: '', visit_date: null, experience_id: null, mood: null }
  expSearch.value = ''
  expDropdownOpen.value = false
  showForm.value = false
}

async function handleDelete(id) {
  if (!confirm('Delete this journal entry?')) return
  await store.deleteJournal(id)
}

onMounted(async () => {
  await Promise.all([
    store.fetchMyJournals(),
    store.fetchExperiences().then(() => { experiences.value = store.experiences }),
  ])
  loading.value = false
})
</script>

<style scoped>
.journal-page {
  background: #ffffff;
  position: relative;
  min-height: 100vh;
}

.hero-header {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  position: relative;
  text-align: center;
  padding: 120px 20px 60px;
}

.hero-header::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 0;
}

.hero-header > * {
  position: relative;
  z-index: 1;
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

.journal-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px;
}

.journal-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 220px;
  padding: 0.6rem 0.9rem;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 50px;
  background: #ffffff;
  color: #666;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}

.search-box svg {
  color: var(--accent);
  flex-shrink: 0;
}

.search-box input {
  width: 100%;
  background: none;
  border: none;
  outline: none;
  color: #333;
  font-size: 0.95rem;
  font-family: inherit;
}

.search-box input::placeholder {
  color: #999;
}

.btn-new {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0.6rem 1.25rem;
  background: var(--accent);
  color: #1a1a1a;
  border: none;
  border-radius: 50px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-new:hover {
  background: var(--accent-hover);
}

.glass-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}

.journal-form h2 {
  font-family: 'Poppins', sans-serif;
  font-size: 1.3rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 1.25rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: #555;
  margin-bottom: 0.35rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.6rem 0.9rem;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 8px;
  background: #fafafa;
  color: #333;
  font-size: 0.95rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--accent);
}

.form-group select option {
  background: #fff;
  color: #333;
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
}

.exp-combobox {
  position: relative;
}

.combobox-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.combobox-input-wrap input {
  width: 100%;
  padding: 0.6rem 2.2rem 0.6rem 0.9rem;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 8px;
  background: #fafafa;
  color: #333;
  font-size: 0.95rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.combobox-input-wrap input:focus {
  border-color: var(--accent);
}

.combobox-chevron {
  position: absolute;
  right: 0.9rem;
  color: #888;
  pointer-events: none;
  font-size: 0.85rem;
}

.combobox-clear {
  position: absolute;
  right: 2rem;
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 2px;
}

.combobox-clear:hover {
  color: #ff6b6b;
}

.combobox-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  max-height: 260px;
  overflow-y: auto;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  z-index: 50;
}

.combobox-option {
  padding: 0.65rem 0.9rem;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  transition: background 0.15s;
}

.combobox-option:last-child {
  border-bottom: none;
}

.combobox-option:hover {
  background: rgba(255, 182, 18, 0.1);
}

.combobox-option.selected {
  background: rgba(255, 182, 18, 0.15);
}

.option-title {
  color: #333;
  font-size: 0.9rem;
  font-weight: 500;
}

.option-meta {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  margin-top: 2px;
  font-size: 0.78rem;
  color: #888;
}

.option-cat {
  background: rgba(255, 182, 18, 0.15);
  color: var(--accent);
  padding: 1px 8px;
  border-radius: 10px;
}

.combobox-empty {
  padding: 1rem;
  text-align: center;
  color: #888;
  font-size: 0.85rem;
}

.combobox-dropdown::-webkit-scrollbar {
  width: 4px;
}

.combobox-dropdown::-webkit-scrollbar-track {
  background: transparent;
}

.combobox-dropdown::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.mood-picker {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.mood-btn {
  padding: 0.4rem 0.8rem;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 20px;
  background: #fafafa;
  color: #555;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.mood-btn:hover {
  border-color: var(--accent);
}

.mood-btn.active {
  background: rgba(255, 182, 18, 0.15);
  border-color: var(--accent);
  color: var(--accent);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.btn-cancel {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  background: #fafafa;
  color: #555;
  font-size: 0.9rem;
  cursor: pointer;
}

.btn-cancel:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.btn-submit {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 8px;
  background: var(--accent);
  color: #1a1a1a;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-submit:hover {
  background: var(--accent-hover);
}

.btn-submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #888;
}

.empty-state svg {
  color: var(--accent);
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

.journal-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.journal-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s, box-shadow 0.3s;
}

.journal-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.journal-header {
  margin-bottom: 0.75rem;
}

.journal-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.journal-title-row h3 {
  margin: 0;
  color: #1a1a1a;
  font-family: 'Poppins', sans-serif;
  font-size: 1.1rem;
}

.mood-tag {
  font-size: 1.2rem;
}

.journal-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.journal-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #888;
  font-size: 0.85rem;
}

.exp-link {
  color: var(--accent) !important;
  font-style: italic;
}

.journal-body p {
  color: #333;
  line-height: 1.7;
  margin: 0 0 1rem;
  white-space: pre-wrap;
}

.journal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid #eaeaea;
}

.journal-date {
  color: #888;
  font-size: 0.8rem;
}

.journal-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.35rem 0.75rem;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit {
  background: rgba(255, 182, 18, 0.15);
  color: var(--accent);
  font-weight: 600;
}

.btn-edit:hover {
  background: var(--accent);
  color: #1a1a1a;
}

.btn-delete {
  background: rgba(255, 77, 77, 0.12);
  color: #ff4d4f;
  font-weight: 600;
}

.btn-delete:hover {
  background: #ff4d4f;
  color: #fff;
}

@media (max-width: 768px) {
  .hero-header h1 {
    font-size: 2rem;
  }
  .hero-header {
    padding: 100px 20px 40px;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
  .journal-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
</style>
