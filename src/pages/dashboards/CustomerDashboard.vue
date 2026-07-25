<template>
  <div class="dashboard-page container">
    <SkeletonLoader v-if="loading" type="stats" :count="4" />
    <template v-else>
    <div class="dash-header">
      <div>
        <h1>{{ $t('dashboards.customer.title') }}</h1>
        <p>{{ $t('dashboards.customer.welcome', { name: authStore.user?.name }) }}</p>
      </div>
      <span class="role-badge customer"><i class="fas fa-user"></i> {{ $t('dashboards.customer.role') }}</span>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon orders"><i class="fas fa-shopping-bag"></i></div>
        <div><span class="stat-value">{{ stats.totalOrders }}</span><span class="stat-label">{{
          $t('dashboards.customer.totalOrders') }}</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon pending"><i class="fas fa-clock"></i></div>
        <div><span class="stat-value">{{ stats.pendingOrders }}</span><span class="stat-label">{{
          $t('dashboards.customer.pending') }}</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon delivered"><i class="fas fa-check-circle"></i></div>
        <div><span class="stat-value">{{ stats.deliveredOrders }}</span><span class="stat-label">{{
          $t('dashboards.customer.delivered') }}</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon addresses"><i class="fas fa-location-dot"></i></div>
        <div><span class="stat-value">{{ stats.addresses }}</span><span class="stat-label">{{
          $t('dashboards.customer.addresses') }}</span></div>
      </div>
    </div>

    <div v-if="hasActiveOrders" class="account-alert">
      <i class="fas fa-bell"></i>
      <div>
        <strong>{{ $t('dashboards.customer.accountReminder') }}</strong>
        <p>{{ $t('dashboards.customer.accountReminderDesc') }}</p>
      </div>
    </div>

    <div class="dash-grid">
      <div class="card dash-section">
        <h2><i class="fas fa-receipt"></i> {{ $t('dashboards.customer.recentOrders') }}</h2>
        <div v-if="recentOrders.length === 0" class="empty-mini">
          <p>{{ $t('dashboards.customer.noOrders') }}</p>
          <router-link to="/products" class="btn btn-primary btn-sm" style="margin-top: 12px"><i
              class="fas fa-shopping-bag"></i> {{ $t('dashboards.customer.startShopping') }}</router-link>
        </div>
        <div v-for="order in recentOrders" :key="order.id" class="list-item">
          <div><strong>{{ order.order_number }}</strong><span class="muted">{{ new
            Date(order.created_at).toLocaleDateString() }}</span></div>
          <span :class="['status-badge', `status-${order.status}`]">{{ $t(`ordersManage.${order.status}`) }}</span>
          <span class="item-price">TSh {{ Number(order.total).toLocaleString('en-TZ') }}</span>
        </div>
        <router-link v-if="recentOrders.length > 0" to="/orders" class="view-all">{{
          $t('dashboards.customer.viewAllOrders') }} <i class="fas fa-arrow-right"></i></router-link>
      </div>

      <div class="card dash-section">
        <h2><i class="fas fa-bolt"></i> {{ $t('dashboards.customer.quickActions') }}</h2>
        <div class="actions-grid">
          <router-link to="/products" class="action-tile"><i class="fas fa-shopping-bag"></i><span>{{
            $t('dashboards.customer.shopNow') }}</span></router-link>
          <router-link to="/cart" class="action-tile"><i class="fas fa-cart-plus"></i><span>{{
            $t('dashboards.customer.myCart') }}</span></router-link>
          <router-link to="/orders" class="action-tile"><i class="fas fa-receipt"></i><span>{{
            $t('dashboards.customer.myOrders') }}</span></router-link>
          <router-link to="/support" class="action-tile"><i class="fas fa-headset"></i><span>{{
            $t('dashboards.customer.support') }}</span></router-link>
          <router-link to="/account" class="action-tile"><i class="fas fa-user-pen"></i><span>{{
            $t('dashboards.customer.editProfile') }}</span></router-link>
          <router-link to="/account" class="action-tile"><i class="fas fa-location-dot"></i><span>{{
            $t('dashboards.customer.addressesAction') }}</span></router-link>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { orderApi, addressApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const authStore = useAuthStore()
const stats = ref({ totalOrders: 0, pendingOrders: 0, deliveredOrders: 0, addresses: 0 })
const recentOrders = ref([])
const loading = ref(true)

const hasActiveOrders = computed(() => recentOrders.value.some(o => ['pending', 'paid', 'processing', 'shipped'].includes(o.status)))

onMounted(async () => {
  await authStore.fetchProfile()
  try {
    const [orderRes, addrRes] = await Promise.all([
      orderApi.getAll({ per_page: 5 }),
      addressApi.getAll(),
    ])
    const orders = orderRes.data.data || []
    recentOrders.value = orders
    stats.value.totalOrders = orderRes.data.total || orders.length
    stats.value.pendingOrders = orders.filter(o => ['pending_payment', 'paid', 'processing'].includes(o.status)).length
    stats.value.deliveredOrders = orders.filter(o => o.status === 'delivered').length
    stats.value.addresses = addrRes.data?.length || 0
  } catch { /* empty */ }
  loading.value = false
})
</script>

<style scoped>
.dashboard-page {
  padding: 32px 0;
}

.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.dash-header h1 {
  font-size: 28px;
  margin-bottom: 4px;
}

.dash-header p {
  color: #888;
}

.role-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.role-badge.customer {
  background: #eafaf1;
  color: #27ae60;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-icon.orders {
  background: #eaf4ff;
  color: #2980b9;
}

.stat-icon.pending {
  background: #fff3cd;
  color: #856404;
}

.stat-icon.delivered {
  background: #eafaf1;
  color: #27ae60;
}

.stat-icon.addresses {
  background: #fef5f5;
  color: #e74c3c;
}

.stat-value {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: #333;
}

.stat-label {
  font-size: 13px;
  color: #888;
}

.account-alert {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: #eaf4ff;
  border: 1px solid #90c8ff;
  border-radius: 8px;
  margin-bottom: 24px;
}

.account-alert i {
  font-size: 24px;
  color: #2980b9;
}

.account-alert div {
  flex: 1;
}

.account-alert strong {
  display: block;
  font-size: 15px;
  color: #2980b9;
}

.account-alert p {
  margin: 2px 0 0;
  font-size: 13px;
  color: #5a9fd4;
}

.dash-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.dash-section {
  padding: 24px;
}

.dash-section h2 {
  font-size: 17px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dash-section h2 i {
  color: #e74c3c;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 14px;
}

.list-item:last-child {
  border-bottom: none;
}

.muted {
  color: #999;
  font-size: 12px;
  margin-left: 8px;
}

.item-price {
  margin-left: auto;
  font-weight: 600;
  color: #e74c3c;
}

.empty-mini {
  text-align: center;
  padding: 24px;
  color: #999;
  font-size: 14px;
}

.view-all {
  display: block;
  text-align: center;
  margin-top: 12px;
  color: #e74c3c;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}

.view-all:hover {
  text-decoration: underline;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 13px;
  text-decoration: none;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: #e74c3c;
  color: #fff;
}

.btn-primary:hover {
  background: #c0392b;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
}

.status-badge {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: capitalize;
  white-space: nowrap;
}

.status-pending_payment {
  background: #fff3cd;
  color: #856404;
}

.status-paid {
  background: #d4edda;
  color: #155724;
}

.status-processing {
  background: #cce5ff;
  color: #004085;
}

.status-shipped {
  background: #e2d5f1;
  color: #563d7c;
}

.status-delivered {
  background: #d4edda;
  color: #155724;
}

.status-cancelled {
  background: #f8d7da;
  color: #721c24;
}

.status-inactive {
  background: #e9ecef;
  color: #6c757d;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.action-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 12px;
  border: 1px solid #eee;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.action-tile i {
  font-size: 22px;
  color: #e74c3c;
}

.action-tile:hover {
  border-color: #e74c3c;
  background: #fef5f5;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .dash-grid {
    grid-template-columns: 1fr;
  }

  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
