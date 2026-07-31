<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-receipt" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('ordersManage.title') }}
        </h1>
        <p>{{ $t('ordersManage.subtitle') }}</p>
      </div>
      <router-link :to="dashboardRoute" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.backToDashboard')
      }}</router-link>
    </div>

    <div class="filters-bar card">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input v-model="search" type="text" :placeholder="$t('ordersManage.searchPlaceholder')"
          @input="debouncedLoad" />
      </div>
      <div class="filter-select-wrap" v-if="branches.length > 0">
        <select v-model="branchFilter" class="filter-select" @change="loadOrders()">
          <option value="">{{ $t('ordersManage.allBranches') }}</option>
          <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
        </select>
      </div>
      <div class="status-filters">
        <button :class="['filter-btn', { active: statusFilter === '' }]" @click="statusFilter = ''; loadOrders()">{{
          $t('ordersManage.all') }}</button>
        <button :class="['filter-btn pending-filter', { active: statusFilter === 'pending' }]"
          @click="statusFilter = 'pending'; loadOrders()"><i class="fas fa-clock"></i> {{ $t('ordersManage.pending')
          }}</button>
        <button :class="['filter-btn', { active: statusFilter === 'paid' }]"
          @click="statusFilter = 'paid'; loadOrders()">{{ $t('ordersManage.paid') }}</button>
        <button :class="['filter-btn', { active: statusFilter === 'processing' }]"
          @click="statusFilter = 'processing'; loadOrders()">{{ $t('ordersManage.processing') }}</button>
        <button :class="['filter-btn', { active: statusFilter === 'shipped' }]"
          @click="statusFilter = 'shipped'; loadOrders()">{{ $t('ordersManage.shipped') }}</button>
        <button :class="['filter-btn', { active: statusFilter === 'delivered' }]"
          @click="statusFilter = 'delivered'; loadOrders()">{{ $t('ordersManage.delivered') }}</button>
        <button :class="['filter-btn', { active: statusFilter === 'cancelled' }]"
          @click="statusFilter = 'cancelled'; loadOrders()">{{ $t('ordersManage.cancelled') }}</button>
        <button :class="['filter-btn', { active: statusFilter === 'inactive' }]"
          @click="statusFilter = 'inactive'; loadOrders()">{{ $t('ordersManage.inactive') }}</button>
      </div>
    </div>

    <div class="summary-row">
      <div class="summary-pill"><span class="pill-num">{{ orders.length }}</span> {{ $t('ordersManage.ordersShown') }}
      </div>
      <div class="summary-pill revenue-pill"><span class="pill-num">{{ $t('common.currency') }} {{
        formatPrice(totalRevenue) }}</span> {{ $t('ordersManage.totalRevenue') }}</div>
    </div>

    <SkeletonLoader v-if="loading" type="list" :count="4" />

    <div v-else-if="orders.length === 0" class="empty-state card">
      <i class="fas fa-receipt"></i>
      <h3>{{ $t('ordersManage.noOrders') }}</h3>
      <p>{{ search || statusFilter ? $t('ordersManage.tryAdjust') : $t('ordersManage.noOrdersYet') }}</p>
    </div>

    <div v-else class="orders-list">
      <div v-for="order in paginatedOrders" :key="order.id" class="order-card card">
        <div class="order-header">
          <div class="order-info">
            <span class="order-number">{{ order.order_number }}</span>
            <span class="order-date">{{ formatDate(order.created_at) }}</span>
          </div>
          <span :class="['status-badge', `status-${order.status}`]">{{ $t(`ordersManage.${order.status}`) }}</span>
        </div>

        <div class="order-customer">
          <div class="customer-avatar"><i class="fas fa-user"></i></div>
          <div>
            <span class="customer-name">{{ order.user?.name || $t('ordersManage.unknown') }}</span>
            <span class="customer-email">{{ order.user?.email || '' }}</span>
          </div>
        </div>

        <div class="order-items">
          <div v-for="item in order.items" :key="item.id" class="order-item">
            <span>{{ item.product_variant?.product?.name || $t('common.product') }}</span>
            <span class="item-meta">{{ [item.product_variant?.color,
            item.product_variant?.storage].filter(Boolean).join(' - ') }} x {{ item.quantity }}</span>
            <span class="item-total">TSh {{ formatPrice(item.total) }}</span>
          </div>
        </div>

        <div class="order-footer">
          <div class="order-totals">
            <div class="total-row"><span>{{ $t('ordersManage.subtotal') }}</span><span>TSh {{
              formatPrice(order.subtotal) }}</span></div>
            <div class="total-row"><span>{{ $t('ordersManage.shipping') }}</span><span>TSh {{
              formatPrice(order.shipping_cost) }}</span></div>
            <div class="total-row grand"><span>{{ $t('ordersManage.total') }}</span><span>TSh {{
              formatPrice(order.total) }}</span></div>
          </div>

          <div v-if="order.payments?.length" class="payment-info">
            <i class="fas fa-credit-card"></i>
            <span>{{ $t('ordersManage.paidVia') }} {{ order.payments[0]?.provider }} — {{
              order.payments[0]?.metadata?.phone_number || 'N/A' }}</span>
          </div>

          <div v-if="order.status === 'pending' && order.payments?.length" class="pending-payment-alert">
            <div class="alert-icon"><i class="fas fa-exclamation-triangle"></i></div>
            <div class="alert-content">
              <strong>{{ $t('ordersManage.awaitingConfirmation') }}</strong>
              <p>{{ $t('ordersManage.customerPaidVia', {
                provider: order.payments[0]?.provider, phone:
                  order.payments[0]?.metadata?.phone_number
              }) }}</p>
              <p>{{ $t('ordersManage.verifyPayment', { provider: order.payments[0]?.provider }) }}</p>
            </div>
          </div>

          <div v-if="order.handler" class="handler-info">
            <i class="fas fa-user-check"></i>
            <span>{{ $t('ordersManage.handledBy') }} {{ order.handler?.name }}</span>
          </div>

          <div class="order-actions" v-if="!['delivered', 'cancelled'].includes(order.status)">
            <button v-if="order.status === 'pending'" class="btn btn-sm btn-success" @click="openConfirmModal(order)">
              <i class="fas fa-check-circle"></i> {{ $t('ordersManage.confirmPayment') }}
            </button>
            <button v-if="order.status === 'pending'" class="btn btn-sm btn-danger"
              @click="updateStatus(order, 'cancelled')">
              <i class="fas fa-times"></i> {{ $t('ordersManage.reject') }}
            </button>
            <button v-if="order.status === 'paid'" class="btn btn-sm btn-primary"
              @click="updateStatus(order, 'processing')">
              <i class="fas fa-cog"></i> {{ $t('ordersManage.markProcessing') }}
            </button>
            <button v-if="order.status === 'processing'" class="btn btn-sm btn-primary"
              @click="updateStatus(order, 'shipped')">
              <i class="fas fa-truck"></i> {{ $t('ordersManage.markShipped') }}
            </button>
            <button v-if="order.status === 'shipped'" class="btn btn-sm btn-primary"
              @click="updateStatus(order, 'delivered')">
              <i class="fas fa-check-circle"></i> {{ $t('ordersManage.markDelivered') }}
            </button>
            <button v-if="['paid', 'processing'].includes(order.status)" class="btn btn-sm btn-danger"
              @click="updateStatus(order, 'cancelled')">
              <i class="fas fa-times"></i> {{ $t('ordersManage.cancelOrder') }}
            </button>
            <button v-if="['paid', 'processing', 'shipped'].includes(order.status) && order.delivery_required"
              class="btn btn-sm btn-outline-dark" @click="openDeliveryModal(order)">
              <i class="fas fa-truck"></i> {{ $t('ordersManage.deliveryDetails') }}
            </button>
          </div>

          <div v-if="order.delivery_required" class="delivery-info">
            <i class="fas fa-truck"></i>
            <span v-if="order.tracking_number">{{ $t('ordersManage.tracking') }} <strong>{{ order.tracking_number
            }}</strong></span>
            <span v-if="order.delivery_notes"> — {{ order.delivery_notes }}</span>
            <span v-if="order.shipped_at"> — {{ $t('ordersManage.shipped') }} {{ new
              Date(order.shipped_at).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>
    </div>

    <TablePagination v-if="orders.length > 15" :current-page="currentPage" :total-pages="totalPages"
      :from="pageInfo.from" :to="pageInfo.to" :total="pageInfo.total" :show-all="showAll" @page="goToPage"
      @toggle-all="toggleShowAll" />

    <!-- Confirm Payment Modal -->
    <Teleport to="body">
      <div v-if="confirmModal.show" class="modal-overlay" @click.self="closeConfirmModal">
        <div class="modal-content card">
          <div class="modal-header">
            <h3><i class="fas fa-shield-halved"></i> {{ $t('ordersManage.confirmPayment') }}</h3>
            <button class="modal-close" @click="closeConfirmModal"><i class="fas fa-times"></i></button>
          </div>
          <div class="modal-body">
            <div class="modal-order-summary">
              <div class="summary-line"><span>{{ $t('ordersManage.order') }}</span><strong>{{
                confirmModal.order?.order_number }}</strong></div>
              <div class="summary-line"><span>{{ $t('ordersManage.customer') }}</span><strong>{{
                confirmModal.order?.user?.name }}</strong></div>
              <div class="summary-line"><span>{{ $t('ordersManage.amount') }}</span><strong>TSh {{
                formatPrice(confirmModal.order?.total) }}</strong></div>
              <div class="summary-line"><span>{{ $t('ordersManage.provider') }}</span><strong>{{
                confirmModal.order?.payments?.[0]?.provider }}</strong></div>
              <div class="summary-line"><span>{{ $t('ordersManage.phone') }}</span><strong>{{
                confirmModal.order?.payments?.[0]?.metadata?.phone_number }}</strong></div>
            </div>
            <div class="confirm-prompt">
              <p>{{ $t('ordersManage.typeCustomerName') }}</p>
              <p class="expected-name">{{ $t('ordersManage.expected') }} <strong>{{
                confirmModal.order?.user?.name?.toUpperCase() }}</strong></p>
              <input v-model="confirmModal.typedName" type="text" class="confirm-input"
                :class="{ valid: confirmModal.typedName === confirmModal.order?.user?.name?.toUpperCase() }"
                :placeholder="$t('ordersManage.namePlaceholder')" @keyup.enter="submitConfirmPayment" autofocus />
              <p v-if="confirmModal.typedName && confirmModal.typedName !== confirmModal.order?.user?.name?.toUpperCase()"
                class="mismatch-warning">
                <i class="fas fa-exclamation-triangle"></i> {{ $t('ordersManage.nameMismatch') }}
              </p>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline" @click="closeConfirmModal">{{ $t('common.cancel') }}</button>
            <button class="btn btn-success"
              :disabled="confirmModal.typedName !== confirmModal.order?.user?.name?.toUpperCase() || confirmModal.submitting"
              @click="submitConfirmPayment">
              <i class="fas" :class="confirmModal.submitting ? 'fa-spinner fa-spin' : 'fa-check-circle'"></i>
              {{ confirmModal.submitting ? $t('ordersManage.confirming') : $t('ordersManage.confirmPayment') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delivery Details Modal -->
    <Teleport to="body">
      <div v-if="deliveryModal.show" class="modal-overlay" @click.self="closeDeliveryModal">
        <div class="modal-content card">
          <div class="modal-header">
            <h3><i class="fas fa-truck"></i> {{ $t('ordersManage.deliveryDetails') }}</h3>
            <button class="modal-close" @click="closeDeliveryModal"><i class="fas fa-times"></i></button>
          </div>
          <div class="modal-body">
            <div class="modal-order-summary">
              <div class="summary-line"><span>{{ $t('ordersManage.order') }}</span><strong>{{
                deliveryModal.order?.order_number }}</strong></div>
              <div class="summary-line"><span>{{ $t('ordersManage.customer') }}</span><strong>{{
                deliveryModal.order?.user?.name }}</strong></div>
              <div v-if="deliveryModal.order?.shippingAddress" class="summary-line"><span>{{ $t('ordersManage.address')
              }}</span><strong>{{ deliveryModal.order?.shippingAddress?.street }}, {{
                    deliveryModal.order?.shippingAddress?.city }}</strong></div>
            </div>
            <div class="form-group">
              <label>{{ $t('ordersManage.trackingNumber') }}</label>
              <input v-model="deliveryForm.tracking_number" type="text"
                :placeholder="$t('ordersManage.trackingPlaceholder')" />
            </div>
            <div class="form-group">
              <label>{{ $t('ordersManage.deliveryNotes') }}</label>
              <textarea v-model="deliveryForm.delivery_notes" rows="3"
                :placeholder="$t('ordersManage.deliveryNotesPlaceholder')"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline" @click="closeDeliveryModal">{{ $t('common.cancel') }}</button>
            <button class="btn btn-primary" @click="saveDelivery" :disabled="deliveryModal.saving">
              <i class="fas" :class="deliveryModal.saving ? 'fa-spinner fa-spin' : 'fa-save'"></i>
              {{ deliveryModal.saving ? $t('common.saving') : $t('common.save') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas fa-check-circle"></i> {{ toastMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { orderManageApi, branchApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import TablePagination from '@/components/TablePagination.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const authStore = useAuthStore()
const dashboardRoute = computed(() => (authStore.isOwner ? '/owner' : '/employee'))

const orders = ref([])
const branches = ref([])
const loading = ref(true)
const search = ref('')
const statusFilter = ref('')
const branchFilter = ref('')
const toastMsg = ref('')
const confirmModal = ref({ show: false, order: null, typedName: '', submitting: false })
const deliveryModal = ref({ show: false, order: null, saving: false })
const deliveryForm = ref({ tracking_number: '', delivery_notes: '' })

const currentPage = ref(1)
const showAll = ref(false)
const PER_PAGE = 15
const paginatedOrders = computed(() => {
  if (showAll.value) return orders.value
  const start = (currentPage.value - 1) * PER_PAGE
  return orders.value.slice(start, start + PER_PAGE)
})
const totalPages = computed(() => Math.ceil(orders.value.length / PER_PAGE))
const pageInfo = computed(() => {
  const total = orders.value.length
  if (showAll.value) return { from: 1, to: total, total }
  const from = total === 0 ? 0 : (currentPage.value - 1) * PER_PAGE + 1
  const to = Math.min(currentPage.value * PER_PAGE, total)
  return { from, to, total }
})
function goToPage(p) { currentPage.value = p; showAll.value = false }
function toggleShowAll() { showAll.value = !showAll.value }

watch([search, statusFilter], () => { currentPage.value = 1; showAll.value = false })

const totalRevenue = computed(() => orders.value.reduce((sum, o) => sum + Number(o.total || 0), 0))

function formatPrice(v) { return Number(v).toLocaleString('en-TZ') }
function formatDate(d) { return new Date(d).toLocaleDateString('en-TZ', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) }

let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadOrders(), 300)
}

async function loadOrders() {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    if (search.value) params.search = search.value
    if (branchFilter.value) params.branch_id = branchFilter.value
    const res = await orderManageApi.getAll(params)
    orders.value = res.data.data || []
  } catch { /* empty */ }
  loading.value = false
}

async function updateStatus(order, status) {
  try {
    const res = await orderManageApi.updateStatus(order.id, status)
    order.status = res.data.order.status
    order.handler = res.data.order.handler
    toastMsg.value = res.data.message
    setTimeout(() => toastMsg.value = '', 3000)
  } catch { /* empty */ }
}

function openConfirmModal(order) {
  confirmModal.value = { show: true, order, typedName: '', submitting: false }
}

function closeConfirmModal() {
  confirmModal.value = { show: false, order: null, typedName: '', submitting: false }
}

async function submitConfirmPayment() {
  const modal = confirmModal.value
  if (modal.typedName !== modal.order?.user?.name?.toUpperCase()) return
  modal.submitting = true
  try {
    const res = await orderManageApi.updateStatus(modal.order.id, 'paid')
    modal.order.status = res.data.order.status
    modal.order.handler = res.data.order.handler
    toastMsg.value = res.data.message
    setTimeout(() => toastMsg.value = '', 3000)
    closeConfirmModal()
  } catch { /* empty */ }
  modal.submitting = false
}

function openDeliveryModal(order) {
  deliveryForm.value = {
    tracking_number: order.tracking_number || '',
    delivery_notes: order.delivery_notes || '',
  }
  deliveryModal.value = { show: true, order, saving: false }
}

function closeDeliveryModal() {
  deliveryModal.value = { show: false, order: null, saving: false }
}

async function saveDelivery() {
  const modal = deliveryModal.value
  modal.saving = true
  try {
    const res = await orderManageApi.updateDelivery(modal.order.id, deliveryForm.value)
    modal.order.tracking_number = res.data.order.tracking_number
    modal.order.delivery_notes = res.data.order.delivery_notes
    toastMsg.value = res.data.message
    setTimeout(() => toastMsg.value = '', 3000)
    closeDeliveryModal()
  } catch { /* empty */ }
  modal.saving = false
}

onMounted(async () => {
  try { const res = await branchApi.getAll(); branches.value = res.data } catch { /* empty */ }
  await loadOrders()
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
  margin-bottom: 24px;
}

.dash-header h1 {
  font-size: 26px;
}

.dash-header p {
  color: #888;
  font-size: 14px;
  margin-top: 4px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  text-decoration: none;
  color: #333;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.back-btn:hover {
  border-color: #e74c3c;
  color: #e74c3c;
}

.filters-bar {
  padding: 16px 20px;
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f8f9fa;
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 10px 14px;
  flex: 1;
  min-width: 150px;
}

.search-box i {
  color: #999;
}

.search-box input {
  flex: 1;
  border: none;
  background: none;
  font-size: 14px;
  outline: none;
}

.filter-select-wrap {
  display: flex;
  align-items: center;
}

.filter-select {
  padding: 6px 12px;
  border: 1px solid #eee;
  border-radius: 6px;
  font-size: 13px;
  font-family: inherit;
  background: #fff;
  cursor: pointer;
  min-width: 140px;
}

.filter-select:focus {
  outline: none;
  border-color: #e74c3c;
}

.status-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 6px 14px;
  border: 1px solid #eee;
  border-radius: 20px;
  background: #fff;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #e74c3c;
  color: #e74c3c;
}

.filter-btn.active {
  background: #e74c3c;
  color: #fff;
  border-color: #e74c3c;
}

.pending-filter.active {
  background: #f39c12;
  border-color: #f39c12;
}

.pending-filter:hover {
  border-color: #f39c12;
  color: #f39c12;
}

.summary-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.summary-pill {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 20px;
  padding: 6px 16px;
  font-size: 13px;
  color: #666;
}

.pill-num {
  font-weight: 700;
  color: #333;
}

.revenue-pill .pill-num {
  color: #27ae60;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #888;
  font-size: 16px;
}

.loading-state i {
  color: #e74c3c;
  margin-right: 8px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-state i {
  font-size: 48px;
  color: #ddd;
  margin-bottom: 16px;
  display: block;
}

.empty-state h3 {
  font-size: 20px;
  margin-bottom: 8px;
}

.empty-state p {
  color: #888;
  font-size: 14px;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-card {
  padding: 24px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.order-number {
  font-size: 16px;
  font-weight: 700;
  color: #333;
}

.order-date {
  font-size: 12px;
  color: #999;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: capitalize;
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

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.order-customer {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.customer-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #eaf4ff;
  color: #2980b9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.customer-name {
  display: block;
  font-weight: 600;
  font-size: 14px;
}

.customer-email {
  display: block;
  font-size: 12px;
  color: #888;
}

.order-items {
  margin-bottom: 16px;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 14px;
}

.order-item:last-child {
  border-bottom: none;
}

.item-meta {
  color: #888;
  font-size: 12px;
}

.item-total {
  margin-left: auto;
  font-weight: 600;
  color: #e74c3c;
}

.order-footer {
  border-top: 1px solid #eee;
  padding-top: 16px;
}

.order-totals {
  margin-bottom: 12px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 4px 0;
  color: #666;
}

.total-row.grand {
  font-size: 16px;
  font-weight: 700;
  color: #e74c3c;
  border-top: 1px solid #eee;
  padding-top: 8px;
  margin-top: 4px;
}

.payment-info,
.handler-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
  padding: 6px 0;
}

.payment-info i {
  color: #27ae60;
}

.handler-info i {
  color: #2980b9;
}

.order-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-primary {
  background: #e74c3c;
  color: #fff;
}

.btn-primary:hover {
  background: #c0392b;
}

.btn-danger {
  background: #fff;
  color: #e74c3c;
  border: 1px solid #e74c3c;
}

.btn-danger:hover {
  background: #fef5f5;
}

.btn-outline-dark {
  background: #fff;
  color: #333;
  border: 1px solid #ddd;
}

.btn-outline-dark:hover {
  border-color: #333;
}

.btn-success {
  background: #27ae60;
  color: #fff;
}

.btn-success:hover {
  background: #219a52;
}

.pending-payment-alert {
  display: flex;
  gap: 12px;
  padding: 14px 16px;
  background: #fff8e1;
  border: 1px solid #ffe082;
  border-radius: 8px;
  margin-top: 12px;
}

.delivery-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #2980b9;
  padding: 8px 12px;
  background: #eaf4ff;
  border-radius: 6px;
  margin-top: 10px;
}

.delivery-info i {
  color: #2980b9;
}

.delivery-info strong {
  color: #1a6da0;
}

.modal-body .form-group {
  margin-bottom: 14px;
}

.modal-body .form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #555;
  margin-bottom: 6px;
}

.modal-body .form-group input,
.modal-body .form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}

.modal-body .form-group input:focus,
.modal-body .form-group textarea:focus {
  outline: none;
  border-color: #e74c3c;
}

.alert-icon {
  color: #f39c12;
  font-size: 20px;
  margin-top: 2px;
  flex-shrink: 0;
}

.alert-content strong {
  display: block;
  font-size: 14px;
  color: #e67e22;
  margin-bottom: 4px;
}

.alert-content p {
  font-size: 12px;
  color: #888;
  margin: 2px 0;
  line-height: 1.5;
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
  color: #27ae60;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  padding: 20px;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  width: 100%;
  max-width: 480px;
  border-radius: 12px;
  overflow: hidden;
  animation: scaleIn 0.2s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-header h3 i {
  color: #e74c3c;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  background: #f5f5f5;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #e74c3c;
  color: #fff;
}

.modal-body {
  padding: 24px;
}

.modal-order-summary {
  background: #f8f9fa;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.summary-line {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 14px;
}

.summary-line span {
  color: #888;
}

.summary-line strong {
  color: #333;
}

.confirm-prompt p {
  font-size: 14px;
  color: #555;
  margin-bottom: 8px;
  line-height: 1.5;
}

.expected-name {
  background: #f0f0f0;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 12px !important;
}

.confirm-input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-family: inherit;
  transition: border-color 0.2s;
}

.confirm-input:focus {
  outline: none;
  border-color: #e74c3c;
}

.confirm-input.valid {
  border-color: #27ae60;
  background: #eafaf1;
}

.mismatch-warning {
  color: #e74c3c;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px;
  border-top: 1px solid #eee;
  background: #f8f9fa;
}

.btn-outline {
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-outline:hover {
  border-color: #999;
}

.btn-success {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  background: #27ae60;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-success:hover {
  background: #219a52;
}

.btn-success:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
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
</style>
