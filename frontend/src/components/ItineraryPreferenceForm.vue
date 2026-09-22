<template>
  <form class="pref-form" @submit.prevent="submit">
    <section class="pf-section">
      <h3><i class="bi bi-geo-alt-fill"></i> Trip information</h3>
      <div class="pf-grid">
        <label class="field">
          <span>Province</span>
          <select v-model="form.province">
            <option value="">Any province</option>
            <option v-for="p in provinces" :key="p" :value="p">{{ p }}</option>
          </select>
        </label>
        <label class="field">
          <span>Number of days</span>
          <input type="number" min="1" max="14" v-model.number="form.num_days" />
        </label>
        <label class="field">
          <span>Approximate budget (R, optional)</span>
          <input type="number" min="0" step="50" v-model.number="form.budget" placeholder="e.g. 1500" />
        </label>
        <div class="field">
          <span>Travel pace</span>
          <div class="segmented">
            <button
              type="button"
              v-for="p in paces"
              :key="p.value"
              :class="{ active: form.pace === p.value }"
              @click="form.pace = p.value"
            >{{ p.label }}</button>
          </div>
        </div>
      </div>
    </section>

    <section class="pf-section">
      <h3><i class="bi bi-heart-fill"></i> What are you into?</h3>
      <p class="pf-hint">Pick a few cultural interests — we'll match real local hotspots to them.</p>
      <div class="chips">
        <button
          type="button"
          v-for="i in INTEREST_OPTIONS"
          :key="i.value"
          class="chip"
          :class="{ active: form.interests.includes(i.value) }"
          @click="toggleInterest(i.value)"
        >
          <i :class="['bi', i.icon]"></i> {{ i.label }}
        </button>
      </div>
    </section>

    <section class="pf-section">
      <h3><i class="bi bi-sliders"></i> Fine-tune</h3>
      <div class="pf-grid">
        <label class="field">
          <span>Preferred experience type</span>
          <select v-model="form.experience_type">
            <option value="any">Any type</option>
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </label>
        <label class="field">
          <span>Minimum rating</span>
          <select v-model.number="form.min_rating">
            <option :value="0">Any rating</option>
            <option :value="3">3.0+</option>
            <option :value="3.5">3.5+</option>
            <option :value="4">4.0+</option>
            <option :value="4.5">4.5+</option>
          </select>
        </label>
        <div class="field">
          <span>Budget preference</span>
          <div class="segmented">
            <button type="button" v-for="b in budgets" :key="b.value"
              :class="{ active: form.budget_preference === b.value }"
              @click="form.budget_preference = b.value">{{ b.label }}</button>
          </div>
        </div>
      </div>
    </section>

    <button class="generate-btn" type="submit" :disabled="loading">
      <i class="bi" :class="loading ? 'bi-hourglass-split' : 'bi-stars'"></i>
      {{ loading ? 'Creating your journey…' : 'Generate my cultural journey' }}
    </button>
  </form>
</template>

<script setup>
import { reactive } from 'vue'
import { INTEREST_OPTIONS } from '../stores/itinerary'

const props = defineProps({
  loading: Boolean,
  provinces: { type: Array, default: () => [] },
  categories: { type: Array, default: () => [] },
})
const emit = defineEmits(['generate'])

const paces = [
  { value: 'relaxed', label: 'Relaxed' },
  { value: 'balanced', label: 'Balanced' },
  { value: 'packed', label: 'Packed' },
]
const budgets = [
  { value: 'budget', label: 'Budget' },
  { value: 'mid', label: 'Mid-range' },
  { value: 'luxury', label: 'Luxury' },
]

const form = reactive({
  province: '',
  num_days: 2,
  budget: null,
  pace: 'balanced',
  interests: ['traditional_food', 'history_heritage'],
  experience_type: 'any',
  min_rating: 0,
  budget_preference: 'mid',
})

function toggleInterest(v) {
  const i = form.interests.indexOf(v)
  if (i === -1) form.interests.push(v)
  else form.interests.splice(i, 1)
}

function submit() {
  emit('generate', {
    province: form.province || null,
    num_days: Math.min(14, Math.max(1, Number(form.num_days) || 1)),
    budget: form.budget ? Number(form.budget) : null,
    pace: form.pace,
    interests: [...form.interests],
    experience_type: form.experience_type,
    min_rating: Number(form.min_rating) || 0,
    budget_preference: form.budget_preference,
  })
}
</script>

<style scoped>
.pref-form { display: flex; flex-direction: column; gap: 18px; }
.pf-section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 18px;
  box-shadow: var(--shadow-sm);
}
.pf-section h3 {
  font-family: 'Poppins', sans-serif; font-size: 1rem; color: var(--heading-color); margin: 0 0 14px;
  display: flex; align-items: center; gap: 8px;
}
.pf-section h3 i { color: var(--accent); }
.pf-hint { font-size: 0.8rem; color: var(--text-muted); margin: -8px 0 14px; }
.pf-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field > span { font-size: 0.76rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: .03em; }
.field select, .field input {
  border: 1px solid var(--border-strong); border-radius: 10px; padding: 10px 12px;
  font-family: inherit; font-size: 0.88rem; background: var(--surface); color: var(--text-color);
}
.segmented { display: flex; gap: 6px; }
.segmented button {
  flex: 1; border: 1px solid var(--border-strong); background: var(--surface); color: var(--text-secondary);
  border-radius: 10px; padding: 9px 6px; font-size: 0.8rem; cursor: pointer; transition: all .18s;
}
.segmented button.active { background: var(--accent-fill); border-color: var(--accent-fill); color: #1a1a1a; font-weight: 600; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  display: inline-flex; align-items: center; gap: 6px;
  border: 1px solid var(--border-strong); background: var(--surface); color: var(--text-secondary);
  border-radius: 50px; padding: 8px 14px; font-size: 0.8rem; cursor: pointer; transition: all .18s;
}
.chip i { color: var(--accent); }
.chip.active { background: var(--accent-fill); border-color: var(--accent-fill); color: #1a1a1a; font-weight: 600; }
.chip.active i { color: #1a1a1a; }
.generate-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 10px;
  background: var(--accent-fill); color: #1a1a1a; border: none; border-radius: 12px;
  padding: 15px 20px; font-family: 'Poppins', sans-serif; font-size: 1rem; font-weight: 700;
  cursor: pointer; transition: all .2s;
}
.generate-btn:hover:not(:disabled) { background: var(--accent-fill-hover); }
.generate-btn:disabled { opacity: .7; cursor: wait; }
@media (max-width: 640px) {
  .pf-grid { grid-template-columns: 1fr; }
}
</style>
