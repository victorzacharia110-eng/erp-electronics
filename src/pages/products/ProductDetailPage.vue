<template>
  <div>
    <div class="product-detail container" v-if="!loading && product">
      <div class="breadcrumb">
        <router-link :to="$storeLink('/')">{{ $t('nav.home') }}</router-link>
        <i class="fas fa-chevron-right"></i>
        <router-link :to="$storeLink('/products')">{{ $t('nav.products') }}</router-link>
        <i class="fas fa-chevron-right"></i>
        <span>{{ product.name }}</span>
      </div>

      <div class="product-layout">
        <div class="product-images">
          <img :src="imageUrl(product.image) || '/placeholder.svg'" :alt="product.name" class="main-image" />
        </div>

        <div class="product-info">
          <span class="product-category">{{ product.category?.name }}</span>
          <h1 class="product-name">{{ product.name }}</h1>
          <p class="product-brand" v-if="product.brand">{{ $t('product.brand') }}: <strong>{{ product.brand }}</strong></p>
          <p class="product-price">TSh {{ formatPrice(selectedVariant?.price || product.price) }}</p>

          <div class="product-description" v-if="product.description">
            <h3>{{ $t('product.description') }}</h3>
            <p>{{ product.description }}</p>
          </div>

          <div class="variants" v-if="product.variants?.length > 1">
            <h3>{{ $t('product.selectVariant') }}</h3>
            <div class="variant-options">
              <button
                v-for="variant in product.variants"
                :key="variant.id"
                :class="['variant-btn', { active: selectedVariant?.id === variant.id }]"
                @click="selectedVariant = variant"
                :disabled="!variant.inventory || variant.inventory.quantity_on_hand < 1"
              >
                {{ [variant.color, variant.storage].filter(Boolean).join(' - ') }}
              </button>
            </div>
          </div>

          <div class="stock-info">
            <span v-if="stockCount > 0" class="in-stock">
              <i class="fas fa-check-circle"></i> {{ $t('product.inStock', { count: stockCount }) }}
            </span>
            <span v-else class="out-of-stock">
              <i class="fas fa-times-circle"></i> {{ $t('product.outOfStock') }}
            </span>
          </div>

          <div class="quantity-selector">
            <label>{{ $t('product.quantity') }}</label>
            <div class="qty-controls">
              <button @click="quantity = Math.max(1, quantity - 1)"><i class="fas fa-minus"></i></button>
              <span>{{ quantity }}</span>
              <button @click="quantity = Math.min(stockCount, quantity + 1)"><i class="fas fa-plus"></i></button>
            </div>
          </div>

          <div v-if="!addedMessage" class="action-buttons">
            <button
              class="btn btn-buy-now"
              @click="handleAddToCart"
              :disabled="adding || stockCount === 0"
            >
              <i class="fas fa-bolt"></i>
              {{ adding ? $t('product.adding') : $t('product.buyNow') }}
            </button>
          </div>

          <div v-if="addedMessage" class="added-banner">
            <div class="added-banner-top">
              <i class="fas fa-check-circle"></i>
              <strong>{{ $t('product.addedToCart') }}</strong>
              <span>{{ product.name }} x {{ quantity }}</span>
            </div>
            <div class="added-banner-actions">
              <router-link :to="$storeLink('/cart')" class="btn btn-outline banner-btn"><i class="fas fa-shopping-cart"></i> {{ $t('product.viewCart') }}</router-link>
              <router-link :to="$storeLink('/checkout')" class="btn btn-primary banner-btn"><i class="fas fa-lock"></i> {{ $t('product.proceedToCheckout') }}</router-link>
            </div>
          </div>

          <div v-if="errorMsg" class="error-toast">
            <i class="fas fa-exclamation-circle"></i>
            <span>{{ errorMsg }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="container" style="padding: 40px 0;">
      <SkeletonLoader type="detail" :count="1" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '@/stores/products'
import { useBusinessStore } from '@/stores/business'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { imageUrl } from '@/utils/image'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const cartStore = useCartStore()
const authStore = useAuthStore()
const businessStore = useBusinessStore()

const loading = ref(true)
const product = ref(null)
const selectedVariant = ref(null)
const quantity = ref(1)
const adding = ref(false)
const addedMessage = ref(false)
const errorMsg = ref('')

const stockCount = computed(() =>
  selectedVariant.value?.inventory?.quantity_on_hand || 0
)

function formatPrice(value) {
  return Number(value).toLocaleString('en-TZ')
}

async function handleAddToCart() {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  if (!selectedVariant.value) return
  adding.value = true
  addedMessage.value = false
  errorMsg.value = ''
  try {
    await cartStore.addItem(selectedVariant.value.id, quantity.value)
    addedMessage.value = true
  } catch (e) {
    errorMsg.value = e.response?.data?.message || t('cart.failedToAdd')
    setTimeout(() => errorMsg.value = '', 4000)
  } finally {
    adding.value = false
  }
}

async function loadProduct() {
  loading.value = true
  selectedVariant.value = null
  try {
    product.value = await productStore.fetchProduct(route.params.slug)
    if (product.value?.variants?.length) {
      selectedVariant.value = product.value.variants[0]
    }
  } finally {
    loading.value = false
  }
}

onMounted(loadProduct)
watch(() => route.params.slug, loadProduct)
watch(() => businessStore.activeSlug, loadProduct)
</script>

<style scoped>
.breadcrumb {
  padding: 20px 0;
  font-size: 13px;
  color: #888;
  display: flex;
  align-items: center;
  gap: 8px;
}

.breadcrumb a {
  color: #888;
  transition: color 0.2s;
}

.breadcrumb a:hover {
  color: #e74c3c;
}

.breadcrumb i {
  font-size: 10px;
}

.breadcrumb span {
  color: #333;
  font-weight: 500;
}

.product-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  padding-bottom: 60px;
}

.main-image {
  width: 100%;
  border-radius: 8px;
  background: #f8f8f8;
  border: 1px solid #eee;
  aspect-ratio: 1;
  object-fit: cover;
}

.product-category {
  font-size: 13px;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.product-name {
  font-size: 28px;
  font-weight: 700;
  margin: 8px 0;
  color: #333;
}

.product-brand {
  color: #777;
  margin-bottom: 16px;
}

.product-price {
  font-size: 28px;
  font-weight: 800;
  color: #e74c3c;
  margin-bottom: 24px;
}

.product-description {
  margin-bottom: 24px;
}

.product-description h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.product-description p {
  color: #666;
  line-height: 1.6;
}

.variants {
  margin-bottom: 24px;
}

.variants h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.variant-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.variant-btn {
  padding: 10px 20px;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.variant-btn:hover:not(:disabled) {
  border-color: #e74c3c;
}

.variant-btn.active {
  border-color: #e74c3c;
  background: #fef5f5;
  color: #e74c3c;
}

.variant-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.stock-info {
  margin-bottom: 20px;
}

.in-stock {
  color: #27ae60;
  font-weight: 600;
}

.out-of-stock {
  color: #e74c3c;
  font-weight: 600;
}

.quantity-selector {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.quantity-selector label {
  font-weight: 600;
}

.qty-controls {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.qty-controls button {
  width: 44px;
  height: 44px;
  background: #f8f8f8;
  font-size: 14px;
  color: #555;
  transition: background 0.2s;
}

.qty-controls button:hover {
  background: #eee;
}

.qty-controls span {
  width: 50px;
  text-align: center;
  font-weight: 700;
  font-size: 16px;
}

.add-to-cart {
  width: 100%;
  padding: 16px;
  font-size: 16px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-buttons .add-to-cart {
  flex: 1;
}

.btn-buy-now {
  flex: 1;
  padding: 16px;
  font-size: 16px;
  background: #2c3e50;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.2s;
  font-family: 'Inter', sans-serif;
}

.btn-buy-now:hover {
  background: #1a252f;
}

.btn-buy-now:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.added-banner {
  margin-top: 16px;
  background: #eafaf1;
  border: 2px solid #27ae60;
  border-radius: 8px;
  padding: 20px;
  animation: slideDown 0.3s ease;
}

.added-banner-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.added-banner-top > i {
  color: #27ae60;
  font-size: 22px;
}

.added-banner-top strong {
  font-size: 16px;
  color: #1a7a42;
}

.added-banner-top span {
  color: #666;
  font-size: 13px;
}

.added-banner-actions {
  display: flex;
  gap: 12px;
}

.banner-btn {
  flex: 1;
  padding: 14px;
  text-align: center;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.added-banner-actions .btn-outline {
  border: 1px solid #ddd;
  background: #fff;
  color: #333;
}

.added-banner-actions .btn-outline:hover {
  border-color: #e74c3c;
  color: #e74c3c;
}

.added-banner-actions .btn-primary {
  background: #e74c3c;
  color: #fff;
  border: 1px solid #e74c3c;
}

.added-banner-actions .btn-primary:hover {
  background: #c0392b;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.error-toast {
  margin-top: 12px;
  background: #fef5f5;
  border: 1px solid #e74c3c;
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #c0392b;
  animation: slideDown 0.3s ease;
}

@media (max-width: 768px) {
  .product-layout {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}
</style>
