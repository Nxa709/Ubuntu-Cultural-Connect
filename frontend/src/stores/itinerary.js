import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const INTEREST_OPTIONS = [
  { value: 'traditional_food', label: 'Traditional Food', icon: 'bi-egg-fried' },
  { value: 'local_cuisine', label: 'Local Cuisine', icon: 'bi-cup-hot' },
  { value: 'arts_crafts', label: 'Arts & Crafts', icon: 'bi-palette' },
  { value: 'music_dance', label: 'Music & Dance', icon: 'bi-music-note-beamed' },
  { value: 'history_heritage', label: 'History & Heritage', icon: 'bi-bank' },
  { value: 'traditional_clothing', label: 'Traditional Clothing', icon: 'bi-bag' },
  { value: 'township_culture', label: 'Township Culture', icon: 'bi-house-door' },
  { value: 'indigenous_culture', label: 'Indigenous Culture', icon: 'bi-globe-africa' },
  { value: 'community_experiences', label: 'Community Experiences', icon: 'bi-people' },
  { value: 'festivals_events', label: 'Festivals & Events', icon: 'bi-calendar-event' },
  { value: 'nature_outdoor', label: 'Nature & Outdoor', icon: 'bi-tree' },
  { value: 'museums_historical', label: 'Museums & Historical Sites', icon: 'bi-building' },
  { value: 'local_markets', label: 'Local Markets', icon: 'bi-shop' },
  { value: 'traditional_activities', label: 'Traditional Activities', icon: 'bi-tools' },
]

export const useItineraryStore = defineStore('itinerary', () => {
  const current = ref(null)
  const list = ref([])
  const generating = ref(false)

  async function generate(payload) {
    generating.value = true
    try {
      const r = await api.post('/itinerary/generate', payload)
      current.value = r.data
      return r.data
    } finally {
      generating.value = false
    }
  }

  async function fetchList() {
    const r = await api.get('/itinerary')
    list.value = r.data
    return r.data
  }

  async function get(id) {
    const r = await api.get(`/itinerary/${id}`)
    current.value = r.data
    return r.data
  }

  async function update(id, payload) {
    const r = await api.put(`/itinerary/${id}`, payload)
    current.value = r.data
    return r.data
  }

  async function remove(id) {
    await api.delete(`/itinerary/${id}`)
    list.value = list.value.filter(i => i.id !== id)
    if (current.value && current.value.id === id) current.value = null
  }

  async function regenerate(id) {
    const r = await api.post(`/itinerary/${id}/regenerate`)
    current.value = r.data
    return r.data
  }

  async function regenerateDay(id, dayNumber) {
    const r = await api.post(`/itinerary/${id}/days/${dayNumber}/regenerate`)
    current.value = r.data
    return r.data
  }

  async function removeItem(id, itemId) {
    const r = await api.delete(`/itinerary/${id}/items/${itemId}`)
    current.value = r.data
    return r.data
  }

  async function replaceItem(id, itemId, experienceId = null) {
    const r = await api.post(`/itinerary/${id}/items/${itemId}/replace`, { experience_id: experienceId })
    current.value = r.data
    return r.data
  }

  async function alternatives(id, itemId) {
    const r = await api.get(`/itinerary/${id}/items/${itemId}/alternatives`)
    return r.data
  }

  async function addItem(id, experienceId, dayNumber) {
    const r = await api.post(`/itinerary/${id}/items`, { experience_id: experienceId, day_number: dayNumber })
    current.value = r.data
    return r.data
  }

  return {
    current, list, generating,
    generate, fetchList, get, update, remove,
    regenerate, regenerateDay, removeItem, replaceItem, alternatives, addItem,
  }
})
