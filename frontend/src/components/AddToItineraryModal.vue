<template>
  <Teleport to="body">
    <div class="modal-overlay" v-if="visible" @click.self="close">
    <div class="modal-card itinerary-modal">

      <!-- Step 1: Choose an Itinerary -->
      <div v-if="modalStep === 1" class="modal-step">
        <button class="modal-close-btn" @click="close">&times;</button>
        <div class="step-indicator">
          <span class="step-badge active">1</span>
          <span class="step-line"></span>
          <span class="step-badge">2</span>
          <span class="step-line"></span>
          <span class="step-badge">3</span>
          <span class="step-line"></span>
          <span class="step-badge">4</span>
        </div>
        <h3>Add to Itinerary</h3>
        <p class="step-desc">Choose an existing itinerary or create a new one for {{ experience?.title }}.</p>

        <div v-if="existingTrips.length" class="trip-options">
          <label
            v-for="t in existingTrips"
            :key="t.id"
            class="option-card"
            :class="{ selected: tripChoice === t.id }"
          >
            <input type="radio" name="trip-choice" :value="t.id" v-model="tripChoice" />
            <div class="option-body">
              <span class="option-title">{{ t.title }}</span>
              <span class="option-sub">{{ t.destination }} &middot; {{ formatCardDay(t.start_date) }} – {{ formatCardDay(t.end_date) }}</span>
            </div>
          </label>
        </div>

        <label class="option-card" :class="{ selected: tripChoice === 'new' }">
          <input type="radio" name="trip-choice" value="new" v-model="tripChoice" />
          <span class="option-title">Create a new trip</span>
        </label>

        <div v-if="tripChoice === 'new'" class="date-inputs new-date-block">
          <div class="form-group">
            <label>Start Date</label>
            <input v-model="tripDates.start_date" type="date" :min="todayStr" />
          </div>
          <div class="form-group">
            <label>End Date</label>
            <input v-model="tripDates.end_date" type="date" :min="tripDates.start_date || todayStr" />
          </div>
        </div>
        <div v-if="tripChoice === 'new' && tripDayCount > 0" class="day-count-badge">
          <span class="day-count-num">{{ tripDayCount }}</span>
          {{ tripDayCount === 1 ? 'day' : 'days' }}
        </div>
        <div v-else-if="tripChoice === 'new' && tripDates.start_date && tripDates.end_date && !datesValid" class="date-error">
          End date must be after start date
        </div>

        <div class="modal-actions">
          <button class="btn btn-primary" :disabled="!selectionValid || modalLoading" @click="continueToDay">
            {{ modalLoading ? 'Loading...' : 'Continue' }}
          </button>
          <button class="btn btn-outline" @click="close">Cancel</button>
        </div>
      </div>

      <!-- Step 2: Select Day -->
      <div v-if="modalStep === 2" class="modal-step">
        <button class="modal-close-btn" @click="close">&times;</button>
        <div class="step-indicator">
          <span class="step-badge done">&#10003;</span>
          <span class="step-line done"></span>
          <span class="step-badge active">2</span>
          <span class="step-line"></span>
          <span class="step-badge">3</span>
          <span class="step-line"></span>
          <span class="step-badge">4</span>
        </div>
        <h3>Select a Day</h3>
        <p class="step-desc">Choose which day to add {{ experience?.title }}.</p>
        <div class="day-cards">
          <div
            v-for="day in tripDays"
            :key="day.day_number"
            class="day-card"
            :class="{ selected: selectedDay?.day_number === day.day_number }"
            @click="selectedDay = day"
          >
            <div class="day-card-number">Day {{ day.day_number }}</div>
            <div class="day-card-date">{{ formatCardDay(day.date) }}</div>
            <div v-if="day.entryCount > 0" class="day-card-entries">{{ day.entryCount }} activit{{ day.entryCount === 1 ? 'y' : 'ies' }}</div>
            <div v-else class="day-card-empty">No activities yet</div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn btn-primary" :disabled="!selectedDay" @click="proceedToTimeSelection">Continue</button>
          <button class="btn btn-outline" @click="modalStep = 1">Back</button>
        </div>
      </div>

      <!-- Step 3: Select Time -->
      <div v-if="modalStep === 3" class="modal-step">
        <button class="modal-close-btn" @click="close">&times;</button>
        <div class="step-indicator">
          <span class="step-badge done">&#10003;</span>
          <span class="step-line done"></span>
          <span class="step-badge done">&#10003;</span>
          <span class="step-line done"></span>
          <span class="step-badge active">3</span>
          <span class="step-line"></span>
          <span class="step-badge">4</span>
        </div>
        <h3>Choose a Time</h3>
        <p class="step-desc" v-if="experienceDuration">Duration: {{ experienceDuration }} hours</p>

        <div v-if="dayEntries.length === 0" class="time-picker-simple">
          <div class="form-group">
            <label>Start Time</label>
            <input v-model="entryTime.start_time" type="time" />
          </div>
          <div class="form-group">
            <label>End Time</label>
            <input v-model="entryTime.end_time" type="time" />
          </div>
          <div v-if="!entryTime.start_time" class="time-suggestion">
            <button class="btn-suggestion" @click="suggestDefaultTime">Suggest a time</button>
          </div>
        </div>

        <div v-else class="timeline-container">
          <div v-if="noAvailableSlots" class="fully-booked">
            <div class="booked-icon">&#128197;</div>
            <p>This day is fully booked.</p>
            <div class="booked-actions">
              <button class="btn btn-outline-sm" @click="modalStep = 2">Choose another day</button>
            </div>
          </div>
          <div v-else class="timeline">
            <div
              v-for="(slot, si) in timeSlots"
              :key="si"
              class="timeline-slot"
              :class="{
                occupied: slot.type === 'occupied',
                available: slot.type === 'available',
                selected: selectedSlotIndex === si,
                'fits-disabled': slot.type === 'available' && !slot.fits,
                recommended: slot.recommended,
              }"
              @click="selectSlot(si)"
            >
              <div class="slot-indicator">
                <span v-if="slot.type === 'occupied'" class="slot-dot occupied-dot"></span>
                <span v-else class="slot-dot available-dot"></span>
              </div>
              <div class="slot-body">
                <div class="slot-time-range">{{ slot.start }} – {{ slot.end }}</div>
                <div class="slot-label">{{ slot.label }}</div>
                <div v-if="slot.recommended" class="slot-recommended">&#9733; Recommended</div>
                <div v-if="slot.type === 'available' && !slot.fits" class="slot-too-small">Experience too long for this gap</div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn-primary" :disabled="!entryTime.start_time || !entryTime.end_time" @click="modalStep = 4">Continue</button>
          <button class="btn btn-outline" @click="modalStep = 2">Back</button>
        </div>
      </div>

      <!-- Step 4: Confirmation -->
      <div v-if="modalStep === 4" class="modal-step">
        <button class="modal-close-btn" @click="close">&times;</button>
        <div class="step-indicator">
          <span class="step-badge done">&#10003;</span>
          <span class="step-line done"></span>
          <span class="step-badge done">&#10003;</span>
          <span class="step-line done"></span>
          <span class="step-badge done">&#10003;</span>
          <span class="step-line done"></span>
          <span class="step-badge active">4</span>
        </div>
        <h3>Confirm Your Plan</h3>
        <div class="confirm-summary">
          <div class="confirm-row">
            <span class="confirm-label">Experience</span>
            <span class="confirm-value">{{ experience?.title }}</span>
          </div>
          <div class="confirm-row">
            <span class="confirm-label">Province</span>
            <span class="confirm-value">{{ experience?.province || '—' }}</span>
          </div>
          <div class="confirm-row">
            <span class="confirm-label">Trip Dates</span>
            <span class="confirm-value">{{ tripDates.start_date }} – {{ tripDates.end_date }}</span>
          </div>
          <div class="confirm-row">
            <span class="confirm-label">Day</span>
            <span class="confirm-value">Day {{ selectedDay?.day_number }} — {{ formatCardDay(selectedDay?.date) }}</span>
          </div>
          <div class="confirm-row">
            <span class="confirm-label">Time</span>
            <span class="confirm-value">{{ entryTime.start_time }} – {{ entryTime.end_time }}</span>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn btn-primary" :disabled="modalLoading" @click="confirmAddToItinerary">
            {{ modalLoading ? 'Saving...' : 'Confirm & Add' }}
          </button>
          <button class="btn btn-outline" @click="modalStep = 3">Back</button>
        </div>
      </div>

      <!-- Step 5: Success -->
      <div v-if="modalStep === 5" class="modal-step success-step">
        <div class="success-icon">&#10003;</div>
        <h3>Added to Itinerary!</h3>
        <p>{{ experience?.title }} has been added to your trip.</p>
        <div class="modal-actions">
          <button class="btn btn-primary" @click="done">Done</button>
        </div>
      </div>

    </div>
  </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useExperienceStore } from '../stores/experience'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  experience: { type: Object, default: null },
  visible: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'success'])

const router = useRouter()
const store = useExperienceStore()
const auth = useAuthStore()

const modalStep = ref(1)
const modalLoading = ref(false)
const createdTrip = ref(null)
const tripDays = ref([])
const selectedDay = ref(null)
const selectedSlotIndex = ref(-1)

const existingTrips = ref([])
const tripChoice = ref('new')

const tripDates = reactive({
  start_date: '',
  end_date: '',
})

const entryTime = reactive({
  start_time: '',
  end_time: '',
})

const DAY_START = '06:00'
const DAY_END = '22:00'

const todayStr = computed(() => new Date().toISOString().split('T')[0])

const selectedTrip = computed(() => existingTrips.value.find(t => t.id === tripChoice.value) || null)

const selectionValid = computed(() => {
  if (tripChoice.value === 'new') return datesValid.value
  return !!selectedTrip.value
})

const datesValid = computed(() => {
  if (!tripDates.start_date || !tripDates.end_date) return false
  return new Date(tripDates.end_date) >= new Date(tripDates.start_date)
})

const tripDayCount = computed(() => {
  if (!datesValid.value) return 0
  const s = new Date(tripDates.start_date)
  const e = new Date(tripDates.end_date)
  return Math.ceil((e - s) / (1000 * 60 * 60 * 24)) + 1
})

const experienceDuration = computed(() => props.experience?.duration_hours || null)

const dayEntries = computed(() => {
  if (!createdTrip.value?.notes || !selectedDay.value) return []
  try {
    const parsed = JSON.parse(createdTrip.value.notes)
    const dayData = parsed.find(d => d.day_number === selectedDay.value.day_number)
    return dayData?.entries || []
  } catch { return [] }
})

const timeSlots = computed(() => {
  const entries = [...dayEntries.value].filter(e => e.start_time && e.end_time)
  if (entries.length === 0) return []
  entries.sort((a, b) => a.start_time.localeCompare(b.start_time))
  const slots = []
  let cursor = DAY_START
  for (const entry of entries) {
    if (entry.start_time > cursor) {
      const gapH = hoursBetween(entry.start_time, cursor)
      const fits = experienceDuration ? gapH >= experienceDuration : true
      slots.push({ type: 'available', start: cursor, end: entry.start_time, label: 'Available', fits, recommended: false })
    }
    slots.push({ type: 'occupied', start: entry.start_time, end: entry.end_time, label: entry.name, fits: false, recommended: false })
    if (entry.end_time > cursor) cursor = entry.end_time
  }
  if (cursor < DAY_END) {
    const gapH = hoursBetween(DAY_END, cursor)
    const fits = experienceDuration ? gapH >= experienceDuration : true
    slots.push({ type: 'available', start: cursor, end: DAY_END, label: 'Available', fits, recommended: false })
  }
  const fitting = slots.filter(s => s.type === 'available' && s.fits)
  if (fitting.length > 0) fitting[0].recommended = true
  return slots
})

const noAvailableSlots = computed(() => {
  return timeSlots.value.filter(s => s.type === 'available' && s.fits).length === 0
})

function hoursBetween(t1, t2) {
  const [h1, m1] = t1.split(':').map(Number)
  const [h2, m2] = t2.split(':').map(Number)
  return ((h1 * 60 + m1) - (h2 * 60 + m2)) / 60
}

function addMinutes(time, mins) {
  const [h, m] = time.split(':').map(Number)
  const total = h * 60 + m + mins
  return `${String(Math.floor(total / 60) % 24).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`
}

function formatCardDay(d) {
  if (!d) return ''
  const dt = new Date(d + 'T00:00:00')
  return dt.toLocaleDateString('en-ZA', { weekday: 'short', month: 'short', day: 'numeric' })
}

function close() {
  modalStep.value = 1
  emit('close')
}

function done() {
  modalStep.value = 1
  emit('success', createdTrip.value ? {
    id: createdTrip.value.id,
    title: createdTrip.value.title,
    start_date: createdTrip.value.start_date,
    end_date: createdTrip.value.end_date,
    entryCount: 1,
  } : null)
  emit('close')
}

async function loadTrips() {
  try {
    await store.fetchMyTrips()
    existingTrips.value = store.myTrips || []
  } catch (e) {
    existingTrips.value = []
  }
}

function buildTripDays(startIso, endIso) {
  const s = new Date(startIso)
  const e = new Date(endIso)
  const count = Math.max(1, Math.ceil((e - s) / 86400000) + 1)
  let notesData = []
  try { notesData = JSON.parse(createdTrip.value?.notes || '[]') } catch {}
  const days = []
  for (let i = 0; i < count; i++) {
    const d = new Date(s)
    d.setDate(d.getDate() + i)
    const dayNum = i + 1
    const dayFromNotes = notesData.find(n => n.day_number === dayNum)
    days.push({
      day_number: dayNum,
      date: d.toISOString().split('T')[0],
      entryCount: dayFromNotes?.entries?.length || 0,
    })
  }
  tripDays.value = days
}

async function continueToDay() {
  if (!selectionValid.value) return
  if (tripChoice.value === 'new') {
    await createNewTripAndProceed()
    return
  }
  const trip = selectedTrip.value
  if (!trip) return
  createdTrip.value = trip
  buildTripDays(trip.start_date, trip.end_date)
  modalStep.value = 2
}

async function createNewTripAndProceed() {
  if (!datesValid.value) return
  modalLoading.value = true
  try {
    const dest = props.experience?.province || props.experience?.location || 'South Africa'
    const trip = await store.createTrip({
      title: `${dest} Vacation`,
      destination: dest,
      start_date: tripDates.start_date,
      end_date: tripDates.end_date,
      notes: '[]',
      days: [],
    })
    createdTrip.value = trip
    buildTripDays(tripDates.start_date, tripDates.end_date)
    modalStep.value = 2
  } catch (e) {
    console.error('Create trip failed:', e)
    alert('Failed to create trip. Please try again.')
  } finally {
    modalLoading.value = false
  }
}

async function proceedToTimeSelection() {
  if (!selectedDay.value) return
  modalStep.value = 3
  selectedSlotIndex.value = -1
  entryTime.start_time = ''
  entryTime.end_time = ''
  if (createdTrip.value) {
    try {
      const refreshed = await store.getItinerary(createdTrip.value.id)
      createdTrip.value = refreshed
      let notesData = []
      try { notesData = JSON.parse(refreshed.notes || '[]') } catch {}
      tripDays.value = tripDays.value.map(d => {
        const dayNotes = notesData.find(n => n.day_number === d.day_number)
        return { ...d, entryCount: dayNotes?.entries?.length || 0 }
      })
    } catch {}
  }
  if (dayEntries.value.length === 0) {
    suggestDefaultTime()
  } else {
    // Auto-select a free slot so the experience lands in available free time.
    const fitting = timeSlots.value.filter(s => s.type === 'available' && s.fits)
    if (fitting.length > 0) {
      const rec = fitting.find(s => s.recommended) || fitting[0]
      selectSlot(timeSlots.value.indexOf(rec))
    } else {
      suggestDefaultTime()
    }
  }
}

function suggestDefaultTime() {
  entryTime.start_time = '09:00'
  entryTime.end_time = '10:00'
}

function selectSlot(index) {
  const slot = timeSlots.value[index]
  if (!slot || slot.type !== 'available' || !slot.fits) return
  selectedSlotIndex.value = index
  entryTime.start_time = slot.start
  entryTime.end_time = slot.end || ''
}

async function confirmAddToItinerary() {
  if (!createdTrip.value || !selectedDay.value || !entryTime.start_time) return
  modalLoading.value = true
  try {
    let notes = []
    try { notes = JSON.parse(createdTrip.value.notes || '[]') } catch {}
    let dayData = notes.find(d => d.day_number === selectedDay.value.day_number)
    if (!dayData) {
      dayData = { day_number: selectedDay.value.day_number, date: selectedDay.value.date, entries: [] }
      notes.push(dayData)
    }
    dayData.entries.push({
      type: 'experience',
      name: props.experience.title,
      location: props.experience.location,
      start_time: entryTime.start_time,
      end_time: entryTime.end_time,
      cost: props.experience.price || 0,
      description: props.experience.description || '',
      province: props.experience.province,
      experience_id: props.experience.id || null,
    })
    await store.updateTrip(createdTrip.value.id, { notes: JSON.stringify(notes) })
    await store.addTripDay(createdTrip.value.id, {
      day_number: selectedDay.value.day_number,
      date: selectedDay.value.date,
      activity: props.experience.title,
      experience_id: props.experience.id || null,
      notes: `Added from experience: ${props.experience.title}`,
    })
    let entryCount = 0
    try {
      const refreshedNotes = JSON.parse(createdTrip.value.notes || '[]')
      entryCount = refreshedNotes.reduce((sum, d) => sum + (d.entries?.length || 0), 0)
    } catch {}
    modalStep.value = 5
  } catch (e) {
    console.error('Save failed:', e)
    alert('Failed to add to itinerary. Please try again.')
  } finally {
    modalLoading.value = false
  }
}

onMounted(() => {
  loadTrips()
})

watch(() => props.visible, async (val) => {
  if (val) {
    await loadTrips()
    if (existingTrips.value.length) {
      tripChoice.value = existingTrips.value[0].id
    } else {
      tripChoice.value = 'new'
    }
  } else {
    modalStep.value = 1
    tripDates.start_date = ''
    tripDates.end_date = ''
    createdTrip.value = null
    tripDays.value = []
    selectedDay.value = null
    selectedSlotIndex.value = -1
    entryTime.start_time = ''
    entryTime.end_time = ''
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.itinerary-modal {
  width: 520px;
  max-width: 94vw;
  max-height: 90vh;
  overflow-y: auto;
  background: rgba(20, 20, 35, 0.98);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.30);
  border-radius: 20px;
  padding: 32px 28px;
  color: #fff;
  animation: slideUp 0.25s ease;
}
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.modal-step { position: relative; }
.modal-close-btn {
  position: absolute; top: -8px; right: -6px;
  background: none; border: none;
  color: rgba(255, 255, 255, 0.80); font-size: 1.6rem;
  cursor: pointer; line-height: 1; padding: 4px 8px;
  transition: color 0.2s;
}
.modal-close-btn:hover { color: #fff; }
.step-indicator {
  display: flex; align-items: center; justify-content: center;
  gap: 0; margin-bottom: 24px;
}
.step-badge {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem; font-weight: 700;
  background: rgba(255, 255, 255, 0.22); color: rgba(255, 255, 255, 0.70);
  transition: all 0.3s;
}
.step-badge.active { background: var(--accent-fill); color: #1a1a1a; }
.step-badge.done { background: rgba(76,175,80,0.3); color: #81c784; }
.step-line { width: 40px; height: 2px; background: rgba(255, 255, 255, 0.26); margin: 0 4px; }
.step-line.done { background: #81c784; }
.itinerary-modal h3 {
  font-family: 'Poppins', sans-serif; font-size: 1.25rem;
  font-weight: 700; text-align: center; margin-bottom: 6px;
}
.step-desc { text-align: center; color: rgba(255, 255, 255, 0.80); font-size: 0.85rem; margin-bottom: 20px; }
.date-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 12px; }
.itinerary-modal .form-group { margin-bottom: 10px; }
.itinerary-modal .form-group label {
  display: block; font-size: 0.75rem; text-transform: uppercase;
  letter-spacing: 0.5px; color: rgba(255, 255, 255, 0.80); margin-bottom: 4px;
}
.itinerary-modal .form-group input,
.itinerary-modal .form-group select {
  width: 100%; padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.38); border-radius: 8px;
  background: rgba(255, 255, 255, 0.22); color: #fff;
  font-size: 0.9rem; font-family: inherit; outline: none;
  transition: border-color 0.2s; box-sizing: border-box;
}
.itinerary-modal input[type="date"] {
  color-scheme: dark;
}
.itinerary-modal input[type="date"]::-webkit-calendar-picker-indicator {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='18' rx='2' ry='2'/%3E%3Cline x1='16' y1='2' x2='16' y2='6'/%3E%3Cline x1='8' y1='2' x2='8' y2='6'/%3E%3Cline x1='3' y1='10' x2='21' y2='10'/%3E%3C/svg%3E");
  background-size: 20px 20px;
  background-position: center;
  background-repeat: no-repeat;
  cursor: pointer;
  opacity: 1;
}
.itinerary-modal .form-group input:focus { border-color: var(--accent); }
.day-count-badge { text-align: center; padding: 8px 0 12px; font-size: 0.9rem; color: rgba(255, 255, 255, 0.88); }
.day-count-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--accent-fill); color: #1a1a1a; font-weight: 700; font-size: 0.85rem; margin-right: 4px;
}
.date-error { text-align: center; color: #ff6b6b; font-size: 0.82rem; padding: 4px 0 8px; }

.trip-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 10px;
  max-height: 260px;
  overflow-y: auto;
}

.option-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.16);
  cursor: pointer;
  transition: all 0.2s;
}

.option-card:hover {
  background: rgba(255, 255, 255, 0.24);
  border-color: rgba(255, 255, 255, 0.50);
}

.option-card.selected {
  border-color: var(--accent);
  background: rgba(232, 162, 0, 0.1);
}

.option-card input[type="radio"] {
  accent-color: var(--accent);
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.option-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.option-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
}

.option-sub {
  font-size: 0.76rem;
  color: rgba(255, 255, 255, 0.78);
  margin-top: 1px;
}

.new-date-block {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed rgba(255, 255, 255, 0.25);
}
.itinerary-modal .modal-actions {
  display: flex; gap: 10px; margin-top: 16px;
  padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.20);
}
.itinerary-modal .modal-actions .btn {
  flex: 1; padding: 10px 16px; border: none; border-radius: 8px;
  font-size: 0.88rem; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s; text-align: center;
}
.itinerary-modal .btn:disabled { opacity: 0.4; cursor: not-allowed; }
.itinerary-modal .btn-primary { background: var(--accent-fill); color: #1a1a1a; }
.itinerary-modal .btn-primary:hover:not(:disabled) { background: var(--accent-fill-hover); }
.itinerary-modal .btn-outline { background: transparent; border: 1px solid rgba(255, 255, 255, 0.55); color: #fff; }
.itinerary-modal .btn-outline:hover { border-color: var(--accent); color: var(--accent); }
.day-cards { display: flex; flex-direction: column; gap: 8px; margin-bottom: 4px; }
.day-card {
  display: flex; align-items: center; gap: 14px; padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.28); border-radius: 10px;
  background: rgba(255, 255, 255, 0.16); cursor: pointer; transition: all 0.2s;
}
.day-card:hover { background: rgba(255, 255, 255, 0.24); border-color: rgba(255, 255, 255, 0.50); }
.day-card.selected { border-color: var(--accent); background: rgba(255,182,18,0.1); }
.day-card-number { font-size: 0.85rem; font-weight: 700; color: var(--accent); min-width: 50px; }
.day-card-date { flex: 1; font-size: 0.88rem; color: #fff; }
.day-card-entries { font-size: 0.77rem; color: var(--accent); background: rgba(255,182,18,0.12); padding: 2px 10px; border-radius: 12px; }
.day-card-empty { font-size: 0.77rem; color: rgba(255, 255, 255, 0.60); font-style: italic; }
.time-picker-simple { max-width: 280px; margin: 0 auto 8px; }
.time-suggestion { text-align: center; margin-top: 8px; }
.btn-suggestion {
  background: none; border: 1px dashed rgba(255, 255, 255, 0.55);
  color: var(--accent); padding: 6px 16px; border-radius: 6px;
  font-size: 0.82rem; cursor: pointer; font-family: inherit; transition: all 0.2s;
}
.btn-suggestion:hover { border-color: var(--accent); background: rgba(255,182,18,0.08); }
.timeline-container { margin: 4px 0 8px; }
.timeline { display: flex; flex-direction: column; gap: 4px; }
.timeline-slot {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 12px; border-radius: 10px; transition: all 0.2s; cursor: default;
}
.timeline-slot.available { cursor: pointer; border: 1px solid rgba(255, 255, 255, 0.24); background: rgba(255, 255, 255, 0.14); }
.timeline-slot.available:hover { background: rgba(76,175,80,0.1); border-color: rgba(76,175,80,0.3); }
.timeline-slot.available.selected { background: rgba(76,175,80,0.18); border-color: #81c784; }
.timeline-slot.recommended { border-color: var(--accent) !important; background: rgba(255,182,18,0.08) !important; }
.timeline-slot.occupied { background: rgba(255, 255, 255, 0.18); border: 1px solid rgba(255, 255, 255, 0.20); opacity: 0.7; }
.timeline-slot.fits-disabled { opacity: 0.35; cursor: not-allowed !important; }
.slot-indicator { padding-top: 3px; }
.slot-dot { display: block; width: 10px; height: 10px; border-radius: 50%; }
.occupied-dot { background: #ff6b6b; }
.available-dot { background: #81c784; }
.slot-body { flex: 1; }
.slot-time-range { font-size: 0.85rem; font-weight: 600; color: #fff; }
.slot-label { font-size: 0.78rem; color: rgba(255, 255, 255, 0.80); margin-top: 1px; }
.slot-recommended {
  display: inline-block; font-size: 0.7rem; color: var(--accent);
  background: rgba(255,182,18,0.15); padding: 1px 8px; border-radius: 10px;
  margin-top: 3px; font-weight: 600;
}
.slot-too-small { font-size: 0.7rem; color: #ff6b6b; margin-top: 2px; }
.fully-booked { text-align: center; padding: 20px 0; }
.booked-icon { font-size: 2.5rem; margin-bottom: 8px; }
.fully-booked p { color: rgba(255, 255, 255, 0.88); margin-bottom: 12px; }
.booked-actions { display: flex; justify-content: center; gap: 8px; }
.btn-outline-sm {
  background: transparent; border: 1px solid rgba(255, 255, 255, 0.50);
  color: #fff; padding: 6px 14px; border-radius: 6px;
  font-size: 0.82rem; cursor: pointer; font-family: inherit; transition: all 0.2s;
}
.btn-outline-sm:hover { border-color: var(--accent); color: var(--accent); }
.confirm-summary {
  background: rgba(255, 255, 255, 0.18); border: 1px solid rgba(255, 255, 255, 0.24);
  border-radius: 12px; padding: 16px 18px; margin: 8px 0 4px;
}
.confirm-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.18);
}
.confirm-row:last-child { border-bottom: none; }
.confirm-label { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.5px; color: rgba(255, 255, 255, 0.75); }
.confirm-value { font-size: 0.92rem; font-weight: 600; color: #fff; text-align: right; max-width: 60%; }
.success-step { text-align: center; padding: 16px 0; }
.success-icon {
  width: 64px; height: 64px; border-radius: 50%;
  background: rgba(76,175,80,0.2); color: #81c784;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.8rem; font-weight: 700; margin: 0 auto 16px;
  animation: popIn 0.4s ease;
}
@keyframes popIn {
  0% { transform: scale(0); opacity: 0; }
  70% { transform: scale(1.15); }
  100% { transform: scale(1); opacity: 1; }
}
.success-step h3 { margin-bottom: 6px; }
.success-step p { color: rgba(255, 255, 255, 0.88); margin-bottom: 16px; }
.itinerary-modal::-webkit-scrollbar { width: 4px; }
.itinerary-modal::-webkit-scrollbar-track { background: transparent; }
.itinerary-modal::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.30); border-radius: 4px; }
@media (max-width: 560px) {
  .itinerary-modal { padding: 24px 18px; }
  .date-inputs { grid-template-columns: 1fr; }
  .step-line { width: 24px; }
}
</style>
