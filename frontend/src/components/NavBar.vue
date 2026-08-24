<template>
  <header class="navbar" :class="{ scrolled: isScrolled }">
    <div class="nav-container">
      <router-link to="/" class="logo">
        <img src="/img/Ubuntu_logo/Ubuntu-logo.png" alt="Ubuntu Cultural Connect" class="logo-img" />
      </router-link>

      <div class="nav-right">
        <nav class="nav-menu" :class="{ open: menuOpen }">
          <ul>
            <li v-if="auth.isTourist || !auth.isLoggedIn"><router-link to="/" @click="menuOpen = false">Home</router-link></li>
            <li><router-link to="/about" @click="menuOpen = false">About Us</router-link></li>

            <template v-if="auth.isLoggedIn">
              <!-- Tourist links -->
              <template v-if="auth.isTourist">
                <li><router-link to="/experiences" @click="menuOpen = false">Experiences</router-link></li>
                <li><router-link to="/preferences" @click="menuOpen = false">Set Preferences</router-link></li>
                <li><router-link to="/plan-trip" class="plan-trip-link" @click="menuOpen = false">Plan Trip</router-link></li>
                <li><router-link to="/journal" @click="menuOpen = false">Journal</router-link></li>
                <li><router-link to="/reviews" @click="menuOpen = false">My Reviews</router-link></li>
              </template>

              <li v-if="auth.isBusinessOwner || auth.isAdmin" class="notif-li">
                <NotificationBell />
              </li>

              <li class="nav-user">
                <router-link to="/profile" class="user-link" @click="menuOpen = false">
                  <span class="user-name">{{ auth.user?.full_name }}</span>
                  <span class="role-tag">{{ auth.userRole?.replace('_', ' ') }}</span>
                </router-link>
              </li>
              <li>
                <button @click="handleLogout" class="logout-btn">Logout</button>
              </li>
            </template>
            <template v-else>
              <li><router-link to="/login" @click="menuOpen = false">Login</router-link></li>
              <li><router-link to="/register" class="register-link" @click="menuOpen = false">Register</router-link></li>
            </template>
          </ul>
        </nav>

        <button class="mobile-toggle" @click="menuOpen = !menuOpen" aria-label="Toggle menu">
          <svg v-if="!menuOpen" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
          <svg v-else width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notification'
import { useRouter } from 'vue-router'
import NotificationBell from './NotificationBell.vue'

const auth = useAuthStore()
const notifStore = useNotificationStore()
const router = useRouter()
const menuOpen = ref(false)
const isScrolled = ref(false)
const adminOpen = ref(false)

function closeAll() {
  menuOpen.value = false
  adminOpen.value = false
}

function handleLogout() {
  closeAll()
  notifStore.stopPolling()
  auth.logout()
  router.push('/login')
}

function onScroll() {
  isScrolled.value = window.scrollY > 50
}

watch(() => auth.isBusinessOwner || auth.isAdmin, (shouldPoll) => {
  if (shouldPoll) {
    notifStore.startPolling(10000)
  } else {
    notifStore.stopPolling()
  }
}, { immediate: true })

onMounted(() => {
  window.addEventListener('scroll', onScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  notifStore.stopPolling()
})
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 997;
  background-color: var(--glass-bg);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: background-color 0.4s ease;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 14px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.logo-img {
  height: 65px;
  width: auto;
}

.nav-right {
  display: flex;
  align-items: center;
}

.nav-menu ul {
  display: flex;
  align-items: center;
  gap: 4px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-menu > ul > li {
  position: relative;
}

.nav-menu a,
.nav-menu button {
  color: #333333;
  font-family: 'Poppins', sans-serif;
  font-size: 0.85rem;
  font-weight: 400;
  padding: 8px 12px;
  border-radius: 6px;
  transition: 0.3s;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  white-space: nowrap;
}

.nav-menu a:hover,
.nav-menu button:hover {
  color: var(--accent);
}

.nav-menu a.router-link-exact-active {
  color: var(--accent);
}

/* Dropdown */
.dropdown-trigger {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #333333;
  font-family: 'Poppins', sans-serif;
  font-size: 0.85rem;
  font-weight: 400;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.3s;
  user-select: none;
}

.dropdown-trigger:hover {
  color: var(--accent);
}

.dropdown-menu {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 180px;
  background: var(--glass-bg);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px;
  padding: 6px;
  list-style: none;
  margin: 0;
  z-index: 1000;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.dropdown-menu.show {
  display: block;
}

.dropdown-menu li a {
  display: block;
  padding: 8px 14px;
  font-size: 0.85rem;
  border-radius: 6px;
  transition: background 0.2s;
}

.dropdown-menu li a:hover {
  background: rgba(232, 162, 0, 0.15);
  color: var(--accent);
}

.register-link {
  background-color: var(--accent-fill) !important;
  color: #1a1a1a !important;
  font-weight: 600 !important;
  border-radius: 8px !important;
  padding: 8px 20px !important;
}

.register-link:hover {
  background-color: var(--accent-fill-hover) !important;
  color: #1a1a1a !important;
}

.plan-trip-link {
  background: var(--accent-light) !important;
  color: var(--accent) !important;
  font-weight: 600 !important;
  border: 1px solid rgba(232, 162, 0, 0.4) !important;
  border-radius: 8px !important;
  padding: 8px 18px !important;
}

.plan-trip-link:hover {
  background: var(--accent-fill) !important;
  color: #1a1a1a !important;
}

.notif-li {
  display: flex;
  align-items: center;
}

.nav-user {
  display: flex;
  align-items: center;
}

.user-link {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  font-size: 0.85rem;
}

.role-tag {
  background: rgba(232, 162, 0, 0.15);
  color: var(--accent);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  text-transform: capitalize;
}

.logout-btn {
  color: var(--text-secondary) !important;
}

.logout-btn:hover {
  color: #ff4d4f !important;
}

.mobile-toggle {
  display: none;
  background: none;
  border: none;
  color: #333333;
  font-size: 24px;
  cursor: pointer;
  padding: 4px;
}

/* Mobile */
@media (max-width: 1024px) {
  .mobile-toggle {
    display: block;
  }

  .nav-menu {
    position: fixed;
    top: 0;
    right: -100%;
    width: 280px;
    height: 100vh;
    background: var(--glass-bg);
    box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
    transition: right 0.3s ease;
    padding: 80px 30px 30px;
    z-index: 9998;
    overflow-y: auto;
  }

  .nav-menu.open {
    right: 0;
  }

  .nav-menu ul {
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
  }

  .nav-menu a,
  .nav-menu button {
    display: block;
    padding: 12px 16px;
    font-size: 1rem;
    text-align: left;
  }

  .dropdown-trigger {
    display: block;
    padding: 12px 16px;
    font-size: 1rem;
    text-align: left;
  }

  .dropdown-menu {
    position: static;
    background: #f5f5f5;
    border: none;
    border-radius: 0;
    padding: 0 0 0 16px;
    box-shadow: none;
    display: none;
  }

  .dropdown-menu.show {
    display: block;
  }

  .dropdown-menu li a {
    padding: 10px 16px;
    font-size: 0.95rem;
  }

  .register-link {
    text-align: center !important;
    margin-top: 12px;
  }
}
</style>
