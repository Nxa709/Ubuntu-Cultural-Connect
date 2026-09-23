<template>
  <div class="fp-page">
    <div class="fp-container">
      <form class="fp-form glass-card" @submit.prevent="onSubmit">
        <h1>{{ step === 'email' ? 'Forgot your password?' : 'Choose a new password' }}</h1>

        <div v-if="error" class="alert alert-error">
          <i class="bi bi-exclamation-triangle"></i> {{ error }}
        </div>
        <div v-if="info" class="alert alert-info">
          <i class="bi bi-info-circle"></i> {{ info }}
        </div>

        <template v-if="step === 'email'">
          <p class="fp-sub">Enter the email address linked to your account and we'll create a reset token.</p>
          <input class="input-modern" v-model="email" type="email" placeholder="Email Address" required />

          <button class="btn-gold" type="submit" :disabled="loading">
            {{ loading ? 'Sending…' : 'Continue' }}
          </button>
        </template>

        <template v-else>
          <p class="fp-sub">Paste the reset token you received, then choose a new password.</p>
          <input class="input-modern" v-model="resetToken" type="text" placeholder="Reset token" required />
          <div class="password-wrapper">
            <input class="input-modern" v-model="newPassword" :type="show1 ? 'text' : 'password'" placeholder="New password (min 6 characters)" required />
            <button type="button" class="pw-toggle" tabindex="-1" @click="show1 = !show1">
              <i :class="show1 ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
            </button>
          </div>
          <div class="password-wrapper">
            <input class="input-modern" v-model="confirmPassword" :type="show2 ? 'text' : 'password'" placeholder="Confirm new password" required />
            <button type="button" class="pw-toggle" tabindex="-1" @click="show2 = !show2">
              <i :class="show2 ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
            </button>
          </div>

          <button class="btn-gold" type="submit" :disabled="loading">
            {{ loading ? 'Resetting…' : 'Reset password' }}
          </button>
        </template>

        <p class="switch-text">
          <router-link to="/login"><i class="bi bi-arrow-left"></i> Back to login</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const step = ref('email')
const email = ref('')
const resetToken = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const show1 = ref(false)
const show2 = ref(false)
const loading = ref(false)
const error = ref('')
const info = ref('')

async function onSubmit() {
  error.value = ''
  info.value = ''

  if (step.value === 'email') {
    if (!email.value) return
    loading.value = true
    try {
      const res = await auth.forgotPassword(email.value)
      info.value = res.message
      if (res.reset_token) {
        resetToken.value = res.reset_token
        info.value = 'A reset token was created for your account. It is pre-filled below — choose a new password.'
      }
      step.value = 'token'
    } catch (e) {
      error.value = e.response?.data?.detail || 'Could not start the password reset.'
    } finally {
      loading.value = false
    }
    return
  }

  // reset step
  if (!resetToken.value.trim()) {
    error.value = 'Please enter your reset token.'
    return
  }
  if (newPassword.value.length < 6) {
    error.value = 'Your new password must be at least 6 characters.'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'The passwords do not match.'
    return
  }
  loading.value = true
  try {
    await auth.resetPassword(resetToken.value.trim(), newPassword.value)
    router.push('/login')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not reset your password.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fp-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: url('/img/cultures/woman.jpeg') no-repeat center top;
  background-size: cover;
  position: relative;
  padding: 80px 20px 40px;
}
.fp-page::before { content: ""; position: absolute; inset: 0; background: rgba(0, 0, 0, 0.15); z-index: 0; }
.fp-container { position: relative; z-index: 1; width: 100%; display: flex; justify-content: center; }
.fp-form {
  width: 450px; max-width: 95%; padding: 40px 35px;
  display: flex; flex-direction: column; gap: 16px;
}
.fp-form h1 { text-align: center; font-size: 24px; color: #ffffff; margin-bottom: 4px; }
.fp-sub { text-align: center; font-size: 0.85rem; color: rgba(255, 255, 255, 0.9); margin: 0; }
.alert { display: flex; align-items: center; gap: 8px; padding: 12px 16px; border-radius: 10px; font-size: 0.9rem; }
.alert-error { background: var(--error-light); color: var(--error); border: 1px solid rgba(220, 38, 38, 0.3); }
.alert-info { background: var(--accent-light); color: var(--accent-dark); border: 1px solid var(--border-strong); }
.password-wrapper { position: relative; display: flex; align-items: center; }
.password-wrapper .input-modern { padding-right: 44px; }
.pw-toggle {
  position: absolute; right: 8px; background: none; border: none; color: var(--text-secondary);
  cursor: pointer; padding: 6px; display: flex; align-items: center; border-radius: 6px;
}
.pw-toggle:hover { color: #000; }
.btn-gold { margin-top: 8px; }
.switch-text { text-align: center; font-size: 13px; color: rgba(255, 255, 255, 0.94); }
.switch-text a { color: var(--accent); font-weight: 600; }
.switch-text a:hover { text-decoration: underline; }
</style>
