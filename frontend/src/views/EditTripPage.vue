<template>
  <div class="edit-trip-page">
    <div class="hero-header">
      <h1><span class="accent-word">Edit</span> Trip</h1>
      <p>Modify your trip details and itinerary.</p>
    </div>

    <LoadingSpinner v-if="loading" message="Loading trip..." />

    <template v-else-if="trip">
      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <div class="edit-layout">
        <div class="card form-card">
          <h2>Trip Details</h2>
          <form @submit.prevent="handleSaveTrip">
            <div class="form-group">
              <label>Trip Name</label>
              <input v-model="tripForm.title" type="text" required />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Destination</label>
                <select v-model="tripForm.destination" required @change="autoGenerateTitle">
                  <option value="">-- Select a destination --</option>
                  <option v-for="prov in provinceList" :key="prov.name" :value="prov.name">
                    {{ prov.name }}
                  </option>
                  <optgroup v-for="prov in provinceList" :key="prov.name + '-loc'" :label="prov.name + ' — Locations'">
                    <option v-for="loc in prov.locations" :key="loc" :value="loc">
                      {{ loc }}
                    </option>
                  </optgroup>
                </select>
              </div>
              <div class="form-group">
                <label>Start Date</label>
                <input v-model="tripForm.start_date" type="date" required />
              </div>
            </div>
            <div class="form-group">
              <label>End Date</label>
              <input v-model="tripForm.end_date" type="date" required />
            </div>
            <div class="form-group">
              <label>Notes</label>
              <textarea v-model="tripForm.notes" rows="3"></textarea>
            </div>
            <button type="submit" class="btn btn-primary" :disabled="savingTrip">
              {{ savingTrip ? 'Saving...' : 'Save Changes' }}
            </button>
          </form>
        </div>

        <div class="itinerary-panel">
          <div class="card">
            <div class="card-header-row">
              <h2>Itinerary</h2>
              <button class="btn btn-add" @click="showAddDay = true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Add Day
              </button>
            </div>

            <div v-if="trip.days && trip.days.length > 0" class="itinerary-timeline">
              <div class="itinerary-day" v-for="day in sortedDays" :key="day.id">
                <div class="day-badge">Day {{ day.day_number }}</div>
                <div class="day-content">
                  <div class="day-header">
                    <span class="day-date">{{ formatDate(day.date) }}</span>
                    <div class="day-actions">
                      <button class="btn-icon" @click="editDay(day)" title="Edit">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                      </button>
                      <button class="btn-icon btn-danger-icon" @click="removeDay(day.id)" title="Delete">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                  <span class="day-activity">{{ day.activity }}</span>
                  <span class="day-exp" v-if="day.experience_title">{{ day.experience_title }}</span>
                  <span class="day-notes" v-if="day.notes">{{ day.notes }}</span>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <p>No days in this trip yet.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Day Modal -->
      <div class="modal-overlay" v-if="editingDay" @click.self="editingDay = null">
        <div class="modal-card glass-card">
          <h3>Edit Day {{ editingDay.day_number }}</h3>
          <form @submit.prevent="handleSaveDay">
            <div class="form-group">
              <label>Day Number</label>
              <input v-model.number="dayForm.day_number" type="number" min="1" required />
            </div>
            <div class="form-group">
              <label>Date</label>
              <input v-model="dayForm.date" type="date" required />
            </div>
            <div class="form-group">
              <label>Activity</label>
              <input v-model="dayForm.activity" type="text" required placeholder="e.g. Visit Zulu Village" />
            </div>
            <div class="form-group">
              <label>Assign Experience (optional)</label>
              <select v-model="dayForm.experience_id">
                <option :value="null">None</option>
                <option v-for="exp in availableExps" :key="exp.id" :value="exp.id">{{ exp.title }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Notes</label>
              <textarea v-model="dayForm.notes" rows="2" placeholder="Optional notes..."></textarea>
            </div>
            <div class="modal-actions">
              <button type="submit" class="btn btn-primary" :disabled="savingDay">
                {{ savingDay ? 'Saving...' : 'Save Day' }}
              </button>
              <button type="button" class="btn btn-outline" @click="editingDay = null">Cancel</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Add Day Modal -->
      <div class="modal-overlay" v-if="showAddDay" @click.self="showAddDay = false">
        <div class="modal-card glass-card">
          <h3>Add New Day</h3>
          <form @submit.prevent="handleAddDay">
            <div class="form-group">
              <label>Day Number</label>
              <input v-model.number="newDayForm.day_number" type="number" min="1" required />
            </div>
            <div class="form-group">
              <label>Date</label>
              <input v-model="newDayForm.date" type="date" required />
            </div>
            <div class="form-group">
              <label>Activity</label>
              <input v-model="newDayForm.activity" type="text" required placeholder="e.g. Visit Zulu Village" />
            </div>
            <div class="form-group">
              <label>Assign Experience (optional)</label>
              <select v-model="newDayForm.experience_id">
                <option :value="null">None</option>
                <option v-for="exp in availableExps" :key="exp.id" :value="exp.id">{{ exp.title }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Notes</label>
              <textarea v-model="newDayForm.notes" rows="2" placeholder="Optional notes..."></textarea>
            </div>
            <div class="modal-actions">
              <button type="submit" class="btn btn-primary" :disabled="savingDay">
                {{ savingDay ? 'Adding...' : 'Add Day' }}
              </button>
              <button type="button" class="btn btn-outline" @click="showAddDay = false">Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </template>

    <div v-else class="empty-state">
      <p>Trip not found.</p>
      <router-link to="/plan-trip" class="btn btn-primary">Back to Trip Planner</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useExperienceStore } from '../stores/experience'
import { provinces } from '../data/provinces'

const route = useRoute()
const router = useRouter()
const store = useExperienceStore()

const trip = ref(null)
const loading = ref(true)
const savingTrip = ref(false)
const savingDay = ref(false)
const error = ref('')
const success = ref('')
const editingDay = ref(null)
const showAddDay = ref(false)
const availableExps = ref([])

const tripForm = reactive({
  title: '',
  destination: '',
  start_date: '',
  end_date: '',
  notes: '',
})

const dayForm = reactive({
  day_number: 1,
  date: '',
  activity: '',
  experience_id: null,
  notes: '',
})

const newDayForm = reactive({
  day_number: 1,
  date: '',
  activity: '',
  experience_id: null,
  notes: '',
})

const provinceList = computed(() => {
  const expMap = {}
  const seenProvinces = new Set()
  for (const exp of store.experiences) {
    const prov = exp.province || 'Other'
    seenProvinces.add(prov)
    if (!expMap[prov]) expMap[prov] = new Set()
    if (exp.location) expMap[prov].add(exp.location)
  }
  const result = provinces.map(p => {
    const dbLocs = expMap[p.name] || new Set()
    const allLocs = new Set([...dbLocs])
    for (const d of p.destinations) {
      allLocs.add(d.location)
    }
    return { name: p.name, locations: [...allLocs].sort() }
  })
  for (const prov of seenProvinces) {
    if (!result.some(p => p.name === prov)) {
      result.push({
        name: prov,
        locations: [...(expMap[prov] || [])].sort(),
      })
    }
  }
  return result
})

function autoGenerateTitle() {
  const dest = tripForm.destination
  if (!dest) return
  for (const prov of provinceList.value) {
    if (prov.name === dest || prov.locations.includes(dest)) {
      tripForm.title = `${prov.name} Vacation`
      return
    }
  }
}

const sortedDays = computed(() => {
  if (!trip.value?.days) return []
  return [...trip.value.days].sort((a, b) => a.day_number - b.day_number)
})

onMounted(async () => {
  try {
    const [data] = await Promise.all([
      store.getItinerary(route.params.id),
      store.fetchExperiences(),
    ])
    trip.value = data
    tripForm.title = data.title
    tripForm.destination = data.destination
    tripForm.start_date = data.start_date
    tripForm.end_date = data.end_date
    tripForm.notes = data.notes || ''

    newDayForm.day_number = (data.days?.length || 0) + 1
    if (data.days?.length > 0) {
      const lastDay = data.days[data.days.length - 1]
      const nextDate = new Date(lastDay.date)
      nextDate.setDate(nextDate.getDate() + 1)
      newDayForm.date = nextDate.toISOString().split('T')[0]
    } else {
      newDayForm.date = data.start_date
    }

    availableExps.value = store.experiences
  } catch (e) {
    error.value = 'Failed to load trip'
  } finally {
    loading.value = false
  }
})

async function handleSaveTrip() {
  savingTrip.value = true
  error.value = ''
  success.value = ''
  try {
    const updated = await store.updateTrip(route.params.id, tripForm)
    trip.value = updated
    success.value = 'Trip updated!'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to update trip'
  } finally {
    savingTrip.value = false
  }
}

function editDay(day) {
  editingDay.value = day
  dayForm.day_number = day.day_number
  dayForm.date = day.date
  dayForm.activity = day.activity
  dayForm.experience_id = day.experience_id
  dayForm.notes = day.notes || ''
}

async function handleSaveDay() {
  savingDay.value = true
  error.value = ''
  try {
    await store.updateTripDay(route.params.id, editingDay.value.id, dayForm)
    const refreshed = await store.getItinerary(route.params.id)
    trip.value = refreshed
    editingDay.value = null
    success.value = 'Day updated!'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to update day'
  } finally {
    savingDay.value = false
  }
}

async function handleAddDay() {
  savingDay.value = true
  error.value = ''
  try {
    await store.addTripDay(route.params.id, newDayForm)
    const refreshed = await store.getItinerary(route.params.id)
    trip.value = refreshed
    showAddDay.value = false

    newDayForm.day_number = refreshed.days.length + 1
    newDayForm.activity = ''
    newDayForm.experience_id = null
    newDayForm.notes = ''
    success.value = 'Day added!'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to add day'
  } finally {
    savingDay.value = false
  }
}

async function removeDay(dayId) {
  if (!confirm('Remove this day from the itinerary?')) return
  error.value = ''
  try {
    await store.deleteTripDay(route.params.id, dayId)
    const refreshed = await store.getItinerary(route.params.id)
    trip.value = refreshed
    success.value = 'Day removed!'
  } catch (e) {
    error.value = 'Failed to remove day'
  }
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-ZA', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<style scoped>
.edit-trip-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
  position: relative;
  min-height: 100vh;
  padding: 5rem 1rem 2rem;
}

.edit-trip-page::before {
  content: "";
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.15);
  z-index: 0;
}

.edit-trip-page > * {
  position: relative;
  z-index: 1;
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

.edit-layout {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 24px;
  max-width: 1100px;
  margin: 0 auto;
}

.card, .form-card {
  background: rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 16px;
  padding: 28px;
  color: #fff;
}

.card h2, .form-card h2 {
  color: #fff;
  font-size: 1.2rem;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.88);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.26);
  color: #fff;
  font-size: 0.95rem;
  font-family: inherit;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--accent);
}

.form-group input[type="date"] {
  color-scheme: dark;
}
.form-group input[type="date"]::-webkit-calendar-picker-indicator {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='18' rx='2' ry='2'/%3E%3Cline x1='16' y1='2' x2='16' y2='6'/%3E%3Cline x1='8' y1='2' x2='8' y2='6'/%3E%3Cline x1='3' y1='10' x2='21' y2='10'/%3E%3C/svg%3E");
  background-size: 20px 20px;
  background-position: center;
  background-repeat: no-repeat;
  cursor: pointer;
  opacity: 1;
}

.form-group select option {
  background: #1a1a2e;
  color: #fff;
}

.form-group textarea {
  resize: vertical;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  font-family: inherit;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-fill);
  color: #1a1a1a;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-fill-hover);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-outline {
  background: var(--surface);
  border: 1px solid var(--border-strong);
  color: var(--text-color);
}

.btn-outline:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.btn-add {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(232, 162, 0, 0.2);
  color: var(--accent);
  border: 1px solid rgba(232, 162, 0, 0.3);
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add:hover {
  background: rgba(232, 162, 0, 0.3);
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header-row h2 {
  margin-bottom: 0;
}

.itinerary-timeline {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.itinerary-day {
  display: flex;
  gap: 14px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.20);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.24);
}

.day-badge {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(232, 162, 0, 0.2);
  color: var(--accent);
  font-size: 0.82rem;
  font-weight: 700;
  border-radius: 10px;
}

.day-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.day-date {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.80);
}

.day-actions {
  display: flex;
  gap: 4px;
}

.btn-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 6px;
  background: var(--surface-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: var(--accent-light);
  color: var(--accent-text);
}

.btn-danger-icon:hover {
  background: rgba(255, 77, 77, 0.3);
  color: #ff6b6b;
}

.day-activity {
  font-size: 0.95rem;
  color: #fff;
  font-weight: 500;
}

.day-exp {
  font-size: 0.82rem;
  color: var(--accent);
}

.day-notes {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.80);
  font-style: italic;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.80);
}

.loading-state {
  text-align: center;
  padding: 60px;
  color: rgba(255, 255, 255, 0.88);
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(255, 255, 255, 0.38);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Modals */
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
  width: 480px;
  max-width: 95vw;
  padding: 28px;
}

.modal-card h3 {
  color: var(--heading-color);
  font-size: 1.2rem;
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.alert {
  max-width: 1100px;
  margin: 0 auto 16px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.9rem;
}

.alert-error {
  background: rgba(255, 77, 77, 0.2);
  color: #ff6b6b;
  border: 1px solid rgba(255, 77, 77, 0.3);
}

.alert-success {
  background: rgba(76, 175, 80, 0.2);
  color: #81c784;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

@media (max-width: 768px) {
  .edit-layout {
    grid-template-columns: 1fr;
  }
}
</style>
