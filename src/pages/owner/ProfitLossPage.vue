<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-chart-pie" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('accounting.reports.profitLoss') }}</h1>
      </div>
      <div class="header-actions">
        <div class="date-range">
          <input v-model="from" type="date" @change="loadReport" />
          <span>—</span>
          <input v-model="to" type="date" @change="loadReport" />
        </div>
        <router-link to="/owner/accounting" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.back') }}</router-link>
      </div>
    </div>

    <SkeletonLoader v-if="loading" type="stats" :count="3" />
    <template v-else>
      <div class="stats-grid">
        <div class="stat-card revenue-card">
          <div class="stat-icon"><i class="fas fa-arrow-trend-up"></i></div>
          <div><span class="stat-value text-green">TSh {{ formatPrice(data.total_revenue) }}</span><span class="stat-label">{{ $t('accounting.reports.totalRevenue') }}</span></div>
        </div>
        <div class="stat-card expense-card">
          <div class="stat-icon expense"><i class="fas fa-arrow-trend-down"></i></div>
          <div><span class="stat-value text-red">TSh {{ formatPrice(data.total_expenses) }}</span><span class="stat-label">{{ $t('accounting.reports.totalExpenses') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" :class="data.net_income >= 0 ? 'balanced' : 'unbalanced'">
            <i :class="data.net_income >= 0 ? 'fas fa-plus-circle' : 'fas fa-minus-circle'"></i>
          </div>
          <div>
            <span class="stat-value" :class="data.net_income >= 0 ? 'text-green' : 'text-red'">
              TSh {{ formatPrice(Math.abs(data.net_income)) }}
            </span>
            <span class="stat-label">{{ data.net_income >= 0 ? $t('accounting.reports.netIncome') : $t('accounting.reports.netLoss') }}</span>
          </div>
        </div>
      </div>

      <div class="report-grid">
        <div class="card">
          <h3 class="card-title revenue-title"><i class="fas fa-arrow-up"></i> {{ $t('accounting.reports.revenue') }}</h3>
          <div v-if="data.revenue.length === 0" class="empty-state">{{ $t('accounting.reports.noRevenue') }}</div>
          <div v-for="item in data.revenue" :key="item.id" class="report-line">
            <span class="line-label">{{ item.code }} {{ item.name }}</span>
            <span class="line-amount text-green">TSh {{ formatPrice(item.amount) }}</span>
          </div>
        </div>
        <div class="card">
          <h3 class="card-title expense-title"><i class="fas fa-arrow-down"></i> {{ $t('accounting.reports.expenses') }}</h3>
          <div v-if="data.expenses.length === 0" class="empty-state">{{ $t('accounting.reports.noExpenses') }}</div>
          <div v-for="item in data.expenses" :key="item.id" class="report-line">
            <span class="line-label">{{ item.code }} {{ item.name }}</span>
            <span class="line-amount text-red">TSh {{ formatPrice(item.amount) }}</span>
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
const from = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0])
const to = ref(new Date().toISOString().split('T')[0])
const data = ref({ revenue: [], total_revenue: 0, expenses: [], total_expenses: 0, net_income: 0 })

function formatPrice(v) { return Number(v || 0).toLocaleString('en-TZ') }

async function loadReport() {
  loading.value = true
  try {
    const res = await accountingReportApi.getProfitLoss({ from: from.value, to: to.value })
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
.date-range { display: flex; align-items: center; gap: 8px; }
.date-range input { padding: 8px 12px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 14px; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; color: #666; text-decoration: none; font-size: 13px; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { background: #fff; border-radius: 10px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.stat-icon { width: 48px; height: 48px; border-radius: 10px; background: #f0fff4; display: flex; align-items: center; justify-content: center; color: #27ae60; font-size: 20px; flex-shrink: 0; }
.stat-icon.expense { background: #fef5f5; color: #e74c3c; }
.stat-icon.balanced { background: #f0fff4; color: #27ae60; }
.stat-icon.unbalanced { background: #fef5f5; color: #e74c3c; }
.stat-value { display: block; font-size: 20px; font-weight: 700; }
.stat-label { display: block; font-size: 12px; color: #888; margin-top: 2px; }
.text-green { color: #27ae60; }
.text-red { color: #e74c3c; }

.report-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); padding: 20px; }
.card-title { font-size: 15px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.revenue-title { color: #27ae60; }
.expense-title { color: #e74c3c; }
.report-line { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f5f5f5; }
.report-line:last-child { border-bottom: none; }
.line-label { font-size: 13px; color: #555; }
.line-amount { font-size: 13px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.empty-state { text-align: center; color: #aaa; padding: 24px; font-size: 13px; }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .stats-grid, .report-grid { grid-template-columns: 1fr; }
}
</style>
