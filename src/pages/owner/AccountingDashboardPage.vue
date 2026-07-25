<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-calculator" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('accounting.dashboard.title') }}</h1>
        <p>{{ $t('accounting.dashboard.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <router-link to="/owner" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.backToDashboard') }}</router-link>
      </div>
    </div>

    <SkeletonLoader v-if="loading" type="stats" :count="4" />
    <template v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-file-invoice-dollar"></i></div>
          <div><span class="stat-value">TSh {{ formatPrice(summary.totalRevenue) }}</span><span class="stat-label">{{ $t('accounting.dashboard.totalRevenue') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orders"><i class="fas fa-file-invoice"></i></div>
          <div><span class="stat-value">{{ summary.totalEntries }}</span><span class="stat-label">{{ $t('accounting.dashboard.postedEntries') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon products"><i class="fas fa-scale-balanced"></i></div>
          <div><span class="stat-value" :class="{ 'text-red': !summary.isBalanced }">{{ summary.isBalanced ? $t('accounting.dashboard.balanced') : $t('accounting.dashboard.unbalanced') }}</span><span class="stat-label">{{ $t('accounting.dashboard.trialBalance') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon users"><i class="fas fa-wallet"></i></div>
          <div><span class="stat-value">TSh {{ formatPrice(summary.netIncome) }}</span><span class="stat-label">{{ $t('accounting.dashboard.netIncome') }}</span></div>
        </div>
      </div>

      <div class="dash-grid">
        <div class="card dash-section">
          <h2><i class="fas fa-link"></i> {{ $t('accounting.dashboard.quickLinks') }}</h2>
          <div class="actions-grid">
            <router-link to="/owner/accounting/chart-of-accounts" class="action-tile">
              <i class="fas fa-book"></i><span>{{ $t('accounting.dashboard.chartOfAccounts') }}</span>
            </router-link>
            <router-link to="/owner/accounting/journal" class="action-tile">
              <i class="fas fa-journal-whills"></i><span>{{ $t('accounting.dashboard.journalEntries') }}</span>
            </router-link>
            <router-link to="/owner/accounting/journal/new" class="action-tile">
              <i class="fas fa-plus-circle"></i><span>{{ $t('accounting.dashboard.newEntry') }}</span>
            </router-link>
            <router-link to="/owner/accounting/trial-balance" class="action-tile">
              <i class="fas fa-scale-unbalanced"></i><span>{{ $t('accounting.dashboard.trialBalance') }}</span>
            </router-link>
            <router-link to="/owner/accounting/profit-loss" class="action-tile">
              <i class="fas fa-chart-pie"></i><span>{{ $t('accounting.dashboard.profitLoss') }}</span>
            </router-link>
            <router-link to="/owner/accounting/balance-sheet" class="action-tile">
              <i class="fas fa-balance-scale"></i><span>{{ $t('accounting.dashboard.balanceSheet') }}</span>
            </router-link>
            <router-link to="/owner/accounting/general-ledger" class="action-tile">
              <i class="fas fa-list-alt"></i><span>{{ $t('accounting.dashboard.generalLedger') }}</span>
            </router-link>
          </div>
        </div>

        <div class="card dash-section">
          <h2><i class="fas fa-clock"></i> {{ $t('accounting.dashboard.recentEntries') }}</h2>
          <div v-if="recentEntries.length === 0" class="empty-mini">
            <i class="fas fa-journal-whills"></i>
            <p>{{ $t('accounting.dashboard.noEntries') }}</p>
          </div>
          <div v-for="entry in recentEntries" :key="entry.id" class="list-item">
            <div>
              <strong>{{ entry.reference }}</strong>
              <span class="muted">{{ entry.description }}</span>
            </div>
            <span :class="['status-badge', `status-${entry.status}`]">{{ entry.status }}</span>
            <span class="item-price">TSh {{ Number(entry.total_debit || 0).toLocaleString('en-TZ') }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { accountingReportApi, journalApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const loading = ref(true)
const summary = ref({ totalRevenue: 0, totalEntries: 0, isBalanced: true, netIncome: 0 })
const recentEntries = ref([])

function formatPrice(v) {
  return Number(v || 0).toLocaleString('en-TZ')
}

onMounted(async () => {
  try {
    const [plRes, tbRes, jeRes] = await Promise.all([
      accountingReportApi.getProfitLoss(),
      accountingReportApi.getTrialBalance(),
      journalApi.getAll({ per_page: 5 }),
    ])
    summary.value.totalRevenue = plRes.data.total_revenue
    summary.value.netIncome = plRes.data.net_income
    summary.value.isBalanced = tbRes.data.is_balanced
    summary.value.totalEntries = jeRes.data.total || jeRes.data.data?.length || 0
    recentEntries.value = jeRes.data.data?.slice(0, 5) || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.dash-header h1 { font-size: 24px; font-weight: 700; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; color: #666; text-decoration: none; font-size: 13px; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { background: #fff; border-radius: 10px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.stat-icon { width: 48px; height: 48px; border-radius: 10px; background: #fef5f5; display: flex; align-items: center; justify-content: center; color: #e74c3c; font-size: 20px; flex-shrink: 0; }
.stat-icon.orders { background: #eef6ff; color: #3498db; }
.stat-icon.products { background: #f0fff4; color: #27ae60; }
.stat-icon.users { background: #fef9e7; color: #f39c12; }
.stat-value { display: block; font-size: 20px; font-weight: 700; }
.stat-label { display: block; font-size: 12px; color: #888; margin-top: 2px; }
.text-red { color: #e74c3c; }

.dash-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.dash-section { padding: 24px; }
.dash-section h2 { font-size: 16px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.dash-section h2 i { color: #e74c3c; }

.actions-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
.action-tile { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 20px 12px; border: 1px solid #eee; border-radius: 10px; text-decoration: none; color: #333; transition: all 0.2s; }
.action-tile:hover { border-color: #e74c3c; color: #e74c3c; background: #fef5f5; }
.action-tile i { font-size: 24px; color: #e74c3c; }
.action-tile span { font-size: 12px; font-weight: 500; text-align: center; }

.list-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f5f5f5; }
.list-item:last-child { border-bottom: none; }
.list-item div:first-child { flex: 1; min-width: 0; }
.list-item strong { font-size: 13px; display: block; }
.muted { font-size: 12px; color: #888; display: block; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.item-price { font-size: 13px; font-weight: 600; white-space: nowrap; }
.empty-mini { text-align: center; padding: 32px; color: #aaa; }
.empty-mini i { font-size: 32px; margin-bottom: 8px; display: block; }
.status-badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.status-draft { background: #fef9e7; color: #7d6608; }
.status-posted { background: #f0fff4; color: #1e8449; }
.status-voided { background: #f8d7da; color: #721c24; }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .dash-grid { grid-template-columns: 1fr; }
  .actions-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
