<template>
  <div class="form-page">
    <div class="form-container">
      <div class="hero-header">
        <h1><span class="accent-word">Edit</span> Hotspot</h1>
        <p>Update your cultural experience details.</p>
      </div>

      <div v-if="rejectionReason" class="appeal-banner">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        <div class="appeal-content">
          <span class="appeal-title">This hotspot was rejected</span>
          <p class="appeal-reason">{{ rejectionReason }}</p>
          <p class="appeal-hint">Update the details below to address the issue, then save to submit an appeal for re-review.</p>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading hotspot...</p>
      </div>

      <div v-else-if="notFound" class="empty-state">
        <p>Hotspot not found or you don't have permission to edit it.</p>
        <router-link to="/host" class="btn btn-primary">Go to My Hotspots</router-link>
      </div>

      <form v-else @submit.prevent="handleSubmit" class="hotspot-form" novalidate>
        <div v-if="serverError" class="alert alert-error">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          {{ serverError }}
        </div>

        <div v-if="saveSuccess" class="alert alert-success">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          {{ rejectionReason ? 'Appeal submitted! Your hotspot will be reviewed by an admin again.' : 'Hotspot updated successfully. It will be reviewed by an admin before going live.' }}
        </div>

        <div class="form-group">
          <label for="title">Hotspot Name *</label>
          <input
            id="title"
            v-model="form.title"
            type="text"
            :class="['form-input', { error: errors.title }]"
            @blur="validateField('title')"
          />
          <span v-if="errors.title" class="field-error">{{ errors.title }}</span>
        </div>

        <div class="form-group">
          <label for="description">Description *</label>
          <textarea
            id="description"
            v-model="form.description"
            :class="['form-input textarea', { error: errors.description }]"
            rows="5"
            @blur="validateField('description')"
          ></textarea>
          <div class="char-count" :class="{ warn: form.description.length > 1800 }">
            {{ form.description.length }} / 2000
          </div>
          <span v-if="errors.description" class="field-error">{{ errors.description }}</span>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="category">Category *</label>
            <select
              id="category"
              v-model="form.category"
              :class="['form-input', { error: errors.category }]"
              @change="validateField('category')"
            >
              <option value="" disabled>Select a category</option>
              <option v-for="cat in categories" :key="cat.value" :value="cat.value">
                {{ cat.label }}
              </option>
            </select>
            <span v-if="errors.category" class="field-error">{{ errors.category }}</span>
          </div>

          <div class="form-group">
            <label for="province">Province</label>
            <select id="province" v-model="form.province" class="form-input">
              <option value="">Select province (optional)</option>
              <option v-for="p in provinces" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="location">Location / Address *</label>
          <input
            id="location"
            v-model="form.location"
            type="text"
            :class="['form-input', { error: errors.location }]"
            @blur="validateField('location')"
          />
          <span v-if="errors.location" class="field-error">{{ errors.location }}</span>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="price">Price (ZAR) *</label>
            <input
              id="price"
              v-model.number="form.price"
              type="number"
              step="0.01"
              min="0.01"
              :class="['form-input', { error: errors.price }]"
              @blur="validateField('price')"
            />
            <span v-if="errors.price" class="field-error">{{ errors.price }}</span>
          </div>

          <div class="form-group">
            <label for="duration">Duration (hours)</label>
            <input
              id="duration"
              v-model.number="form.duration_hours"
              type="number"
              step="0.5"
              min="0.5"
              :class="['form-input', { error: errors.duration_hours }]"
              @blur="validateField('duration_hours')"
            />
            <span v-if="errors.duration_hours" class="field-error">{{ errors.duration_hours }}</span>
          </div>

          <div class="form-group">
            <label for="max">Max Participants</label>
            <input
              id="max"
              v-model.number="form.max_participants"
              type="number"
              min="1"
              max="100"
              :class="['form-input', { error: errors.max_participants }]"
              @blur="validateField('max_participants')"
            />
            <span v-if="errors.max_participants" class="field-error">{{ errors.max_participants }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="image">Image URL (optional)</label>
          <input
            id="image"
            v-model="form.image_url"
            type="url"
            class="form-input"
            placeholder="https://example.com/image.jpg"
          />
        </div>

        <div class="form-notice">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          Editing will require re-approval by an admin before the changes go live.
        </div>

        <div class="form-actions">
          <router-link to="/host" class="btn btn-cancel">Cancel</router-link>
          <button type="submit" class="btn btn-primary" :class="{ 'btn-appeal': rejectionReason }" :disabled="submitting">
            <span v-if="submitting" class="btn-spinner"></span>
            {{ submitting ? 'Submitting...' : rejectionReason ? 'Submit Appeal' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useExperienceStore } from '../stores/experience'

const route = useRoute()
const router = useRouter()
const store = useExperienceStore()

const categories = ref([])
const loading = ref(true)
const notFound = ref(false)
const submitting = ref(false)
const serverError = ref('')
const saveSuccess = ref(false)
const rejectionReason = ref('')

const form = reactive({
  title: '',
  description: '',
  category: '',
  location: '',
  province: '',
  price: null,
  duration_hours: null,
  max_participants: 10,
  image_url: '',
})

const errors = reactive({
  title: '',
  description: '',
  category: '',
  location: '',
  price: '',
  duration_hours: '',
  max_participants: '',
})

const provinces = [
  'Eastern Cape', 'Free State', 'Gauteng', 'KwaZulu-Natal',
  'Limpopo', 'Mpumalanga', 'Northern Cape', 'North West', 'Western Cape',
]

function validateField(field) {
  errors[field] = ''

  if (field === 'title') {
    if (!form.title.trim()) errors.title = 'Name is required'
    else if (form.title.trim().length < 3) errors.title = 'Name must be at least 3 characters'
    else if (form.title.trim().length > 120) errors.title = 'Name must be 120 characters or fewer'
  }

  if (field === 'description') {
    if (!form.description.trim()) errors.description = 'Description is required'
    else if (form.description.trim().length < 10) errors.description = 'Description must be at least 10 characters'
    else if (form.description.trim().length > 2000) errors.description = 'Description must be 2000 characters or fewer'
  }

  if (field === 'category') {
    if (!form.category) errors.category = 'Please select a category'
  }

  if (field === 'location') {
    if (!form.location.trim()) errors.location = 'Location is required'
    else if (form.location.trim().length < 2) errors.location = 'Location must be at least 2 characters'
  }

  if (field === 'price') {
    if (form.price === null || form.price === '') errors.price = 'Price is required'
    else if (form.price <= 0) errors.price = 'Price must be greater than 0'
  }

  if (field === 'duration_hours') {
    if (form.duration_hours !== null && form.duration_hours !== '' && form.duration_hours <= 0) {
      errors.duration_hours = 'Duration must be greater than 0'
    }
  }

  if (field === 'max_participants') {
    if (form.max_participants < 1) errors.max_participants = 'Must be at least 1'
    else if (form.max_participants > 100) errors.max_participants = 'Must be 100 or fewer'
  }
}

function validateAll() {
  ;['title', 'description', 'category', 'location', 'price', 'duration_hours', 'max_participants'].forEach(validateField)
  return !Object.values(errors).some(e => e)
}

async function handleSubmit() {
  serverError.value = ''
  saveSuccess.value = ''
  if (!validateAll()) return

  submitting.value = true
  try {
    const data = {
      title: form.title.trim(),
      description: form.description.trim(),
      category: form.category,
      location: form.location.trim(),
      province: form.province || null,
      price: form.price,
      duration_hours: form.duration_hours || null,
      max_participants: form.max_participants,
      image_url: form.image_url.trim() || null,
    }
    await store.updateExperience(route.params.id, data)
    saveSuccess.value = true
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (err) {
    serverError.value = err.response?.data?.detail || 'Failed to update hotspot. Please try again.'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const [exp] = await Promise.all([
      store.getExperience(route.params.id),
      store.fetchCategories(),
    ])
    categories.value = store.categories
    form.title = exp.title
    form.description = exp.description
    form.category = exp.category
    form.location = exp.location
    form.province = exp.province || ''
    form.price = exp.price
    form.duration_hours = exp.duration_hours
    form.max_participants = exp.max_participants
    form.image_url = exp.image_url || ''
    rejectionReason.value = exp.rejection_reason || ''
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.form-page {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  position: relative;
  min-height: 100vh;
  padding: 5rem 1rem 2rem;
}

.form-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 0;
}

.form-page > * {
  position: relative;
  z-index: 1;
  max-width: 700px;
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

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #ccc;
}

.spinner {
  width: 36px; height: 36px;
  border: 3px solid rgba(0,0,0,0.15);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

.hotspot-form {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 16px;
  padding: 2rem;
}

.form-group { margin-bottom: 1.25rem; }

.form-group label {
  display: block;
  font-weight: 600;
  color: #fff;
  margin-bottom: 0.4rem;
  font-size: 0.9rem;
}

.form-input {
  width: 100%;
  padding: 0.65rem 0.9rem;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 8px;
  font-size: 0.95rem;
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
}

.form-input.error {
  border-color: #C62828;
  background: #FFF5F5;
}

.textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

select.form-input {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%236D5D4E' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.field-error {
  display: block;
  color: #C62828;
  font-size: 0.8rem;
  margin-top: 0.3rem;
}

.char-count {
  text-align: right;
  font-size: 0.8rem;
  color: #999;
  margin-top: 0.2rem;
}

.char-count.warn { color: #E65100; }

.form-notice {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.75rem 1rem;
  background: #FFF8E1;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 8px;
  color: #F57F17;
  font-size: 0.85rem;
  margin-bottom: 1.25rem;
}

.alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.9rem;
}

.alert-error {
  background: #FFEBEE;
  color: #C62828;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.alert-success {
  background: #E8F5E9;
  color: #2E7D32;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.appeal-banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: rgba(198, 40, 40, 0.16);
  border: 1px solid rgba(198, 40, 40, 0.35);
  border-radius: 10px;
  padding: 16px 18px;
  margin-bottom: 1.25rem;
  color: #fff;
}

.appeal-banner svg {
  color: #EF9A9A;
  flex-shrink: 0;
  margin-top: 2px;
}

.appeal-title {
  display: block;
  font-weight: 700;
  color: #EF9A9A;
  font-family: 'Poppins', sans-serif;
  margin-bottom: 4px;
}

.appeal-reason {
  margin: 0 0 6px;
  color: #fff;
  line-height: 1.5;
  font-size: 0.92rem;
}

.appeal-hint {
  margin: 0;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.82rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.18);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0.65rem 1.4rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-primary { background: var(--accent); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--accent-hover); }

.btn-appeal { background: #E53935; }
.btn-appeal:hover:not(:disabled) { background: #B71C1C; }

.btn-cancel { background: #F5F5F5; color: #666; }
.btn-cancel:hover { background: #E0E0E0; }

.btn-spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
</style>
