<template>
  <div class="dashboard-page container">
    <SkeletonLoader v-if="loading" type="stats" :count="4" />
    <template v-else>
    <div class="dash-header">
      <div>
        <h1>{{ $t('dashboards.employee.title') }}</h1>
        <p>{{ $t('dashboards.employee.welcome', { name: authStore.user?.name }) }}</p>
      </div>
      <span class="role-badge employee"><i class="fas fa-id-badge"></i> {{ $t('dashboards.employee.role') }}</span>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon pending"><i class="fas fa-clock"></i></div>
        <div><span class="stat-value">{{ stats.pendingOrders }}</span><span class="stat-label">{{
          $t('dashboards.employee.pendingOrders') }}</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon processing"><i class="fas fa-cog"></i></div>
        <div><span class="stat-value">{{ stats.processingOrders }}</span><span class="stat-label">{{
          $t('dashboards.employee.processing') }}</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon shipped"><i class="fas fa-truck"></i></div>
        <div><span class="stat-value">{{ stats.shippedToday }}</span><span class="stat-label">{{
          $t('dashboards.employee.shippedToday') }}</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon products"><i class="fas fa-box"></i></div>
        <div><span class="stat-value">{{ stats.totalProducts }}</span><span class="stat-label">{{
          $t('dashboards.employee.totalProducts') }}</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon customers"><i class="fas fa-users"></i></div>
        <div><span class="stat-value">{{ stats.totalCustomers }}</span><span class="stat-label">{{
          $t('dashboards.employee.totalCustomers') }}</span></div>
      </div>
    </div>

    <div v-if="stats.pendingOrders > 0" class="alert-banner">
      <i class="fas fa-exclamation-triangle"></i>
      <div>
        <strong>{{ stats.pendingOrders }} {{ $t('dashboards.employee.pendingConfirmations') }}</strong>
        <p>{{ $t('dashboards.employee.pendingConfirmDesc') }}</p>
      </div>
      <router-link to="/employee/orders" class="btn btn-primary btn-sm">
        <i class="fas fa-check-circle"></i> {{ $t('dashboards.employee.goToOrders') }}
      </router-link>
    </div>

    <div v-if="unreadTickets > 0" class="alert-banner support-alert">
      <i class="fas fa-envelope"></i>
      <div>
        <strong>{{ unreadTickets }} {{ $t('dashboards.employee.newSupportMessages') }}</strong>
        <p>{{ $t('dashboards.employee.supportMessageDesc') }}</p>
      </div>
      <router-link to="/employee/support" class="btn btn-outline btn-sm">
        <i class="fas fa-inbox"></i> {{ $t('dashboards.employee.viewInbox') }}
      </router-link>
    </div>

    <div class="card dash-section accounting-issues">
      <div class="section-header-row">
        <h2><i class="fas fa-balance-scale"></i> {{ $t('dashboards.employee.accountingIssues') }}</h2>
        <span v-if="accountingIssues.length > 0" class="issue-total">
          {{ $t('dashboards.employee.issueCount', { count: accountingIssues.length }) }}
        </span>
      </div>
      <p class="issue-desc">{{ $t('dashboards.employee.accountingIssuesDesc') }}</p>
      <div v-if="accountingIssues.length === 0" class="empty-mini">{{ $t('dashboards.employee.accountingIssuesEmpty') }}</div>
      <div v-for="issue in accountingIssues" :key="issue.type" class="issue-item">
        <span class="sev-dot" :class="`sev-${issue.severity}`"></span>
        <div class="issue-body">
          <strong>{{ locale === 'sw' ? issue.title_sw : issue.title_en }}</strong>
          <span class="issue-desc-text">{{ locale === 'sw' ? issue.description_sw : issue.description_en }}</span>
        </div>
        <span class="issue-count">{{ issue.count }}</span>
      </div>
    </div>

    <div class="dash-grid">
      <div class="card dash-section">
        <div class="section-header-row">
          <h2><i class="fas fa-receipt"></i> {{ $t('dashboards.employee.recentOrders') }}</h2>
          <router-link to="/employee/orders" class="view-all-link">{{ $t('common.viewAll') }} <i
              class="fas fa-arrow-right"></i></router-link>
        </div>
        <div v-if="recentOrders.length === 0" class="empty-mini">{{ $t('dashboards.employee.noRecentOrders') }}</div>
        <div v-for="order in recentOrders" :key="order.id" class="list-item">
          <div><strong>{{ order.order_number }}</strong><span class="muted">{{ new
            Date(order.created_at).toLocaleDateString() }}</span></div>
          <span :class="['status-badge', `status-${order.status}`]">{{ $t(`ordersManage.${order.status}`) }}</span>
          <span class="item-price">TSh {{ Number(order.total).toLocaleString('en-TZ') }}</span>
        </div>
      </div>

      <div class="card dash-section">
        <h2><i class="fas fa-bolt"></i> {{ $t('dashboards.employee.quickActions') }}</h2>
        <div class="actions-grid">
          <router-link to="/employee/clients" class="action-tile"><i class="fas fa-users"></i><span>{{
            $t('dashboards.employee.clients') }}</span></router-link>
          <router-link to="/employee/orders" class="action-tile"><i class="fas fa-receipt"></i><span>{{
            $t('dashboards.employee.manageOrders') }}</span></router-link>
          <router-link to="/employee/support" class="action-tile"><i class="fas fa-inbox"></i><span>{{
            $t('dashboards.employee.supportInbox') }}</span></router-link>
          <router-link to="/employee/inbox" class="action-tile"><i class="fas fa-comments"></i><span>{{
            $t('dashboards.employee.ownerInbox') }}</span></router-link>
          <router-link to="/products" class="action-tile"><i class="fas fa-box"></i><span>{{
            $t('dashboards.employee.viewProducts') }}</span></router-link>
          <router-link to="/account" class="action-tile"><i class="fas fa-user"></i><span>{{
            $t('dashboards.employee.myProfile') }}</span></router-link>
          <router-link to="/employee/earnings" class="action-tile"><i class="fas fa-coins"></i><span>{{
            $t('dashboards.employee.myEarnings') }}</span></router-link>
          <router-link to="/employee/wingas" class="action-tile"><i class="fas fa-user-tie"></i><span>{{
            $t('dashboards.employee.wingas') }}</span></router-link>
          <router-link to="/employee/winga-commissions" class="action-tile"><i class="fas fa-money-bill-wave"></i><span>{{
            $t('dashboards.employee.wingaCommissions') }}</span></router-link>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { productApi, orderApi, customerApi, supportApi, accountingIssuesApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const { locale } = useI18n()
const authStore = useAuthStore()
const stats = ref({ pendingOrders: 0, processingOrders: 0, shippedToday: 0, totalProducts: 0, totalCustomers: 0 })
const recentOrders = ref([])
const unreadTickets = ref(0)
const accountingIssues = ref([])
const loading = ref(true)

onMounted(async () => {
  await authStore.fetchProfile()
  try {
    const [prodRes, orderRes, custRes, unreadRes, issuesRes] = await Promise.all([
      productApi.getAll({ per_page: 1 }),
      orderApi.getAll({ per_page: 10 }),
      customerApi.getAll().catch(() => ({ data: [] })),
      supportApi.getUnreadCount().catch(() => ({ data: { open_tickets: 0 } })),
      accountingIssuesApi.get().catch(() => ({ data: { issues: [] } })),
    ])
    stats.value.totalProducts = prodRes.data.total || 0
    stats.value.totalCustomers = custRes.data?.length || 0
    unreadTickets.value = unreadRes.data?.open_tickets || 0
    accountingIssues.value = issuesRes.data?.issues || []
    const orders = orderRes.data.data || []
    recentOrders.value = orders.slice(0, 5)
    stats.value.pendingOrders = orders.filter(o => o.status === 'pending').length
    stats.value.processingOrders = orders.filter(o => o.status === 'paid' || o.status === 'processing').length
    stats.value.shippedToday = orders.filter(o => o.status === 'shipped').length
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

.role-badge.employee {
  background: #eaf4ff;
  color: #2980b9;
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

.stat-icon.pending {
  background: #fff3cd;
  color: #856404;
}

.stat-icon.processing {
  background: #cce5ff;
  color: #004085;
}

.stat-icon.shipped {
  background: #e2d5f1;
  color: #563d7c;
}

.stat-icon.products {
  background: #eafaf1;
  color: #27ae60;
}

.stat-icon.customers {
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

.alert-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  margin-bottom: 24px;
}

.alert-banner i {
  font-size: 24px;
  color: #856404;
}

.alert-banner div {
  flex: 1;
}

.alert-banner strong {
  display: block;
  font-size: 15px;
  color: #856404;
}

.alert-banner p {
  margin: 2px 0 0;
  font-size: 13px;
  color: #a5841e;
}

.alert-banner.support-alert {
  background: #f0f7ff;
  border-color: #90c8ff;
}

.alert-banner.support-alert i {
  color: #2980b9;
}

.alert-banner.support-alert strong {
  color: #2980b9;
}

.alert-banner.support-alert p {
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

.accounting-issues {
  margin-bottom: 24px;
}

.accounting-issues h2 i {
  color: #8e44ad;
}

.issue-total {
  font-size: 13px;
  font-weight: 600;
  color: #8e44ad;
  background: #f4ecfb;
  border-radius: 12px;
  padding: 4px 12px;
}

.issue-desc {
  font-size: 13px;
  color: #888;
  margin: -8px 0 12px;
}

.issue-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 14px;
}

.issue-item:last-child {
  border-bottom: none;
}

.sev-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.sev-dot.sev-high {
  background: #e74c3c;
}

.sev-dot.sev-medium {
  background: #f39c12;
}

.sev-dot.sev-low {
  background: #95a5a6;
}

.issue-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.issue-body strong {
  font-size: 14px;
  color: #333;
}

.issue-desc-text {
  font-size: 12px;
  color: #999;
}

.issue-count {
  font-size: 14px;
  font-weight: 700;
  color: #8e44ad;
  background: #f4ecfb;
  border-radius: 12px;
  padding: 2px 10px;
  min-width: 40px;
  text-align: center;
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
