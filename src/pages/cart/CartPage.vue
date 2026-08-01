<template>
  <div class="cart-page container">
    <h1 class="page-title">{{ $t('cart.title') }}</h1>

    <SkeletonLoader v-if="cartStore.loading" type="list" :count="3" />

    <div v-else-if="cartStore.items.length === 0" class="empty-state">
      <i class="fas fa-shopping-cart"></i>
      <h3>{{ $t('cart.empty') }}</h3>
      <p>{{ $t('cart.emptyDesc') }}</p>
      <router-link :to="$storeLink('/products')" class="btn btn-primary" style="margin-top: 16px;">
        <i class="fas fa-shopping-bag"></i> {{ $t('cart.browseProducts') }}
      </router-link>
    </div>

    <div v-else class="cart-layout">
      <div class="cart-items">
        <div v-for="item in cartStore.items" :key="item.id" class="cart-item card">
          <img :src="imageUrl(item.product_variant?.product?.image) || '/placeholder.svg'" :alt="item.product_variant?.product?.name" class="item-image" />
          <div class="item-details">
            <h3>{{ item.product_variant?.product?.name }}</h3>
            <p class="item-variant">{{ [item.product_variant?.color, item.product_variant?.storage].filter(Boolean).join(' - ') }}</p>
            <p class="item-price">TSh {{ formatPrice(item.unit_price) }}</p>
          </div>
          <div class="item-quantity">
            <button @click="updateQuantity(item, item.quantity - 1)" :disabled="item.quantity <= 1"><i class="fas fa-minus"></i></button>
            <span>{{ item.quantity }}</span>
            <button @click="updateQuantity(item, item.quantity + 1)"><i class="fas fa-plus"></i></button>
          </div>
          <div class="item-total">TSh {{ formatPrice(item.total) }}</div>
          <button class="remove-btn" @click="cartStore.removeItem(item.id)"><i class="fas fa-trash"></i></button>
        </div>
      </div>

      <div class="cart-summary card">
        <h2>{{ $t('cart.orderSummary') }}</h2>
        <div class="summary-row"><span>{{ $t('cart.subtotal', { count: cartStore.itemCount }) }}</span><span>TSh {{ formatPrice(cartStore.subtotal) }}</span></div>
        <div class="summary-row"><span>{{ $t('cart.shipping') }}</span><span>TSh 5,000</span></div>
        <div class="summary-row total"><span>{{ $t('cart.total') }}</span><span>TSh {{ formatPrice(cartStore.total) }}</span></div>
        <router-link :to="$storeLink('/checkout')" class="btn btn-primary checkout-btn"><i class="fas fa-lock"></i> {{ $t('cart.proceedToCheckout') }}</router-link>
        <router-link :to="$storeLink('/products')" class="btn btn-outline continue-btn"><i class="fas fa-arrow-left"></i> {{ $t('cart.continueShopping') }}</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { imageUrl } from '@/utils/image'
const cartStore = useCartStore()
function formatPrice(v) { return Number(v).toLocaleString('en-TZ') }
async function updateQuantity(item, qty) { if (qty >= 1) await cartStore.updateItem(item.id, qty) }
onMounted(() => cartStore.fetchCart())
</script>

<style scoped>
.cart-layout { display: grid; grid-template-columns: 1fr 360px; gap: 32px; align-items: start; }
.cart-page { overflow-x: hidden; }
.cart-item { display: flex; align-items: center; gap: 16px; padding: 20px; margin-bottom: 12px; }
.item-image { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; background: #f8f8f8; }
.item-details { flex: 1; }
.item-details h3 { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
.item-variant { font-size: 13px; color: #888; }
.item-price { font-weight: 600; color: #e74c3c; margin-top: 4px; }
.item-quantity { display: flex; align-items: center; border: 1px solid #ddd; border-radius: 4px; overflow: hidden; }
.item-quantity button { width: 36px; height: 36px; background: #f8f8f8; }
.item-quantity button:hover { background: #eee; }
.item-quantity span { width: 40px; text-align: center; font-weight: 600; }
.item-total { font-weight: 700; min-width: 120px; text-align: right; color: #e74c3c; }
.remove-btn { color: #ccc; padding: 8px; }
.remove-btn:hover { color: #e74c3c; }
.cart-summary { padding: 24px; }
.cart-summary h2 { font-size: 18px; margin-bottom: 20px; }
.summary-row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee; font-size: 14px; }
.summary-row.total { font-size: 18px; font-weight: 700; border-bottom: none; color: #e74c3c; }
.checkout-btn { width: 100%; margin-top: 20px; }
.continue-btn { width: 100%; margin-top: 8px; }
.empty-state { text-align: center; padding: 80px 0; }
.empty-state i { font-size: 48px; color: #ddd; margin-bottom: 16px; }
.empty-state h3 { margin-bottom: 8px; }
.empty-state p { color: #888; }
@media (max-width: 768px) {
  .cart-layout { grid-template-columns: 1fr; gap: 16px; }
  .cart-item { flex-wrap: wrap; gap: 10px; padding: 14px; position: relative; }
  .item-image { width: 60px; height: 60px; flex-shrink: 0; }
  .item-details { min-width: 0; flex: 1 1 45%; }
  .item-details h3 { font-size: 14px; word-break: break-word; }
  .item-quantity { flex: 0 0 auto; }
  .item-total { min-width: 0; width: auto; font-size: 14px; margin-left: auto; }
  .remove-btn { padding: 4px; flex-shrink: 0; }
  .cart-summary { padding: 16px; }
}
</style>
