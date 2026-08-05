<template>
  <div class="home-page">
    <!-- Hero Banner -->
    <section class="hero-banner">
      <div class="container hero-inner">
        <div class="hero-content">
          <span class="hero-badge">{{ hc('heroBadge') }}</span>
          <h1>{{ hc('heroTitle') }} <span>{{ hc('heroTitleHighlight') }}</span></h1>
          <p>{{ hc('heroDesc') }}</p>
          <div class="hero-actions">
            <router-link :to="$storeLink('/products')" class="btn btn-primary">
              <i class="fas fa-shopping-bag"></i> {{ hc('shopNow') }}
            </router-link>
            <router-link :to="$storeLink('/products')" class="btn btn-outline-white">
              {{ hc('viewCatalog') }} <i class="fas fa-arrow-right"></i>
            </router-link>
          </div>
        </div>
        <div class="hero-image">
          <div class="hero-shape"></div>
        </div>
      </div>
    </section>

    <!-- Features Strip -->
    <section class="features-strip">
      <div class="container features-inner">
        <div class="feature-item">
          <i class="fas fa-truck-fast"></i>
          <div>
            <strong>{{ hc('freeDelivery') }}</strong>
            <span>{{ hc('freeDeliveryDesc') }}</span>
          </div>
        </div>
        <div class="feature-item">
          <i class="fas fa-shield-halved"></i>
          <div>
            <strong>{{ hc('securePayment') }}</strong>
            <span>{{ hc('securePaymentDesc') }}</span>
          </div>
        </div>
        <div class="feature-item">
          <i class="fas fa-rotate-left"></i>
          <div>
            <strong>{{ hc('easyReturns') }}</strong>
            <span>{{ hc('easyReturnsDesc') }}</span>
          </div>
        </div>
        <div class="feature-item">
          <i class="fas fa-headset"></i>
          <div>
            <strong>{{ hc('support247') }}</strong>
            <span>{{ hc('support247Desc') }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Categories -->
    <section class="categories-section">
      <div class="container">
        <h2 class="section-title">{{ hc('shopByCategory') }}</h2>
        <p class="section-subtitle">{{ hc('browseCategories') }}</p>

        <div v-if="productStore.categories.length > 0" class="categories-grid">
          <router-link v-for="cat in productStore.categories" :key="cat.id" :to="$storeLink(`/category/${cat.slug}`)"
            class="category-card">
            <div class="cat-icon-wrap">
              <i :class="getCategoryIcon(cat.name)"></i>
            </div>
            <h3>{{ cat.translated_name || cat.name }}</h3>
            <span class="cat-count">{{ productsCountLabel(cat.products_count || 0) }}</span>
          </router-link>
        </div>
        <div v-else class="empty-state">
          <i class="fas fa-layer-group"></i>
          <p>{{ hc('categoriesComingSoon') }}</p>
        </div>
      </div>
    </section>

    <!-- New Arrivals -->
    <section class="products-section">
      <div class="container">
        <h2 class="section-title">{{ hc('newArrivals') }}</h2>
        <p class="section-subtitle">{{ hc('newArrivalsDesc') }}</p>

        <SkeletonLoader v-if="loading" type="card" :count="4" />

        <div v-else-if="productStore.featuredProducts.length > 0" class="products-grid">
          <ProductCard v-for="product in productStore.featuredProducts" :key="product.id" :product="product" />
        </div>

        <div v-else class="empty-state">
          <i class="fas fa-box-open"></i>
          <p>{{ hc('noProductsYet') }}</p>
        </div>

        <div class="section-action" v-if="productStore.featuredProducts.length > 0">
          <router-link :to="$storeLink('/products')" class="btn btn-outline">
            {{ hc('viewMoreProducts') }} <i class="fas fa-arrow-right"></i>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Hot Selling Banner -->
    <section class="promo-banner">
      <div class="container">
        <div class="promo-inner">
          <div class="promo-content">
            <span class="promo-badge">{{ hc('hotDeals') }}</span>
            <h2>{{ hc('hotDealsTitle') }}</h2>
            <p>{{ hc('hotDealsDesc') }}</p>
            <router-link :to="$storeLink('/products')" class="btn btn-white">
              {{ hc('shopTheSale') }} <i class="fas fa-arrow-right"></i>
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Hot Selling Products -->
    <section class="products-section">
      <div class="container">
        <h2 class="section-title">{{ hc('hotSelling') }}</h2>
        <p class="section-subtitle">{{ hc('hotSellingDesc') }}</p>

        <div v-if="allProducts.length > 0" class="products-grid">
          <ProductCard v-for="product in allProducts.slice(0, 8)" :key="product.id" :product="product" />
        </div>

        <div class="section-action" v-if="allProducts.length > 0">
          <router-link :to="$storeLink('/products')" class="btn btn-outline">
            {{ hc('viewAllProducts') }} <i class="fas fa-arrow-right"></i>
          </router-link>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-grid">
          <div class="cta-card">
            <i class="fas fa-user-plus"></i>
            <h3>{{ hc('createAccount') }}</h3>
            <p>{{ hc('createAccountDesc') }}</p>
            <router-link to="/register" class="btn btn-primary btn-sm">{{ hc('register') }}</router-link>
          </div>
          <div class="cta-card">
            <i class="fas fa-mobile-screen-button"></i>
            <h3>{{ hc('mobileMoney') }}</h3>
            <p>{{ hc('mobileMoneyDesc') }}</p>
          </div>
          <div class="cta-card">
            <i class="fas fa-truck"></i>
            <h3>{{ hc('fastDeliveryTitle') }}</h3>
            <p>{{ hc('fastDeliveryDesc') }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useProductStore } from '@/stores/products'
import { useBusinessStore } from '@/stores/business'
import ProductCard from '@/components/product/ProductCard.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { settingsApi } from '@/api'

const { t, locale } = useI18n()
const route = useRoute()
const productStore = useProductStore()
const businessStore = useBusinessStore()
const loading = ref(true)
const allProducts = ref([])
const content = ref({ en: {}, sw: {} })

function hc(key) {
  const current = content.value[locale.value]
  if (current && current[key] && String(current[key]).trim()) {
    return current[key]
  }
  return t(`home.${key}`)
}

function productsCountLabel(count) {
  const current = content.value[locale.value]
  if (current && current.productsCount && String(current.productsCount).trim()) {
    return String(current.productsCount).replace('{count}', count)
  }
  return t('home.productsCount', { count })
}

function getCategoryIcon(name) {
  const icons = {
    'Phones': 'fas fa-mobile-screen-button',
    'Accessories': 'fas fa-plug',
    'Audio': 'fas fa-headphones',
    'Wearables': 'fas fa-clock',
    'Computers': 'fas fa-laptop',
  }
  return icons[name] || 'fas fa-box'
}

async function loadStoreData() {
  if (route.params.businessSlug && !businessStore.activeSlug) return
  loading.value = true
  try {
    const [res] = await Promise.all([
      settingsApi.getHomeContent(),
      productStore.fetchCategories(),
      productStore.fetchFeatured(),
      productStore.fetchProducts({ per_page: 8 }),
    ])
    content.value = res.data || { en: {}, sw: {} }
    allProducts.value = productStore.products
  } catch {
    try {
      await Promise.all([
        productStore.fetchCategories(),
        productStore.fetchFeatured(),
        productStore.fetchProducts({ per_page: 8 }),
      ])
      allProducts.value = productStore.products
    } catch { /* empty */ }
  } finally {
    loading.value = false
  }
}

onMounted(loadStoreData)
watch(() => businessStore.activeSlug, loadStoreData)
</script>

<style scoped>
/* Hero Banner */
.hero-banner {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  padding: 60px 0;
  overflow: hidden;
}

.hero-inner {
  display: flex;
  align-items: center;
  gap: 40px;
}

.hero-content {
  flex: 1;
  max-width: 550px;
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

.hero-content h1 {
  font-size: 42px;
  font-weight: 800;
  color: #fff;
  line-height: 1.2;
  margin-bottom: 16px;
}

.hero-content h1 span {
  color: #e74c3c;
}

.hero-content p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 28px;
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.btn-outline-white {
  color: #fff;
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 12px 28px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-outline-white:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #fff;
  color: #fff;
}

.hero-image {
  flex: 1;
  display: flex;
  justify-content: center;
}

.hero-shape {
  width: 350px;
  height: 350px;
  background: linear-gradient(135deg, rgba(231, 76, 60, 0.2), rgba(231, 76, 60, 0.05));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Features Strip */
.features-strip {
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  padding: 20px 0;
}

.features-inner {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.feature-item i {
  font-size: 28px;
  color: #e74c3c;
}

.feature-item strong {
  display: block;
  font-size: 14px;
  color: #333;
}

.feature-item span {
  font-size: 12px;
  color: #888;
}

/* Categories */
.categories-section {
  padding: 60px 0;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
}

.category-card {
  text-align: center;
  padding: 32px 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  transition: all 0.3s;
  text-decoration: none;
}

.category-card:hover {
  border-color: #e74c3c;
  box-shadow: 0 8px 30px rgba(231, 76, 60, 0.1);
  transform: translateY(-4px);
}

.cat-icon-wrap {
  width: 64px;
  height: 64px;
  background: #fef5f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  transition: all 0.3s;
}

.cat-icon-wrap i {
  font-size: 24px;
  color: #e74c3c;
}

.category-card:hover .cat-icon-wrap {
  background: #e74c3c;
}

.category-card:hover .cat-icon-wrap i {
  color: #fff;
}

.category-card h3 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #333;
}

.cat-count {
  font-size: 12px;
  color: #999;
}

/* Products */
.products-section {
  padding: 60px 0;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
}

.section-action {
  text-align: center;
  margin-top: 32px;
}

/* Promo Banner */
.promo-banner {
  padding: 40px 0;
}

.promo-inner {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  border-radius: 12px;
  padding: 48px;
  color: #fff;
}

.promo-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 12px;
}

.promo-content h2 {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 8px;
}

.promo-content p {
  opacity: 0.9;
  margin-bottom: 20px;
  font-size: 16px;
}

/* CTA Section */
.cta-section {
  padding: 60px 0;
  background: #f8f9fa;
}

.cta-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.cta-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 32px 24px;
  text-align: center;
  transition: all 0.3s;
}

.cta-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
}

.cta-card i {
  font-size: 32px;
  color: #e74c3c;
  margin-bottom: 16px;
}

.cta-card h3 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
}

.cta-card p {
  font-size: 13px;
  color: #777;
  margin-bottom: 16px;
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
  .hero-inner {
    flex-direction: column;
    text-align: center;
  }

  .hero-content h1 {
    font-size: 28px;
  }

  .hero-actions {
    justify-content: center;
  }

  .hero-image {
    display: none;
  }

  .features-inner {
    grid-template-columns: 1fr 1fr;
  }

  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .promo-inner {
    padding: 32px 24px;
  }

  .promo-content h2 {
    font-size: 24px;
  }

  .cta-grid {
    grid-template-columns: 1fr;
  }

  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}
</style>
