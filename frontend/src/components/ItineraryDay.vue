<template>
  <section class="day-block">
    <header class="day-head">
      <div class="day-title">
        <span class="day-badge">Day {{ day.day_number }}</span>
        <span class="day-sub">{{ day.items.filter(i => i.experience_id).length }} experiences · R{{ Math.round(day.estimated_cost || 0) }}</span>
      </div>
      <div class="day-tools">
        <button class="tool-btn" @click="$emit('add', day.day_number)"><i class="bi bi-plus-lg"></i> Add</button>
        <button class="tool-btn" @click="$emit('regenerate-day', day.day_number)"><i class="bi bi-arrow-repeat"></i> Regenerate day</button>
      </div>
    </header>
    <div class="day-items">
      <ItineraryExperienceCard
        v-for="item in sortedItems"
        :key="item.id"
        :item="item"
        @remove="$emit('remove', item)"
        @replace="$emit('replace', item)"
      />
      <p v-if="!day.items.length" class="day-empty">No experiences scheduled for this day yet.</p>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import ItineraryExperienceCard from './ItineraryExperienceCard.vue'

const props = defineProps({
  day: { type: Object, required: true },
})
defineEmits(['remove', 'replace', 'regenerate-day', 'add'])

const sortedItems = computed(() =>
  [...(props.day.items || [])].sort((a, b) => (a.start_time || '').localeCompare(b.start_time || ''))
)
</script>

<style scoped>
.day-block { margin-bottom: 28px; }
.day-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding-bottom: 10px;
  margin-bottom: 14px;
  border-bottom: 2px solid var(--border);
}
.day-title { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.day-badge {
  font-family: 'Poppins', sans-serif;
  font-weight: 700;
  font-size: 1.05rem;
  color: var(--heading-color);
}
.day-sub { font-size: 0.8rem; color: var(--text-muted); }
.day-tools { display: flex; gap: 8px; }
.tool-btn {
  display: inline-flex; align-items: center; gap: 6px;
  border: 1px solid var(--border); background: var(--surface); color: var(--text-secondary);
  border-radius: 8px; padding: 7px 12px; font-size: 0.78rem; cursor: pointer; transition: all .18s;
}
.tool-btn:hover { border-color: var(--accent); color: var(--accent); }
.day-items { display: flex; flex-direction: column; gap: 12px; }
.day-empty { font-size: 0.85rem; color: var(--text-muted); }
</style>
