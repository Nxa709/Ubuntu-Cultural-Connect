import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import HomePage from '../views/HomePage.vue'
import AboutPage from '../views/AboutPage.vue'
import LoginPage from '../views/LoginPage.vue'
import RegisterPage from '../views/RegisterPage.vue'

import ProfilePage from '../views/ProfilePage.vue'
import PreferencesPage from '../views/PreferencesPage.vue'
import ExperiencesPage from '../views/ExperiencesPage.vue'
import PlanTripPage from '../views/PlanTripPage.vue'
import RateExperiencePage from '../views/RateExperiencePage.vue'
import AnalyticsPage from '../views/AnalyticsPage.vue'
import AdminReviewComments from '../views/AdminReviewComments.vue'
import AdminReviewHotspots from '../views/AdminReviewHotspots.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import AdminRegisteredHotspots from '../views/AdminRegisteredHotspots.vue'
import AdminManageUsers from '../views/AdminManageUsers.vue'
import HostDashboard from '../views/HostDashboard.vue'
import OwnerDashboard from '../views/OwnerDashboard.vue'
import RegisterHotspot from '../views/RegisterHotspot.vue'
import EditHotspot from '../views/EditHotspot.vue'
import HostReviews from '../views/HostReviews.vue'
import HostPerformance from '../views/HostPerformance.vue'
import EditTripPage from '../views/EditTripPage.vue'
import TravelJournalPage from '../views/TravelJournalPage.vue'
import ReviewHistoryPage from '../views/ReviewHistoryPage.vue'
import ExperienceDetailPage from '../views/ExperienceDetailPage.vue'
import ProvincePage from '../views/ProvincePage.vue'
import DestinationDetail from '../views/DestinationDetail.vue'
import KznDirectoryPage from '../views/KznDirectoryPage.vue'
import KznItemDetail from '../views/KznItemDetail.vue'
import HotspotAnalytics from '../views/HotspotAnalytics.vue'
import OverallAnalytics from '../views/OverallAnalytics.vue'

const routes = [
  { path: '/', name: 'Home', component: HomePage },
  { path: '/about', name: 'About', component: AboutPage },
  { path: '/login', name: 'Login', component: LoginPage, meta: { guest: true } },
  { path: '/register', name: 'Register', component: RegisterPage, meta: { guest: true } },
  { path: '/profile', name: 'Profile', component: ProfilePage, meta: { requiresAuth: true } },
  { path: '/preferences', name: 'Preferences', component: PreferencesPage, meta: { requiresAuth: true } },
  { path: '/experiences', name: 'Experiences', component: ExperiencesPage, meta: { requiresAuth: true } },
  { path: '/experience/:id', name: 'ExperienceDetail', component: ExperienceDetailPage, meta: { requiresAuth: true } },
  { path: '/plan-trip', name: 'PlanTrip', component: PlanTripPage, meta: { requiresAuth: true } },
  { path: '/rate/:id', name: 'RateExperience', component: RateExperiencePage, meta: { requiresAuth: true } },
  { path: '/analytics', name: 'Analytics', component: AnalyticsPage, meta: { requiresAuth: true } },
  { path: '/overall-analytics', name: 'OverallAnalytics', component: OverallAnalytics, meta: { requiresAuth: true } },
  { path: '/kzn-directory', name: 'KznDirectory', component: KznDirectoryPage },
  { path: '/kzn-directory/item/:slug', name: 'KznItemDetail', component: KznItemDetail },
  { path: '/province/:slug', name: 'Province', component: ProvincePage },
  { path: '/destination/:id', name: 'DestinationDetail', component: DestinationDetail },
  { path: '/admin/registered-hotspots', name: 'AdminRegisteredHotspots', component: AdminRegisteredHotspots, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/comments', name: 'AdminReviewComments', component: AdminReviewComments, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/hotspots', name: 'AdminReviewHotspots', component: AdminReviewHotspots, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/users', name: 'AdminManageUsers', component: AdminManageUsers, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/host/dashboard', name: 'OwnerDashboard', component: OwnerDashboard, meta: { requiresAuth: true, requiresHost: true } },
  { path: '/host', name: 'HostDashboard', component: HostDashboard, meta: { requiresAuth: true, requiresHost: true }, alias: '/my-hotspots' },
  { path: '/host/register', name: 'RegisterHotspot', component: RegisterHotspot, meta: { requiresAuth: true, requiresHost: true } },
  { path: '/host/edit/:id', name: 'EditHotspot', component: EditHotspot, meta: { requiresAuth: true, requiresHost: true } },
  { path: '/host/reviews', name: 'HostReviews', component: HostReviews, meta: { requiresAuth: true, requiresHost: true } },
  { path: '/host/performance', name: 'HostPerformance', component: HostPerformance, meta: { requiresAuth: true, requiresHost: true } },
  { path: '/host/analytics', redirect: '/analytics' },
  { path: '/host/analytics/:id', name: 'HotspotAnalytics', component: HotspotAnalytics, meta: { requiresAuth: true, requiresHost: true } },
  { path: '/plan-trip/edit/:id', name: 'EditTrip', component: EditTripPage, meta: { requiresAuth: true } },
  { path: '/journal', name: 'TravelJournal', component: TravelJournalPage, meta: { requiresAuth: true } },
  { path: '/reviews', name: 'ReviewHistory', component: ReviewHistoryPage, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresAdmin && !auth.isAdmin) {
    const fallback = auth.isBusinessOwner ? '/my-hotspots' : '/'
    next(fallback)
  } else if (to.meta.requiresHost && !auth.isBusinessOwner && !auth.isAdmin) {
    const fallback = auth.isTourist ? '/' : '/my-hotspots'
    next(fallback)
  } else if (to.meta.guest && auth.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
