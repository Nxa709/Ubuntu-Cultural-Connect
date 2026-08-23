<template>
  <div class="loading-spinner" :class="`size-${size}`">
    <span class="spinner" aria-hidden="true"></span>
    <p v-if="message" class="loading-msg">{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: { type: String, default: 'Loading...' },
  size: { type: String, default: 'md' },
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 3rem 1rem;
  text-align: center;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--accent-light);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.size-sm .spinner { width: 24px; height: 24px; border-width: 3px; }
.size-md .spinner { width: 48px; height: 48px; border-width: 4px; }
.size-lg .spinner { width: 64px; height: 64px; border-width: 5px; }

.loading-msg {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-secondary);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
