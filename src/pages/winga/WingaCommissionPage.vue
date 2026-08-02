<template>
  <div class="container page">
    <div class="page-header">
      <div>
        <h1>{{ $t('wingaCommissions.title') }}</h1>
        <p class="subtitle">{{ $t('wingaCommissions.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <router-link :to="wingasLink" class="btn btn-outline"><i class="fas fa-arrow-left"></i> {{ $t('wingas.title') }}</router-link>
      </div>
    </div>

    <div class="tax-note"><i class="fas fa-info-circle"></i> {{ $t('wingaCommissions.taxNote') }}</div>

    <SkeletonLoader v-if="loading" type="stats" :count="4" />

    <template v-else>
      <div class="summary-cards">
        <div class="summary-card pending">
          <div class="summary-header">
            <span class="summary-title">{{ $t('wingaCommissions.pending') }}</span>
            <span class="count-badge">{{ summary.pending.count }} {{ $t('wingaCommissions.commissionCount') }}</span>
          </div>
          <div class="summary-body">
            <div class="summary-row"><span>{{ $t('wingaCommissions.gross') }}</span><strong>TSh {{ fmt(summary.pending.gross) }}</strong></div>
            <div class="summary-row"><span>{{ $t('wingaCommissions.tax') }}</span><strong class="tax-text">TSh {{ fmt(summary.pending.tax) }}</strong></div>
            <div class="summary-row highlight"><span>{{ $t('wingaCommissions.net') }}</span><strong>TSh {{ fmt(summary.pending.net) }}</strong></div>
          </div>
        </div>
        <div class="summary-card paid">
          <div class="summary-header">
            <span class="summary-title">{{ $t('wingaCommissions.paid') }}</span>
            <span class="count-badge paid">{{ summary.paid.count }} {{ $t('wingaCommissions.commissionCount') }}</span>
          </div>
          <div class="summary-body">
            <div class="summary-row"><span>{{ $t('wingaCommissions.gross') }}</span><strong>TSh {{ fmt(summary.paid.gross) }}</strong></div>
            <div class="summary-row"><span>{{ $t('wingaCommissions.tax') }}</span><strong class="tax-text">TSh {{ fmt(summary.paid.tax) }}</strong></div>
            <div class="summary-row highlight"><span>{{ $t('wingaCommissions.net') }}</span><strong>TSh {{ fmt(summary.paid.net) }}</strong></div>
          </div>
        </div>
      </div>

      <div v-if="pendingCommissions.length > 0" class="section-actions">
        <button class="btn btn-primary" :disabled="payAllLoading" @click="payAllPending">
          <i class="fas fa-check-double"></i> {{ payAllLoading ? $t('wingaCommissions.payAllProcessing') : $t('wingaCommissions.payAll') }}
        </button>
      </div>

      <div class="card table-section">
        <div class="table-section-header">
          <h2><i class="fas fa-clock" style="color: #e67e22;"></i> {{ $t('wingaCommissions.pending') }}</h2>
          <span class="count-badge">{{ pendingCommissions.length }}</span>
        </div>
        <div class="table-wrap">
          <table class="sa-table">
            <thead>
              <tr>
                <th>{{ $t('wingaCommissions.wingaName') }}</th>
                <th>{{ $t('wingaCommissions.orderNumber') }}</th>
                <th class="amount-cell">{{ $t('wingaCommissions.orderAmount') }}</th>
                <th>{{ $t('wingaCommissions.rate') }}</th>
                <th class="amount-cell">{{ $t('wingaCommissions.commission') }}</th>
                <th class="amount-cell">{{ $t('wingaCommissions.tax') }}</th>
                <th class="amount-cell">{{ $t('wingaCommissions.net') }}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in pendingCommissions" :key="c.id">
                <td class="code-cell">{{ c.winga?.name || '-' }}</td>
                <td>{{ c.order?.order_number || c.order_id }}</td>
                <td class="amount-cell">TSh {{ fmt(c.order_amount) }}</td>
                <td>{{ c.commission_rate }}%</td>
                <td class="amount-cell">TSh {{ fmt(c.commission_amount) }}</td>
                <td class="amount-cell tax-text">TSh {{ fmt(c.withholding_tax) }}</td>
                <td class="amount-cell">TSh {{ fmt(c.net_amount) }}</td>
                <td class="actions-cell">
                  <button class="btn btn-success btn-sm" :disabled="c._paying" @click="payCommission(c)">
                    <i class="fas fa-money-bill-wave"></i> {{ c._paying ? $t('wingaCommissions.paying') : $t('wingaCommissions.pay') }}
                  </button>
                </td>
              </tr>
              <tr v-if="pendingCommissions.length === 0">
                <td colspan="8" class="empty-row">{{ $t('wingaCommissions.noPending') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card table-section">
        <div class="table-section-header">
          <h2><i class="fas fa-check-circle" style="color: #27ae60;"></i> {{ $t('wingaCommissions.paid') }}</h2>
          <span class="count-badge paid">{{ paidCommissions.length }}</span>
        </div>
        <div class="table-wrap">
          <table class="sa-table">
            <thead>
              <tr>
                <th>{{ $t('wingaCommissions.wingaName') }}</th>
                <th>{{ $t('wingaCommissions.orderNumber') }}</th>
                <th class="amount-cell">{{ $t('wingaCommissions.orderAmount') }}</th>
                <th>{{ $t('wingaCommissions.rate') }}</th>
                <th class="amount-cell">{{ $t('wingaCommissions.commission') }}</th>
                <th class="amount-cell">{{ $t('wingaCommissions.tax') }}</th>
                <th class="amount-cell">{{ $t('wingaCommissions.net') }}</th>
                <th>{{ $t('wingaCommissions.paidOn') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in paidCommissions" :key="c.id">
                <td class="code-cell">{{ c.winga?.name || '-' }}</td>
                <td>{{ c.order?.order_number || c.order_id }}</td>
                <td class="amount-cell">TSh {{ fmt(c.order_amount) }}</td>
                <td>{{ c.commission_rate }}%</td>
                <td class="amount-cell">TSh {{ fmt(c.commission_amount) }}</td>
                <td class="amount-cell tax-text">TSh {{ fmt(c.withholding_tax) }}</td>
                <td class="amount-cell">TSh {{ fmt(c.net_amount) }}</td>
                <td>{{ c.paid_at ? new Date(c.paid_at).toLocaleDateString('en-TZ') : '-' }}</td>
              </tr>
              <tr v-if="paidCommissions.length === 0">
                <td colspan="8" class="empty-row">{{ $t('wingaCommissions.noPaid') }}</td>
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
import { useAuthStore } from '@/stores/auth'
import { wingaCommissionApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const authStore = useAuthStore()

const loading = ref(true)
const commissions = ref([])
const summary = ref({ pending: { count: 0, gross: 0, tax: 0, net: 0 }, paid: { count: 0, gross: 0, tax: 0, net: 0 }, by_winga: [] })
const payAllLoading = ref(false)

const isOwner = computed(() => authStore.user?.role === 'owner')
const wingasLink = computed(() => (isOwner.value ? '/owner/wingas' : '/employee/wingas'))

const pendingCommissions = computed(() => commissions.value.filter(c => c.status === 'pending'))
const paidCommissions = computed(() => commissions.value.filter(c => c.status === 'paid'))

function fmt(v) { return Number(v || 0).toLocaleString('en-TZ') }

async function loadData() {
  loading.value = true
  try {
    const [listRes, sumRes] = await Promise.all([
      wingaCommissionApi.getAll().catch(() => ({ data: { data: [] } })),
      wingaCommissionApi.getSummary().catch(() => ({ data: { pending: { count: 0, gross: 0, tax: 0, net: 0 }, paid: { count: 0, gross: 0, tax: 0, net: 0 }, by_winga: [] } })),
    ])
    commissions.value = (listRes.data.data || listRes.data || []).map(c => ({ ...c, _paying: false }))
    summary.value = sumRes.data
  } catch { /* empty */ }
  loading.value = false
}

async function payCommission(c) {
  c._paying = true
  try {
    await wingaCommissionApi.pay(c.id)
    c.status = 'paid'
    c.paid_at = new Date().toISOString()
    await loadData()
  } catch { /* empty */ }
  c._paying = false
}

async function payAllPending() {
  payAllLoading.value = true
  try {
    await wingaCommissionApi.payAll()
    await loadData()
  } catch { /* empty */ }
  payAllLoading.value = false
}

onMounted(loadData)
</script>

<style scoped>
.page { padding: 32px 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h1 { font-size: 26px; margin-bottom: 4px; }
.subtitle { color: #888; font-size: 14px; }
.header-actions { display: flex; gap: 10px; align-items: center; }

.tax-note { display: flex; align-items: center; gap: 8px; padding: 12px 16px; background: #fef9e7; border: 1px solid #fdebd0; border-radius: 8px; color: #7d6608; font-size: 13px; margin-bottom: 20px; }
.tax-note i { color: #b7950b; }

.summary-cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 24px; }
.summary-card { border-radius: 10px; padding: 20px; }
.summary-card.pending { background: #fffbf0; border: 1px solid #fdebd0; }
.summary-card.paid { background: #f2fbf6; border: 1px solid #d1f2e5; }
.summary-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.summary-title { font-size: 15px; font-weight: 700; color: #333; }
.count-badge { background: #fef9e7; color: #7d6608; font-size: 12px; font-weight: 600; padding: 2px 10px; border-radius: 12px; }
.count-badge.paid { background: #f0fff4; color: #1e8449; }
.summary-body { display: flex; flex-direction: column; gap: 8px; }
.summary-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #666; }
.summary-row.highlight { padding-top: 8px; border-top: 1px dashed #e0d5c0; }
.summary-row.highlight span { font-weight: 600; color: #333; }
.summary-row.highlight strong { font-size: 15px; color: #e74c3c; }
.tax-text { color: #b7950b; }
.summary-row strong { font-family: 'JetBrains Mono', monospace; }

.section-actions { display: flex; justify-content: flex-end; margin-bottom: 16px; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.table-section { margin-bottom: 20px; }
.table-section-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #f0f0f0; }
.table-section-header h2 { font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 8px; margin: 0; }

.table-wrap { overflow-x: auto; }
.sa-table { width: 100%; border-collapse: collapse; }
.sa-table th { padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 1px solid #f0f0f0; background: #fafafa; }
.sa-table td { padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.code-cell { font-weight: 600; color: #333; }
.amount-cell { text-align: right; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.empty-row { text-align: center; color: #aaa; padding: 32px; }
.actions-cell { white-space: nowrap; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; font-family: 'Inter', sans-serif; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #c0392b; }
.btn-success { background: #27ae60; color: #fff; }
.btn-success:hover:not(:disabled) { background: #219a52; }
.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; text-decoration: none; }
.btn-outline:hover { border-color: #999; }
.btn-sm { padding: 6px 12px; font-size: 12px; }

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .summary-cards { grid-template-columns: 1fr; }
}
</style>
