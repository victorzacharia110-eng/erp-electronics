<template>
  <div class="dashboard-page container">
    <SkeletonLoader v-if="loading" type="stats" :count="3" />
    <template v-else>
      <div class="dash-header">
        <div>
          <h1><i class="fas fa-truck" style="color: #e74c3c; margin-right: 12px;"></i>Supplier Portal</h1>
          <p>{{ profile?.company_name || 'Your Supplier Dashboard' }}</p>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon"><i class="fas fa-file-invoice"></i></div>
          <div>
            <span class="stat-value">{{ stats.total }}</span>
            <span class="stat-label">Total Orders</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orders"><i class="fas fa-clock"></i></div>
          <div>
            <span class="stat-value">{{ stats.pending }}</span>
            <span class="stat-label">Pending Delivery</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon products"><i class="fas fa-check-circle"></i></div>
          <div>
            <span class="stat-value">{{ stats.completed }}</span>
            <span class="stat-label">Completed</span>
          </div>
        </div>
      </div>

      <SkeletonLoader v-if="loadingOrders" type="table" :count="5" />

      <div v-else-if="orders.length === 0" class="empty-state card">
        <i class="fas fa-file-invoice"></i>
        <h3>No purchase orders yet</h3>
        <p>You have no purchase orders assigned to you at this time.</p>
      </div>

      <template v-else>
        <div class="card table-wrap">
          <table class="sa-table">
            <thead>
              <tr>
                <th>PO Number</th>
                <th>Date</th>
                <th>Items</th>
                <th>Total Cost</th>
                <th>Status</th>
                <th>Expected Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="po in orders" :key="po.id">
                <td class="code-cell">{{ po.po_number }}</td>
                <td>{{ formatDate(po.created_at) }}</td>
                <td>{{ (po.line_items || []).length }}</td>
                <td class="amount-cell">TSh {{ Number(po.total_cost || 0).toLocaleString('en-TZ') }}</td>
                <td>
                  <span :class="['status-badge', `status-${po.status}`]">{{ po.status }}</span>
                </td>
                <td>{{ formatDate(po.expected_date) }}</td>
                <td class="actions-cell">
                  <button class="btn-icon" title="View Details" @click="viewOrder(po)">
                    <i class="fas fa-eye"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <TablePagination
          v-if="totalPages > 1"
          :current-page="currentPage"
          :total-pages="totalPages"
          :from="pageInfo.from"
          :to="pageInfo.to"
          :total="pageInfo.total"
          @page="goToPage"
        />
      </template>

      <div class="modal-overlay" v-if="showDetailModal" @click.self="showDetailModal = false">
        <div class="modal-card modal-lg">
          <div class="modal-header">
            <h3><i class="fas fa-file-invoice"></i> {{ selectedPO?.po_number }}</h3>
            <button class="modal-close" @click="showDetailModal = false"><i class="fas fa-times"></i></button>
          </div>
          <div class="modal-body" v-if="selectedPO">
            <div class="po-detail-grid">
              <div class="po-detail">
                <span class="detail-label">Supplier</span>
                <span class="detail-value">{{ selectedPO.supplier_name }}</span>
              </div>
              <div class="po-detail">
                <span class="detail-label">Status</span>
                <span :class="['status-badge', `status-${selectedPO.status}`]">{{ selectedPO.status }}</span>
              </div>
              <div class="po-detail">
                <span class="detail-label">Date</span>
                <span class="detail-value">{{ formatDate(selectedPO.created_at) }}</span>
              </div>
              <div class="po-detail">
                <span class="detail-label">Expected Date</span>
                <span class="detail-value">{{ formatDate(selectedPO.expected_date) }}</span>
              </div>
              <div class="po-detail">
                <span class="detail-label">Total Cost</span>
                <span class="detail-value amount-cell">TSh {{ Number(selectedPO.total_cost || 0).toLocaleString('en-TZ') }}</span>
              </div>
              <div class="po-detail">
                <span class="detail-label">Notes</span>
                <span class="detail-value">{{ selectedPO.notes || '—' }}</span>
              </div>
            </div>

            <div class="line-items-section">
              <h4>Line Items</h4>
              <div class="table-wrap">
                <table class="sa-table line-table">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Qty</th>
                      <th>Unit Cost</th>
                      <th>Total</th>
                      <th>Qty Received</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, idx) in selectedPO.line_items || []" :key="idx">
                      <td>{{ item.product_name || '—' }}</td>
                      <td>{{ item.quantity }}</td>
                      <td class="amount-cell">TSh {{ Number(item.unit_cost || 0).toLocaleString('en-TZ') }}</td>
                      <td class="amount-cell">TSh {{ Number((item.quantity || 0) * (item.unit_cost || 0)).toLocaleString('en-TZ') }}</td>
                      <td>{{ item.quantity_received ?? 0 }}</td>
                    </tr>
                    <tr v-if="!selectedPO.line_items?.length">
                      <td colspan="5" class="empty-row">No line items</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="total-row">
              <span class="total-label">Total Cost:</span>
              <span class="total-value">TSh {{ Number(selectedPO.total_cost || 0).toLocaleString('en-TZ') }}</span>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline" @click="showDetailModal = false">Close</button>
            <button
              v-if="selectedPO?.status === 'ordered'"
              class="btn btn-success"
              @click="confirmMarkReceived"
            >
              <i class="fas fa-check-double"></i> Mark as Received
            </button>
          </div>
        </div>
      </div>

      <div class="modal-overlay" v-if="showConfirmModal" @click.self="showConfirmModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h3><i class="fas fa-exclamation-triangle" style="color: #f39c12;"></i> Confirm Receipt</h3>
            <button class="modal-close" @click="showConfirmModal = false"><i class="fas fa-times"></i></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to mark this purchase order as received?</p>
            <p class="po-ref" v-if="selectedPO">{{ selectedPO.po_number }} &mdash; {{ selectedPO.supplier_name }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline" @click="showConfirmModal = false">Cancel</button>
            <button class="btn btn-success" :disabled="submitting" @click="doMarkReceived">
              <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
              {{ submitting ? 'Updating...' : 'Yes, Mark Received' }}
            </button>
          </div>
        </div>
      </div>

      <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
        <i class="fas fa-check-circle"></i> {{ toastMsg }}
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { supplierPortalApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import TablePagination from '@/components/TablePagination.vue'

const loading = ref(true)
const loadingOrders = ref(true)
const submitting = ref(false)
const toastMsg = ref('')
const profile = ref(null)
const orders = ref([])

const currentPage = ref(1)
const totalPages = ref(1)
const pageInfo = ref({ from: 0, to: 0, total: 0 })

const showDetailModal = ref(false)
const showConfirmModal = ref(false)
const selectedPO = ref(null)

const stats = computed(() => {
  const all = orders.value.length
  const pending = orders.value.filter(o => o.status === 'ordered').length
  const completed = orders.value.filter(o => o.status === 'received').length
  return { total: all, pending, completed }
})

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-TZ')
}

function showToast(msg) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 3000)
}

function goToPage(page) {
  currentPage.value = page
  loadOrders()
}

async function loadProfile() {
  try {
    const res = await supplierPortalApi.getProfile()
    profile.value = res.data
  } catch (e) {
    console.error(e)
  }
}

async function loadOrders() {
  loadingOrders.value = true
  try {
    const res = await supplierPortalApi.getOrders({ page: currentPage.value, per_page: 15 })
    orders.value = res.data.data || []
    totalPages.value = res.data.last_page || 1
    pageInfo.value = {
      from: res.data.from || 0,
      to: res.data.to || 0,
      total: res.data.total || 0
    }
  } catch (e) {
    console.error(e)
  } finally {
    loadingOrders.value = false
    loading.value = false
  }
}

async function viewOrder(po) {
  try {
    const res = await supplierPortalApi.getOrder(po.id)
    selectedPO.value = res.data
  } catch {
    selectedPO.value = po
  }
  showDetailModal.value = true
}

function confirmMarkReceived() {
  showDetailModal.value = false
  showConfirmModal.value = true
}

async function doMarkReceived() {
  submitting.value = true
  try {
    await supplierPortalApi.updateOrderStatus(selectedPO.value.id, { status: 'received' })
    showConfirmModal.value = false
    showToast('Purchase order marked as received')
    await loadOrders()
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadProfile(), loadOrders()])
})
</script>

<style scoped>
.dashboard-page { padding: 32px 0; }
.dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.dash-header h1 { font-size: 24px; font-weight: 700; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }

.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 32px; }
.stat-card { background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 24px; display: flex; align-items: center; gap: 16px; }
.stat-icon { width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; background: #fef5f5; color: #e74c3c; }
.stat-icon.orders { background: #eef6ff; color: #2874a6; }
.stat-icon.products { background: #eafaf1; color: #27ae60; }
.stat-value { display: block; font-size: 22px; font-weight: 700; color: #333; }
.stat-label { font-size: 13px; color: #888; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.table-wrap { overflow-x: auto; }
.sa-table { width: 100%; border-collapse: collapse; }
.sa-table th { padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 1px solid #f0f0f0; background: #fafafa; }
.sa-table td { padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.code-cell { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #555; }
.amount-cell { text-align: right; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.empty-row { text-align: center; color: #aaa; padding: 32px; }

.status-badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.status-draft { background: #fef9e7; color: #7d6608; }
.status-ordered { background: #eef6ff; color: #2874a6; }
.status-received { background: #f0fff4; color: #1e8449; }

.actions-cell { white-space: nowrap; display: flex; gap: 6px; }
.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 13px; color: #666; transition: all 0.2s; }
.btn-icon:hover { border-color: #e74c3c; color: #e74c3c; }

.empty-state { text-align: center; padding: 60px 20px; }
.empty-state i { font-size: 48px; color: #ddd; margin-bottom: 16px; display: block; }
.empty-state h3 { font-size: 20px; margin-bottom: 8px; }
.empty-state p { color: #888; font-size: 14px; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-success { background: #27ae60; color: #fff; }
.btn-success:hover { background: #219a52; }
.btn-success:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-outline { padding: 10px 20px; border: 1px solid #ddd; border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px; font-weight: 500; color: #666; transition: all 0.2s; }
.btn-outline:hover { border-color: #999; color: #333; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 2000; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: #fff; border-radius: 10px; width: 100%; max-width: 480px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); max-height: 90vh; display: flex; flex-direction: column; }
.modal-lg { max-width: 720px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
.modal-header h3 { font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 8px; margin: 0; }
.modal-header h3 i { color: #e74c3c; }
.modal-close { background: none; border: none; cursor: pointer; font-size: 18px; color: #999; padding: 4px; transition: color 0.2s; }
.modal-close:hover { color: #333; }
.modal-body { padding: 24px; overflow-y: auto; flex: 1; }
.modal-body p { color: #555; font-size: 14px; line-height: 1.6; margin: 0 0 8px; }
.modal-footer { display: flex; gap: 12px; justify-content: flex-end; padding: 16px 24px; border-top: 1px solid #f0f0f0; }

.po-detail-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.po-detail { display: flex; flex-direction: column; }
.detail-label { font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 4px; }
.detail-value { font-size: 14px; color: #333; }

.line-items-section { margin-top: 8px; }
.line-items-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 10px; }
.line-table th { font-size: 11px; }
.line-table td { padding: 8px 12px; }

.total-row { display: flex; justify-content: flex-end; align-items: center; gap: 12px; margin-top: 16px; padding-top: 16px; border-top: 2px solid #f0f0f0; }
.total-label { font-size: 14px; font-weight: 600; color: #555; }
.total-value { font-size: 20px; font-weight: 700; color: #e74c3c; font-family: 'JetBrains Mono', monospace; }

.po-ref { font-weight: 600; color: #333; margin-top: 8px !important; }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #2c3e50; color: #fff; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 2000; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); animation: slideUp 0.3s ease; }
.toast i { color: #27ae60; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .stats-grid { grid-template-columns: 1fr; }
  .modal-card { margin: 10px; }
  .modal-lg { max-width: 100%; }
  .po-detail-grid { grid-template-columns: 1fr 1fr; }
  .line-table th:nth-child(1),
  .line-table td:nth-child(1) { min-width: 160px; }
}
</style>
