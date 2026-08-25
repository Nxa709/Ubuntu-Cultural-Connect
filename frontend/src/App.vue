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
  /* Surfaces — warm cream/off-white */
  --bg-color: #F6F0E3;
  --surface: #FFFDF7;
  --surface-secondary: #F2EAD8;
  --border: rgba(186, 150, 74, 0.28);
  --border-strong: rgba(186, 150, 74, 0.45);

  /* Text — warm dark for contrast on light surfaces */
  --text-color: #2C2416;
  --text-secondary: #6B6150;
  --text-muted: #8A7F6B;
  --heading-color: #2A2112;

  /* Brand — refined amber-gold */
  /* --accent: deep readable gold for text/accents on light */
  /* --accent-fill: bright gold for button/badge fills (paired with dark text) */
  --accent: #B57912;
  --accent-hover: #96630B;
  --accent-fill: #E8A200;
  --accent-fill-hover: #D09100;
  --accent-light: rgba(232, 162, 0, 0.15);
  --accent-dark: #7A4E00;
  --accent-text: var(--accent);
  --nav-bg: #241D10;

  /* Glass tokens (now warm cream) */
  --glass-bg: #FFFDF7;
  --glass-border: #E7E0D0;

  /* Semantic */
  --success: #16a34a;
  --success-light: #dcfce7;
  --warning: #B45309;
  --warning-light: #FEF3C7;
  --error: #dc2626;
  --error-light: #fee2e2;
  --info: #3b82f6;
  --info-light: #dbeafe;

  --contrast: #ffffff;
  --overlay: rgba(40, 32, 20, 0.55);

  /* Radii & shadows */
  --radius: 12px;
  --radius-sm: 8px;
  --shadow-sm: 0 1px 2px rgba(60, 45, 20, 0.08);
  --shadow: 0 1px 3px rgba(60, 45, 20, 0.12), 0 1px 2px rgba(60, 45, 20, 0.08);
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
  color: var(--accent-text);
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
  min-width: 0;
}

main.sidebar-shifted {
  margin-left: 232px;
}

/* Keep the top-nav logo clear of the fixed sidebar */
#app.has-sidebar .navbar .nav-container {
  margin-left: 232px;
  max-width: calc(100% - 232px);
}

@media (max-width: 768px) {
  main.sidebar-shifted {
    margin-left: 0;
  }
  #app.has-sidebar .navbar .nav-container {
    margin-left: 0;
    max-width: 1200px;
  }
}

/* Global button styles */
.btn-gold {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 28px;
  border: none;
  border-radius: var(--radius-sm);
  background-color: var(--accent-fill);
  color: #1a1a1a;
  font-family: 'Poppins', sans-serif;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
  text-decoration: none;
  box-shadow: var(--shadow-sm);
}

.btn-gold:hover {
  background-color: var(--accent-fill-hover);
  color: #1a1a1a;
  box-shadow: var(--shadow);
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
  padding: 12px 28px;
  border: 1px solid rgba(255, 255, 255, 0.75);
  border-radius: var(--radius-sm);
  background: transparent;
  color: #ffffff;
  font-family: 'Poppins', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-outline-light:hover {
  background-color: var(--accent-fill);
  border-color: var(--accent-fill);
  color: #1a1a1a;
}

/* Card mixin (light) */
.glass-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  color: var(--text-color);
}

/* Light glass card for inner pages */
.glass-card-light {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  color: var(--text-color);
}

/* ============ Clean SaaS light theme (global) ============ */

/* Page roots: very light neutral background */
.experiences-page,
.preferences-page,
.plan-trip-page,
.kzn-page,
.province-page,
.detail-page,
.host-page,
.profile-page,
.review-page,
.journal-page,
.rate-page,
.login-page,
.register-page,
.form-page,
.edit-trip-page,
.owner-dash,
.ana-page,
.admin-page,
.dashboard,
.about-page {
  background: var(--bg-color) !important;
  color: var(--text-color) !important;
}

/* Neutralize old dark page overlays */
.experiences-page::before,
.experiences-page::after,
.preferences-page::before,
.plan-trip-page::before,
.plan-trip-page::after,
.kzn-page::before,
.kzn-page::after,
.province-page::before,
.province-page::after,
.detail-page::before,
.host-page::before,
.host-page::after,
.profile-page::before,
.review-page::before,
.journal-page::before,
.rate-page::before,
.login-page::before,
.register-page::before,
.form-page::before,
.edit-trip-page::before,
.owner-dash::before,
.owner-dash::after,
.ana-page::before,
.admin-page::before,
.dashboard::before,
.hero-header::before,
.about-hero::before,
.welcome::before,
.dashboard-header::before,
.ana-header::before,
.exp-header::before {
  background: transparent !important;
}

/* Page headers: image banner with dark overlay */
.hero-header,
.about-hero,
.welcome,
.dashboard-header,
.exp-header {
  background: linear-gradient(rgba(15, 23, 42, 0.25), rgba(15, 23, 42, 0.45)), url('/img/cultures/woman.jpeg') no-repeat center top / cover !important;
  background-size: cover !important;
  text-align: center !important;
  padding: 40px 20px 36px !important;
  position: relative !important;
  min-height: 340px !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
}

.ana-header {
  background: linear-gradient(rgba(15, 23, 42, 0.25), rgba(15, 23, 42, 0.45)), url('/img/cultures/woman.jpeg') no-repeat center top / cover !important;
  background-size: cover !important;
  min-height: 340px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 16px !important;
  flex-wrap: wrap !important;
  padding: 40px 28px 36px !important;
  position: relative !important;
}

.hero-header h1,
.about-hero h1,
.welcome h1,
.dashboard-header h1,
.ana-header h1,
.exp-header h1 {
  font-family: 'Poppins', sans-serif !important;
  font-size: clamp(1.9rem, 4.5vw, 2.8rem) !important;
  font-weight: 700 !important;
  color: #ffffff !important;
  max-width: 800px !important;
  margin: 0 auto 16px !important;
  line-height: 1.2 !important;
  letter-spacing: 0 !important;
}

.hero-header .accent-word,
.about-hero .accent-word,
.welcome .accent-word,
.dashboard-header .accent-word,
.ana-header .accent-word,
.exp-header .accent-word {
  font-family: 'Pacifico', cursive !important;
  font-weight: 400 !important;
  color: var(--accent) !important;
}

.hero-header p,
.about-hero p,
.welcome p,
.dashboard-header p,
.ana-header p,
.exp-header p {
  font-size: 1.02rem !important;
  color: rgba(255, 255, 255, 0.9) !important;
  max-width: 640px !important;
  margin: 0 auto !important;
  line-height: 1.65 !important;
}

/* Cards: clean white light surface */
.info-card,
.exp-card,
.rec-card,
.hotspot-card,
.profile-card,
.exp-info-card,
.trip-card,
.stat-card,
.s-card,
.kpi-card,
.trip-day-card,
.trip-overview,
.admin-review-card,
.comment-card,
.analytics-card,
.metric-card,
.form-card,
.form-section,
.rate-form,
.rating-section,
.pref-category,
.pref-option,
.sidebar-card,
.itinerary-banner,
.mini-itinerary,
.map-container,
.card,
.login-form,
.register-form,
.review-card,
.journal-card,
.stat,
.combobox-dropdown,
.quick-card,
.ov-card {
  background: var(--surface) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow: var(--shadow-sm) !important;
  color: var(--text-color) !important;
}

/* Card headings: navy */
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
.trip-card h3,
.trip-day-card h3,
.trip-day-card h4,
.trip-overview h2,
.trip-overview h3,
.admin-review-card h3,
.comment-card h3,
.analytics-card h3,
.analytics-card h4,
.metric-card h3,
.metric-lbl,
.metric-val,
.form-card h2,
.form-card h3,
.form-section h2,
.rate-form h2,
.rate-form h3,
.rating-section h2,
.card h1,
.card h2,
.card h3,
.card h4,
.card h5,
.exp-body h3,
.exp-price,
.ov-value,
.ov-label,
.ov-title,
.s-value,
.stat-label,
.stat-number,
.quick-card h3,
.stats-preview h2,
.review-name,
.reviews-card h3,
.exp-cat-badge,
.banner-title,
.mini-trip-name,
.mini-itinerary-header,
.dashboard-header h1,
.journal-title-row h3,
.review-title-row h3,
.hotspot-group-title,
.hs-rating,
.stat-lbl,
.bar-count,
.bar-label,
.summary-lbl,
.bs-value,
.bs-value.active-v,
.card-desc,
.history-cat,
.history-date,
.history-province,
.history-top-row,
.travel-history-card,
.journal-date,
.journal-meta,
.journal-title-row,
.exp-link,
.mood-btn,
.journal-form,
.review-comment,
.review-location,
.review-title-row,
.avg-label,
.avg-score,
.exp-cat,
.review-meta,
.review-score,
.appeal-hint,
.appeal-reason,
.file-title,
.day-activity,
.day-date,
.day-notes,
.action-label,
.user-name-row,
.comment-score,
.exp-title,
.subtitle,
.user-name,
.hotspot-body,
.hotspot-title-row,
.detail-label,
.detail-value,
.char-count,
.modal-subtitle,
.rejection-reason,
.pending-title,
.pending-sub,
.success-message,
.loading-state,
.option-title,
.journal-form h2,
.banner-left,
.description-full,
.price-lbl,
.summary-count,
.no-reviews,
.section,
.host-label,
.host-name,
.review-location,
.score-text,
.option-meta {
  color: var(--heading-color) !important;
}

/* Card body text: secondary gray */
.info-card p,
.info-card label,
.info-item p,
.info-item label,
.info-label,
.info-value,
.exp-desc,
.exp-details span,
.exp-rating,
.rec-body p,
.hotspot-card p,
.profile-card p,
.profile-card label,
.trip-card p,
.trip-day-card p,
.trip-overview p,
.card-desc,
.meta-item,
.admin-review-card p,
.comment-card p,
.comment-text,
.analytics-card p,
.form-card p,
.form-section p,
.form-label,
.rate-form p,
.rating-section p,
.ov-sub,
.ov-visits,
.s-label,
.quick-card p,
.detail-row,
.price-val,
.sidebar-details,
.sidebar-price,
.mini-trip-dates,
.mini-trip-entries,
.banner-meta,
.mini-itinerary-body,
.journal-meta span,
.journal-body p,
.review-comment p,
.review-location,
.score-text,
.stat-lbl,
.search-box,
.search-box input,
.combobox-chevron,
.combobox-clear,
.combobox-option,
.mood-btn,
.btn-cancel,
.history-item:hover,
.existing-comment,
.field-note,
.rec-body,
.rec-badge,
.rec-loc,
.journal-date,
.option-meta,
.review-date,
.combobox-empty {
  color: var(--text-secondary) !important;
}

.info-value.stars,
.info-value.link {
  color: var(--accent) !important;
}

/* On-cream page headings */
.dir-heading,
.login-form h1,
.register-form h1,
.login-page h1,
.register-page h1,
.auth-heading,
.desc-section h2,
.services-section h2,
.loc-section h2,
.loc-main,
.switch-text,
.auth-subtitle {
  color: var(--heading-color) !important;
}

.dir-sub,
.switch-text,
.auth-subtitle,
.loc-province,
.location-detail,
.desc-section p,
.services-list li,
.loc-section p {
  color: var(--text-secondary) !important;
}

/* Buttons: blue primary, light secondary, red destructive */
.btn-link,
.btn-primary-sm,
.rec-rate,
.btn-edit,
.btn-toggle,
.btn-rate,
.filter-btn,
.quick-btn,
.btn-view,
.btn-cancel,
.btn-approve,
.btn-details {
  background: var(--surface) !important;
  border: 1px solid var(--border-strong) !important;
  color: var(--text-color) !important;
}

.btn-link:hover,
.btn-rate:hover,
.rec-rate:hover,
.filter-btn.active,
.btn-view:hover,
.btn-edit:hover,
.btn-cancel:hover,
.mood-btn:hover,
.btn-details:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  background: var(--accent-light) !important;
}

.btn-primary-sm {
  background: var(--accent-fill) !important;
  border-color: var(--accent-fill) !important;
  color: #1a1a1a !important;
}

.btn-primary-sm:hover {
  background: var(--accent-fill-hover) !important;
  color: #1a1a1a !important;
}

.btn-delete {
  background: var(--error-light) !important;
  color: var(--error) !important;
  border-color: transparent !important;
}

.btn-delete:hover {
  background: #fecaca !important;
  color: #b91c1c !important;
}

.btn-approve {
  background: var(--success-light) !important;
  color: var(--success) !important;
}

.mood-btn {
  background: var(--surface-secondary) !important;
}

.mood-btn.active {
  background: var(--accent-light) !important;
  border-color: var(--accent) !important;
  color: var(--accent) !important;
}

/* Inputs: white, thin subtle border, gold focus */
.search-input,
.filter-select,
.role-select,
.search-box,
.search-bar,
.combobox-input-wrap,
.form-group input,
.form-group textarea,
.form-group select,
.review-textarea,
.form-input,
.input-modern {
  background: var(--glass-bg) !important;
  border: 1px solid var(--border-strong) !important;
  color: var(--text-color) !important;
}

.search-input::placeholder,
.form-group input::placeholder,
.form-group textarea::placeholder,
.combobox-input-wrap input::placeholder,
.input-modern::placeholder {
  color: var(--text-muted) !important;
}

.search-input:focus,
.filter-select:focus,
.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus,
.input-modern:focus,
.search-box:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(232, 162, 0, 0.18) !important;
}

.filter-select option,
.form-group select option,
.role-select option,
.combobox-input-wrap option {
  background: var(--glass-bg);
  color: var(--text-color);
}

.form-group label {
  color: var(--text-secondary) !important;
}

/* Status badges: tinted */
.status-badge.approved {
  background: var(--success-light) !important;
  color: var(--success) !important;
}

.status-badge.pending {
  background: var(--warning-light) !important;
  color: var(--warning) !important;
}

.status-badge.rejected {
  background: var(--error-light) !important;
  color: var(--error) !important;
}

.status-badge,
.category-tag,
.rec-badge,
.pref-tag,
.exp-cat-badge,
.exp-cat {
  color: var(--text-secondary) !important;
}

/* Host / owner cards */
.host-page .hotspot-card,
.host-page .stat-card,
.ov-card {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow: var(--shadow-sm) !important;
  color: var(--text-color) !important;
}

.ov-card.ov-most {
  border-color: rgba(232, 162, 0, 0.5) !important;
  background: var(--accent-light) !important;
}

/* Directories back buttons on light */
.kzn-page .back-btn,
.province-page .back-btn {
  background: var(--surface) !important;
  border: 1px solid var(--border-strong) !important;
  color: var(--text-color) !important;
}

.kzn-page .back-btn:hover,
.province-page .back-btn:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
}

/* Empty states */
.empty-state,
.empty-state p,
.no-results {
  color: var(--text-secondary) !important;
}

.empty-state a,
.empty-rec a {
  color: var(--accent) !important;
}

/* Plan Trip page */
.plan-trip-page .tl-start,
.plan-trip-page .tl-name,
.plan-trip-page .sum-value,
.plan-trip-page .day-detail-header h3,
.plan-trip-page .trip-title {
  color: var(--heading-color) !important;
}

.plan-trip-page .tl-end,
.plan-trip-page .tl-meta,
.plan-trip-page .trip-dest,
.plan-trip-page .sum-label,
.plan-trip-page .booking-note,
.plan-trip-page .day-cost,
.plan-trip-page .form-group label {
  color: var(--text-secondary) !important;
}

.plan-trip-page .tl-reason {
  color: var(--accent) !important;
}

.plan-trip-page .tl-meal-suggest {
  background: var(--accent-light) !important;
  border-color: rgba(232, 162, 0, 0.4) !important;
  color: var(--text-color) !important;
}

.plan-trip-page .meal-heading {
  color: var(--text-secondary) !important;
}

.plan-trip-page .tl-btn-danger {
  background: var(--error-light) !important;
  color: var(--error) !important;
}

.plan-trip-page .tag-meal {
  background: var(--accent-fill) !important;
  color: #1a1a1a !important;
}

/* Home page on light background */
.home-page .category-box {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow-sm) !important;
}

.home-page .category-name {
  color: var(--heading-color) !important;
}

.home-page .category-desc {
  color: var(--text-muted) !important;
}

.home-page .hotspot-location,
.hotspot-location {
  color: var(--text-secondary) !important;
}

.home-page .hotspot-rating,
.hotspot-rating {
  color: var(--warning) !important;
}

/* Stars / ratings: gold accent */
.star,
.rec-rating,
.exp-rating,
.avg-score,
.hs-rating,
.home-page .hotspot-rating,
.hotspot-rating {
  color: var(--accent) !important;
}

.star {
  color: #d1d5db !important;
}

.star.filled {
  color: var(--accent) !important;
}

.preferences-page .rec-cat-badge {
  background: var(--accent-fill) !important;
  color: #1a1a1a !important;
}

/* Context: keep white on image banners (detail hero, card photo overlays, flip-card fronts) */
.detail-hero-content,
.detail-hero-content h1,
.detail-hero-content .meta-item,
.detail-hero-content .back-link,
.detail-hero-content .cat-badge,
.hc-hero-content,
.hc-hero-content h3,
.hc-hero-content .hc-location,
.hc-hero-content .hc-status,
.hotspot-overlay,
.hotspot-overlay h3,
.province-overlay h3,
.rec-front,
.rec-front h3,
.rec-front .rec-loc,
.rec-cat,
.rec-rating,
.front-name-bar {
  color: #ffffff !important;
}

/* Page wrapper (light utility) */
.page-bg {
  background-color: var(--bg-color) !important;
}
.page-bg::before {
  background: transparent !important;
}

/* Input styles */.input-modern {
  width: 100%;
  padding: 14px 16px;
  border: none;
  border-radius: 12px;
  outline: none;
  background: var(--glass-bg);
  color: var(--text-color);
  font-size: 0.95rem;
  font-family: 'Roboto', sans-serif;
  transition: box-shadow 0.3s;
}

.input-modern:focus {
  box-shadow: 0 0 0 3px rgba(232, 162, 0, 0.3);
}

.input-modern::placeholder {
  color: var(--text-muted);
}

select.input-modern {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='m2 5 6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px 12px;
  padding-right: 40px;
}

/* Admin pages: restore clear approve / reject / filter controls */
.admin-page .filter-btn {
  background: #ffffff !important;
  border: 1px solid #d7dce3 !important;
  color: #495057 !important;
}

.admin-page .filter-btn:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
}

.admin-page .filter-btn.active {
  background: #16212f !important;
  border-color: #16212f !important;
  color: #ffffff !important;
}

.admin-page .btn-details {
  background: #16212f !important;
  border-color: #16212f !important;
  color: #ffffff !important;
}

.admin-page .btn-approve {
  background: #2E7D32 !important;
  border-color: #2E7D32 !important;
  color: #ffffff !important;
}

.admin-page .btn-approve:hover:not(:disabled) {
  background: #1B5E20 !important;
}

.admin-page .btn-reject {
  background: #C62828 !important;
  border-color: #C62828 !important;
  color: #ffffff !important;
}

.admin-page .btn-reject:hover:not(:disabled) {
  background: #B71C1C !important;
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
