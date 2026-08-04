<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-exclamation-triangle" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('stockAlerts.title') }}</h1>
        <p>{{ $t('stockAlerts.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <router-link to="/owner/accounting" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.back') }}</router-link>
      </div>
    </div>

    <SkeletonLoader v-if="loading" type="table" :count="8" />
    <template v-else>
      <div class="filter-row">
        <div class="filter-tabs">
          <button
            v-for="tab in filterTabs"
            :key="tab.value"
            :class="['filter-tab', { active: activeFilter === tab.value }]"
            @click="setFilter(tab.value)"
          >
            {{ tab.label }}
            <span v-if="tab.count > 0" class="tab-count">{{ tab.count }}</span>
          </button>
        </div>
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input v-model="search" :placeholder="$t('stockAlerts.searchPlaceholder')" @input="debouncedFilter" />
        </div>
      </div>

      <div v-if="filteredAlerts.length === 0" class="empty-state card">
        <i class="fas fa-check-circle"></i>
        <h3>{{ $t('stockAlerts.noAlertsTitle') }}</h3>
        <p>{{ $t('stockAlerts.noAlertsDesc') }}</p>
      </div>

      <div v-else class="card">
        <div class="table-wrap">
          <table class="sa-table">
            <thead>
              <tr>
                <th>{{ $t('stockAlerts.type') }}</th>
                <th>{{ $t('stockAlerts.product') }}</th>
                <th>{{ $t('stockAlerts.sku') }}</th>
                <th>{{ $t('stockAlerts.quantity') }}</th>
                <th>{{ $t('stockAlerts.reorderLevel') }}</th>
                <th>{{ $t('stockAlerts.message') }}</th>
                <th>{{ $t('stockAlerts.created') }}</th>
                <th>{{ $t('stockAlerts.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="alert in paginatedAlerts" :key="alert.id">
                <td>
                  <span :class="['type-badge', alert.type === 'out_of_stock' ? 'out-of-stock' : 'low-stock']">
                    <i :class="alert.type === 'out_of_stock' ? 'fas fa-times-circle' : 'fas fa-exclamation-circle'"></i>
                    {{ alert.type === 'out_of_stock' ? $t('stockAlerts.outOfStock') : $t('stockAlerts.lowStock') }}
                  </span>
                </td>
                <td>
                  <strong>{{ alert.product_variant?.product?.name || $t('stockAlerts.unknownProduct') }}</strong>
                  <span v-if="alert.product_variant?.color || alert.product_variant?.storage" class="muted">
                    {{ [alert.product_variant.color, alert.product_variant.storage].filter(Boolean).join(' / ') }}
                  </span>
                </td>
                <td class="sku-cell">{{ alert.product_variant?.product?.sku || $t('stockAlerts.nA') }}</td>
                <td class="qty-cell" :class="{ 'qty-zero': (alert.current_quantity || 0) === 0 }">
                  {{ alert.current_quantity ?? 0 }}
                </td>
                <td>{{ alert.reorder_level ?? '—' }}</td>
                <td class="message-cell">{{ alert.message || '—' }}</td>
                <td>{{ formatDate(alert.created_at) }}</td>
                <td class="actions-cell">
                  <button
                    v-if="alert.status === 'active'"
                    class="btn-action acknowledge"
                    @click="handleAcknowledge(alert)"
                    :disabled="processingId === alert.id"
                    :title="$t('stockAlerts.acknowledge')"
                  >
                    <i class="fas fa-check"></i> {{ $t('stockAlerts.acknowledge') }}
                  </button>
                  <button
                    v-if="alert.status !== 'resolved'"
                    class="btn-action resolve"
                    @click="handleResolve(alert)"
                    :disabled="processingId === alert.id"
                    :title="$t('stockAlerts.resolve')"
                  >
                    <i class="fas fa-check-double"></i> {{ $t('stockAlerts.resolve') }}
                  </button>
                  <span v-if="alert.status === 'resolved'" class="status-badge resolved">
                    <i class="fas fa-check-circle"></i> {{ $t('stockAlerts.resolveStatus') }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <TablePagination
        v-if="filteredAlerts.length > PER_PAGE"
        :current-page="currentPage" :total-pages="totalPages"
        :from="pageInfo.from" :to="pageInfo.to" :total="pageInfo.total"
        :show-all="showAll"
        @page="goToPage" @toggle-all="toggleShowAll"
      />
    </template>

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas fa-check-circle"></i> {{ toastMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { stockAlertApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import TablePagination from '@/components/TablePagination.vue'

const { t } = useI18n()
const loading = ref(true)
const alerts = ref([])
const search = ref('')
const activeFilter = ref('all')
const currentPage = ref(1)
const showAll = ref(false)
const PER_PAGE = 20
const toastMsg = ref('')
const processingId = ref(null)

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-TZ', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const filterTabs = computed(() => {
  const all = alerts.value
  return [
    { label: t('stockAlerts.all'), value: 'all', count: all.length },
    { label: t('stockAlerts.active'), value: 'active', count: all.filter(a => a.status === 'active').length },
    { label: t('stockAlerts.acknowledged'), value: 'acknowledged', count: all.filter(a => a.status === 'acknowledged').length },
    { label: t('stockAlerts.resolved'), value: 'resolved', count: all.filter(a => a.status === 'resolved').length },
  ]
})

const filteredAlerts = computed(() => {
  let items = alerts.value
  if (activeFilter.value !== 'all') {
    items = items.filter(a => a.status === activeFilter.value)
  }
  if (search.value) {
    const s = search.value.toLowerCase()
    items = items.filter(a =>
      (a.product_variant?.product?.name || '').toLowerCase().includes(s) ||
      (a.product_variant?.product?.sku || '').toLowerCase().includes(s) ||
      (a.product_variant?.color || '').toLowerCase().includes(s) ||
      (a.product_variant?.storage || '').toLowerCase().includes(s)
    )
  }
  return items
})

const totalPages = computed(() => Math.ceil(filteredAlerts.value.length / PER_PAGE))
const pageInfo = computed(() => {
  const total = filteredAlerts.value.length
  if (showAll.value) return { from: 1, to: total, total }
  const from = total === 0 ? 0 : (currentPage.value - 1) * PER_PAGE + 1
  const to = Math.min(currentPage.value * PER_PAGE, total)
  return { from, to, total }
})
const paginatedAlerts = computed(() => {
  if (showAll.value) return filteredAlerts.value
  const start = (currentPage.value - 1) * PER_PAGE
  return filteredAlerts.value.slice(start, start + PER_PAGE)
})

function goToPage(p) { currentPage.value = p; showAll.value = false }
function toggleShowAll() { showAll.value = !showAll.value }

function setFilter(value) {
  activeFilter.value = value
  currentPage.value = 1
  showAll.value = false
}

let debounceTimer = null
function debouncedFilter() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { currentPage.value = 1; showAll.value = false }, 200)
}

async function handleAcknowledge(alert) {
  processingId.value = alert.id
  try {
    await stockAlertApi.acknowledge(alert.id)
    alert.status = 'acknowledged'
    toastMsg.value = t('stockAlerts.acknowledgedSuccess')
    setTimeout(() => toastMsg.value = '', 3000)
  } catch { /* empty */ }
  processingId.value = null
}

async function handleResolve(alert) {
  processingId.value = alert.id
  try {
    await stockAlertApi.resolve(alert.id)
    alert.status = 'resolved'
    toastMsg.value = t('stockAlerts.resolvedSuccess')
    setTimeout(() => toastMsg.value = '', 3000)
  } catch { /* empty */ }
  processingId.value = null
}

async function loadAlerts() {
  loading.value = true
  try {
    const res = await stockAlertApi.getAll()
    alerts.value = res.data?.data || res.data || []
  } catch { /* empty */ }
  loading.value = false
}

onMounted(loadAlerts)
</script>

<style scoped>
.dashboard-page { padding: 32px 0; }
.dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.dash-header h1 { font-size: 24px; font-weight: 700; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; color: #666; text-decoration: none; font-size: 13px; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.filter-row { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.filter-tabs { display: flex; gap: 4px; background: #f5f5f5; border-radius: 8px; padding: 4px; }
.filter-tab { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: none; border-radius: 6px; background: transparent; font-size: 13px; font-weight: 500; color: #666; cursor: pointer; transition: all 0.2s; }
.filter-tab:hover { color: #333; }
.filter-tab.active { background: #fff; color: #e74c3c; box-shadow: 0 1px 3px rgba(0,0,0,0.08); font-weight: 600; }
.tab-count { font-size: 11px; background: rgba(0,0,0,0.06); padding: 1px 6px; border-radius: 10px; }
.filter-tab.active .tab-count { background: #fef5f5; color: #e74c3c; }

.search-box { display: flex; align-items: center; gap: 8px; border: 1px solid #e0e0e0; border-radius: 6px; padding: 0 12px; background: #fff; width: 280px; }
.search-box i { color: #999; }
.search-box input { border: none; outline: none; padding: 10px 0; font-size: 14px; width: 100%; }

.empty-state { text-align: center; padding: 60px 20px; }
.empty-state i { font-size: 48px; color: #ddd; margin-bottom: 16px; display: block; }
.empty-state h3 { font-size: 20px; margin-bottom: 8px; }
.empty-state p { color: #888; font-size: 14px; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.table-wrap { overflow-x: auto; }
.sa-table { width: 100%; border-collapse: collapse; }
.sa-table th { padding: 10px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 1px solid #f0f0f0; background: #fafafa; }
.sa-table td { padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.muted { display: block; font-size: 12px; color: #999; margin-top: 2px; }

.type-badge { display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; white-space: nowrap; }
.type-badge.low-stock { background: #fef9e7; color: #e67e22; }
.type-badge.out-of-stock { background: #fef5f5; color: #e74c3c; }

.sku-cell { font-family: monospace; font-size: 12px; color: #666; }
.qty-cell { font-weight: 700; }
.qty-zero { color: #e74c3c; }
.message-cell { max-width: 220px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #666; }

.actions-cell { white-space: nowrap; display: flex; gap: 6px; align-items: center; }
.btn-action { display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; border: 1px solid #ddd; border-radius: 6px; background: #fff; font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.2s; }
.btn-action:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-action.acknowledge { color: #e67e22; }
.btn-action.acknowledge:hover:not(:disabled) { border-color: #e67e22; background: #fef9e7; }
.btn-action.resolve { color: #27ae60; }
.btn-action.resolve:hover:not(:disabled) { border-color: #27ae60; background: #eafaf1; }
.status-badge { display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.status-badge.resolved { background: #eafaf1; color: #27ae60; }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #2c3e50; color: #fff; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 2000; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); animation: slideUp 0.3s ease; }
.toast i { color: #27ae60; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .header-actions { flex-wrap: wrap; }
  .filter-row { flex-direction: column; align-items: stretch; }
  .filter-tabs { overflow-x: auto; }
  .search-box { width: 100%; }
  .sa-table th:nth-child(6), .sa-table td:nth-child(6) { display: none; }
  .actions-cell { flex-direction: column; align-items: flex-start; }
  .btn-action { width: 100%; justify-content: center; }
}

@media (max-width: 480px) {
  .sa-table th:nth-child(5), .sa-table td:nth-child(5) { display: none; }
}
</style>
