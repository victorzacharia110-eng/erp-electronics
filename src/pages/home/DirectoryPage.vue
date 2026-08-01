<template>
  <div class="directory-page">
    <section class="directory-hero">
      <div class="container">
        <span class="hero-badge">{{ $t('directory.badge') }}</span>
        <h1>{{ $t('directory.title') }}</h1>
        <p>{{ $t('directory.subtitle') }}</p>
      </div>
    </section>

    <section class="directory-section">
      <div class="container">
        <div v-if="loading" class="directory-grid">
          <div v-for="i in 6" :key="i" class="store-card skeleton-card"></div>
        </div>

        <div v-else-if="businesses.length > 0" class="directory-grid">
          <router-link
            v-for="store in businesses"
            :key="store.id"
            :to="`/${store.slug}`"
            class="store-card"
          >
            <div
              v-if="store.new_arrivals_count > 0"
              class="new-badge"
              :title="$t('directory.newArrivals', { count: store.new_arrivals_count })"
            >
              <span>{{ $t('directory.new') }}</span>
              <i v-if="store.new_arrivals_count > 1" class="new-count">{{ store.new_arrivals_count }}</i>
            </div>
            <div
              class="store-logo"
              :style="logoStyle(store)"
            >
              <img v-if="store.logo_path" :src="store.logo_path" :alt="store.store_name" />
              <i v-else class="fas fa-store"></i>
            </div>
            <div class="store-info">
              <h3>{{ store.store_name }}</h3>
              <p v-if="store.tagline" class="store-tagline">{{ store.tagline }}</p>
              <span class="store-meta">
                <i class="fas fa-box-open"></i>
                {{ $t('directory.productsCount', { count: store.products_count || 0 }) }}
              </span>
            </div>
            <div class="store-cta">
              <span>{{ $t('directory.visitStore') }} <i class="fas fa-arrow-right"></i></span>
            </div>
          </router-link>
        </div>

        <div v-else class="empty-state">
          <i class="fas fa-store-slash"></i>
          <p>{{ $t('directory.empty') }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { businessApi } from '@/api'

const businesses = ref([])
const loading = ref(true)

function logoStyle(store) {
  return {
    background: store.brand_color || '#e74c3c',
  }
}

onMounted(async () => {
  try {
    const res = await businessApi.list()
    businesses.value = res.data.data || []
  } catch {
    businesses.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.directory-hero {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  padding: 60px 0;
  text-align: center;
  color: #fff;
}

.hero-badge {
  display: inline-block;
  background: rgba(231, 76, 60, 0.15);
  color: #e74c3c;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 16px;
}

.directory-hero h1 {
  font-size: 38px;
  font-weight: 800;
  margin-bottom: 10px;
}

.directory-hero p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 16px;
}

.directory-section {
  padding: 60px 0;
}

.directory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.store-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 20px;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s;
  position: relative;
}

.store-card:hover {
  border-color: #e74c3c;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  transform: translateY(-4px);
}

.new-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 58px;
  height: 58px;
  background: #e74c3c;
  clip-path: polygon(
    25% 6%, 38% 2%, 50% 8%, 62% 2%, 75% 6%,
    94% 25%, 98% 38%, 92% 50%, 98% 62%, 94% 75%,
    75% 94%, 62% 98%, 50% 92%, 38% 98%, 25% 94%,
    6% 75%, 2% 62%, 8% 50%, 2% 38%, 6% 25%
  );
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  color: #fff;
  box-shadow: 0 4px 14px rgba(231, 76, 60, 0.5);
  animation: newBadgePop 1.6s ease-in-out infinite;
}

.new-badge span {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1px;
  transform: rotate(-18deg);
  text-transform: uppercase;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
}

.new-badge .new-count {
  position: absolute;
  right: 2px;
  top: 2px;
  background: #fff;
  color: #e74c3c;
  font-size: 9px;
  font-weight: 800;
  font-style: normal;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: rotate(10deg);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

@keyframes newBadgePop {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}

.store-logo {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 22px;
  flex-shrink: 0;
}

.store-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.store-info {
  flex: 1;
  min-width: 0;
}

.store-info h3 {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.store-tagline {
  font-size: 12px;
  color: #888;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.store-meta {
  font-size: 12px;
  color: #999;
}

.store-meta i {
  color: #e74c3c;
  margin-right: 4px;
}

.store-cta {
  color: #e74c3c;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.skeleton-card {
  height: 100px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #999;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.3;
}

@media (max-width: 768px) {
  .directory-hero h1 {
    font-size: 28px;
  }

  .directory-grid {
    grid-template-columns: 1fr;
  }
}
</style>
