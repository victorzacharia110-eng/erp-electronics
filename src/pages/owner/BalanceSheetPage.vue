<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-balance-scale" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('accounting.reports.balanceSheet') }}</h1>
      </div>
      <div class="header-actions">
        <div class="date-field">
          <label>{{ $t('accounting.reports.asOf') }}</label>
          <input v-model="asOf" type="date" @change="loadReport" />
        </div>
        <router-link to="/owner/accounting" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.back') }}</router-link>
      </div>
    </div>

    <SkeletonLoader v-if="loading" type="stats" :count="3" />
    <template v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon asset"><i class="fas fa-building"></i></div>
          <div><span class="stat-value">TSh {{ formatPrice(data.total_assets) }}</span><span class="stat-label">{{ $t('accounting.reports.totalAssets') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon liability"><i class="fas fa-hand-holding-dollar"></i></div>
          <div><span class="stat-value">TSh {{ formatPrice(data.total_liabilities) }}</span><span class="stat-label">{{ $t('accounting.reports.totalLiabilities') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon equity"><i class="fas fa-user-shield"></i></div>
          <div><span class="stat-value">TSh {{ formatPrice(data.total_equity) }}</span><span class="stat-label">{{ $t('accounting.reports.totalEquity') }}</span></div>
        </div>
      </div>

      <div class="report-grid">
        <div class="card">
          <h3 class="card-title asset-title"><i class="fas fa-building"></i> {{ $t('accounting.reports.assets') }}</h3>
          <div v-if="data.assets.length === 0" class="empty-state">{{ $t('accounting.reports.noAssets') }}</div>
          <div v-for="item in data.assets" :key="item.id" class="report-line">
            <span class="line-label">{{ item.code }} {{ item.name }}</span>
            <span class="line-amount">TSh {{ formatPrice(item.amount) }}</span>
          </div>
          <div class="report-total">
            <span>{{ $t('accounting.reports.totalAssets') }}</span>
            <span class="line-amount">TSh {{ formatPrice(data.total_assets) }}</span>
          </div>
        </div>
        <div class="card">
          <h3 class="card-title liability-title"><i class="fas fa-hand-holding-dollar"></i> {{ $t('accounting.reports.liabilitiesEquity') }}</h3>
          <div v-if="data.liabilities.length === 0 && data.equity.length === 0" class="empty-state">{{ $t('accounting.reports.noLiabilitiesEquity') }}</div>
          <div v-for="item in data.liabilities" :key="'l'+item.id" class="report-line">
            <span class="line-label">{{ item.code }} {{ item.name }}</span>
            <span class="line-amount">TSh {{ formatPrice(item.amount) }}</span>
          </div>
          <div v-if="data.liabilities.length > 0 && data.equity.length > 0" class="report-divider"></div>
          <div v-for="item in data.equity" :key="'e'+item.id" class="report-line">
            <span class="line-label">{{ item.code }} {{ item.name }}</span>
            <span class="line-amount">TSh {{ formatPrice(item.amount) }}</span>
          </div>
          <div class="report-total">
            <span>{{ $t('accounting.reports.totalLiabilitiesEquity') }}</span>
            <span class="line-amount">TSh {{ formatPrice(data.total_liabilities + data.total_equity) }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { accountingReportApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const loading = ref(true)
const asOf = ref(new Date().toISOString().split('T')[0])
const data = ref({ assets: [], total_assets: 0, liabilities: [], total_liabilities: 0, equity: [], total_equity: 0 })

function formatPrice(v) { return Number(v || 0).toLocaleString('en-TZ') }

async function loadReport() {
  loading.value = true
  try {
    const res = await accountingReportApi.getBalanceSheet({ as_of: asOf.value })
    data.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadReport)
</script>

<style scoped>
.dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.dash-header h1 { font-size: 24px; font-weight: 700; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.date-field { display: flex; align-items: center; gap: 8px; }
.date-field label { font-size: 13px; color: #666; font-weight: 500; }
.date-field input { padding: 8px 12px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 14px; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; color: #666; text-decoration: none; font-size: 13px; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { background: #fff; border-radius: 10px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.stat-icon { width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.stat-icon.asset { background: #eef6ff; color: #3498db; }
.stat-icon.liability { background: #fef5f5; color: #e74c3c; }
.stat-icon.equity { background: #f5f0ff; color: #9b59b6; }
.stat-value { display: block; font-size: 20px; font-weight: 700; }
.stat-label { display: block; font-size: 12px; color: #888; margin-top: 2px; }

.report-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); padding: 20px; }
.card-title { font-size: 15px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.asset-title { color: #3498db; }
.liability-title { color: #e74c3c; }
.report-line { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f5f5f5; }
.report-line:last-child { border-bottom: none; }
.line-label { font-size: 13px; color: #555; }
.line-amount { font-size: 13px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.report-divider { height: 1px; background: #e0e0e0; margin: 8px 0; }
.report-total { display: flex; justify-content: space-between; padding: 12px 0 0; border-top: 2px solid #e0e0e0; margin-top: 8px; font-weight: 700; font-size: 14px; }
.empty-state { text-align: center; color: #aaa; padding: 24px; font-size: 13px; }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .stats-grid, .report-grid { grid-template-columns: 1fr; }
}
</style>
