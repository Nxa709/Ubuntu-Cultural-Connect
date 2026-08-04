import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'https://ubuntu-cultural-connect-production.up.railway.app/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isNotifPoll = error.config && error.config.url && error.config.url.includes('/notifications')
    if (error.response && error.response.status === 401 && !isNotifPoll) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
