<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-warehouse" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('inventory.title') }}</h1>
        <p>{{ $t('inventory.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" @click="activeTab = activeTab === 'inventory' ? 'transactions' : 'inventory'">
          <i :class="activeTab === 'inventory' ? 'fas fa-history' : 'fas fa-boxes'"></i>
          {{ activeTab === 'inventory' ? $t('inventory.transactions') : $t('inventory.inventory') }}
        </button>
        <router-link to="/owner/accounting" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('inventory.back') }}</router-link>
      </div>
    </div>

    <!-- Dashboard Stats -->
    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-icon blue"><i class="fas fa-boxes-stacked"></i></div>
        <div class="stat-info">
          <span class="stat-value">{{ dashboardStats.total_items }}</span>
          <span class="stat-label">{{ $t('inventory.totalItems') }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon green"><i class="fas fa-cubes"></i></div>
        <div class="stat-info">
          <span class="stat-value">{{ dashboardStats.total_stock }}</span>
          <span class="stat-label">{{ $t('inventory.totalStockUnits') }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon red"><i class="fas fa-exclamation-triangle"></i></div>
        <div class="stat-info">
          <span class="stat-value">{{ dashboardStats.low_stock_count }}</span>
          <span class="stat-label">{{ $t('inventory.lowStockItems') }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon purple"><i class="fas fa-coins"></i></div>
        <div class="stat-info">
          <span class="stat-value">TSh {{ formatPrice(dashboardStats.total_value) }}</span>
          <span class="stat-label">{{ $t('inventory.totalStockValue') }}</span>
        </div>
      </div>
    </div>

    <!-- Low Stock Alert -->
    <div v-if="lowStockItems.length > 0" class="low-stock-alert card">
      <div class="alert-header">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>{{ $t('inventory.lowStockAlerts') }}</h3>
        <span class="alert-count">{{ $t('inventory.itemsBelowReorder', { count: lowStockItems.length }) }}</span>
      </div>
      <div class="alert-list">
        <div v-for="item in lowStockItems" :key="item.id" class="alert-item">
          <div class="alert-product">
            <strong>{{ item.product?.name || $t('inventory.unknownProduct') }}</strong>
            <span class="alert-sku">{{ $t('inventory.sku') }}: {{ item.product?.sku || $t('inventory.nA') }}</span>
          </div>
          <div class="alert-stock">
            <span class="current">{{ $t('inventory.units', { count: item.quantity_on_hand }) }}</span>
            <span class="arrow">→</span>
            <span class="reorder">{{ $t('inventory.reorderAt', { level: item.reorder_level }) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Inventory Tab -->
    <template v-if="activeTab === 'inventory'">
      <SkeletonLoader v-if="loading" type="table" :count="8" />
      <template v-else>
        <div class="filter-row">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input v-model="search" :placeholder="$t('inventory.searchPlaceholder')" @input="debouncedFilter" />
          </div>
          <select v-model="statusFilter" class="filter-select" @change="filterInventory">
            <option value="">{{ $t('inventory.allStatus') }}</option>
            <option value="ok">{{ $t('inventory.statusOk') }}</option>
            <option value="low">{{ $t('inventory.statusLow') }}</option>
            <option value="out">{{ $t('inventory.statusOut') }}</option>
          </select>
        </div>

        <div v-if="filteredItems.length === 0" class="empty-state card">
          <i class="fas fa-box-open"></i>
          <h3>{{ $t('inventory.noInventoryItems') }}</h3>
          <p>{{ $t('inventory.noInventoryHint') }}</p>
        </div>

        <div v-else class="card">
          <div class="table-wrap">
            <table class="sa-table">
              <thead>
                <tr>
                  <th>{{ $t('inventory.product') }}</th>
                  <th>{{ $t('inventory.variant') }}</th>
                  <th>{{ $t('inventory.qtyOnHand') }}</th>
                  <th>{{ $t('inventory.reorderLevel') }}</th>
                  <th>{{ $t('inventory.stockValue') }}</th>
                  <th>{{ $t('inventory.status') }}</th>
                  <th>{{ $t('inventory.actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in paginatedItems" :key="item.id">
                  <td>
                    <strong>{{ item.product?.name || $t('inventory.unknown') }}</strong>
                    <span class="muted">{{ $t('inventory.sku') }}: {{ item.product?.sku || $t('inventory.nA') }}</span>
                  </td>
                  <td>
                    <span v-if="item.color || item.storage" class="variant-info">
                      <span v-if="item.color" class="variant-tag color">
                        <span class="color-dot" :style="{ background: item.color_hex || '#999' }"></span>
                        {{ item.color }}
                      </span>
                      <span v-if="item.storage" class="variant-tag storage">{{ item.storage }}</span>
                    </span>
                    <span v-else class="muted">{{ $t('inventory.base') }}</span>
                  </td>
                  <td class="qty-cell" :class="{ 'qty-zero': item.quantity_on_hand === 0 }">
                    {{ item.quantity_on_hand }}
                  </td>
                  <td>{{ item.reorder_level }}</td>
                  <td class="value-cell">
                    TSh {{ formatPrice((item.quantity_on_hand || 0) * (item.cost_price || 0)) }}
                  </td>
                  <td>
                    <span :class="['status-badge', getStatusClass(item)]">
                      {{ getStatusText(item) }}
                    </span>
                  </td>
                  <td class="actions-cell">
                    <button class="btn-icon" @click="openAdjustModal(item)" :title="$t('inventory.adjustStock')">
                      <i class="fas fa-sliders-h"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <TablePagination
          v-if="filteredItems.length > PER_PAGE"
          :current-page="currentPage" :total-pages="totalPages"
          :from="pageInfo.from" :to="pageInfo.to" :total="pageInfo.total"
          :show-all="showAll"
          @page="goToPage" @toggle-all="toggleShowAll"
        />
      </template>
    </template>

    <!-- Transactions Tab -->
    <template v-if="activeTab === 'transactions'">
      <SkeletonLoader v-if="loadingTransactions" type="table" :count="5" />
      <template v-else>
        <div class="filter-row">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input v-model="transactionSearch" :placeholder="$t('inventory.searchTransactionsPlaceholder')" @input="debouncedFilterTransactions" />
          </div>
        </div>

        <div v-if="filteredTransactions.length === 0" class="empty-state card">
          <i class="fas fa-history"></i>
          <h3>{{ $t('inventory.noTransactions') }}</h3>
          <p>{{ $t('inventory.noTransactionsHint') }}</p>
        </div>

        <div v-else class="card">
          <div class="table-wrap">
            <table class="sa-table">
              <thead>
                <tr>
                  <th>{{ $t('inventory.date') }}</th>
                  <th>{{ $t('inventory.product') }}</th>
                  <th>{{ $t('inventory.type') }}</th>
                  <th>{{ $t('inventory.change') }}</th>
                  <th>{{ $t('inventory.qtyAfter') }}</th>
                  <th>{{ $t('inventory.notes') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="tx in paginatedTransactions" :key="tx.id">
                  <td>{{ formatDate(tx.created_at) }}</td>
                  <td>
                    <strong>{{ tx.product_variant?.product?.name || tx.product?.name || $t('inventory.unknown') }}</strong>
                    <span class="muted" v-if="tx.product_variant">
                      {{ [tx.product_variant.color, tx.product_variant.storage].filter(Boolean).join(' / ') }}
                    </span>
                  </td>
                  <td>
                    <span :class="['type-badge', tx.type]">{{ getTxTypeText(tx.type) }}</span>
                  </td>
                  <td :class="tx.quantity_change >= 0 ? 'change-positive' : 'change-negative'">
                    {{ tx.quantity_change >= 0 ? '+' : '' }}{{ tx.quantity_change }}
                  </td>
                  <td>{{ tx.quantity_after }}</td>
                  <td class="notes-cell">{{ tx.notes || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <TablePagination
          v-if="filteredTransactions.length > TX_PER_PAGE"
          :current-page="txCurrentPage" :total-pages="txTotalPages"
          :from="txPageInfo.from" :to="txPageInfo.to" :total="txPageInfo.total"
          :show-all="txShowAll"
          @page="goToTxPage" @toggle-all="toggleTxShowAll"
        />
      </template>
    </template>

    <!-- Stock Adjustment Modal -->
    <div class="modal-overlay" v-if="adjustModal.show" @click.self="closeAdjustModal">
      <div class="modal-card">
        <h2><i class="fas fa-sliders-h"></i> {{ $t('inventory.adjustStock') }}</h2>
        <div class="form-group">
          <label>{{ $t('inventory.productVariant') }}</label>
          <input type="text" :value="adjustModal.label" disabled class="readonly-input" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>{{ $t('inventory.currentStock') }}</label>
            <input type="text" :value="adjustModal.currentStock" disabled class="readonly-input" />
          </div>
          <div class="form-group">
            <label>{{ $t('inventory.adjustmentType') }}</label>
            <select v-model="adjustModal.type">
              <option value="adjustment">{{ $t('inventory.adjustment') }}</option>
              <option value="damage">{{ $t('inventory.damage') }}</option>
              <option value="opening">{{ $t('inventory.openingBalance') }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>{{ $t('inventory.quantityChange') }}</label>
          <input v-model.number="adjustModal.quantity" type="number" :placeholder="$t('inventory.quantityPlaceholder')" />
          <span class="field-hint">{{ $t('inventory.quantityHint') }}</span>
        </div>
        <div class="form-group">
          <label>{{ $t('inventory.notes') }}</label>
          <textarea v-model="adjustModal.notes" rows="3" :placeholder="$t('inventory.notesPlaceholder')"></textarea>
        </div>
        <div v-if="adjustModal.error" class="field-error"><i class="fas fa-exclamation-circle"></i> {{ adjustModal.error }}</div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="closeAdjustModal">{{ $t('inventory.cancel') }}</button>
          <button class="btn btn-primary" @click="submitAdjust" :disabled="adjustModal.saving">
            <i class="fas fa-check"></i> {{ adjustModal.saving ? $t('inventory.saving') : $t('inventory.submitAdjustment') }}
          </button>
        </div>
      </div>
    </div>

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas fa-check-circle"></i> {{ toastMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { inventoryApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import TablePagination from '@/components/TablePagination.vue'

const { t } = useI18n()
const loading = ref(true)
const loadingTransactions = ref(true)
const activeTab = ref('inventory')
const toastMsg = ref('')

const dashboardStats = reactive({ total_items: 0, total_stock: 0, low_stock_count: 0, total_value: 0 })
const lowStockItems = ref([])
const inventoryItems = ref([])
const transactions = ref([])

const search = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const showAll = ref(false)
const PER_PAGE = 20

const transactionSearch = ref('')
const txCurrentPage = ref(1)
const txShowAll = ref(false)
const TX_PER_PAGE = 20

function formatPrice(v) { return Number(v || 0).toLocaleString('en-TZ') }
function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-TZ', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function getStatusClass(item) {
  if (item.quantity_on_hand <= 0) return 'out-of-stock'
  if (item.quantity_on_hand <= (item.reorder_level || 0)) return 'low-stock'
  return 'ok'
}

function getStatusText(item) {
  if (item.quantity_on_hand <= 0) return t('inventory.statusOut')
  if (item.quantity_on_hand <= (item.reorder_level || 0)) return t('inventory.statusLow')
  return t('inventory.statusOk')
}

function getTxTypeText(type) {
  if (type === 'damage') return t('inventory.damage')
  if (type === 'opening') return t('inventory.openingBalance')
  return t('inventory.adjustment')
}

function buildItemLabel(item) {
  const name = item.product?.name || t('inventory.unknown')
  const parts = [item.color, item.storage].filter(Boolean)
  return parts.length ? `${name} (${parts.join(' / ')})` : name
}

// Inventory pagination
const filteredItems = computed(() => {
  let items = inventoryItems.value
  if (search.value) {
    const s = search.value.toLowerCase()
    items = items.filter(i =>
      (i.product?.name || '').toLowerCase().includes(s) ||
      (i.product?.sku || '').toLowerCase().includes(s)
    )
  }
  if (statusFilter.value) {
    items = items.filter(i => getStatusClass(i) === statusFilter.value)
  }
  return items
})

const totalPages = computed(() => Math.ceil(filteredItems.value.length / PER_PAGE))
const pageInfo = computed(() => {
  const total = filteredItems.value.length
  if (showAll.value) return { from: 1, to: total, total }
  const from = total === 0 ? 0 : (currentPage.value - 1) * PER_PAGE + 1
  const to = Math.min(currentPage.value * PER_PAGE, total)
  return { from, to, total }
})
const paginatedItems = computed(() => {
  if (showAll.value) return filteredItems.value
  const start = (currentPage.value - 1) * PER_PAGE
  return filteredItems.value.slice(start, start + PER_PAGE)
})

function goToPage(p) { currentPage.value = p; showAll.value = false }
function toggleShowAll() { showAll.value = !showAll.value }

// Transaction pagination
const filteredTransactions = computed(() => {
  if (!transactionSearch.value) return transactions.value
  const s = transactionSearch.value.toLowerCase()
  return transactions.value.filter(tx =>
    (tx.product_variant?.product?.name || '').toLowerCase().includes(s) ||
    (tx.product?.name || '').toLowerCase().includes(s) ||
    (tx.type || '').toLowerCase().includes(s) ||
    (tx.notes || '').toLowerCase().includes(s)
  )
})

const txTotalPages = computed(() => Math.ceil(filteredTransactions.value.length / TX_PER_PAGE))
const txPageInfo = computed(() => {
  const total = filteredTransactions.value.length
  if (txShowAll.value) return { from: 1, to: total, total }
  const from = total === 0 ? 0 : (txCurrentPage.value - 1) * TX_PER_PAGE + 1
  const to = Math.min(txCurrentPage.value * TX_PER_PAGE, total)
  return { from, to, total }
})
const paginatedTransactions = computed(() => {
  if (txShowAll.value) return filteredTransactions.value
  const start = (txCurrentPage.value - 1) * TX_PER_PAGE
  return filteredTransactions.value.slice(start, start + TX_PER_PAGE)
})

function goToTxPage(p) { txCurrentPage.value = p; txShowAll.value = false }
function toggleTxShowAll() { txShowAll.value = !txShowAll.value }

// Debounce
let debounceTimer = null
function debouncedFilter() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { currentPage.value = 1; showAll.value = false }, 200)
}

let txDebounceTimer = null
function debouncedFilterTransactions() {
  clearTimeout(txDebounceTimer)
  txDebounceTimer = setTimeout(() => { txCurrentPage.value = 1; txShowAll.value = false }, 200)
}

function filterInventory() {
  currentPage.value = 1
  showAll.value = false
}

// Adjust modal
const adjustModal = reactive({
  show: false,
  itemId: null,
  label: '',
  currentStock: 0,
  type: 'adjustment',
  quantity: 0,
  notes: '',
  error: '',
  saving: false,
})

function openAdjustModal(item) {
  adjustModal.itemId = item.id
  adjustModal.label = buildItemLabel(item)
  adjustModal.currentStock = item.quantity_on_hand
  adjustModal.type = 'adjustment'
  adjustModal.quantity = 0
  adjustModal.notes = ''
  adjustModal.error = ''
  adjustModal.saving = false
  adjustModal.show = true
}

function closeAdjustModal() {
  adjustModal.show = false
}

async function submitAdjust() {
  adjustModal.error = ''
  if (!adjustModal.quantity || adjustModal.quantity === 0) {
    adjustModal.error = t('inventory.quantityRequired')
    return
  }
  adjustModal.saving = true
  try {
    await inventoryApi.adjust({
      inventory_id: adjustModal.itemId,
      type: adjustModal.type,
      quantity_change: adjustModal.quantity,
      notes: adjustModal.notes,
    })
    closeAdjustModal()
    toastMsg.value = t('inventory.adjustSuccess')
    setTimeout(() => toastMsg.value = '', 3000)
    await loadAll()
  } catch (e) {
    adjustModal.error = e.response?.data?.message || t('inventory.adjustFailed')
  } finally {
    adjustModal.saving = false
  }
}

// Data loading
async function loadDashboard() {
  try {
    const res = await inventoryApi.getDashboard()
    const d = res.data
    dashboardStats.total_items = d.total_items || 0
    dashboardStats.total_stock = d.total_stock || 0
    dashboardStats.low_stock_count = d.low_stock_count || 0
    dashboardStats.total_value = d.total_value || 0
  } catch { /* empty */ }
}

async function loadLowStock() {
  try {
    const res = await inventoryApi.getLowStock()
    lowStockItems.value = res.data?.data || res.data || []
  } catch { /* empty */ }
}

async function loadInventory() {
  loading.value = true
  try {
    const res = await inventoryApi.getAll()
    inventoryItems.value = res.data?.data || res.data || []
  } catch { /* empty */ }
  loading.value = false
}

async function loadTransactions() {
  loadingTransactions.value = true
  try {
    const res = await inventoryApi.getTransactions()
    transactions.value = res.data?.data || res.data || []
  } catch { /* empty */ }
  loadingTransactions.value = false
}

async function loadAll() {
  await Promise.all([loadDashboard(), loadLowStock(), loadInventory(), loadTransactions()])
}

onMounted(loadAll)
</script>

<style scoped>
.dashboard-page { padding: 32px 0; }
.dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.dash-header h1 { font-size: 24px; font-weight: 700; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; color: #666; text-decoration: none; font-size: 13px; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 13px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; }
.btn-outline:hover { border-color: #999; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { display: flex; align-items: center; gap: 16px; padding: 20px; }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.stat-icon.blue { background: #ebf5fb; color: #3498db; }
.stat-icon.green { background: #eafaf1; color: #27ae60; }
.stat-icon.red { background: #fef5f5; color: #e74c3c; }
.stat-icon.purple { background: #f5eef8; color: #9b59b6; }
.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 22px; font-weight: 700; color: #333; line-height: 1.2; }
.stat-label { font-size: 13px; color: #888; margin-top: 2px; }

.low-stock-alert { border-left: 4px solid #f39c12; margin-bottom: 24px; }
.alert-header { display: flex; align-items: center; gap: 10px; padding: 16px 20px; border-bottom: 1px solid #f0f0f0; }
.alert-header i { color: #f39c12; font-size: 18px; }
.alert-header h3 { font-size: 16px; font-weight: 600; margin: 0; }
.alert-count { margin-left: auto; font-size: 12px; color: #f39c12; background: #fef9e7; padding: 4px 10px; border-radius: 12px; font-weight: 600; }
.alert-list { padding: 12px 20px; }
.alert-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f8f8f8; }
.alert-item:last-child { border-bottom: none; }
.alert-product { display: flex; flex-direction: column; gap: 2px; }
.alert-product strong { font-size: 14px; }
.alert-sku { font-size: 12px; color: #888; }
.alert-stock { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.alert-stock .current { font-weight: 700; color: #e74c3c; }
.alert-stock .arrow { color: #ccc; }
.alert-stock .reorder { color: #888; }

.filter-row { display: flex; gap: 12px; margin-bottom: 20px; }
.search-box { display: flex; align-items: center; gap: 8px; border: 1px solid #e0e0e0; border-radius: 6px; padding: 0 12px; background: #fff; flex: 1; max-width: 300px; }
.search-box i { color: #999; }
.search-box input { border: none; outline: none; padding: 10px 0; font-size: 14px; width: 100%; }
.filter-select { padding: 10px 14px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 14px; background: #fff; }

.empty-state { text-align: center; padding: 60px 20px; }
.empty-state i { font-size: 48px; color: #ddd; margin-bottom: 16px; display: block; }
.empty-state h3 { font-size: 20px; margin-bottom: 8px; }
.empty-state p { color: #888; font-size: 14px; }

.table-wrap { overflow-x: auto; }
.sa-table { width: 100%; border-collapse: collapse; }
.sa-table th { padding: 10px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 1px solid #f0f0f0; background: #fafafa; }
.sa-table td { padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.muted { display: block; font-size: 12px; color: #999; margin-top: 2px; }

.variant-info { display: flex; gap: 6px; flex-wrap: wrap; }
.variant-tag { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; padding: 2px 8px; border-radius: 4px; background: #f0f0f0; color: #666; }
.variant-tag .color-dot { width: 8px; height: 8px; border-radius: 50%; border: 1px solid rgba(0,0,0,0.1); }

.qty-cell { font-weight: 700; }
.qty-zero { color: #e74c3c; }
.value-cell { font-weight: 600; white-space: nowrap; }

.status-badge { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; white-space: nowrap; }
.status-badge.ok { background: #eafaf1; color: #27ae60; }
.status-badge.low-stock { background: #fef9e7; color: #f39c12; }
.status-badge.out-of-stock { background: #fef5f5; color: #e74c3c; }

.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 13px; color: #666; transition: all 0.2s; }
.btn-icon:hover { border-color: #e74c3c; color: #e74c3c; }
.actions-cell { white-space: nowrap; }

.type-badge { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: capitalize; }
.type-badge.adjustment { background: #ebf5fb; color: #3498db; }
.type-badge.damage { background: #fef5f5; color: #e74c3c; }
.type-badge.opening { background: #eafaf1; color: #27ae60; }

.change-positive { color: #27ae60; font-weight: 700; }
.change-negative { color: #e74c3c; font-weight: 700; }
.notes-cell { max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #888; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 24px; }
.modal-card { width: 100%; max-width: 500px; background: #fff; border-radius: 12px; padding: 32px; }
.modal-card h2 { font-size: 20px; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; }
.modal-card h2 i { color: #e74c3c; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
.form-group input, .form-group select, .form-group textarea {
  width: 100%; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 6px;
  font-size: 14px; box-sizing: border-box; font-family: inherit; resize: vertical;
}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: #e74c3c; }
.readonly-input { background: #f8f8f8 !important; color: #666; cursor: not-allowed; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.field-hint { display: block; font-size: 12px; color: #999; margin-top: 4px; }
.field-error { display: flex; align-items: center; gap: 6px; margin-top: 8px; font-size: 12px; color: #e74c3c; font-weight: 500; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #2c3e50; color: #fff; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 2000; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); animation: slideUp 0.3s ease; }
.toast i { color: #27ae60; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .header-actions { flex-wrap: wrap; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .stat-value { font-size: 16px; }
  .filter-row { flex-direction: column; }
  .search-box { max-width: 100%; }
  .form-row { grid-template-columns: 1fr; }
  .alert-item { flex-direction: column; align-items: flex-start; gap: 6px; }
}

@media (max-width: 480px) {
  .stats-grid { grid-template-columns: 1fr; }
}
</style>
