<template>
  <div class="pj-page">
    <header class="pj-hero">
      <h1>Plan Your <span class="accent-word">Cultural</span> Journey</h1>
      <p>Tell us what you love, and we'll build a personalised day-by-day cultural itinerary from real local hotspots.</p>
      <ol class="steps">
        <li class="done"><span>1</span> Tell us what you like</li>
        <li :class="{ done: itinerary }"><span>2</span> Generate</li>
        <li :class="{ done: itinerary }"><span>3</span> Review</li>
        <li :class="{ done: itinerary }"><span>4</span> Edit</li>
        <li :class="{ done: itinerary }"><span>5</span> Save</li>
      </ol>
    </header>

    <div class="pj-layout">
      <!-- Saved journeys -->
      <aside class="pj-side" v-if="store.list.length">
        <h3><i class="bi bi-bookmark-star"></i> My saved journeys</h3>
        <button
          v-for="s in store.list"
          :key="s.id"
          class="saved-item"
          :class="{ active: itinerary && itinerary.id === s.id }"
          @click="loadItinerary(s.id)"
        >
          <span class="saved-title">{{ s.title }}</span>
          <span class="saved-meta">{{ s.num_days }} days · {{ s.activity_count }} stops · R{{ Math.round(s.estimated_cost || 0) }}</span>
        </button>
        <button class="new-btn" @click="reset"><i class="bi bi-plus-lg"></i> Plan a new journey</button>
      </aside>

      <main class="pj-main">
        <p class="pj-error" v-if="error"><i class="bi bi-exclamation-triangle"></i> {{ error }}</p>

        <template v-if="store.generating">
          <div class="pj-loading">
            <div class="spinner"></div>
            <p>Creating your personalised cultural journey…</p>
          </div>
        </template>

        <template v-else-if="!itinerary">
          <ItineraryPreferenceForm
            :loading="store.generating"
            :provinces="provinces"
            :categories="categories"
            @generate="generate"
          />
        </template>

        <template v-else>
          <ItinerarySummary :itinerary="itinerary" @regenerate="doRegenerate" @save="saveItinerary" />

          <ItineraryDay
            v-for="day in itinerary.days"
            :key="day.day_number"
            :day="day"
            @remove="removeItem"
            @replace="openReplace"
            @regenerate-day="doRegenerateDay"
            @add="openAdd"
          />

          <button class="back-to-form" @click="reset"><i class="bi bi-arrow-left"></i> Start over with new preferences</button>
        </template>
      </main>
    </div>

    <!-- Replace modal -->
    <ReplaceExperienceModal
      :visible="showReplace"
      :loading="replaceLoading"
      :alternatives="alternatives"
      :item-title="replaceTarget?.title"
      @close="showReplace = false"
      @select="chooseReplace"
      @auto="autoReplace"
    />

    <!-- Add experience modal -->
    <div v-if="showAdd" class="modal-backdrop" @click.self="showAdd = false">
      <div class="modal">
        <header class="modal-head">
          <div>
            <h3>Add an experience to Day {{ addDay }}</h3>
            <p class="modal-sub">Pick another real hotspot to slot into your day.</p>
          </div>
          <button class="close" @click="showAdd = false"><i class="bi bi-x-lg"></i></button>
        </header>
        <input v-model="addSearch" class="add-search" type="text" placeholder="Search experiences…" />
        <div class="add-list">
          <button v-for="e in addResults" :key="e.id" class="add-row" @click="addExperience(e)">
            <span class="add-img" :style="{ backgroundImage: `url(${e.image_url || '/img/cultures/Safari.jpg'})` }"></span>
            <span class="add-body">
              <span class="add-title">{{ e.title }}</span>
              <span class="add-meta">{{ e.category }}<template v-if="e.avg_rating"> · ★ {{ e.avg_rating }}</template> · R{{ Math.round(e.price || 0) }}</span>
            </span>
            <i class="bi bi-plus-circle"></i>
          </button>
          <p v-if="!addResults.length" class="modal-empty">No matching experiences.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useItineraryStore } from '../stores/itinerary'
import { useExperienceStore } from '../stores/experience'
import ItineraryPreferenceForm from '../components/ItineraryPreferenceForm.vue'
import ItinerarySummary from '../components/ItinerarySummary.vue'
import ItineraryDay from '../components/ItineraryDay.vue'
import ReplaceExperienceModal from '../components/ReplaceExperienceModal.vue'

const store = useItineraryStore()
const expStore = useExperienceStore()

const itinerary = computed(() => store.current)
const error = ref('')
const saved = ref(false)

const provinces = ref([])
const categories = ref([])

const showReplace = ref(false)
const replaceTarget = ref(null)
const alternatives = ref([])
const replaceLoading = ref(false)

const showAdd = ref(false)
const addDay = ref(1)
const addSearch = ref('')

const addResults = computed(() => {
  const q = addSearch.value.trim().toLowerCase()
  const list = expStore.experiences || []
  const used = new Set((itinerary.value?.days || []).flatMap(d => (d.items || []).map(i => i.experience_id)))
  return list
    .filter(e => !used.has(e.id))
    .filter(e => !q || e.title.toLowerCase().includes(q) || (e.category || '').toLowerCase().includes(q))
    .slice(0, 40)
})

onMounted(async () => {
  try {
    const [_, exps] = await Promise.allSettled([store.fetchList(), expStore.fetchExperiences()])
    const list = (exps.status === 'fulfilled' && exps.value) || expStore.experiences || []
    provinces.value = [...new Set(list.map(e => e.province).filter(Boolean))].sort()
    categories.value = [...new Set(list.map(e => e.category).filter(Boolean))].sort()
  } catch (e) {
    console.error(e)
  }
})

async function generate(payload) {
  error.value = ''
  try {
    await store.generate(payload)
    await store.fetchList()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Something went wrong while generating your journey.'
  }
}

async function loadItinerary(id) {
  error.value = ''
  try {
    await store.get(id)
  } catch (e) {
    error.value = 'Could not load that saved journey.'
  }
}

async function doRegenerate() {
  error.value = ''
  try {
    await store.regenerate(itinerary.value.id)
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Could not regenerate the itinerary.'
  }
}

async function doRegenerateDay(dayNumber) {
  error.value = ''
  try {
    await store.regenerateDay(itinerary.value.id, dayNumber)
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No alternatives available for that day.'
  }
}

async function removeItem(item) {
  error.value = ''
  try {
    await store.removeItem(itinerary.value.id, item.id)
    openReplaceAfterRemove(item)
  } catch (e) {
    error.value = 'Could not remove that experience.'
  }
}

// After removing, offer alternatives in the same slot.
async function openReplaceAfterRemove() {
  // lightweight: nothing forced; the day simply reflects the removal.
}

function openReplace(item) {
  replaceTarget.value = item
  alternatives.value = []
  showReplace.value = true
  replaceLoading.value = true
  store.alternatives(itinerary.value.id, item.id)
    .then(a => { alternatives.value = a })
    .catch(() => { alternatives.value = [] })
    .finally(() => { replaceLoading.value = false })
}

async function chooseReplace(alt) {
  try {
    await store.replaceItem(itinerary.value.id, replaceTarget.value.id, alt.experience_id)
    showReplace.value = false
  } catch (e) {
    error.value = 'Could not replace that experience.'
  }
}

async function autoReplace() {
  try {
    await store.replaceItem(itinerary.value.id, replaceTarget.value.id, null)
    showReplace.value = false
  } catch (e) {
    error.value = e?.response?.data?.detail || 'No alternative available.'
  }
}

function openAdd(dayNumber) {
  addDay.value = dayNumber
  addSearch.value = ''
  showAdd.value = true
}

async function addExperience(exp) {
  try {
    await store.addItem(itinerary.value.id, exp.id, addDay.value)
    showAdd.value = false
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Could not add that experience.'
  }
}

async function saveItinerary() {
  try {
    await store.update(itinerary.value.id, { title: itinerary.value.title })
    saved.value = true
    setTimeout(() => { saved.value = false }, 2000)
  } catch (e) {
    error.value = 'Could not save the itinerary.'
  }
}

function reset() {
  store.current = null
  error.value = ''
}
</script>

<style scoped>
.pj-page { min-height: 100vh; background: var(--bg-color); padding: 96px 24px 48px; }
.pj-hero { max-width: 1100px; margin: 0 auto 28px; text-align: center; }
.pj-hero h1 { font-family: 'Poppins', sans-serif; font-size: clamp(1.8rem, 4vw, 2.6rem); color: var(--heading-color); margin: 0 0 10px; }
.pj-hero .accent-word { font-family: 'Pacifico', cursive; font-weight: 400; color: var(--accent); }
.pj-hero p { color: var(--text-secondary); max-width: 640px; margin: 0 auto; }
.steps {
  list-style: none; display: flex; flex-wrap: wrap; justify-content: center; gap: 10px 18px; padding: 0; margin: 20px 0 0;
}
.steps li { display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: var(--text-muted); }
.steps li span {
  width: 22px; height: 22px; border-radius: 50%; background: var(--surface-secondary); color: var(--text-secondary);
  display: inline-flex; align-items: center; justify-content: center; font-size: 0.72rem; font-weight: 700;
}
.steps li.done { color: var(--heading-color); font-weight: 600; }
.steps li.done span { background: var(--accent-fill); color: #1a1a1a; }
.pj-layout { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 260px 1fr; gap: 24px; align-items: start; }
.pj-side {
  background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 16px;
  box-shadow: var(--shadow-sm); position: sticky; top: 96px;
}
.pj-side h3 { font-family: 'Poppins', sans-serif; font-size: 0.9rem; color: var(--heading-color); margin: 0 0 12px; display: flex; align-items: center; gap: 8px; }
.pj-side h3 i { color: var(--accent); }
.saved-item {
  display: flex; flex-direction: column; gap: 3px; width: 100%; text-align: left;
  border: 1px solid var(--border); background: var(--surface); border-radius: 10px; padding: 10px; margin-bottom: 8px; cursor: pointer; transition: all .18s;
}
.saved-item:hover, .saved-item.active { border-color: var(--accent); }
.saved-title { font-size: 0.84rem; font-weight: 600; color: var(--heading-color); }
.saved-meta { font-size: 0.72rem; color: var(--text-muted); }
.new-btn { width: 100%; border: 1px dashed var(--border-strong); background: none; border-radius: 10px; padding: 10px; color: var(--accent); font-weight: 600; cursor: pointer; }
.pj-main { min-width: 0; }
.pj-error { background: var(--error-light); color: var(--error); border-radius: 10px; padding: 12px 14px; font-size: 0.85rem; margin-bottom: 16px; }
.pj-loading { text-align: center; padding: 80px 0; color: var(--text-secondary); }
.spinner { width: 44px; height: 44px; margin: 0 auto 16px; border-radius: 50%; border: 4px solid var(--accent-light); border-top-color: var(--accent); animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.back-to-form { background: none; border: none; color: var(--accent); font-weight: 600; cursor: pointer; padding: 8px 0; }
.modal-backdrop { position: fixed; inset: 0; z-index: 1200; background: rgba(20,15,6,.55); display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal { width: 100%; max-width: 520px; max-height: 84vh; overflow-y: auto; background: var(--surface); border-radius: 16px; padding: 20px; box-shadow: var(--shadow); }
.modal-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.modal-head h3 { font-family: 'Poppins', sans-serif; font-size: 1.05rem; color: var(--heading-color); margin: 0; }
.modal-sub { font-size: 0.8rem; color: var(--text-secondary); margin: 4px 0 0; }
.close { border: none; background: var(--surface-secondary); border-radius: 8px; width: 32px; height: 32px; cursor: pointer; color: var(--text-secondary); }
.add-search { width: 100%; border: 1px solid var(--border-strong); border-radius: 10px; padding: 10px 12px; font-family: inherit; margin-bottom: 12px; }
.add-list { display: flex; flex-direction: column; gap: 8px; }
.add-row { display: flex; align-items: center; gap: 12px; width: 100%; text-align: left; border: 1px solid var(--border); background: var(--surface); border-radius: 10px; padding: 8px; cursor: pointer; }
.add-row:hover { border-color: var(--accent); }
.add-img { width: 46px; height: 46px; border-radius: 8px; background-size: cover; background-position: center; background-color: var(--surface-secondary); flex-shrink: 0; }
.add-body { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.add-title { font-size: 0.86rem; font-weight: 600; color: var(--heading-color); }
.add-meta { font-size: 0.74rem; color: var(--text-secondary); }
.add-row i { color: var(--accent); }
.modal-empty { font-size: 0.85rem; color: var(--text-muted); }
@media (max-width: 900px) {
  .pj-layout { grid-template-columns: 1fr; }
  .pj-side { position: static; }
}
</style>
