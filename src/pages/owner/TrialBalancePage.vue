<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-scale-unbalanced" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('accounting.reports.trialBalance') }}</h1>
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
          <div class="stat-icon"><i class="fas fa-arrow-down"></i></div>
          <div><span class="stat-value">TSh {{ formatPrice(data.total_debit) }}</span><span class="stat-label">{{ $t('accounting.reports.totalDebit') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon credit"><i class="fas fa-arrow-up"></i></div>
          <div><span class="stat-value">TSh {{ formatPrice(data.total_credit) }}</span><span class="stat-label">{{ $t('accounting.reports.totalCredit') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" :class="data.is_balanced ? 'balanced' : 'unbalanced'">
            <i :class="data.is_balanced ? 'fas fa-check-circle' : 'fas fa-exclamation-triangle'"></i>
          </div>
          <div>
            <span class="stat-value" :class="{ 'text-red': !data.is_balanced }">{{ data.is_balanced ? $t('accounting.reports.balanced') : $t('accounting.reports.unbalanced') }}</span>
            <span class="stat-label">{{ $t('accounting.reports.status') }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="table-wrap">
          <table class="sa-table">
            <thead>
              <tr>
                <th>{{ $t('accounting.journal.account') }}</th>
                <th class="amount-col">{{ $t('accounting.journal.debit') }}</th>
                <th class="amount-col">{{ $t('accounting.journal.credit') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in data.accounts" :key="item.account.id">
                <td>
                  <strong>{{ item.account.code }}</strong>
                  <span style="margin-left: 8px;">{{ item.account.name }}</span>
                  <span :class="['type-tag', item.account.type]">{{ item.account.type }}</span>
                </td>
                <td class="amount-col">{{ item.debit > 0 ? formatPrice(item.debit) : '-' }}</td>
                <td class="amount-col">{{ item.credit > 0 ? formatPrice(item.credit) : '-' }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td><strong>{{ $t('accounting.journal.totals') }}</strong></td>
                <td class="amount-col"><strong>TSh {{ formatPrice(data.total_debit) }}</strong></td>
                <td class="amount-col"><strong>TSh {{ formatPrice(data.total_credit) }}</strong></td>
              </tr>
            </tfoot>
          </table>
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
const data = ref({ accounts: [], total_debit: 0, total_credit: 0, is_balanced: true })

function formatPrice(v) { return Number(v || 0).toLocaleString('en-TZ') }

async function loadReport() {
  loading.value = true
  try {
    const res = await accountingReportApi.getTrialBalance({ as_of: asOf.value })
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
.stat-icon { width: 48px; height: 48px; border-radius: 10px; background: #fef5f5; display: flex; align-items: center; justify-content: center; color: #e74c3c; font-size: 20px; flex-shrink: 0; }
.stat-icon.credit { background: #eef6ff; color: #3498db; }
.stat-icon.balanced { background: #f0fff4; color: #27ae60; }
.stat-icon.unbalanced { background: #fef9e7; color: #e74c3c; }
.stat-value { display: block; font-size: 20px; font-weight: 700; }
.stat-label { display: block; font-size: 12px; color: #888; margin-top: 2px; }
.text-red { color: #e74c3c; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); overflow: hidden; }
.table-wrap { overflow-x: auto; }
.sa-table { width: 100%; border-collapse: collapse; }
.sa-table th { padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 2px solid #f0f0f0; background: #fafafa; }
.sa-table td { padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.sa-table tfoot td { border-top: 2px solid #e0e0e0; background: #fafafa; }
.amount-col { text-align: right; font-family: 'JetBrains Mono', monospace; }
.type-tag { display: inline-block; margin-left: 8px; padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: 600; text-transform: uppercase; }
.type-tag.asset { background: #eef6ff; color: #3498db; }
.type-tag.liability { background: #fef5f5; color: #e74c3c; }
.type-tag.equity { background: #f5f0ff; color: #9b59b6; }
.type-tag.revenue { background: #f0fff4; color: #27ae60; }
.type-tag.expense { background: #fef9e7; color: #f39c12; }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .stats-grid { grid-template-columns: 1fr; }
}
</style>
