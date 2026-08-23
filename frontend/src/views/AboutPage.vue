<template>
  <div class="about-page">
    <section class="about-hero">
      <h1>About <span class="accent-word">Ubuntu Cultural Connect</span></h1>
      <p>
        We connect travellers with authentic South African cultural experiences through local
        community hosts, celebrating indigenous traditions, township life, and rural heritage.
      </p>
    </section>

    <section class="about-content">
      <div class="about-grid">
        <div class="about-card">
          <i class="bi bi-people-fill"></i>
          <h3>Our Mission</h3>
          <p>
            To preserve and promote South Africa's rich cultural heritage while empowering local
            communities through responsible tourism.
          </p>
        </div>
        <div class="about-card">
          <i class="bi bi-globe-africa"></i>
          <h3>Our Story</h3>
          <p>
            Born from the spirit of Ubuntu — "I am because we are" — we believe travel should
            connect people, not just places.
          </p>
        </div>
        <div class="about-card">
          <i class="bi bi-heart-fill"></i>
          <h3>Our Values</h3>
          <p>
            Authenticity, respect, and community. Every experience supports local hosts and keeps
            cultural traditions alive for future generations.
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
</script>

<style scoped>
.about-page {
  min-height: 100vh;
  background: #ffffff;
}

.about-hero {
  background: url('/img/cultures/woman.jpeg') no-repeat center center;
  background-size: cover;
  position: relative;
  text-align: center;
  padding: 140px 20px 80px;
}

.about-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
}

.about-hero h1,
.about-hero p {
  position: relative;
  z-index: 1;
}

.about-hero h1 {
  font-family: 'Poppins', sans-serif;
  font-size: clamp(2rem, 5vw, 3.2rem);
  font-weight: 700;
  color: #fff;
  max-width: 800px;
  margin: 0 auto 16px;
  line-height: 1.2;
}

.about-hero .accent-word {
  font-family: 'Pacifico', cursive;
  font-weight: 400;
  color: var(--accent);
}

.about-hero p {
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.94);
  max-width: 640px;
  margin: 0 auto;
  line-height: 1.7;
}

.about-content {
  padding: 60px 20px;
}

.about-grid {
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.about-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}

.about-card i {
  font-size: 2rem;
  color: var(--accent);
  margin-bottom: 16px;
}

.about-card h3 {
  font-size: 1.2rem;
  color: #1a1a1a;
  margin-bottom: 12px;
}

.about-card p {
  font-size: 0.9rem;
  color: #555;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .about-grid {
    grid-template-columns: 1fr;
  }
}
</style>
