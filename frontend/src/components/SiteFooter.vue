<template>
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-top">
        <div class="footer-brand">
          <img src="/img/Ubuntu_logo/Ubuntu-logo.png" alt="Ubuntu Cultural Connect" class="footer-logo" />
          <p class="footer-tagline">Connecting cultures, preserving heritage, celebrating South Africa's rich diversity.</p>
        </div>

        <div class="footer-links">
          <div class="link-group">
            <h4>Explore</h4>
            <ul>
              <li><router-link to="/experiences">Experiences</router-link></li>
              <li v-if="auth.isLoggedIn && !auth.isTourist"><router-link to="/dashboard">Dashboard</router-link></li>
              <li><router-link to="/plan-trip">Plan a Trip</router-link></li>
            </ul>
          </div>

          <div class="link-group" v-if="auth.isLoggedIn && (auth.isBusinessOwner || auth.isAdmin)">
            <h4>Host</h4>
            <ul>
              <li><router-link to="/host">My Hotspots</router-link></li>
              <li><router-link to="/host/reviews">Guest Reviews</router-link></li>
              <li><router-link to="/host/performance">Performance</router-link></li>
            </ul>
          </div>

          <div class="link-group" v-if="auth.isLoggedIn && auth.isAdmin">
            <h4>Admin</h4>
            <ul>
              <li><router-link to="/admin">Dashboard</router-link></li>
              <li><router-link to="/admin/users">Manage Users</router-link></li>
              <li><router-link to="/admin/hotspots">Review Hotspots</router-link></li>
            </ul>
          </div>

          <div class="link-group">
            <h4>Account</h4>
            <ul>
              <li v-if="!auth.isLoggedIn"><router-link to="/login">Login</router-link></li>
              <li v-if="!auth.isLoggedIn"><router-link to="/register">Register</router-link></li>
              <li v-if="auth.isLoggedIn"><router-link to="/profile">Profile</router-link></li>
              <li v-if="auth.isLoggedIn"><router-link to="/preferences">Preferences</router-link></li>
              <li v-if="auth.isLoggedIn"><a href="#" @click.prevent="handleLogout">Logout</a></li>
            </ul>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <p>&copy; {{ currentYear }} Ubuntu Cultural Connect. All rights reserved.</p>
        <p class="ubuntu-text">
          <span class="accent">Ubuntu</span> — I am because we are
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const currentYear = computed(() => new Date().getFullYear())

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.site-footer {
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.7);
  padding: 3rem 1.5rem 1.5rem;
  margin-top: auto;
}

.footer-inner {
  max-width: 1100px;
  margin: 0 auto;
}

.footer-top {
  display: grid;
  grid-template-columns: 1.4fr 2fr;
  gap: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.footer-logo {
  height: 50px;
  width: auto;
  margin-bottom: 0.75rem;
}

.footer-tagline {
  font-size: 0.9rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.5);
  max-width: 280px;
}

.footer-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 1.5rem;
}

.link-group h4 {
  font-family: 'Poppins', sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.75rem;
}

.link-group ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.link-group li {
  margin-bottom: 0.4rem;
}

.link-group a {
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  font-size: 0.88rem;
  transition: color 0.2s;
}

.link-group a:hover {
  color: var(--accent);
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1.5rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.footer-bottom p {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.35);
  margin: 0;
}

.ubuntu-text {
  font-size: 0.82rem;
}

.accent {
  font-family: 'Pacifico', cursive;
  color: var(--accent);
}

@media (max-width: 768px) {
  .footer-top {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
}
</style>
