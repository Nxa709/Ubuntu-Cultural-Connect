import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('token') || null)

  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || null)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isTourist = computed(() => user.value?.role === 'tourist')
  const isBusinessOwner = computed(() => user.value?.role === 'business_owner')

  function setAuth(userData, tokenValue) {
    user.value = userData
    token.value = tokenValue
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('token', tokenValue)
  }

  function clearAuth() {
    user.value = null
    token.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  async function register(data) {
    const response = await api.post('/auth/register', data)
    return response.data
  }

  async function login(email, password) {
    const response = await api.post('/auth/login', { email, password })
    setAuth(response.data.user, response.data.access_token)
    return response.data
  }

  async function fetchMe() {
    const response = await api.get('/auth/me')
    user.value = response.data
    localStorage.setItem('user', JSON.stringify(response.data))
    return response.data
  }

  async function updateProfile(data) {
    const params = new URLSearchParams()
    if (data.full_name) params.append('full_name', data.full_name)
    if (data.phone_number) params.append('phone_number', data.phone_number)
    const response = await api.put('/auth/me', null, { params })
    user.value = response.data
    localStorage.setItem('user', JSON.stringify(response.data))
    return response.data
  }

  async function deregister() {
    await api.delete('/auth/deregister')
    clearAuth()
  }

  function logout() {
    clearAuth()
  }

  return {
    user,
    token,
    isLoggedIn,
    userRole,
    isAdmin,
    isTourist,
    isBusinessOwner,
    register,
    login,
    fetchMe,
    updateProfile,
    deregister,
    logout,
  }
})
