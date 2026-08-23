<template>
  <div class="plan-trip-page">
    <div class="hero-header">
      <button class="back-btn" @click="goBack">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Back
      </button>
      <h1><span class="accent-word">Plan</span> Your Trip</h1>
      <p>Generate a personalized itinerary from your saved interests and local cultural experiences.</p>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div class="plan-layout">
      <!-- LEFT: My Trips -->
      <div class="left-col">
        <div class="card">
          <div class="card-head-row">
            <h2>My Trips</h2>
            <router-link to="/journal" class="ghost-link">Journal</router-link>
          </div>
          <div v-if="myTrips.length === 0" class="empty-trips">No trips planned yet. Create one on the right.</div>
          <div v-else class="trip-list">
            <div class="trip-item" v-for="trip in myTrips" :key="trip.id">
              <div class="trip-header" :class="{ active: selectedTrip && selectedTrip.id === trip.id }" @click="openTrip(trip)">
                <div>
                  <span class="trip-title">{{ trip.title }}</span>
                  <span class="trip-dest">{{ trip.destination }} · {{ formatDate(trip.start_date) }} – {{ formatDate(trip.end_date) }}</span>
                </div>
                <button class="btn-sm btn-delete" @click.stop="removeTrip(trip.id)">Delete</button>
              </div>
            </div>
          </div>
        </div>
        <button class="btn-new-itinerary new-itinerary-under" @click="resetPlan">+ New Itinerary</button>
      </div>

      <!-- RIGHT: Planner -->
      <div class="right-col">
        <!-- New plan form -->
        <div class="card" v-if="!itinerary">
          <h2>Plan a new trip</h2>
          <div class="pref-box" v-if="prefs.length">
            <span class="pref-label">Based on your saved interests</span>
            <div class="pref-chips">
              <span class="pref-chip" v-for="p in prefs" :key="p">{{ p }}</span>
              <router-link to="/preferences" class="pref-edit">Change</router-link>
            </div>
          </div>
          <p v-else class="empty-trips">
            Set your interests on the <router-link to="/preferences" class="accent-link">Preferences page</router-link>
            for a more personalized plan — you can still generate one now.
          </p>

          <form @submit.prevent="generate">
            <div class="form-group">
              <label>Destination</label>
              <select v-model="tripForm.destination" required>
                <option value="" disabled>Select a province or area</option>
                <option v-for="p in provinceOptions" :key="p.value" :value="p.value">{{ p.label }}</option>
              </select>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Start date</label>
                <input v-model="tripForm.start_date" type="date" required :min="today" />
              </div>
              <div class="form-group">
                <label>End date</label>
                <input v-model="tripForm.end_date" type="date" required :min="tripForm.start_date || today" />
              </div>
            </div>
            <button type="submit" class="btn btn-primary" :disabled="generating">
              {{ generating ? 'Generating…' : 'Generate Itinerary' }}
            </button>
          </form>
        </div>

        <!-- Itinerary view -->
        <div class="card" v-if="itinerary">
          <div class="card-head-row">
            <h2>{{ itinerary.title || itinerary.destination }} Itinerary</h2>
          </div>

          <div class="trip-summary">
            <div class="sum-item"><span class="sum-label">Destination</span><span class="sum-value">{{ itinerary.destination }}</span></div>
            <div class="sum-item"><span class="sum-label">Dates</span><span class="sum-value">{{ formatDate(itinerary.start_date) }} – {{ formatDate(itinerary.end_date) }}</span></div>
            <div class="sum-item"><span class="sum-label">Total activities</span><span class="sum-value">{{ activityCount }}</span></div>
            <div class="sum-item"><span class="sum-label">Total estimated cost</span><span class="sum-value accent">R{{ totalCost }}</span></div>
          </div>

          <div class="itinerary-actions">
            <button class="btn-outline btn-sm-wide" @click="regenerateAll" :disabled="generating">Regenerate all</button>
            <button class="btn btn-primary" @click="confirmItinerary" :disabled="saving || activityCount === 0">
              {{ itinerary.isNew ? 'Confirm Itinerary' : 'Save Changes' }}
            </button>
          </div>

          <div class="day-tabs">
            <button
              v-for="d in itinerary.days"
              :key="d.day_number"
              :class="['day-tab', { active: activeDay === d.day_number }]"
              @click="selectDay(d.day_number)"
            >
              Day {{ d.day_number }}
              <span class="day-tab-date">{{ formatShortDate(d.date) }}</span>
            </button>
          </div>

          <div class="day-list">
            <div
              v-for="day in itinerary.days"
              :key="day.day_number"
              :id="'day-' + day.day_number"
              class="day-block"
              :class="'day-color-' + ((day.day_number - 1) % 5)"
            >
              <div class="day-block-header">
                <div class="day-block-title">
                  <span class="day-block-badge">Day {{ day.day_number }}</span>
                  <span class="day-block-date">{{ formatDate(day.date) }}</span>
                </div>
                <button class="btn-outline btn-sm-wide" @click="regenerateDay(day.day_number)" :disabled="generating">Regenerate day</button>
              </div>

              <div class="timeline">
                <div class="tl-row" v-for="(en, idx) in day.entries" :key="idx" :class="'tl-' + en.type">
                  <div class="tl-time">
                    <span class="tl-start">{{ en.start_time || '—' }}</span>
                    <span class="tl-end">{{ en.end_time ? '– ' + en.end_time : '' }}</span>
                  </div>
                  <div class="tl-body">
                    <div class="tl-name-row">
                      <span class="tl-name">{{ en.name }}</span>
                      <span v-if="en.type === 'meal'" class="tl-tag tag-meal">{{ en.meal }}</span>
                      <span v-if="en.type === 'break'" class="tl-tag tag-break">Break</span>
                      <span v-if="en.type === 'experience'" class="tl-tag tag-exp">{{ en.category }}</span>
                    </div>
                    <div class="tl-meta-line">
                      <span class="tl-meta" v-if="en.location">&#128205; {{ en.location }}{{ en.province ? ', ' + en.province : '' }}</span>
                      <span class="tl-meta" v-if="en.duration_hours">&#9201; {{ en.duration_hours }}h</span>
                      <span class="tl-meta" v-if="en.cost">&#128176; R{{ en.cost }}</span>
                    </div>
                    <p class="tl-reason" v-if="en.reason">{{ en.reason }}</p>
                    <div class="tl-actions" v-if="en.type === 'experience' || en.type === 'meal'">
                      <button class="tl-btn" @click="moveEntry(day.day_number, idx, -1)" title="Move up">&uarr;</button>
                      <button class="tl-btn" @click="moveEntry(day.day_number, idx, 1)" title="Move down">&darr;</button>
                      <button class="tl-btn tl-btn-accent" @click="openReplace(day.day_number, idx)">Replace</button>
                      <button class="tl-btn tl-btn-danger" @click="removeEntry(day.day_number, idx)">Remove</button>
                    </div>
                  </div>
                  <div class="tl-cost" v-if="en.cost">R{{ en.cost }}</div>
                </div>
              </div>

              <div class="day-footer">
                <span class="day-cost">Day {{ day.day_number }} estimated cost: <strong class="accent">R{{ dayCostFor(day) }}</strong> &middot; {{ dayActivityCountFor(day) }} activit{{ dayActivityCountFor(day) === 1 ? 'y' : 'ies' }}</span>
                <button class="btn-add-entry" @click="startAddEntry(day.day_number)">+ Add activity</button>
              </div>
            </div>
          </div>

          <p class="booking-note">Booking is arranged directly with each host. Use this itinerary to plan your trip, then contact hosts to confirm availability.</p>
        </div>
      </div>
    </div>

    <!-- Add entry modal -->
    <div class="modal-overlay" v-if="showEntryModal" @click.self="showEntryModal = false">
      <div class="modal-card">
        <h3>Add activity to Day {{ addTargetDay }}</h3>
        <div class="add-tabs">
          <button type="button" :class="['add-tab', { active: addMode === 'pick' }]" @click="addMode = 'pick'">From experiences</button>
          <button type="button" :class="['add-tab', { active: addMode === 'manual' }]" @click="addMode = 'manual'">Manual</button>
        </div>

        <div v-if="addMode === 'pick'" class="exp-picker">
          <div class="form-group">
            <input v-model="expSearch" type="text" placeholder="Search experiences..." />
          </div>
          <div class="exp-pick-list">
            <button v-for="x in filteredExperiences" :key="x.id" class="exp-pick-item" @click="addExperienceEntry(x)">
              <span class="exp-pick-name">{{ x.title }}</span>
              <span class="exp-pick-meta">{{ x.category }} &middot; {{ x.location }} &middot; {{ x.price > 0 ? 'R' + x.price : 'Free' }}</span>
            </button>
            <p v-if="filteredExperiences.length === 0" class="empty-trips">No experiences match your search.</p>
          </div>
        </div>

        <form v-else @submit.prevent="confirmAddEntry">
          <div class="form-group">
            <label>Name</label>
            <input v-model="entryForm.name" type="text" required placeholder="e.g. Zulu Village Tour" />
          </div>
          <div class="form-group">
            <label>Location</label>
            <input v-model="entryForm.location" type="text" placeholder="e.g. Durban" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Start</label>
              <input v-model="entryForm.start_time" type="time" />
            </div>
            <div class="form-group">
              <label>End</label>
              <input v-model="entryForm.end_time" type="time" />
            </div>
          </div>
          <div class="form-group">
            <label>Cost (R)</label>
            <input v-model.number="entryForm.cost" type="number" min="0" step="0.01" placeholder="0" />
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary">Add</button>
          </div>
        </form>

        <div class="modal-actions modal-footer">
          <button type="button" class="btn btn-outline" @click="showEntryModal = false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Replace modal -->
    <div class="modal-overlay" v-if="showReplaceModal" @click.self="showReplaceModal = false">
      <div class="modal-card modal-wide">
        <h3>Replace activity</h3>
        <p class="replace-sub">Pick an alternative. Suggested options match your interests and the current slot.</p>
        <div class="replace-list" v-if="replaceOptions.length">
          <button v-for="alt in replaceOptions" :key="alt.id" class="replace-item" @click="chooseReplace(alt)">
            <span class="replace-name">{{ alt.title }}</span>
            <span class="replace-meta">{{ alt.category }} · {{ alt.location }} · {{ alt.price > 0 ? 'R' + alt.price : 'Free' }}</span>
          </button>
        </div>
        <p v-else class="empty-trips">No other experiences available right now.</p>
        <div class="modal-actions">
          <button type="button" class="btn btn-outline" @click="showReplaceModal = false">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useExperienceStore } from '../stores/experience'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const store = useExperienceStore()
const auth = useAuthStore()

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

const myTrips = ref([])
const prefs = ref([])
const provinceOptions = ref([])
const tripForm = reactive({ destination: '', start_date: '', end_date: '' })
const generating = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const itinerary = ref(null)
const selectedTrip = ref(null)
const activeDay = ref(1)
const allExperiences = ref([])
const showEntryModal = ref(false)
const showReplaceModal = ref(false)
const replaceTarget = ref(null)
const entryForm = reactive({ name: '', location: '', start_time: '', end_time: '', cost: 0 })
const addMode = ref('pick')
const expSearch = ref('')
const addTargetDay = ref(null)

const DRAFT_KEY = 'ucc_itinerary_draft'

function draftKey() {
  const uid = auth.user?.id || 'anon'
  return `${DRAFT_KEY}_${uid}`
}

const today = new Date().toISOString().split('T')[0]

const currentDay = computed(() => {
  if (!itinerary.value) return null
  return itinerary.value.days.find(d => d.day_number === activeDay.value) || null
})

const activityCount = computed(() => {
  if (!itinerary.value) return 0
  return itinerary.value.days.reduce((s, d) => s + d.entries.filter(e => e.type === 'experience' || e.type === 'meal').length, 0)
})

const totalCost = computed(() => {
  if (!itinerary.value) return 0
  return itinerary.value.days.reduce((s, d) => s + d.entries.reduce((x, e) => x + (e.cost || 0), 0), 0)
})

const dayCost = computed(() => {
  if (!currentDay.value) return 0
  return currentDay.value.entries.reduce((s, e) => s + (e.cost || 0), 0)
})

const dayActivityCount = computed(() => {
  if (!currentDay.value) return 0
  return currentDay.value.entries.filter(e => e.type === 'experience' || e.type === 'meal').length
})

function dayCostFor(day) {
  return (day.entries || []).reduce((s, e) => s + (e.cost || 0), 0)
}

function dayActivityCountFor(day) {
  return (day.entries || []).filter(e => e.type === 'experience' || e.type === 'meal').length
}

function selectDay(n) {
  activeDay.value = n
  const el = document.getElementById('day-' + n)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const replaceOptions = computed(() => {
  if (!replaceTarget.value || !itinerary.value) return []
  const target = replaceTarget.value
  const day = itinerary.value.days.find(d => d.day_number === target.day)
  if (!day) return []
  const current = day.entries[target.idx]
  const usedIds = new Set()
  for (const d of itinerary.value.days) {
    for (const e of d.entries) if (e.experience_id) usedIds.add(e.experience_id)
  }
  let options = allExperiences.value.filter(x => !usedIds.has(x.id))
  if (current && current.category) {
    const sameCat = options.filter(x => x.category === current.category)
    if (sameCat.length) options = sameCat
  }
  return options.slice(0, 8)
})

onMounted(async () => {
  try {
    await Promise.all([
      store.fetchMyTrips(),
      store.fetchPreferences(),
      store.fetchProvinces(),
      store.fetchExperiences(),
    ])
  } catch (e) {
    /* ignore */
  }
  myTrips.value = store.myTrips
  prefs.value = store.preferences || []
  provinceOptions.value = (store.provinces || []).length
    ? store.provinces
    : [{ value: 'KwaZulu-Natal', label: 'KwaZulu-Natal' }]
  allExperiences.value = store.experiences || []

  const tripId = route.query.trip
  if (tripId) {
    const found = myTrips.value.find(t => t.id === parseInt(tripId))
    if (found) openTrip(found)
  } else {
    restoreDraft()
  }
})

function saveDraft() {
  try {
    const key = draftKey()
    if (itinerary.value) {
      localStorage.setItem(key, JSON.stringify(itinerary.value))
    } else {
      localStorage.removeItem(key)
    }
  } catch (e) { /* ignore */ }
}

function restoreDraft() {
  try {
    const raw = localStorage.getItem(draftKey())
    if (!raw) return
    const draft = JSON.parse(raw)
    if (!draft || !Array.isArray(draft.days)) return
    itinerary.value = draft
    selectedTrip.value = draft.isNew ? null : (myTrips.value.find(t => t.id === draft.tripId) || null)
    activeDay.value = 1
  } catch (e) { /* ignore */ }
}

watch(itinerary, saveDraft, { deep: true })

function makeDays(count, startIso) {
  const start = new Date(startIso)
  return Array.from({ length: count }, (_, i) => {
    const d = new Date(start)
    d.setDate(d.getDate() + i)
    return { day_number: i + 1, date: d.toISOString().split('T')[0], entries: [] }
  })
}

function openTrip(trip) {
  selectedTrip.value = trip
  activeDay.value = 1
  const start = new Date(trip.start_date)
  const end = new Date(trip.end_date)
  const count = Math.max(1, Math.ceil((end - start) / 86400000) + 1)
  const days = makeDays(count, trip.start_date)
  if (trip.notes) {
    try {
      const parsed = JSON.parse(trip.notes)
      parsed.forEach(pd => {
        const day = days.find(d => d.day_number === pd.day_number)
        if (day) day.entries = pd.entries || []
      })
    } catch (e) {
      /* ignore */
    }
  }
  itinerary.value = {
    isNew: false,
    tripId: trip.id,
    title: trip.title,
    destination: trip.destination,
    start_date: trip.start_date,
    end_date: trip.end_date,
    days,
  }
  error.value = ''
  success.value = ''
}

function resetPlan() {
  itinerary.value = null
  selectedTrip.value = null
  activeDay.value = 1
  error.value = ''
  success.value = ''
}

async function generate() {
  if (!tripForm.destination || !tripForm.start_date || !tripForm.end_date) {
    error.value = 'Please choose a destination and dates'
    return
  }
  if (tripForm.end_date < tripForm.start_date) {
    error.value = 'End date must be after start date'
    return
  }
  generating.value = true
  error.value = ''
  success.value = ''
  try {
    const resp = await api.post('/experiences/trips/generate', {
      destination: tripForm.destination,
      start_date: tripForm.start_date,
      end_date: tripForm.end_date,
      exclude_ids: [],
    })
    itinerary.value = {
      isNew: true,
      tripId: null,
      title: '',
      destination: tripForm.destination,
      start_date: tripForm.start_date,
      end_date: tripForm.end_date,
      days: resp.data.days || [],
    }
    activeDay.value = 1
    success.value = 'Itinerary generated from your saved interests.'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to generate itinerary'
  } finally {
    generating.value = false
  }
}

function excludeIdsExcept(dayNumber) {
  const ids = []
  for (const d of itinerary.value.days) {
    if (d.day_number === dayNumber) continue
    for (const e of d.entries) if (e.experience_id) ids.push(e.experience_id)
  }
  return ids
}

async function regenerateDay(dayNumber) {
  generating.value = true
  error.value = ''
  try {
    const resp = await api.post('/experiences/trips/generate', {
      destination: itinerary.value.destination,
      start_date: itinerary.value.start_date,
      end_date: itinerary.value.end_date,
      day_number: dayNumber,
      exclude_ids: excludeIdsExcept(dayNumber),
    })
    const newDay = resp.data.days[0]
    if (newDay) {
      const idx = itinerary.value.days.findIndex(d => d.day_number === dayNumber)
      if (idx !== -1) itinerary.value.days[idx] = newDay
    }
    success.value = `Day ${dayNumber} regenerated.`
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to regenerate day'
  } finally {
    generating.value = false
  }
}

async function regenerateAll() {
  generating.value = true
  error.value = ''
  try {
    const resp = await api.post('/experiences/trips/generate', {
      destination: itinerary.value.destination,
      start_date: itinerary.value.start_date,
      end_date: itinerary.value.end_date,
      exclude_ids: [],
    })
    itinerary.value.days = resp.data.days || []
    activeDay.value = 1
    success.value = 'Itinerary regenerated.'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to regenerate itinerary'
  } finally {
    generating.value = false
  }
}

function getDay(dayNumber) {
  return itinerary.value.days.find(d => d.day_number === dayNumber)
}

function removeEntry(dayNumber, idx) {
  const day = getDay(dayNumber)
  if (!day) return
  day.entries.splice(idx, 1)
}

function moveEntry(dayNumber, idx, dir) {
  const day = getDay(dayNumber)
  if (!day) return
  const target = idx + dir
  if (target < 0 || target >= day.entries.length) return
  const arr = day.entries
  const tmp = arr[idx]
  arr[idx] = arr[target]
  arr[target] = tmp
}

function openReplace(dayNumber, idx) {
  replaceTarget.value = { day: dayNumber, idx }
  showReplaceModal.value = true
}

function chooseReplace(alt) {
  const target = replaceTarget.value
  const day = getDay(target.day)
  if (!day) return
  const current = day.entries[target.idx]
  day.entries[target.idx] = {
    type: 'experience',
    name: alt.title,
    location: alt.location,
    province: alt.province,
    category: alt.category,
    start_time: current ? current.start_time : '',
    end_time: current ? current.end_time : '',
    cost: alt.price || 0,
    duration_hours: alt.duration_hours,
    description: alt.description,
    experience_id: alt.id,
    reason: 'Selected to match your itinerary and interests.',
  }
  showReplaceModal.value = false
}

function startAddEntry(dayNumber) {
  addTargetDay.value = dayNumber
  addMode.value = 'pick'
  expSearch.value = ''
  entryForm.name = ''
  entryForm.location = ''
  entryForm.start_time = ''
  entryForm.end_time = ''
  entryForm.cost = 0
  showEntryModal.value = true
}

function addDayForAdd() {
  return getDay(addTargetDay.value)
}

function toMinutes(t) {
  if (!t) return null
  const parts = String(t).split(':').map(Number)
  if (parts.length < 2 || isNaN(parts[0]) || isNaN(parts[1])) return null
  return parts[0] * 60 + parts[1]
}

function toTimeString(min) {
  const h = Math.floor(min / 60) % 24
  const m = min % 60
  return String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0')
}

function fitFreeSlot(day, durationHours) {
  const dur = Math.max(60, Math.round((durationHours || 1.5) * 60))
  const dayStart = 9 * 60
  const dayEnd = 19 * 60
  const occupied = (day.entries || [])
    .filter(e => e.start_time && e.end_time)
    .map(e => [toMinutes(e.start_time), toMinutes(e.end_time)])
    .filter(x => x[0] !== null && x[1] !== null)
    .sort((a, b) => a[0] - b[0])

  let cursor = dayStart
  for (const [s, e] of occupied) {
    if (s - cursor >= dur) {
      return { start: toTimeString(cursor), end: toTimeString(cursor + dur) }
    }
    if (e > cursor) cursor = e
  }
  if (dayEnd - cursor >= dur) {
    return { start: toTimeString(cursor), end: toTimeString(cursor + dur) }
  }
  if (occupied.length) {
    const last = occupied[occupied.length - 1]
    return { start: toTimeString(last[1]), end: toTimeString(last[1] + dur) }
  }
  return { start: '09:00', end: toTimeString(9 * 60 + dur) }
}

const filteredExperiences = computed(() => {
  const q = expSearch.value.trim().toLowerCase()
  const usedIds = new Set()
  for (const d of (itinerary.value?.days || [])) {
    for (const e of d.entries) if (e.experience_id) usedIds.add(e.experience_id)
  }
  let list = allExperiences.value.filter(x => !usedIds.has(x.id))
  if (q) {
    list = list.filter(x =>
      (x.title || '').toLowerCase().includes(q) ||
      (x.category || '').toLowerCase().includes(q) ||
      (x.location || '').toLowerCase().includes(q)
    )
  }
  return list.slice(0, 20)
})

function addExperienceEntry(x) {
  const day = addDayForAdd()
  if (!day) return
  const slot = fitFreeSlot(day, x.duration_hours)
  day.entries.push({
    type: 'experience',
    name: x.title,
    location: x.location,
    province: x.province,
    category: x.category,
    start_time: slot.start,
    end_time: slot.end,
    cost: x.price || 0,
    duration_hours: x.duration_hours,
    description: x.description,
    experience_id: x.id,
    reason: 'Added to your itinerary.',
  })
  showEntryModal.value = false
  expSearch.value = ''
}

function confirmAddEntry() {
  const day = addDayForAdd()
  if (!entryForm.name || !day) return
  let start_time = entryForm.start_time
  let end_time = entryForm.end_time
  if (!start_time || !end_time) {
    const slot = fitFreeSlot(day, 1.5)
    start_time = slot.start
    end_time = slot.end
  }
  day.entries.push({
    type: 'experience',
    name: entryForm.name,
    location: entryForm.location,
    start_time,
    end_time,
    cost: entryForm.cost || 0,
  })
  showEntryModal.value = false
}

async function confirmItinerary() {
  if (!itinerary.value || activityCount.value === 0) {
    error.value = 'Add at least one activity before confirming'
    return
  }
  saving.value = true
  error.value = ''
  success.value = ''
  const it = itinerary.value
  try {
    if (it.isNew) {
      const payloadDays = it.days.map(d => {
        const exps = d.entries.filter(e => e.type === 'experience' || e.type === 'meal')
        return {
          day_number: d.day_number,
          date: d.date,
          activity: exps[0]?.name || `Day ${d.day_number} exploration`,
          experience_id: exps[0]?.experience_id || null,
          notes: null,
        }
      })
      const notes = JSON.stringify(it.days.map(d => ({ day_number: d.day_number, date: d.date, entries: d.entries })))
      const created = await store.createTrip({
        title: `${it.destination} Vacation`,
        destination: it.destination,
        start_date: it.start_date,
        end_date: it.end_date,
        notes,
        days: payloadDays,
      })
      await trackItineraryAdds(created.id, it.days)
      success.value = 'Itinerary confirmed and saved!'
      await store.fetchMyTrips()
      myTrips.value = store.myTrips
      selectedTrip.value = created
      it.isNew = false
      it.tripId = created.id
      it.title = created.title
    } else {
      const notes = JSON.stringify(it.days.map(d => ({ day_number: d.day_number, date: d.date, entries: d.entries })))
      await store.updateTrip(it.tripId, { notes })
      await trackItineraryAdds(it.tripId, it.days)
      success.value = 'Itinerary updated.'
      await store.fetchMyTrips()
      myTrips.value = store.myTrips
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save itinerary'
  } finally {
    saving.value = false
  }
}

async function trackItineraryAdds(tripId, days) {
  const ids = []
  for (const d of days) {
    for (const e of d.entries) {
      if (e.experience_id) ids.push(e.experience_id)
    }
  }
  if (!ids.length) return
  try {
    await api.post(`/experiences/trips/${tripId}/track-itinerary-adds`, { experience_ids: ids })
  } catch (e) {
    /* tracking is best-effort */
  }
}

async function removeTrip(id) {
  try {
    await store.deleteTrip(id)
    myTrips.value = myTrips.value.filter(t => t.id !== id)
    if (selectedTrip.value?.id === id) resetPlan()
  } catch (e) {
    error.value = 'Failed to delete trip'
  }
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-ZA', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatShortDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-ZA', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.plan-trip-page {
  background: #faf8f3;
  min-height: 100vh;
  padding: 0;
}

.hero-header {
  text-align: center;
  padding: 10px 20px 36px;
  position: relative;
}

.back-btn {
  position: absolute;
  top: 14px;
  left: 20px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--glass-bg);
  border: 1px solid rgba(0, 0, 0, 0.12);
  color: #333333;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 0.82rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.hero-header h1 {
  font-family: 'Poppins', sans-serif;
  font-size: clamp(1.8rem, 4vw, 2.6rem);
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.hero-header .accent-word {
  font-family: 'Pacifico', cursive;
  font-weight: 400;
  color: var(--accent);
}

.hero-header p {
  font-size: 0.95rem;
  color: var(--text-secondary);
  max-width: 560px;
  margin: 0 auto;
}

.plan-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px 60px;
}

.left-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: var(--glass-bg);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  padding: 24px;
  color: #333333;
}

.card h2 {
  color: #1a1a1a;
  font-size: 1.15rem;
  margin-bottom: 16px;
  font-family: 'Poppins', sans-serif;
}

.card-head-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-head-row h2 {
  margin-bottom: 0;
}

.ghost-link {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 0.82rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  text-decoration: none;
  padding: 0;
}

.ghost-link:hover {
  color: #b8860b;
}

.btn-new-itinerary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid rgba(232, 162, 0, 0.45);
  border-radius: 8px;
  background: var(--accent-light);
  color: #b8860b;
  font-family: 'Poppins', sans-serif;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-new-itinerary:hover {
  background: var(--accent-fill);
  color: #1a1a1a;
}

.new-itinerary-under {
  width: 100%;
  justify-content: center;
  padding: 12px 16px;
}

.accent {
  color: var(--accent);
}

.accent-link {
  color: var(--accent);
  font-weight: 600;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  font-size: 0.78rem;
  color: var(--text-secondary);
  margin-bottom: 5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 10px;
  background: var(--glass-bg);
  color: #333333;
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.3s, box-shadow 0.3s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(232, 162, 0, 0.15);
}

.form-group select option {
  background: var(--glass-bg);
  color: #333333;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  font-family: inherit;
  transition: all 0.2s;
}

.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--accent-fill); color: #1a1a1a; width: 100%; margin-top: 4px; }
.btn-primary:hover:not(:disabled) { background: var(--accent-fill-hover); }
.btn-outline { background: var(--glass-bg); border: 1px solid rgba(0, 0, 0, 0.18); color: #333333; }
.btn-outline:hover { border-color: var(--accent); color: var(--accent); }
.btn-sm { padding: 5px 12px; border: none; border-radius: 6px; font-size: 0.72rem; cursor: pointer; font-family: inherit; font-weight: 500; }
.btn-sm-wide { padding: 8px 16px; border-radius: 8px; font-size: 0.8rem; }
.btn-delete { background: #e5484d; color: #ffffff; font-weight: 600; }
.btn-delete:hover { background: #ff4d4f; }

/* Preferences */
.pref-box {
  background: rgba(232, 162, 0, 0.08);
  border: 1px solid rgba(232, 162, 0, 0.25);
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 16px;
}

.pref-label {
  display: block;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 600;
}

.pref-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.pref-chip {
  font-size: 0.72rem;
  padding: 3px 10px;
  border-radius: 20px;
  background: var(--accent-fill);
  color: #1a1a1a;
  font-weight: 600;
}

.pref-edit {
  margin-left: 4px;
  font-size: 0.78rem;
  color: var(--accent);
  font-weight: 600;
}

/* Trip list */
.trip-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.trip-item {
  border: 1px solid rgba(0, 0, 0, 0.10);
  border-radius: 10px;
  overflow: hidden;
  background: var(--glass-bg);
}

.trip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.trip-header:hover { background: rgba(0, 0, 0, 0.04); }
.trip-header.active { background: rgba(232, 162, 0, 0.10); border-left: 3px solid var(--accent); }

.trip-title {
  display: block;
  font-weight: 600;
  color: #1a1a1a;
  font-size: 0.88rem;
}

.trip-dest {
  display: block;
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 2px;
}

.empty-trips { color: var(--text-secondary); font-size: 0.85rem; padding: 8px 0; }
.alert { padding: 10px 14px; border-radius: 10px; margin: 24px auto 12px; max-width: 1200px; font-size: 0.85rem; width: calc(100% - 40px); }
.alert-error { background: rgba(255, 77, 77, 0.08); color: #d64545; border: 1px solid rgba(255, 77, 77, 0.25); }
.alert-success { background: rgba(76, 175, 80, 0.10); color: #2e7d32; border: 1px solid rgba(76, 175, 80, 0.3); }

/* Trip summary */
.trip-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.sum-item {
  background: var(--glass-bg);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sum-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  font-weight: 600;
}

.sum-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1a1a1a;
}

.sum-value.accent { color: var(--accent); }

.itinerary-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.itinerary-actions .btn-primary {
  width: auto;
  margin: 0;
  padding: 8px 20px;
}

/* Day tabs */
.day-tabs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.day-tab {
  padding: 8px 14px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 10px;
  background: var(--glass-bg);
  color: var(--text-secondary);
  font-size: 0.78rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1.3;
}

.day-tab:hover { background: rgba(0, 0, 0, 0.04); color: #1a1a1a; }
.day-tab.active { background: var(--accent-fill); color: #1a1a1a; border-color: var(--accent); font-weight: 600; }
.day-tab-date { font-size: 0.65rem; opacity: 0.7; font-weight: 400; }
.day-tab.active .day-tab-date { opacity: 0.8; }

.day-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.day-detail-header h3 {
  font-size: 1rem;
  color: #1a1a1a;
  margin: 0;
  font-family: 'Poppins', sans-serif;
}

/* Day blocks: each day is its own colored section */
.day-list {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.day-block {
  border-radius: 14px;
  border: 1px solid;
  padding: 20px 20px 16px;
}

.day-color-0 { --day-c: #d97706; background: rgba(232, 162, 0, 0.06); border-color: rgba(232, 162, 0, 0.30); }
.day-color-1 { --day-c: #2563eb; background: rgba(37, 99, 235, 0.05); border-color: rgba(37, 99, 235, 0.30); }
.day-color-2 { --day-c: #16a34a; background: rgba(22, 163, 74, 0.05); border-color: rgba(22, 163, 74, 0.30); }
.day-color-3 { --day-c: #9333ea; background: rgba(147, 51, 234, 0.05); border-color: rgba(147, 51, 234, 0.30); }
.day-color-4 { --day-c: #dc2626; background: rgba(220, 38, 38, 0.05); border-color: rgba(220, 38, 38, 0.30); }

.day-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.day-block-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.day-block-badge {
  background: var(--day-c);
  color: #ffffff;
  font-weight: 700;
  font-size: 0.8rem;
  padding: 4px 14px;
  border-radius: 20px;
  font-family: 'Poppins', sans-serif;
}

.day-block-date {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

/* Timeline */
.timeline {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.tl-row {
  display: grid;
  grid-template-columns: 96px 1fr auto;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.tl-row:last-child { border-bottom: none; }

.tl-time {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  font-family: 'Poppins', sans-serif;
}

.tl-start { font-size: 0.9rem; font-weight: 600; color: #1a1a1a; }
.tl-end { font-size: 0.72rem; color: var(--text-muted); }
.tl-break .tl-start { color: var(--text-secondary); font-weight: 500; }

.tl-body { min-width: 0; }

.tl-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.tl-name { font-size: 0.9rem; font-weight: 600; color: #1a1a1a; }

.tl-tag { font-size: 0.66rem; padding: 2px 8px; border-radius: 20px; font-weight: 600; }
.tag-exp { background: var(--accent-light); color: var(--accent-dark); }
.tag-meal { background: var(--error); color: #ffffff; }
.tag-break { background: rgba(0, 0, 0, 0.06); color: var(--text-secondary); }

.tl-meta-line {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.tl-meta { font-size: 0.75rem; color: var(--text-secondary); }

.tl-reason {
  font-size: 0.76rem;
  color: #b8860b;
  font-style: italic;
  margin: 6px 0 0;
}

.tl-actions {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.tl-btn {
  background: var(--glass-bg);
  border: 1px solid rgba(0, 0, 0, 0.15);
  color: #333333;
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.tl-btn:hover { background: rgba(0, 0, 0, 0.05); }
.tl-btn-accent { background: rgba(232, 162, 0, 0.12); border-color: rgba(232, 162, 0, 0.4); color: #b8860b; }
.tl-btn-accent:hover { background: rgba(232, 162, 0, 0.2); }
.tl-btn-danger { background: #e5484d; border-color: #e5484d; color: #ffffff; }
.tl-btn-danger:hover { background: #ff4d4f; }

.tl-cost {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--accent);
  white-space: nowrap;
}

.day-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 10px;
  padding: 12px 14px;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.day-cost { font-size: 0.85rem; color: #333333; }

.btn-add-entry {
  background: rgba(232, 162, 0, 0.12);
  border: 1px solid rgba(232, 162, 0, 0.35);
  color: #b8860b;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
}

.btn-add-entry:hover { background: rgba(232, 162, 0, 0.2); }

.booking-note {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 16px;
  text-align: center;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-card {
  width: 440px;
  max-width: 100%;
  background: var(--glass-bg);
  border: 1px solid rgba(0, 0, 0, 0.10);
  border-radius: 16px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.18);
  padding: 28px;
  color: #333333;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-wide { width: 560px; }

.modal-card h3 {
  font-size: 1.15rem;
  margin-bottom: 18px;
  font-family: 'Poppins', sans-serif;
  color: #1a1a1a;
}

.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 6px;
}

.modal-actions .btn { flex: 1; }

.replace-sub {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.replace-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.replace-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  text-align: left;
  padding: 12px 14px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 10px;
  background: var(--glass-bg);
  color: #333333;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.replace-item:hover { border-color: var(--accent); background: rgba(232, 162, 0, 0.06); }

.replace-name { font-size: 0.88rem; font-weight: 600; color: #1a1a1a; }
.replace-meta { font-size: 0.75rem; color: var(--text-secondary); }

/* Add-entry picker */
.add-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.add-tab {
  flex: 1;
  padding: 9px 12px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 10px;
  background: var(--glass-bg);
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.add-tab.active {
  border-color: var(--accent);
  background: rgba(232, 162, 0, 0.12);
  color: #b8860b;
}

.exp-picker .form-group {
  margin-bottom: 10px;
}

.exp-pick-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 4px;
}

.exp-pick-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  text-align: left;
  padding: 11px 14px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 10px;
  background: var(--glass-bg);
  color: #333333;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.exp-pick-item:hover {
  border-color: var(--accent);
  background: rgba(232, 162, 0, 0.06);
}

.exp-pick-name { font-size: 0.88rem; font-weight: 600; color: #1a1a1a; }
.exp-pick-meta { font-size: 0.75rem; color: var(--text-secondary); }

.modal-footer {
  margin-top: 14px;
}

@media (max-width: 900px) {
  .plan-layout {
    grid-template-columns: 1fr;
  }
  .hero-header h1 { font-size: 2rem; }
  .tl-row { grid-template-columns: 84px 1fr; }
  .tl-cost { grid-column: 2; }
}
</style>
