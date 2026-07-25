<template>
  <div class="product-card" @click="navigateToProduct">
    <div class="card-image">
      <img :src="imageUrl(product.image) || '/placeholder.svg'" :alt="product.name" />
      <span class="card-badge" v-if="product.brand">{{ product.brand }}</span>
      <button
        class="add-to-cart-btn"
        :class="{ 'added': added }"
        @click.stop="handleAddToCart"
        :disabled="adding"
      >
        <i :class="added ? 'fas fa-check' : 'fas fa-cart-plus'"></i>
      </button>
    </div>
    <div class="card-body">
      <span class="card-category">{{ product.category?.name }}</span>
      <h3 class="card-title">{{ product.name }}</h3>
      <div class="card-price">TSh {{ formatPrice(product.price) }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { imageUrl } from '@/utils/image'

const props = defineProps({
  product: { type: Object, required: true },
})

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()
const adding = ref(false)
const added = ref(false)

function formatPrice(value) {
  return Number(value).toLocaleString('en-TZ')
}

function navigateToProduct() {
  router.push(`/products/${props.product.slug}`)
}

async function handleAddToCart() {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: '/cart' } })
    return
  }

  const variant = props.product.variants?.[0]
  if (!variant) return

  adding.value = true
  added.value = false
  try {
    await cartStore.addItem(variant.id)
    added.value = true
    setTimeout(() => { added.value = false }, 1500)
  } finally {
    adding.value = false
  }
}
</script>

<style scoped>
.product-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;
}

.product-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
}

.card-image {
  position: relative;
  height: 200px;
  background: #f8f8f8;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.product-card:hover .card-image img {
  transform: scale(1.05);
}

.card-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: #e74c3c;
  color: #fff;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.add-to-cart-btn {
  position: absolute;
  bottom: 12px;
  right: 12px;
  width: 40px;
  height: 40px;
  background: #e74c3c;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.product-card:hover .add-to-cart-btn {
  opacity: 1;
  transform: translateY(0);
}

.add-to-cart-btn:hover {
  background: #c0392b;
}

.add-to-cart-btn.added {
  background: #27ae60;
  opacity: 1;
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.add-to-cart-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.card-body {
  padding: 16px;
}

.card-category {
  font-size: 12px;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  margin: 6px 0;
  color: #333;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.card-price {
  font-size: 18px;
  font-weight: 700;
  color: #e74c3c;
}
</style>
