<template>
  <div class="loading-spinner" :class="`size-${size}`">
    <img src="/img/Ubuntu_logo/Ubuntu-logo.png" alt="Loading..." class="logo-spin" />
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

.logo-spin {
  width: auto;
  animation: logo-spin 1.2s linear infinite;
}

.size-sm .logo-spin { height: 40px; }
.size-md .logo-spin { height: 90px; }
.size-lg .logo-spin { height: 140px; }

.loading-msg {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-secondary);
}

@keyframes logo-spin {
  to { transform: rotate(360deg); }
}
</style>
