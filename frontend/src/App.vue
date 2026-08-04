<template>
  <div id="app" :class="{ 'has-sidebar': showSidebar }">
    <NavBar />
    <BusinessSidebar />
    <main :class="{ 'sidebar-shifted': showSidebar }">
      <router-view />
    </main>
    <SiteFooter v-if="!showSidebar" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from './stores/auth'
import NavBar from './components/NavBar.vue'
import BusinessSidebar from './components/BusinessSidebar.vue'
import SiteFooter from './components/SiteFooter.vue'

const auth = useAuthStore()
const showSidebar = computed(() => auth.isBusinessOwner || auth.isAdmin)
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&family=Roboto:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap');

:root {
  --bg-color: #ffffff;
  --text-color: #212529;
  --heading-color: #2d465e;
  --accent: #FFB612;
  --accent-hover: #e5a310;
  --surface: #ffffff;
  --contrast: #ffffff;
  --nav-bg: rgba(0, 0, 0, 0.2);
  --glass-bg: rgba(255, 255, 255, 0.12);
  --glass-border: rgba(255, 255, 255, 0.18);
  --overlay: rgba(0, 0, 0, 0.55);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: 'Roboto', sans-serif;
  background-color: var(--bg-color);
  color: var(--text-color);
  overflow-x: hidden;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Poppins', sans-serif;
  color: var(--heading-color);
}

a {
  color: var(--accent);
  text-decoration: none;
  transition: 0.3s;
}

a:hover {
  color: var(--accent-hover);
  text-decoration: none;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

#app.has-sidebar {
  flex-direction: row;
}

main {
  flex: 1;
}

main.sidebar-shifted {
  margin-left: 220px;
}

@media (max-width: 768px) {
  main.sidebar-shifted {
    margin-left: 0;
  }
}

/* Global button styles */
.btn-gold {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 32px;
  border: none;
  border-radius: 50px;
  background-color: var(--accent);
  color: #1a1a1a;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.btn-gold:hover {
  background-color: #ffffff;
  color: #1a1a1a;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 182, 18, 0.4);
}

.btn-gold:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-outline-light {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 32px;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 50px;
  background: transparent;
  color: #ffffff;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.btn-outline-light:hover {
  background-color: var(--accent);
  border-color: var(--accent);
  color: #1a1a1a;
  transform: translateY(-2px);
}

/* Glass card mixin */
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid var(--glass-border);
  border-radius: 18px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4);
  color: #fff;
}

/* Light glass card for inner pages */
.glass-card-light {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

/* Global glass overrides for inner pages */
.info-card,
.exp-card,
.rec-card,
.hotspot-card,
.profile-card,
.exp-info-card,
.trip-card {
  background: rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
  color: #fff;
}

.stat-card {
  background: rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
  color: #fff;
}

/* Glass text overrides for inner pages */
.info-card h1,
.info-card h2,
.info-card h3,
.info-card h4,
.info-card h5,
.exp-card h3,
.rec-card h4,
.hotspot-card h3,
.profile-card h1,
.profile-card h2,
.hotspot-card h1,
.hotspot-card h2,
.exp-info-card h1,
.exp-info-card h2,
.trip-card h2,
.trip-card h3 {
  color: #fff !important;
}

.info-card p,
.info-card label,
.info-item p,
.info-item label,
.exp-desc,
.exp-details span,
.rec-body p,
.hotspot-card p,
.profile-card p,
.trip-card p,
.card-desc,
.meta-item {
  color: rgba(255, 255, 255, 0.8) !important;
}

.info-card .card-row h2,
.info-card .card-row h3,
.dashboard-header h1 {
  color: #fff !important;
}

.dashboard-header .role-label {
  color: rgba(255, 255, 255, 0.7) !important;
}

/* Glass buttons on inner pages */
.btn-link,
.btn-primary-sm,
.rec-rate,
.btn-edit,
.btn-toggle,
.btn-delete,
.btn-rate,
.filter-btn,
.quick-btn {
  color: #fff !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
}

.btn-link:hover,
.btn-rate:hover,
.rec-rate:hover,
.filter-btn.active {
  color: var(--accent) !important;
  border-color: var(--accent) !important;
}

.btn-primary-sm {
  background: var(--accent) !important;
  color: #1a1a1a !important;
}

.btn-primary-sm:hover {
  background: #fff !important;
}

/* Glass input overrides */
.search-input,
.filter-select {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: #fff !important;
}

.search-input::placeholder,
.filter-select {
  color: rgba(255, 255, 255, 0.6) !important;
}

.search-input:focus,
.filter-select:focus {
  border-color: var(--accent) !important;
}

.filter-select option {
  background: #1a1a2e;
  color: #fff;
}

/* Glass page headers */
.page-header h1,
.page-header h2 {
  color: #fff !important;
}

.page-header p {
  color: rgba(255, 255, 255, 0.7) !important;
}

/* Glass empty states */
.empty-state,
.empty-rec,
.empty-state p {
  color: rgba(255, 255, 255, 0.6) !important;
}

.empty-state a,
.empty-rec a {
  color: var(--accent) !important;
}

/* Glass badges */
.status-badge,
.category-tag,
.rec-badge,
.exp-cat-badge,
.exp-cat,
.pref-tag {
  color: #fff !important;
}

/* Glass star ratings */
.exp-rating,
.avg-score,
.avg-label,
.rec-rating {
  color: rgba(255, 255, 255, 0.8) !important;
}

/* Glass trip page specific */
.trip-day-card,
.trip-overview {
  background: rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
  color: #fff;
}

.trip-day-card h3,
.trip-day-card h4,
.trip-overview h2,
.trip-overview h3 {
  color: #fff !important;
}

.trip-day-card p,
.trip-overview p {
  color: rgba(255, 255, 255, 0.8) !important;
}

/* Glass admin pages */
.admin-page h1,
.admin-page h2,
.admin-page h3,
.admin-review-card h3,
.comment-card h3 {
  color: #fff !important;
}

.admin-page p,
.admin-review-card p,
.comment-card p,
.comment-text {
  color: rgba(255, 255, 255, 0.8) !important;
}

.admin-review-card,
.comment-card {
  background: rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  border-radius: 16px;
}

/* Glass analytics */
.analytics-card,
.metric-card {
  background: rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  border-radius: 16px;
  color: #fff;
}

.analytics-card h3,
.analytics-card h4,
.metric-card h3 {
  color: #fff !important;
}

/* Glass form pages */
.form-card,
.form-section {
  background: rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  border-radius: 16px;
}

.form-card h2,
.form-card h3,
.form-section h2 {
  color: #fff !important;
}

.form-card p,
.form-section p,
.form-label {
  color: rgba(255, 255, 255, 0.8) !important;
}

/* Glass rate page form */
.rate-form,
.rating-section {
  background: rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  border-radius: 16px;
  color: #fff;
}

.rate-form h2,
.rate-form h3,
.rating-section h2 {
  color: #fff !important;
}

/* Glass preferences */
.pref-category,
.pref-option {
  background: rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  border-radius: 12px;
  color: #fff;
}

/* Glass profile */
.profile-card {
  background: rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  border-radius: 16px;
}

.profile-card h1,
.profile-card h2 {
  color: #fff !important;
}

.profile-card p,
.profile-card label {
  color: rgba(255, 255, 255, 0.8) !important;
}

/* Glass host page */
.host-page .hotspot-card,
.host-page .stat-card {
  background: rgba(255, 255, 255, 0.12) !important;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
  color: #fff;
}

.host-page .stat-value {
  color: #fff !important;
}

.host-page .stat-label {
  color: rgba(255, 255, 255, 0.7) !important;
}

.host-page .hotspot-card h3 {
  color: #fff !important;
}

.host-page .hotspot-card p {
  color: rgba(255, 255, 255, 0.8) !important;
}

/* Background page wrapper */
.page-bg {
  min-height: 100vh;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
}

.page-bg::before {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--overlay);
  z-index: 0;
}

.page-bg > * {
  position: relative;
  z-index: 1;
}

/* Input styles */
.input-modern {
  width: 100%;
  padding: 14px 16px;
  border: none;
  border-radius: 12px;
  outline: none;
  background: rgba(255, 255, 255, 0.92);
  color: #333;
  font-size: 0.95rem;
  font-family: 'Roboto', sans-serif;
  transition: box-shadow 0.3s;
}

.input-modern:focus {
  box-shadow: 0 0 0 3px rgba(255, 182, 18, 0.3);
}

.input-modern::placeholder {
  color: #999;
}

select.input-modern {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='m2 5 6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px 12px;
  padding-right: 40px;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #bbb;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style>
