<template>
  <div class="orders-page container">
    <h1 class="page-title">{{ $t('orders.title') }}</h1>
    <SkeletonLoader v-if="loading" type="list" :count="4" />
    <div v-else-if="orders.length === 0" class="empty-state">
      <i class="fas fa-receipt"></i><h3>{{ $t('orders.empty') }}</h3><p>{{ $t('orders.emptyDesc') }}</p>
      <router-link :to="$storeLink('/products')" class="btn btn-primary" style="margin-top: 16px;"><i class="fas fa-shopping-bag"></i> {{ $t('cart.browseProducts') }}</router-link>
    </div>
    <div v-else class="orders-list">
      <div v-for="order in orders" :key="order.id" class="order-card card">
        <div class="order-header">
          <div><span class="order-number">{{ order.order_number }}</span><span class="order-date">{{ new Date(order.created_at).toLocaleDateString() }}</span></div>
          <span :class="['status-badge', `status-${order.status}`]">{{ $t(`ordersManage.${order.status}`) }}</span>
        </div>
        <div class="order-items">
          <div v-for="item in order.items" :key="item.id" class="order-item"><span>{{ item.product_variant?.product?.name }} x {{ item.quantity }}</span><span>TSh {{ Number(item.total).toLocaleString('en-TZ') }}</span></div>
        </div>
        <div class="order-footer"><span class="order-total">{{ $t('orders.total') }} TSh {{ Number(order.total).toLocaleString('en-TZ') }}</span></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { orderApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
const orders = ref([])
const loading = ref(true)
onMounted(async () => { try { const r = await orderApi.getAll(); orders.value = r.data.data } finally { loading.value = false } })
</script>

<style scoped>
.orders-list { display: flex; flex-direction: column; gap: 16px; }
.order-card { padding: 24px; }
.order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.order-number { font-weight: 700; font-size: 16px; }
.order-date { margin-left: 12px; color: #888; font-size: 14px; }
.status-badge { padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: capitalize; }
.status-pending_payment { background: #fff3cd; color: #856404; }
.status-paid { background: #d4edda; color: #155724; }
.status-processing { background: #cce5ff; color: #004085; }
.status-shipped { background: #e2d5f1; color: #563d7c; }
.status-delivered { background: #d4edda; color: #155724; }
.status-cancelled { background: #f8d7da; color: #721c24; }
.status-inactive { background: #e9ecef; color: #6c757d; }
.order-item { display: flex; justify-content: space-between; padding: 10px 0; font-size: 14px; color: #666; border-bottom: 1px solid #f0f0f0; }
.order-footer { display: flex; justify-content: flex-end; padding-top: 12px; }
.order-total { font-weight: 700; font-size: 16px; color: #e74c3c; }
.empty-state { text-align: center; padding: 80px 0; }
.empty-state i { font-size: 48px; color: #ddd; margin-bottom: 16px; }
.empty-state h3 { margin-bottom: 8px; }
.empty-state p { color: #888; }
</style>
