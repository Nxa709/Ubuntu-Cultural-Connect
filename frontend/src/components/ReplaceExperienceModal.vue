<template>
  <div v-if="visible" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal">
      <header class="modal-head">
        <div>
          <h3>Replace experience</h3>
          <p v-if="itemTitle" class="modal-sub">Finding alternatives for “{{ itemTitle }}”</p>
        </div>
        <button class="close" @click="$emit('close')"><i class="bi bi-x-lg"></i></button>
      </header>

      <div v-if="loading" class="modal-loading">
        <div class="spinner"></div>
        <p>Finding suitable alternatives…</p>
      </div>

      <div v-else class="alt-list">
        <button class="alt" @click="$emit('auto')">
          <span class="alt-auto"><i class="bi bi-magic"></i> Auto-pick the best match</span>
        </button>
        <button
          v-for="a in alternatives"
          :key="a.experience_id"
          class="alt"
          @click="$emit('select', a)"
        >
          <span class="alt-img" :style="{ backgroundImage: `url(${a.image_url || fallback})` }"></span>
          <span class="alt-body">
            <span class="alt-title">{{ a.title }}</span>
            <span class="alt-meta">
              {{ a.category }}
              <template v-if="a.avg_rating"> · <i class="bi bi-star-fill"></i> {{ a.avg_rating.toFixed(1) }}</template>
              · R{{ Math.round(a.price || 0) }}
            </span>
            <span class="alt-reason" v-if="a.reason">{{ a.reason }}</span>
          </span>
          <span class="alt-score">{{ Math.round(a.score) }}</span>
        </button>
        <p v-if="!alternatives.length" class="modal-empty">
          No alternatives match your preferences right now. Try regenerating or removing this experience.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: Boolean,
  loading: Boolean,
  alternatives: { type: Array, default: () => [] },
  itemTitle: String,
})
defineEmits(['close', 'select', 'auto'])
const fallback = '/img/cultures/Safari.jpg'
</script>

<style scoped>
.modal-backdrop {
  position: fixed; inset: 0; z-index: 1200;
  background: rgba(20, 15, 6, 0.55);
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.modal {
  width: 100%; max-width: 560px; max-height: 84vh; overflow-y: auto;
  background: var(--surface); border-radius: 16px; padding: 20px;
  box-shadow: var(--shadow);
}
.modal-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
.modal-head h3 { font-family: 'Poppins', sans-serif; font-size: 1.1rem; color: var(--heading-color); margin: 0; }
.modal-sub { font-size: 0.8rem; color: var(--text-secondary); margin: 4px 0 0; }
.close { border: none; background: var(--surface-secondary); border-radius: 8px; width: 32px; height: 32px; cursor: pointer; color: var(--text-secondary); }
.alt-list { display: flex; flex-direction: column; gap: 10px; }
.alt {
  display: flex; align-items: center; gap: 12px; width: 100%; text-align: left;
  border: 1px solid var(--border); background: var(--surface); border-radius: 12px;
  padding: 10px; cursor: pointer; transition: all .18s;
}
.alt:hover { border-color: var(--accent); box-shadow: var(--shadow-sm); }
.alt-auto { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; padding: 12px; font-weight: 600; color: #1a1a1a; }
.alt-img { width: 54px; height: 54px; border-radius: 9px; background-size: cover; background-position: center; background-color: var(--surface-secondary); flex-shrink: 0; }
.alt-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px; }
.alt-title { font-weight: 600; color: var(--heading-color); font-size: 0.9rem; }
.alt-meta { font-size: 0.76rem; color: var(--text-secondary); }
.alt-reason { font-size: 0.72rem; color: var(--accent-dark); }
.alt-score { font-family: 'Poppins', sans-serif; font-weight: 700; color: var(--accent); font-size: 0.9rem; }
.modal-loading { text-align: center; padding: 34px 0; color: var(--text-secondary); }
.spinner {
  width: 34px; height: 34px; margin: 0 auto 12px; border-radius: 50%;
  border: 3px solid var(--accent-light); border-top-color: var(--accent);
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.modal-empty { font-size: 0.85rem; color: var(--text-muted); }
</style>
