<template>
  <div class="dashboard-page container">
    <SkeletonLoader v-if="loading" type="stats" :count="4" />
    <template v-else>
    <div class="dash-header">
      <div>
        <h1>{{ $t('dashboards.owner.title') }}</h1>
        <p>{{ $t('dashboards.owner.welcome', { name: authStore.user?.name }) }}</p>
      </div>
      <span class="role-badge owner"><i class="fas fa-crown"></i> {{ $t('dashboards.owner.role') }}</span>
    </div>

    <div v-if="businessStore.mine.length > 1" class="business-switcher">
      <span class="switcher-label"><i class="fas fa-store"></i> {{ $t('dashboards.owner.selectBusiness') }}</span>
      <div class="switcher-chips">
        <button
          v-for="b in businessStore.mine"
          :key="b.id"
          :class="['business-chip', { active: businessStore.current?.id === b.id }]"
          @click="selectBusiness(b)"
        >
          <i class="fas fa-store"></i>
          {{ b.store_name }}
        </button>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-dollar-sign"></i></div>
        <div><span class="stat-value">TSh {{ formatPrice(stats.revenue) }}</span><span class="stat-label">{{
          $t('dashboards.owner.totalRevenue') }}</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orders"><i class="fas fa-shopping-bag"></i></div>
        <div><span class="stat-value">{{ stats.totalOrders }}</span><span class="stat-label">{{
          $t('dashboards.owner.totalOrders') }}</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon products"><i class="fas fa-box"></i></div>
        <div><span class="stat-value">{{ stats.totalProducts }}</span><span class="stat-label">{{
          $t('dashboards.owner.products') }}</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon users"><i class="fas fa-users"></i></div>
        <div><span class="stat-value">{{ stats.totalEmployees }}</span><span class="stat-label">{{
          $t('dashboards.owner.employees') }}</span></div>
      </div>
    </div>

    <SalesCharts @loaded="onAnalyticsLoaded" />

    <div class="dash-grid">
      <div class="card dash-section">
        <div class="section-header-row">
          <h2><i class="fas fa-clock"></i> {{ $t('dashboards.owner.recentOrders') }}</h2>
          <router-link to="/orders" class="view-all-link">{{ $t('common.viewAll') }} <i
              class="fas fa-arrow-right"></i></router-link>
        </div>
        <div v-if="recentOrders.length === 0" class="empty-mini">
          <i class="fas fa-receipt"></i>
          <p>{{ $t('dashboards.owner.noOrders') }}</p>
        </div>
        <div v-for="order in recentOrders" :key="order.id" class="list-item">
          <div><strong>{{ order.order_number }}</strong><span class="muted">{{ new
            Date(order.created_at).toLocaleDateString() }}</span></div>
          <span :class="['status-badge', `status-${order.status}`]">{{ $t(`ordersManage.${order.status}`) }}</span>
          <span class="item-price">TSh {{ Number(order.total).toLocaleString('en-TZ') }}</span>
        </div>
      </div>

      <div class="card dash-section">
        <h2><i class="fas fa-gauge-high"></i> {{ $t('dashboards.owner.quickActions') }}</h2>
        <div class="actions-grid">
          <router-link to="/owner/employees" class="action-tile"><i class="fas fa-users-gear"></i><span>{{
            $t('dashboards.owner.employeesAction') }}</span></router-link>
          <router-link to="/owner/branches" class="action-tile"><i class="fas fa-store"></i><span>{{
            $t('dashboards.owner.branchesAction') }}</span></router-link>
          <router-link to="/owner/products" class="action-tile"><i class="fas fa-box"></i><span>{{
            $t('dashboards.owner.productsAction') }}</span></router-link>
          <router-link to="/owner/orders" class="action-tile"><i class="fas fa-receipt"></i><span>{{
            $t('dashboards.owner.ordersAction') }}</span></router-link>
          <router-link to="/owner/customers" class="action-tile"><i class="fas fa-users"></i><span>{{
            $t('dashboards.owner.customersAction') }}</span></router-link>
          <router-link to="/owner/reports" class="action-tile"><i class="fas fa-chart-line"></i><span>{{
            $t('dashboards.owner.reportsAction') }}</span></router-link>
          <router-link to="/owner/inventory" class="action-tile"><i
              class="fas fa-warehouse"></i><span>{{ $t('dashboards.owner.inventoryAction') }}</span></router-link>
          <router-link to="/owner/purchase-orders" class="action-tile"><i
              class="fas fa-truck-loading"></i><span>{{ $t('dashboards.owner.purchaseOrdersAction') }}</span></router-link>
          <router-link to="/owner/commissions" class="action-tile"><i
              class="fas fa-coins"></i><span>{{ $t('dashboards.owner.commissionsAction') }}</span></router-link>
          <router-link to="/owner/wingas" class="action-tile"><i
              class="fas fa-user-tie"></i><span>{{ $t('dashboards.owner.wingasAction') }}</span></router-link>
          <router-link to="/owner/winga-commissions" class="action-tile"><i
              class="fas fa-money-bill-wave"></i><span>{{ $t('dashboards.owner.wingaCommissionsAction') }}</span></router-link>
          <router-link to="/owner/suppliers" class="action-tile"><i
              class="fas fa-truck"></i><span>{{ $t('dashboards.owner.suppliersAction') }}</span></router-link>
          <router-link to="/owner/stock-alerts" class="action-tile" :class="{ 'alert-tile': stockAlertCount > 0 }">
            <i class="fas fa-bell"></i>
            <span>{{ $t('dashboards.owner.stockAlerts') }}</span>
            <span v-if="stockAlertCount > 0" class="alert-badge">{{ stockAlertCount }}</span>
          </router-link>
          <router-link to="/owner/payment-settings" class="action-tile"><i class="fas fa-gear"></i><span>{{
            $t('dashboards.owner.settingsAction') }}</span></router-link>
          <router-link to="/owner/shipping" class="action-tile"><i class="fas fa-truck"></i><span>{{
            $t('dashboards.owner.shippingSettings') }}</span></router-link>
          <router-link to="/owner/accounting" class="action-tile"><i class="fas fa-calculator"></i><span>{{
            $t('dashboards.owner.accountingAction') }}</span></router-link>
          <router-link to="/owner/billing" class="action-tile"><i class="fas fa-credit-card"></i><span>{{
            $t('dashboards.owner.billingAction') }}</span></router-link>
          <router-link to="/owner/store-settings" class="action-tile"><i class="fas fa-store"></i><span>{{
            $t('dashboards.owner.storeSettingsAction') }}</span></router-link>
          <router-link to="/account" class="action-tile"><i class="fas fa-user-pen"></i><span>{{ $t('account.profile') }}</span></router-link>
        </div>
      </div>
    </div>

    <div class="card dash-section">
      <div class="section-header-row">
        <h2><i class="fas fa-box"></i> {{ $t('dashboards.owner.productsOverview') }}</h2>
        <router-link to="/owner/products" class="view-all-link">{{ $t('common.viewAll') }} <i
            class="fas fa-arrow-right"></i></router-link>
      </div>
      <div v-if="products.length === 0" class="empty-mini">
        <i class="fas fa-box-open"></i>
        <p>{{ $t('dashboards.owner.noProducts') }}</p>
      </div>
      <div v-for="product in products.slice(0, 5)" :key="product.id" class="list-item">
        <span class="prod-name">{{ product.name }}</span>
        <span class="prod-brand muted">{{ product.brand }}</span>
        <span class="item-price">TSh {{ Number(product.price).toLocaleString('en-TZ') }}</span>
      </div>
    </div>

    <AiSuggestions :analytics-data="analyticsData" />

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas fa-info-circle"></i> {{ toastMsg }}
    </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useBusinessStore } from '@/stores/business'
import { productManageApi, orderApi, employeeApi, stockAlertApi } from '@/api'
import SalesCharts from './analytics/SalesCharts.vue'
import AiSuggestions from './analytics/AiSuggestions.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const authStore = useAuthStore()
const businessStore = useBusinessStore()
const stats = ref({ revenue: 0, totalOrders: 0, totalProducts: 0, totalEmployees: 0 })
const recentOrders = ref([])
const stockAlertCount = ref(0)
const products = ref([])
const toastMsg = ref('')
const analyticsData = ref(null)
const loading = ref(true)

function onAnalyticsLoaded(data) {
  analyticsData.value = data
}

function formatPrice(v) { return Number(v).toLocaleString('en-TZ') }

function selectBusiness(business) {
  businessStore.setCurrent(business)
  loadDashboard()
}

async function loadDashboard() {
  try {
    const [prodRes, orderRes, empRes, alertRes] = await Promise.all([
      productManageApi.getAll({ per_page: 5 }),
      orderApi.getAll({ per_page: 5 }),
      employeeApi.getAll().catch(() => ({ data: [] })),
      stockAlertApi.getCount().catch(() => ({ data: { count: 0 } })),
    ])
    products.value = prodRes.data.data || []
    stats.value.totalProducts = prodRes.data.total || 0
    const orders = orderRes.data.data || []
    recentOrders.value = orders
    stats.value.totalOrders = orderRes.data.total || orders.length
    stats.value.revenue = orders.reduce((s, o) => s + Number(o.total || 0), 0)
    stats.value.totalEmployees = empRes.data?.data?.length || 0
    stockAlertCount.value = alertRes.data?.count || 0
  } catch { /* empty */ }
  loading.value = false
}

onMounted(async () => {
  await authStore.fetchProfile()
  try {
    await businessStore.fetchMine()
  } catch { /* empty */ }
  businessStore.restoreFromStorage()
  if (!businessStore.current && businessStore.mine.length === 1) {
    businessStore.setCurrent(businessStore.mine[0])
  }
  await loadDashboard()
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

.role-badge.owner {
  background: #fef5f5;
  color: #e74c3c;
}

.business-switcher {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 24px;
}

.switcher-label {
  font-size: 13px;
  font-weight: 600;
  color: #888;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.switcher-label i {
  color: #e74c3c;
}

.switcher-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.business-chip {
  padding: 8px 14px;
  border: 1px solid #eee;
  border-radius: 20px;
  background: #fff;
  color: #555;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
}

.business-chip:hover {
  border-color: #e74c3c;
}

.business-chip.active {
  background: #e74c3c;
  border-color: #e74c3c;
  color: #fff;
}

.business-chip.active i {
  color: #fff;
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
  background: #fef5f5;
  color: #e74c3c;
}

.stat-icon.orders {
  background: #eaf4ff;
  color: #2980b9;
}

.stat-icon.products {
  background: #eafaf1;
  color: #27ae60;
}

.stat-icon.users {
  background: #fef9e7;
  color: #f39c12;
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

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header-row h2 {
  margin-bottom: 0;
}

.view-all-link {
  font-size: 13px;
  color: #e74c3c;
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: opacity 0.2s;
}

.view-all-link:hover {
  opacity: 0.8;
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
}

.item-price {
  margin-left: auto;
  font-weight: 600;
  color: #e74c3c;
}

.prod-name {
  font-weight: 500;
}

.prod-brand {
  margin-left: auto;
}

.empty-mini {
  text-align: center;
  padding: 32px 16px;
  color: #999;
  font-size: 14px;
}

.empty-mini i {
  font-size: 28px;
  color: #ddd;
  margin-bottom: 12px;
  display: block;
}

.empty-mini p {
  margin: 0;
  line-height: 1.5;
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
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.action-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 24px 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
  background: #fff;
  cursor: pointer;
}

.action-tile i {
  font-size: 24px;
  color: #e74c3c;
}

.action-tile:hover {
  border-color: #e74c3c;
  background: #fef5f5;
}

.alert-tile {
  border-color: #e74c3c;
  background: #fef5f5;
}

.alert-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #e74c3c;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
}

.action-tile {
  position: relative;
}

.placeholder-btn {
  font-family: 'Inter', sans-serif;
}

.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: #2c3e50;
  color: #fff;
  padding: 14px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  z-index: 2000;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease;
}

.toast i {
  color: #f39c12;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
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
