import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import { useAuthStore } from './stores/auth'

async function validateStoredToken() {
  const auth = useAuthStore()
  if (!auth.isLoggedIn) return
  try {
    await auth.fetchMe()
  } catch (e) {
    auth.clearAuth()
    if (window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
  }
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      const registrations = await navigator.serviceWorker.getRegistrations()
      for (const reg of registrations) {
        await reg.unregister()
      }
      if ('caches' in window) {
        const keys = await caches.keys()
        await Promise.all(keys.map((k) => caches.delete(k)))
      }
    } catch (e) {
      console.warn('SW cleanup skipped:', e)
    }
  })
}

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')

validateStoredToken()
