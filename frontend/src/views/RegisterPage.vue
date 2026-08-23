<template>
  <div class="register-page">
    <div class="register-container">
      <form class="register-form glass-card" @submit.prevent="handleSubmit">
        <h1>Create your Account</h1>
        <p class="form-subtitle">Join Ubuntu Cultural Connect and start your journey</p>

        <div v-if="error" class="alert alert-error">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          {{ error }}
        </div>
        <div v-if="success" class="alert alert-success">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          {{ success }}
        </div>

        <input class="input-modern" v-model="form.full_name" type="text" placeholder="Full Name" required />
        <input class="input-modern" v-model="form.email" type="email" placeholder="Email Address" required />
        <input class="input-modern" v-model="form.phone_number" type="tel" placeholder="Phone Number (optional)" />
        <input class="input-modern" v-model="form.password" type="password" placeholder="Password (min 6 characters)" required minlength="6" />

        <select class="input-modern" v-model="form.role">
          <option value="tourist">I am a Tourist</option>
          <option value="business_owner">I am a Business Owner (Host)</option>
        </select>

        <button class="btn-gold" type="submit" :disabled="loading">
          {{ loading ? 'Creating account...' : 'Register' }}
        </button>

        <p class="switch-text">
          Already have an account? <router-link to="/login">Log in here</router-link>
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
  full_name: '',
  email: '',
  phone_number: '',
  password: '',
  role: 'tourist',
})

const loading = ref(false)
const error = ref('')
const success = ref('')

async function handleSubmit() {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await auth.register(form)
    success.value = 'Account created! Redirecting to login...'
    setTimeout(() => router.push('/login'), 1500)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: url('/img/cultures/woman.jpeg') no-repeat center top;
  background-size: cover;
  position: relative;
  padding: 80px 20px 40px;
}

.register-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.15);
  z-index: 0;
}

.register-container {
  position: relative;
  z-index: 1;
  width: 100%;
  display: flex;
  justify-content: center;
}

.register-form {
  width: 460px;
  max-width: 95%;
  padding: 40px 35px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.register-form h1 {
  text-align: center;
  font-size: 24px;
  color: #ffffff;
  margin-bottom: 4px;
}

.form-subtitle {
  text-align: center;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.94);
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

.alert-success {
  background: rgba(46, 125, 50, 0.2);
  color: #81c784;
  border: 1px solid rgba(46, 125, 50, 0.3);
}

.btn-gold {
  margin-top: 6px;
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
  .register-form {
    padding: 30px 25px;
  }
}
</style>
