import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useExperienceStore = defineStore('experience', () => {
  const experiences = ref([])
  const myExperiences = ref([])
  const recommended = ref([])
  const preferences = ref([])
  const myTrips = ref([])
  const categories = ref([])
  const provinces = ref([])
  const ownerStats = ref(null)
  const myJournals = ref([])
  const myReviews = ref([])
  const hostReviews = ref([])
  const hostPerformance = ref([])
  const travelHistory = ref([])

  async function fetchCategories() {
    const r = await api.get('/experiences/categories')
    categories.value = r.data
  }

  async function fetchProvinces() {
    const r = await api.get('/experiences/provinces')
    provinces.value = r.data
  }

  async function fetchExperiences(params = {}) {
    const r = await api.get('/experiences/', { params })
    experiences.value = r.data
  }

  async function getExperience(id) {
    const r = await api.get(`/experiences/${id}`)
    return r.data
  }

  async function createExperience(data) {
    const r = await api.post('/experiences/', data)
    experiences.value.push(r.data)
    return r.data
  }

  async function uploadImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    const r = await api.post('/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return r.data.url
  }

  async function updateExperience(id, data) {
    const r = await api.put(`/experiences/${id}`, data)
    const idx = myExperiences.value.findIndex(e => e.id === id)
    if (idx !== -1) myExperiences.value[idx] = r.data
    return r.data
  }

  async function deleteExperience(id) {
    await api.delete(`/experiences/${id}`)
    myExperiences.value = myExperiences.value.filter(e => e.id !== id)
  }

  async function toggleActive(id) {
    const r = await api.put(`/experiences/${id}/toggle-active`)
    const exp = myExperiences.value.find(e => e.id === id)
    if (exp) exp.is_active = r.data.is_active
    return r.data
  }

  async function fetchMyExperiences() {
    const r = await api.get('/experiences/mine')
    myExperiences.value = r.data
    return r.data
  }

  async function fetchOwnerStats() {
    const r = await api.get('/experiences/owner/stats')
    ownerStats.value = r.data
    return r.data
  }

  async function fetchPreferences() {
    const r = await api.get('/experiences/prefs/me')
    preferences.value = r.data.categories
  }

  async function savePreferences(cats) {
    const r = await api.post('/experiences/prefs', { categories: cats })
    preferences.value = r.data.categories
  }

  async function fetchRecommended() {
    const r = await api.get('/experiences/recommended')
    recommended.value = r.data
  }

  async function fetchMyTrips() {
    const r = await api.get('/experiences/trips/me')
    myTrips.value = r.data
  }

  async function createTrip(data) {
    const r = await api.post('/experiences/trips', data)
    myTrips.value.push(r.data)
    return r.data
  }

  async function deleteTrip(id) {
    await api.delete(`/experiences/trips/${id}`)
    myTrips.value = myTrips.value.filter(t => t.id !== id)
  }

  async function updateTrip(id, data) {
    const r = await api.put(`/experiences/trips/${id}`, data)
    const idx = myTrips.value.findIndex(t => t.id === id)
    if (idx !== -1) myTrips.value[idx] = r.data
    return r.data
  }

  async function addTripDay(tripId, data) {
    const r = await api.post(`/experiences/trips/${tripId}/days`, data)
    return r.data
  }

  async function updateTripDay(tripId, dayId, data) {
    const r = await api.put(`/experiences/trips/${tripId}/days/${dayId}`, data)
    return r.data
  }

  async function deleteTripDay(tripId, dayId) {
    await api.delete(`/experiences/trips/${tripId}/days/${dayId}`)
  }

  async function getItinerary(tripId) {
    const r = await api.get(`/experiences/trips/${tripId}/itinerary`)
    return r.data
  }

  async function getRatings(expId) {
    const r = await api.get(`/experiences/${expId}/ratings`)
    return r.data
  }

  async function submitRating(expId, data) {
    const r = await api.post(`/experiences/${expId}/ratings`, data)
    return r.data
  }

  async function getAnalytics(range = 'all') {
    const r = await api.get('/experiences/analytics/overview', { params: { range } })
    return r.data
  }

  async function getHotspotAnalytics(id) {
    const r = await api.get(`/experiences/${id}/analytics`)
    return r.data
  }

  async function recordView(id) {
    try {
      await api.post(`/experiences/${id}/view`)
    } catch (e) { /* tracking is best-effort */ }
  }

  async function recordContact(id) {
    const r = await api.post(`/experiences/${id}/contact`)
    return r.data
  }

  async function fetchMyJournals() {
    const r = await api.get('/experiences/journals/mine')
    myJournals.value = r.data
    return r.data
  }

  async function createJournal(data) {
    const r = await api.post('/experiences/journals', data)
    myJournals.value.unshift(r.data)
    return r.data
  }

  async function updateJournal(id, data) {
    const r = await api.put(`/experiences/journals/${id}`, data)
    const idx = myJournals.value.findIndex(j => j.id === id)
    if (idx !== -1) myJournals.value[idx] = r.data
    return r.data
  }

  async function deleteJournal(id) {
    await api.delete(`/experiences/journals/${id}`)
    myJournals.value = myJournals.value.filter(j => j.id !== id)
  }

  async function fetchMyReviews() {
    const r = await api.get('/experiences/reviews/mine')
    myReviews.value = r.data
    return r.data
  }

  async function fetchTravelHistory() {
    const r = await api.get('/experiences/travel-history')
    travelHistory.value = r.data
    return r.data
  }

  async function fetchHostReviews() {
    const r = await api.get('/experiences/owner/reviews')
    hostReviews.value = r.data
    return r.data
  }

  async function fetchHostPerformance() {
    const r = await api.get('/experiences/owner/performance')
    hostPerformance.value = r.data
    return r.data
  }

  // Add experience to trip plan - creates new trip or adds to existing
  async function addExperienceToTrip(experienceId, tripData = {}) {
    const r = await api.post(`/experiences/trips/add-experience/${experienceId}`, tripData)
    return r.data
  }

  return {
    experiences, myExperiences, recommended, preferences, myTrips, categories, provinces, ownerStats,
    myJournals, myReviews, hostReviews, hostPerformance, travelHistory,
    fetchCategories, fetchProvinces, fetchExperiences, getExperience, createExperience,
    uploadImage, updateExperience, deleteExperience, toggleActive, fetchMyExperiences, fetchOwnerStats,
    fetchPreferences, savePreferences, fetchRecommended,
    fetchMyTrips, createTrip, deleteTrip, updateTrip, addTripDay, updateTripDay, deleteTripDay, getItinerary, addExperienceToTrip,
    getRatings, submitRating, getAnalytics, getHotspotAnalytics, recordView, recordContact,
    fetchMyJournals, createJournal, updateJournal, deleteJournal, fetchMyReviews,
    fetchHostReviews, fetchHostPerformance, fetchTravelHistory,
  }
})
