<template>
  <div class="login-page">
    <div class="login-container">
      <form class="login-form glass-card" @submit.prevent="handleSubmit">
        <h1>Login to your Account</h1>

        <div v-if="error" class="alert alert-error">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          {{ error }}
        </div>

        <input
          class="input-modern"
          v-model="form.email"
          type="email"
          placeholder="Email Address"
          required
        />
        <div class="password-wrapper">
          <input
            class="input-modern"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Password"
            required
          />
          <button type="button" class="pw-toggle" @click="showPassword = !showPassword" tabindex="-1">
            <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
              <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
              <line x1="1" y1="1" x2="23" y2="23"/>
              <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/>
            </svg>
          </button>
        </div>

        <button class="btn-gold" type="submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>

        <p class="switch-text">
          Don't have an account? <router-link to="/register">Register here</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({
  email: '',
  password: '',
})

const loading = ref(false)
const showPassword = ref(false)
const error = ref('')

async function handleSubmit() {
  loading.value = true
  error.value = ''

  try {
    await auth.login(form.email, form.password)
    router.push(auth.isTourist ? '/' : auth.isBusinessOwner ? '/my-hotspots' : '/admin')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: url('/img/cultures/woman.jpeg') no-repeat center top;
  background-size: cover;
  position: relative;
  padding: 80px 20px 40px;
}

.login-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.15);
  z-index: 0;
}

.login-container {
  position: relative;
  z-index: 1;
  width: 100%;
  display: flex;
  justify-content: center;
}

.login-form {
  width: 450px;
  max-width: 95%;
  padding: 40px 35px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-form h1 {
  text-align: center;
  font-size: 24px;
  color: #ffffff;
  margin-bottom: 8px;
}

.alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.9rem;
}

.alert-error {
  background: rgba(255, 77, 77, 0.2);
  color: #ff6b6b;
  border: 1px solid rgba(255, 77, 77, 0.3);
}

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-wrapper .input-modern {
  padding-right: 44px;
}

.pw-toggle {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  color: #555;
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  border-radius: 6px;
  transition: color 0.2s;
}

.pw-toggle:hover {
  color: #000;
}

.btn-gold {
  margin-top: 8px;
}

.switch-text {
  text-align: center;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.94);
}

.switch-text a {
  color: var(--accent);
  font-weight: 600;
}

.switch-text a:hover {
  text-decoration: underline;
}

@media (max-width: 600px) {
  .login-form {
    padding: 30px 25px;
  }
}
</style>
