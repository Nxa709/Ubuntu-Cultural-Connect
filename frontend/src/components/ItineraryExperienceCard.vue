<template>
  <div class="itin-item" :class="{ 'itin-break': item.item_type === 'break' || !item.experience_id }">
    <div class="itin-time">
      <span class="t-start">{{ item.start_time || '—' }}</span>
      <span class="t-end">{{ item.end_time }}</span>
    </div>

    <template v-if="item.experience_id">
      <div class="itin-img" :style="{ backgroundImage: `url(${item.image_url || fallback})` }"></div>
      <div class="itin-body">
        <div class="itin-top">
          <h3>{{ item.title }}</h3>
          <span class="itin-cat">{{ item.category }}</span>
        </div>
        <p class="itin-desc" v-if="item.description">{{ item.description }}</p>
        <div class="itin-meta">
          <span v-if="item.avg_rating"><i class="bi bi-star-fill"></i> {{ item.avg_rating.toFixed(1) }}</span>
          <span><i class="bi bi-cash"></i> R{{ Math.round(item.price || 0) }}</span>
          <span v-if="item.duration_hours"><i class="bi bi-clock"></i> {{ item.duration_hours }}h</span>
          <span v-if="item.location"><i class="bi bi-geo-alt-fill"></i> {{ item.location }}</span>
        </div>
      </div>
      <div class="itin-actions">
        <button class="ibtn" title="Replace" @click="$emit('replace', item)"><i class="bi bi-arrow-repeat"></i></button>
        <button class="ibtn ibtn-danger" title="Remove" @click="$emit('remove', item)"><i class="bi bi-trash"></i></button>
      </div>
    </template>

    <template v-else>
      <div class="itin-break-icon"><i class="bi bi-cup-hot"></i></div>
      <div class="itin-body">
        <h3>{{ item.title || 'Break' }}</h3>
      </div>
    </template>
  </div>
</template>

<script setup>
defineProps({
  item: { type: Object, required: true },
})
defineEmits(['remove', 'replace'])
const fallback = '/img/cultures/Safari.jpg'
</script>

<style scoped>
.itin-item {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px;
  box-shadow: var(--shadow-sm);
}
.itin-break {
  background: var(--surface-secondary);
  border-style: dashed;
}
.itin-time {
  display: flex;
  flex-direction: column;
  min-width: 58px;
  text-align: right;
}
.t-start { font-weight: 700; color: var(--heading-color); font-family: 'Poppins', sans-serif; }
.t-end { font-size: 0.72rem; color: var(--text-muted); }
.itin-img {
  width: 84px;
  height: 84px;
  border-radius: 10px;
  background-size: cover;
  background-position: center;
  background-color: var(--surface-secondary);
  flex-shrink: 0;
}
.itin-body { flex: 1; min-width: 0; }
.itin-top { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.itin-top h3 { font-family: 'Poppins', sans-serif; font-size: 1rem; font-weight: 600; color: var(--heading-color); margin: 0; }
.itin-cat {
  font-size: 0.68rem;
  font-weight: 600;
  color: #1a1a1a;
  background: var(--accent-fill);
  border-radius: 50px;
  padding: 2px 10px;
}
.itin-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin: 6px 0 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.itin-meta { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px; font-size: 0.78rem; color: var(--text-secondary); }
.itin-meta i { color: var(--accent); margin-right: 3px; }
.itin-reason { margin: 8px 0 0; font-size: 0.76rem; color: var(--accent-dark); }
.itin-reason i { margin-right: 4px; }
.itin-actions { display: flex; flex-direction: column; gap: 8px; }
.ibtn {
  width: 32px; height: 32px; border-radius: 8px; cursor: pointer;
  border: 1px solid var(--border); background: var(--surface); color: var(--text-secondary);
  display: flex; align-items: center; justify-content: center; transition: all .18s;
}
.ibtn:hover { border-color: var(--accent); color: var(--accent); }
.ibtn-danger:hover { border-color: var(--error); color: var(--error); }
.itin-break-icon {
  width: 42px; height: 42px; border-radius: 10px; background: var(--accent-light);
  color: var(--accent-dark); display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
</style>
