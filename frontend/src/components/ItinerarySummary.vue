<template>
  <div class="summary">
    <div class="summary-head">
      <div>
        <h2>{{ itinerary.title || 'Your Cultural Journey' }}</h2>
        <p class="summary-sub">{{ itinerary.province || 'South Africa' }} · {{ itinerary.num_days }} day{{ itinerary.num_days > 1 ? 's' : '' }} · {{ itinerary.pace }} pace</p>
      </div>
      <div class="summary-actions">
        <button class="s-btn" @click="$emit('regenerate')"><i class="bi bi-arrow-repeat"></i> Regenerate itinerary</button>
        <button class="s-btn s-btn-primary" @click="$emit('save')"><i class="bi bi-save"></i> Save</button>
      </div>
    </div>

    <div class="summary-stats">
      <div class="stat"><span class="v">{{ itinerary.num_days }}</span><span class="l">Days</span></div>
      <div class="stat"><span class="v">{{ itinerary.activity_count }}</span><span class="l">Experiences</span></div>
      <div class="stat"><span class="v">R{{ Math.round(itinerary.estimated_cost || 0) }}</span><span class="l">Estimated cost</span></div>
      <div class="stat" v-if="itinerary.budget != null"><span class="v">R{{ Math.round(itinerary.budget) }}</span><span class="l">Budget</span></div>
      <div class="stat" v-if="itinerary.remaining_budget != null" :class="{ neg: itinerary.remaining_budget < 0 }">
        <span class="v">R{{ Math.round(itinerary.remaining_budget) }}</span><span class="l">Remaining</span>
      </div>
    </div>

    <div class="interests" v-if="interestLabels.length">
      <span class="i-chip" v-for="i in interestLabels" :key="i">{{ i }}</span>
    </div>

    <p class="summary-note" v-if="itinerary.summary">{{ itinerary.summary }}</p>
    <p class="summary-warning" v-if="itinerary.warning"><i class="bi bi-exclamation-triangle"></i> {{ itinerary.warning }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { INTEREST_OPTIONS } from '../stores/itinerary'

const props = defineProps({
  itinerary: { type: Object, required: true },
})
defineEmits(['regenerate', 'save'])

const interestLabels = computed(() => {
  const map = Object.fromEntries(INTEREST_OPTIONS.map(o => [o.value, o.label]))
  return (props.itinerary.interests || []).map(i => map[i] || i)
})
</script>

<style scoped>
.summary {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 24px;
}
.summary-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
.summary-head h2 { font-family: 'Poppins', sans-serif; font-size: 1.35rem; color: var(--heading-color); margin: 0 0 4px; }
.summary-sub { font-size: 0.85rem; color: var(--text-secondary); margin: 0; text-transform: capitalize; }
.summary-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.s-btn {
  display: inline-flex; align-items: center; gap: 7px;
  border: 1px solid var(--border-strong); background: var(--surface); color: var(--text-secondary);
  border-radius: 10px; padding: 9px 14px; font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: all .18s;
}
.s-btn:hover { border-color: var(--accent); color: var(--accent); }
.s-btn-primary { background: var(--accent-fill); border-color: var(--accent-fill); color: #1a1a1a; }
.s-btn-primary:hover { background: var(--accent-fill-hover); border-color: var(--accent-fill-hover); color: #1a1a1a; }
.summary-stats { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 16px; }
.stat {
  background: var(--surface-secondary);
  border-radius: 12px;
  padding: 10px 16px;
  min-width: 96px;
}
.stat.neg { background: var(--error-light); }
.stat .v { display: block; font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 1.1rem; color: var(--heading-color); }
.stat.neg .v { color: var(--error); }
.stat .l { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: .04em; }
.interests { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.i-chip { font-size: 0.74rem; background: var(--accent-light); color: var(--accent-dark); border-radius: 50px; padding: 4px 12px; font-weight: 600; }
.summary-note { font-size: 0.85rem; color: var(--text-secondary); margin: 14px 0 0; line-height: 1.6; }
.summary-warning { font-size: 0.82rem; color: #8a6d1a; background: var(--warning-light, #fff5e0); border-radius: 10px; padding: 10px 12px; margin: 12px 0 0; }
</style>
