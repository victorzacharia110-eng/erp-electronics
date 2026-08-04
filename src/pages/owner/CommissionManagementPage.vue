<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-percentage" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('commissions.title') }}</h1>
        <p>{{ $t('commissions.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <router-link to="/owner/accounting" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('commissions.back') }}</router-link>
      </div>
    </div>

    <SkeletonLoader v-if="loading" type="stats" :count="4" />

    <template v-else>
      <div class="employee-cards">
        <div v-for="emp in employeeSummaries" :key="emp.id" class="emp-summary-card card">
          <div class="emp-summary-header">
            <div class="emp-avatar"><i class="fas fa-user"></i></div>
            <div class="emp-summary-info">
              <h3>{{ emp.name }}</h3>
              <span class="commission-rate">{{ $t('commissions.commissionRate', { rate: emp.commission_rate }) }}</span>
            </div>
          </div>
          <div class="emp-summary-stats">
            <div class="emp-stat">
              <span class="emp-stat-label">{{ $t('commissions.totalProfit') }}</span>
              <span class="emp-stat-value">TSh {{ Number(emp.total_profit || 0).toLocaleString('en-TZ') }}</span>
            </div>
            <div class="emp-stat">
              <span class="emp-stat-label">{{ $t('commissions.pending') }}</span>
              <span class="emp-stat-value pending-text">{{ emp.pending_count }} · TSh {{ Number(emp.pending_amount || 0).toLocaleString('en-TZ') }}</span>
            </div>
            <div class="emp-stat">
              <span class="emp-stat-label">{{ $t('commissions.paid') }}</span>
              <span class="emp-stat-value paid-text">{{ emp.paid_count }} · TSh {{ Number(emp.paid_amount || 0).toLocaleString('en-TZ') }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="pendingCommissions.length > 0" class="section-actions">
        <button class="btn btn-primary" :disabled="payAllLoading" @click="payAllPending">
          <i class="fas fa-check-double"></i> {{ payAllLoading ? $t('commissions.processing') : $t('commissions.payAllPending') }}
        </button>
      </div>

      <div class="card table-section">
        <div class="table-section-header">
          <h2><i class="fas fa-clock" style="color: #e74c3c;"></i> {{ $t('commissions.pendingCommissions') }}</h2>
          <span class="count-badge">{{ pendingCommissions.length }}</span>
        </div>
        <div class="table-wrap">
          <table class="sa-table">
            <thead>
              <tr>
                <th>{{ $t('commissions.employee') }}</th>
                <th>{{ $t('commissions.orderNumber') }}</th>
                <th>{{ $t('commissions.orderAmount') }}</th>
                <th>{{ $t('commissions.profit') }}</th>
                <th>{{ $t('commissions.rate') }}</th>
                <th>{{ $t('commissions.commission') }}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in pendingCommissions" :key="c.id">
                <td class="code-cell">{{ c.employee_name }}</td>
                <td>{{ c.order_number }}</td>
                <td class="amount-cell">TSh {{ Number(c.profit_amount || 0).toLocaleString('en-TZ') }}</td>
                <td>{{ c.commission_rate }}%</td>
                <td class="amount-cell">TSh {{ Number(c.commission_amount || 0).toLocaleString('en-TZ') }}</td>
                <td class="actions-cell">
                  <button class="btn btn-success btn-sm" :disabled="c._paying" @click="payCommission(c)">
                    <i class="fas fa-money-bill-wave"></i> {{ c._paying ? $t('commissions.paying') : $t('commissions.pay') }}
                  </button>
                </td>
              </tr>
              <tr v-if="pendingCommissions.length === 0">
                <td colspan="6" class="empty-row">{{ $t('commissions.noPendingCommissions') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card table-section">
        <div class="table-section-header">
          <h2><i class="fas fa-check-circle" style="color: #27ae60;"></i> {{ $t('commissions.paidCommissions') }}</h2>
          <span class="count-badge paid">{{ paidCommissions.length }}</span>
        </div>
        <div class="table-wrap">
          <table class="sa-table">
            <thead>
              <tr>
                <th>{{ $t('commissions.employee') }}</th>
                <th>{{ $t('commissions.orderNumber') }}</th>
                <th>{{ $t('commissions.orderAmount') }}</th>
                <th>{{ $t('commissions.rate') }}</th>
                <th>{{ $t('commissions.commission') }}</th>
                <th>{{ $t('commissions.paidOn') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in paidCommissions" :key="c.id">
                <td class="code-cell">{{ c.employee_name }}</td>
                <td>{{ c.order_number }}</td>
                <td class="amount-cell">TSh {{ Number(c.profit_amount || 0).toLocaleString('en-TZ') }}</td>
                <td>{{ c.commission_rate }}%</td>
                <td class="amount-cell">TSh {{ Number(c.commission_amount || 0).toLocaleString('en-TZ') }}</td>
                <td>{{ c.paid_at ? new Date(c.paid_at).toLocaleDateString('en-TZ') : '-' }}</td>
              </tr>
              <tr v-if="paidCommissions.length === 0">
                <td colspan="6" class="empty-row">{{ $t('commissions.noPaidCommissions') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { commissionApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const loading = ref(true)
const commissions = ref([])
const payAllLoading = ref(false)

const pendingCommissions = computed(() => commissions.value.filter(c => c.status === 'pending'))
const paidCommissions = computed(() => commissions.value.filter(c => c.status === 'paid'))

const employeeSummaries = computed(() => {
  const map = {}
  for (const c of commissions.value) {
    const id = c.employee_id
    if (!map[id]) {
      map[id] = {
        id,
        name: c.employee_name,
        commission_rate: c.commission_rate,
        total_profit: 0,
        pending_count: 0,
        pending_amount: 0,
        paid_count: 0,
        paid_amount: 0,
      }
    }
    map[id].total_profit += Number(c.profit_amount || 0)
    if (c.status === 'pending') {
      map[id].pending_count++
      map[id].pending_amount += Number(c.commission_amount || 0)
    } else if (c.status === 'paid') {
      map[id].paid_count++
      map[id].paid_amount += Number(c.commission_amount || 0)
    }
  }
  return Object.values(map)
})

async function loadCommissions() {
  loading.value = true
  try {
    const res = await commissionApi.getAll()
    commissions.value = (res.data.data || res.data || []).map(c => ({ ...c, _paying: false }))
  } catch (e) {
    console.error(e)
    commissions.value = []
  } finally {
    loading.value = false
  }
}

async function payCommission(c) {
  c._paying = true
  try {
    await commissionApi.pay(c.id)
    c.status = 'paid'
    c.paid_at = new Date().toISOString()
  } catch (e) {
    console.error(e)
  } finally {
    c._paying = false
  }
}

async function payAllPending() {
  payAllLoading.value = true
  try {
    await commissionApi.payAll()
    await loadCommissions()
  } catch (e) {
    console.error(e)
  } finally {
    payAllLoading.value = false
  }
}

onMounted(loadCommissions)
</script>

<style scoped>
.dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.dash-header h1 { font-size: 24px; font-weight: 700; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; color: #666; text-decoration: none; font-size: 13px; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.employee-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; margin-bottom: 24px; }
.emp-summary-card { padding: 20px; }
.emp-summary-header { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
.emp-avatar { width: 44px; height: 44px; background: #fef5f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #e74c3c; font-size: 18px; flex-shrink: 0; }
.emp-summary-info h3 { font-size: 15px; font-weight: 600; margin-bottom: 2px; }
.commission-rate { font-size: 12px; color: #888; }
.emp-summary-stats { display: flex; flex-direction: column; gap: 10px; }
.emp-stat { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #fafafa; border-radius: 6px; }
.emp-stat-label { font-size: 12px; color: #888; font-weight: 500; }
.emp-stat-value { font-size: 13px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.pending-text { color: #e67e22; }
.paid-text { color: #27ae60; }

.section-actions { display: flex; justify-content: flex-end; margin-bottom: 16px; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.table-section { margin-bottom: 20px; }
.table-section-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #f0f0f0; }
.table-section-header h2 { font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 8px; margin: 0; }
.count-badge { background: #fef9e7; color: #7d6608; font-size: 12px; font-weight: 600; padding: 2px 10px; border-radius: 12px; }
.count-badge.paid { background: #f0fff4; color: #1e8449; }

.table-wrap { overflow-x: auto; }
.sa-table { width: 100%; border-collapse: collapse; }
.sa-table th { padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 1px solid #f0f0f0; background: #fafafa; }
.sa-table td { padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.code-cell { font-weight: 600; color: #333; }
.amount-cell { text-align: right; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.empty-row { text-align: center; color: #aaa; padding: 32px; }
.actions-cell { white-space: nowrap; }

.status-badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.status-pending { background: #fef9e7; color: #7d6608; }
.status-paid { background: #f0fff4; color: #1e8449; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #c0392b; }
.btn-success { background: #27ae60; color: #fff; }
.btn-success:hover:not(:disabled) { background: #219a52; }
.btn-sm { padding: 6px 12px; font-size: 12px; }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .header-actions { flex-wrap: wrap; }
  .employee-cards { grid-template-columns: 1fr; }
  .emp-summary-stats { gap: 6px; }
}
</style>
