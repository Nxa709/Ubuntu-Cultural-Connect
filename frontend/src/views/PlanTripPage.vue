<template>
  <div class="plan-trip-page">
    <div class="hero-header">
      <button class="back-btn" @click="goBack">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Back
      </button>
      <h1><span class="accent-word">Plan</span> Your Trip</h1>
      <p>Build a custom itinerary of cultural experiences across South Africa.</p>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div class="plan-layout">
      <!-- LEFT: My Trips -->
      <div class="left-col">
        <!-- My Trips -->
        <div class="card">
          <h2>My Trips</h2>
          <div v-if="myTrips.length === 0" class="empty-trips">
            <p>No trips planned yet. Create one above.</p>
          </div>
          <div v-else class="trip-list">
            <div class="trip-item" v-for="trip in myTrips" :key="trip.id">
              <div class="trip-header" @click="selectTrip(trip)">
                <div>
                  <span class="trip-title">{{ trip.title }}</span>
                  <span class="trip-dest">{{ trip.destination }} | {{ formatDate(trip.start_date) }} - {{ formatDate(trip.end_date) }}</span>
                </div>
                <div class="trip-actions">
                  <button class="btn-sm btn-outline-sm" @click.stop="selectTrip(trip)">Edit</button>
                  <button class="btn-sm btn-delete" @click.stop="removeTrip(trip.id)">Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT: Itinerary Builder -->
      <div class="right-col" v-if="activeTrip">
        <div class="card">
          <div class="card-header-row">
            <h2>{{ activeTrip.title }} - Itinerary</h2>
            <span class="trip-dates">{{ formatDate(activeTrip.start_date) }} - {{ formatDate(activeTrip.end_date) }}</span>
          </div>

          <div v-if="dayCount === 0" class="empty-trips">
            <p>No days in this trip yet. Add a day below.</p>
          </div>

          <!-- Day tabs -->
          <div class="day-tabs" v-if="days.length > 0">
            <button
              v-for="day in days"
              :key="day.day_number"
              :class="['day-tab', { active: activeDay === day.day_number }]"
              @click="activeDay = day.day_number"
            >
              Day {{ day.day_number }}
              <span class="day-tab-date">{{ formatShortDate(day.date) }}</span>
            </button>
            <button class="day-tab add-day-tab" @click="addDay">+ Add Day</button>
          </div>

          <!-- Active Day Detail -->
          <div v-if="currentDay" class="day-detail">
            <div class="day-detail-header">
              <h3>Day {{ currentDay.day_number }} - {{ formatDate(currentDay.date) }}</h3>
            </div>

            <!-- Entries for this day -->
            <div class="entries-section">
              <!-- Experiences -->
              <div class="entry-group">
                <div class="entry-group-header">
                  <span class="entry-group-label">Experiences</span>
                  <button class="btn-add-entry" @click="startAddEntry('experience')">+ Add</button>
                </div>
                <div v-if="getEntries('experience').length === 0" class="entry-empty">No experiences added yet.</div>
                <div v-else v-for="(entry, ei) in getEntries('experience')" :key="ei" class="entry-row">
                  <div class="entry-info">
                    <div class="entry-name-row">
                      <span class="entry-name">{{ entry.name }}</span>
                      <span class="entry-time" v-if="entry.start_time">{{ entry.start_time }} - {{ entry.end_time || '?' }}</span>
                    </div>
                    <span class="entry-meta" v-if="entry.location">{{ entry.location }} &middot; {{ entry.cost ? 'R' + entry.cost : 'Free' }}</span>
                  </div>
                  <button class="btn-remove-entry" @click="removeEntry('experience', ei)">&times;</button>
                </div>
              </div>
            </div>

            <!-- Conflict Warnings -->
            <div v-if="conflicts.length > 0" class="conflict-section">
              <div class="conflict-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                Schedule Conflicts
              </div>
              <div class="conflict-item" v-for="(c, ci) in conflicts" :key="ci">
                <span class="conflict-icon">&#9888;</span>
                <span>{{ c }}</span>
              </div>
            </div>

            <!-- Cost Summary -->
            <div class="cost-summary">
              <div class="cost-row">
                <span>Day {{ currentDay.day_number }} Total:</span>
                <span class="cost-value">R{{ dayCost }}</span>
              </div>
              <div class="cost-row total">
                <span>Trip Total:</span>
                <span class="cost-value">R{{ totalCost }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Entry Modal -->
    <div class="modal-overlay" v-if="showEntryModal" @click.self="showEntryModal = false">
      <div class="modal-card">
        <h3>Add {{ entryTypeLabel }}</h3>
        <form @submit.prevent="confirmAddEntry">
          <div class="form-group">
            <label>Name</label>
            <input v-model="entryForm.name" type="text" required :placeholder="'e.g. ' + entryTypePlaceholder" />
          </div>
          <div class="form-group">
            <label>Location</label>
            <input v-model="entryForm.location" type="text" placeholder="e.g. Durban" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Start Time</label>
              <input v-model="entryForm.start_time" type="time" />
            </div>
            <div class="form-group">
              <label>End Time</label>
              <input v-model="entryForm.end_time" type="time" />
            </div>
          </div>
          <div class="form-group">
            <label>Cost (R)</label>
            <input v-model.number="entryForm.cost" type="number" min="0" step="0.01" placeholder="0" />
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary">Add</button>
            <button type="button" class="btn btn-outline" @click="showEntryModal = false">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useExperienceStore } from '../stores/experience'

const route = useRoute()
const router = useRouter()

const store = useExperienceStore()

function goBack() {
  router.push('/')
}
const myTrips = ref([])
const error = ref('')
const success = ref('')
const activeTrip = ref(null)
const activeDay = ref(1)
const showEntryModal = ref(false)
const entryType = ref('experience')
const entryTypeLabel = ref('Experience')
const entryTypePlaceholder = ref('Zulu Village Tour')

const entryForm = reactive({
  name: '',
  location: '',
  start_time: '',
  end_time: '',
  cost: 0,
})

// Extended days state with entries
const days = ref([])

const dayCount = computed(() => days.value.length)

const currentDay = computed(() => {
  return days.value.find(d => d.day_number === activeDay.value) || null
})

const allEntries = computed(() => {
  if (!currentDay.value) return []
  return currentDay.value.entries || []
})

function getEntries(type) {
  return allEntries.value
    .filter(e => e.type === type)
    .sort((a, b) => {
      if (!a.start_time && !b.start_time) return 0
      if (!a.start_time) return 1
      if (!b.start_time) return -1
      return a.start_time.localeCompare(b.start_time)
    })
}

const dayCost = computed(() => {
  return allEntries.value.reduce((sum, e) => sum + (e.cost || 0), 0)
})

const totalCost = computed(() => {
  return days.value.reduce((sum, day) => {
    return sum + (day.entries || []).reduce((s, e) => s + (e.cost || 0), 0)
  }, 0)
})

// Conflict detection
const conflicts = computed(() => {
  const warnings = []
  const entries = allEntries.value.filter(e => e.start_time && e.end_time)
  for (let i = 0; i < entries.length; i++) {
    for (let j = i + 1; j < entries.length; j++) {
      const a = entries[i]
      const b = entries[j]
      if (timesOverlap(a.start_time, a.end_time, b.start_time, b.end_time)) {
        warnings.push(`Schedule Conflict: You have selected two activities at ${a.start_time} on Day ${currentDay.value?.day_number}. "${a.name}" and "${b.name}" overlap.`)
      }
    }
  }
  return warnings
})

function timesOverlap(s1, e1, s2, e2) {
  return s1 < e2 && s2 < e1
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-ZA', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatShortDate(d) {
  return new Date(d).toLocaleDateString('en-ZA', { month: 'short', day: 'numeric' })
}

onMounted(async () => {
  await store.fetchMyTrips()
  myTrips.value = store.myTrips

  // Auto-select a trip if ?trip=ID is in URL (from Add Trip To Plan flow)
  const tripId = route.query.trip
  if (tripId) {
    const found = myTrips.value.find(t => t.id === parseInt(tripId))
    if (found) selectTrip(found)
  }
})

function initDaysFromTrip(trip) {
  const start = new Date(trip.start_date)
  const end = new Date(trip.end_date)
  const count = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
  const arr = []
  for (let i = 0; i < count; i++) {
    const d = new Date(start)
    d.setDate(d.getDate() + i)
    arr.push({
      day_number: i + 1,
      date: d.toISOString().split('T')[0],
      entries: [],
    })
  }
  // Restore entries from stored JSON if available (stored in notes field)
  if (trip.notes) {
    try {
      const parsed = JSON.parse(trip.notes)
      parsed.forEach(pd => {
        const day = arr.find(d => d.day_number === pd.day_number)
        if (day) day.entries = pd.entries || []
      })
    } catch (e) { /* ignore */ }
  }
  days.value = arr
  activeDay.value = 1
}

function selectTrip(trip) {
  activeTrip.value = trip
  initDaysFromTrip(trip)
}

async function handleCreate() {
  if (!form.destination) {
    error.value = 'Please select a destination'
    return
  }
  if (!form.title) {
    // Auto-generate if somehow empty
    for (const prov of provinceList.value) {
      if (prov.name === form.destination || prov.locations.includes(form.destination)) {
        form.title = `${prov.name} Vacation`
        break
      }
    }
  }
  if (!form.title || !form.start_date || !form.end_date) {
    error.value = 'Please fill in all required fields'
    return
  }
  saving.value = true
  error.value = ''
  success.value = ''

  try {
    const startDate = new Date(form.start_date)
    const endDate = new Date(form.end_date)
    const dayCount = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1

    const days = []
    for (let i = 0; i < dayCount; i++) {
      const d = new Date(startDate)
      d.setDate(d.getDate() + i)
      days.push({
        day_number: i + 1,
        date: d.toISOString().split('T')[0],
        activity: `Day ${i + 1} exploration`,
      })
    }

    await store.createTrip({ ...form, days })
    success.value = 'Trip created!'
    form.title = ''
    form.destination = ''
    form.travellers = 1
    form.start_date = ''
    form.end_date = ''
    await store.fetchMyTrips()
    myTrips.value = store.myTrips
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to create trip'
  } finally {
    saving.value = false
  }
}

async function addDay() {
  if (!activeTrip.value) return
  const nextNum = days.value.length + 1
  const lastDate = days.value.length > 0 ? days.value[days.value.length - 1].date : activeTrip.value.start_date
  const nextDate = new Date(lastDate)
  nextDate.setDate(nextDate.getDate() + 1)
  days.value.push({
    day_number: nextNum,
    date: nextDate.toISOString().split('T')[0],
    entries: [],
  })
  activeDay.value = nextNum
  await saveItinerary()
}

function startAddEntry(type) {
  entryType.value = type
  entryTypeLabel.value = 'Experience'
  entryTypePlaceholder.value = 'Zulu Village Tour'
  entryForm.name = ''
  entryForm.location = ''
  entryForm.start_time = ''
  entryForm.end_time = ''
  entryForm.cost = 0
  showEntryModal.value = true
}

function confirmAddEntry() {
  if (!entryForm.name) return
  const day = days.value.find(d => d.day_number === activeDay.value)
  if (!day) return
  if (!day.entries) day.entries = []
  day.entries.push({
    type: entryType.value,
    name: entryForm.name,
    location: entryForm.location,
    start_time: entryForm.start_time,
    end_time: entryForm.end_time,
    cost: entryForm.cost,
  })
  showEntryModal.value = false
  saveItinerary()
}

function removeEntry(type, index) {
  const day = days.value.find(d => d.day_number === activeDay.value)
  if (!day || !day.entries) return
  day.entries = day.entries.filter((e, i) => !(e.type === type && i === index))
  saveItinerary()
}

async function saveItinerary() {
  if (!activeTrip.value) return
  const data = days.value.map(d => ({
    day_number: d.day_number,
    date: d.date,
    entries: d.entries || [],
  }))
  try {
    await store.updateTrip(activeTrip.value.id, { notes: JSON.stringify(data) })
    const refreshed = await store.getItinerary(activeTrip.value.id)
    activeTrip.value = refreshed
    initDaysFromTrip(refreshed)
  } catch (e) {
    // silently fail
  }
}

async function removeTrip(id) {
  try {
    await store.deleteTrip(id)
    myTrips.value = myTrips.value.filter(t => t.id !== id)
    if (activeTrip.value?.id === id) {
      activeTrip.value = null
      days.value = []
    }
  } catch (e) {
    error.value = 'Failed to delete trip'
  }
}
</script>

<style scoped>
.plan-trip-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  position: relative;
  min-height: 100vh;
  padding: 100px 20px 40px;
}

.plan-trip-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 0;
}

.plan-trip-page > * {
  position: relative;
  z-index: 1;
}

.hero-header {
  text-align: center;
  padding: 20px 20px 32px;
  position: relative;
}

.back-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.8);
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.82rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
}

.hero-header h1 {
  font-family: 'Poppins', sans-serif;
  font-size: 2.8rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 8px;
}

.hero-header .accent-word {
  font-family: 'Pacifico', cursive;
  font-weight: 400;
  color: var(--accent);
}

.hero-header p {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
  max-width: 500px;
  margin: 0 auto;
}

.plan-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 24px;
  max-width: 1300px;
  margin: 0 auto;
}

.left-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 16px;
  padding: 24px;
  color: #fff;
}

.card h2 {
  color: #fff;
  font-size: 1.15rem;
  margin-bottom: 16px;
  font-family: 'Poppins', sans-serif;
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

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  font-size: 0.88rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  border-color: var(--accent);
}

.form-group select option {
  background: #1a1a2e;
  color: #fff;
}

.form-group input[readonly] {
  opacity: 0.7;
  cursor: default;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 600;
  font-family: inherit;
  transition: all 0.2s;
}

.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--accent); color: #1a1a1a; width: 100%; margin-top: 4px; }
.btn-primary:hover:not(:disabled) { background: #fff; }
.btn-outline { background: transparent; border: 1px solid rgba(255, 255, 255, 0.3); color: #fff; }
.btn-outline:hover { border-color: var(--accent); color: var(--accent); }
.btn-sm { padding: 5px 12px; border: none; border-radius: 5px; font-size: 0.72rem; cursor: pointer; font-family: inherit; font-weight: 500; }
.btn-outline-sm { background: rgba(255, 255, 255, 0.15); color: #fff; }
.btn-outline-sm:hover { background: rgba(255, 255, 255, 0.25); }
.btn-delete { background: rgba(255, 77, 77, 0.2); color: #ff6b6b; }
.btn-delete:hover { background: rgba(255, 77, 77, 0.35); }

.trip-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.trip-item {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  overflow: hidden;
}

.trip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.trip-header:hover { background: rgba(255, 255, 255, 0.08); }

.trip-title {
  display: block;
  font-weight: 600;
  color: #fff;
  font-size: 0.88rem;
}

.trip-dest {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

.trip-actions { display: flex; gap: 5px; }

.empty-trips { color: rgba(255, 255, 255, 0.5); font-size: 0.85rem; padding: 8px 0; }
.alert { padding: 10px 14px; border-radius: 8px; margin: 0 auto 12px; max-width: 1300px; font-size: 0.85rem; }
.alert-error { background: rgba(255, 77, 77, 0.2); color: #ff6b6b; border: 1px solid rgba(255, 77, 77, 0.3); }
.alert-success { background: rgba(76, 175, 80, 0.2); color: #81c784; border: 1px solid rgba(76, 175, 80, 0.3); }

/* Right col */
.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header-row h2 { margin-bottom: 0; }
.trip-dates { font-size: 0.78rem; color: rgba(255, 255, 255, 0.5); }

/* Day tabs */
.day-tabs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.day-tab {
  padding: 8px 14px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.78rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1.3;
}

.day-tab:hover { background: rgba(255, 255, 255, 0.12); color: #fff; }
.day-tab.active { background: var(--accent); color: #1a1a1a; border-color: var(--accent); font-weight: 600; }
.day-tab-date { font-size: 0.65rem; opacity: 0.7; font-weight: 400; }
.day-tab.active .day-tab-date { opacity: 0.8; }
.add-day-tab { border-style: dashed; color: var(--accent); border-color: rgba(255, 182, 18, 0.3); }
.add-day-tab:hover { background: rgba(255, 182, 18, 0.15); }

.day-detail-header h3 {
  font-size: 1rem;
  color: #fff;
  margin-bottom: 16px;
  font-family: 'Poppins', sans-serif;
}

/* Entry groups */
.entries-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 16px;
}

.entry-group {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.entry-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.entry-group-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-add-entry {
  background: rgba(255, 182, 18, 0.15);
  border: 1px solid rgba(255, 182, 18, 0.25);
  color: var(--accent);
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}

.btn-add-entry:hover { background: rgba(255, 182, 18, 0.25); }

.entry-empty {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.4);
  font-style: italic;
  padding: 4px 0;
}

.entry-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.entry-row:last-child { border-bottom: none; }

.entry-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.entry-name {
  font-size: 0.85rem;
  color: #fff;
  font-weight: 500;
}

.entry-time {
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.08);
  padding: 1px 6px;
  border-radius: 4px;
}

.entry-meta {
  display: block;
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.45);
  margin-top: 1px;
}

.btn-remove-entry {
  background: none;
  border: none;
  color: rgba(255, 77, 77, 0.6);
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}

.btn-remove-entry:hover { color: #ff6b6b; }

/* Conflicts */
.conflict-section {
  background: rgba(255, 152, 0, 0.12);
  border: 1px solid rgba(255, 152, 0, 0.25);
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 14px;
}

.conflict-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #FFB74D;
  margin-bottom: 6px;
}

.conflict-item {
  font-size: 0.78rem;
  color: rgba(255, 183, 77, 0.9);
  padding: 3px 0;
  display: flex;
  align-items: flex-start;
  gap: 6px;
}

.conflict-icon { color: #FFB74D; font-size: 0.85rem; }

/* Cost summary */
.cost-summary {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.cost-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  padding: 4px 0;
}

.cost-row.total {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 4px;
  padding-top: 8px;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
}

.cost-value {
  color: var(--accent);
  font-weight: 600;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  width: 440px;
  max-width: 95vw;
  background: rgba(25, 25, 45, 0.98);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 28px;
  color: #fff;
}

.modal-card h3 {
  font-size: 1.15rem;
  margin-bottom: 18px;
  font-family: 'Poppins', sans-serif;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 6px;
}

.modal-actions .btn { flex: 1; }

@media (max-width: 900px) {
  .plan-layout {
    grid-template-columns: 1fr;
  }
}
</style>
