# Spinning-Logo Loading Spinner (All Pages)

## What was changed

Every page that has an async loading state now shows a **spinning Ubuntu logo** while data is being fetched, instead of the old generic CSS spinner or a blank screen. This was the same logo loader previously added to the Experiences page, now rolled out site-wide as a reusable component.

## How it was done

1. **Created one reusable component** — `frontend/src/components/LoadingSpinner.vue`
   - Renders the logo (`/img/Ubuntu_logo/Ubuntu-logo.png`) rotating with a CSS `@keyframes` animation.
   - Accepts two props:
     - `message` (String, default `"Loading..."`) — optional text shown under the logo.
     - `size` (`sm` | `md` | `lg`, default `md`) — logo height 40px / 90px / 140px. `sm` is used for small inline section loaders, `md` for full-page loaders.

2. **Registered it globally** — `frontend/src/main.js`
   - Imported the component and called `app.component('LoadingSpinner', LoadingSpinner)` before `app.mount('#app')`. Because it is global, no view needs its own `import` — any file can use `<LoadingSpinner />` directly.

3. **Replaced every page loader with the component** — each `<div class="loading-state"><div class="spinner"></div><p>...</p></div>` block was swapped for one line:
   ```html
   <LoadingSpinner v-if="loading" message="Loading..." />
   ```

## Files changed

### New file
- `frontend/src/components/LoadingSpinner.vue` — the reusable spinning-logo loader.

### Modified files
- `frontend/src/main.js` — global registration of `LoadingSpinner`.

Views (template loader swapped to `<LoadingSpinner>`):

| File | Loading message / usage |
|---|---|
| `frontend/src/views/AdminDashboard.vue` | "Loading dashboard..." |
| `frontend/src/views/AdminManageUsers.vue` | "Loading users..." |
| `frontend/src/views/AdminRegisteredHotspots.vue` | "Loading hotspots..." |
| `frontend/src/views/AdminReviewComments.vue` | "Loading comments..." |
| `frontend/src/views/AdminReviewHotspots.vue` | "Loading hotspots..." |
| `frontend/src/views/AnalyticsPage.vue` | "Loading analytics..." |
| `frontend/src/views/DestinationDetail.vue` | "Loading..." (when item is null) |
| `frontend/src/views/EditHotspot.vue` | "Loading hotspot..." |
| `frontend/src/views/EditTripPage.vue` | "Loading trip..." |
| `frontend/src/views/ExperienceDetailPage.vue` | "Loading experience..." |
| `frontend/src/views/ExperiencesPage.vue` | "Loading experiences..." (old inline `.exp-loading` markup and styles removed) |
| `frontend/src/views/HostDashboard.vue` | "Loading your hotspots..." |
| `frontend/src/views/HostPerformance.vue` | "Loading performance data..." |
| `frontend/src/views/HostReviews.vue` | "Loading reviews..." |
| `frontend/src/views/HomePage.vue` | `size="sm"`, "Loading experiences..." (recommendations section) |
| `frontend/src/views/KznItemDetail.vue` | "Loading..." (when item is null) |
| `frontend/src/views/ProfilePage.vue` | `size="sm"` (recommendations + travel-history sections) |
| `frontend/src/views/ProvincePage.vue` | "Loading directory..." |
| `frontend/src/views/RateExperiencePage.vue` | "Loading experience..." (loader added — page previously showed blank) |
| `frontend/src/views/ReviewHistoryPage.vue` | "Loading reviews..." |
| `frontend/src/views/TravelJournalPage.vue` | "Loading journal..." |

## Where to find it

- **Component source**: `frontend/src/components/LoadingSpinner.vue`
- **Global registration**: `frontend/src/main.js` (lines 5 and 41)
- **Usage**: search any view for `<LoadingSpinner` — e.g. `grep -rn "<LoadingSpinner" frontend/src/views`

## Notes

- Small inline submit-button spinners (`.btn-spinner` in `RegisterHotspot.vue`, `EditHotspot.vue`) were intentionally left unchanged — they are button states, not page loads.
- The old `.loading-state` / `.spinner` CSS rules left inside individual views are now unused dead styles. They are harmless and can be removed later as a cleanup pass.
