<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-file-invoice" style="color: #e74c3c; margin-right: 12px;"></i>Purchase Orders</h1>
        <p>Manage supplier purchase orders and inventory restocking</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" @click="openCreateModal"><i class="fas fa-plus"></i> New Purchase Order</button>
        <router-link to="/owner/accounting" class="back-btn"><i class="fas fa-arrow-left"></i> Back</router-link>
      </div>
    </div>

    <div class="status-tabs">
      <button
        v-for="tab in statusTabs"
        :key="tab.value"
        :class="['tab-btn', { active: statusFilter === tab.value }]"
        @click="filterByStatus(tab.value)"
      >
        {{ tab.label }}
        <span v-if="tab.count !== null" class="tab-count">{{ tab.count }}</span>
      </button>
    </div>

    <SkeletonLoader v-if="loading" type="table" :count="5" />

    <div v-else-if="purchaseOrders.length === 0" class="empty-state card">
      <i class="fas fa-file-invoice"></i>
      <h3>No purchase orders yet</h3>
      <p>Create your first purchase order to start tracking supplier orders and inventory.</p>
      <button class="btn btn-primary" style="margin-top: 16px;" @click="openCreateModal"><i class="fas fa-plus"></i> Create Purchase Order</button>
    </div>

    <template v-else>
      <div class="card table-wrap">
        <table class="sa-table">
          <thead>
            <tr>
              <th>PO Number</th>
              <th>Supplier</th>
              <th>Date</th>
              <th>Total Cost</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="po in purchaseOrders" :key="po.id">
              <td class="code-cell">{{ po.po_number }}</td>
              <td>{{ po.supplier_name }}</td>
              <td>{{ formatDate(po.created_at) }}</td>
              <td class="amount-cell">TSh {{ Number(po.total_cost || 0).toLocaleString('en-TZ') }}</td>
              <td>
                <span :class="['status-badge', `status-${po.status}`]">{{ po.status }}</span>
              </td>
              <td class="actions-cell">
                <button class="btn-icon" title="View" @click="viewPO(po)">
                  <i class="fas fa-eye"></i>
                </button>
                <button
                  v-if="po.status === 'ordered'"
                  class="btn-icon btn-success-icon"
                  title="Receive"
                  @click="confirmReceive(po)"
                >
                  <i class="fas fa-truck-loading"></i>
                </button>
                <button
                  v-if="po.status === 'draft'"
                  class="btn-icon btn-danger-icon"
                  title="Delete"
                  @click="confirmDelete(po)"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="purchaseOrders.length === 0">
              <td colspan="6" class="empty-row">No purchase orders found</td>
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
        @page-change="goToPage"
      />
    </template>

    <!-- Create Purchase Order Modal -->
    <div class="modal-overlay" v-if="showCreateModal" @click.self="showCreateModal = false">
      <div class="modal-card modal-lg">
        <div class="modal-header">
          <h3><i class="fas fa-file-invoice"></i> New Purchase Order</h3>
          <button class="modal-close" @click="showCreateModal = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label>Supplier Name <span class="required">*</span></label>
              <input v-model="form.supplier_name" type="text" placeholder="e.g. Tech Suppliers Ltd" />
            </div>
            <div class="form-group">
              <label>Supplier Contact</label>
              <input v-model="form.supplier_contact" type="text" placeholder="Phone or email" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Expected Date</label>
              <input v-model="form.expected_date" type="date" />
            </div>
            <div class="form-group">
              <label>Notes</label>
              <input v-model="form.notes" type="text" placeholder="Optional notes" />
            </div>
          </div>

          <div class="line-items-section">
            <div class="section-header">
              <h4>Line Items</h4>
              <button class="btn btn-sm btn-outline" @click="addLineItem"><i class="fas fa-plus"></i> Add Item</button>
            </div>
            <div class="table-wrap">
              <table class="sa-table line-table">
                <thead>
                  <tr>
                    <th>Product Variant</th>
                    <th style="width: 110px;">Quantity</th>
                    <th style="width: 140px;">Unit Cost</th>
                    <th style="width: 140px;">Total</th>
                    <th style="width: 50px;"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in form.line_items" :key="index">
                    <td>
                      <select v-model="item.product_variant_id" class="variant-select">
                        <option value="">Select variant...</option>
                        <option v-for="v in allVariants" :key="v.id" :value="v.id">
                          {{ v.product?.name || 'Product' }} - {{ v.name || v.sku }} ({{ v.sku }})
                        </option>
                      </select>
                    </td>
                    <td>
                      <input v-model.number="item.quantity" type="number" min="1" class="num-input" />
                    </td>
                    <td>
                      <input v-model.number="item.unit_cost" type="number" min="0" class="num-input" />
                    </td>
                    <td class="amount-cell">TSh {{ Number((item.quantity || 0) * (item.unit_cost || 0)).toLocaleString('en-TZ') }}</td>
                    <td>
                      <button v-if="form.line_items.length > 1" class="btn-icon btn-danger-icon" title="Remove" @click="removeLineItem(index)">
                        <i class="fas fa-times"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="total-row">
            <span class="total-label">Total Cost:</span>
            <span class="total-value">TSh {{ Number(formTotalCost).toLocaleString('en-TZ') }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showCreateModal = false">Cancel</button>
          <button class="btn btn-primary" :disabled="submitting || !form.supplier_name.trim()" @click="submitPO">
            <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
            {{ submitting ? 'Creating...' : 'Create Purchase Order' }}
          </button>
        </div>
      </div>
    </div>

    <!-- View Purchase Order Modal -->
    <div class="modal-overlay" v-if="showViewModal" @click.self="showViewModal = false">
      <div class="modal-card modal-lg">
        <div class="modal-header">
          <h3><i class="fas fa-file-invoice"></i> {{ viewingPO?.po_number }}</h3>
          <button class="modal-close" @click="showViewModal = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body" v-if="viewingPO">
          <div class="po-detail-grid">
            <div class="po-detail">
              <span class="detail-label">Supplier</span>
              <span class="detail-value">{{ viewingPO.supplier_name }}</span>
            </div>
            <div class="po-detail">
              <span class="detail-label">Contact</span>
              <span class="detail-value">{{ viewingPO.supplier_contact || '—' }}</span>
            </div>
            <div class="po-detail">
              <span class="detail-label">Status</span>
              <span :class="['status-badge', `status-${viewingPO.status}`]">{{ viewingPO.status }}</span>
            </div>
            <div class="po-detail">
              <span class="detail-label">Date</span>
              <span class="detail-value">{{ formatDate(viewingPO.created_at) }}</span>
            </div>
            <div class="po-detail">
              <span class="detail-label">Expected</span>
              <span class="detail-value">{{ viewingPO.expected_date ? formatDate(viewingPO.expected_date) : '—' }}</span>
            </div>
            <div class="po-detail">
              <span class="detail-label">Notes</span>
              <span class="detail-value">{{ viewingPO.notes || '—' }}</span>
            </div>
          </div>

          <div class="line-items-section" style="margin-top: 20px;">
            <h4>Line Items</h4>
            <div class="table-wrap">
              <table class="sa-table line-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Variant</th>
                    <th>Qty</th>
                    <th>Unit Cost</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, idx) in viewingPO.line_items || []" :key="idx">
                    <td>{{ item.product_name || '—' }}</td>
                    <td>{{ item.variant_name || item.variant_sku || '—' }}</td>
                    <td>{{ item.quantity }}</td>
                    <td class="amount-cell">TSh {{ Number(item.unit_cost || 0).toLocaleString('en-TZ') }}</td>
                    <td class="amount-cell">TSh {{ Number((item.quantity || 0) * (item.unit_cost || 0)).toLocaleString('en-TZ') }}</td>
                  </tr>
                  <tr v-if="!viewingPO.line_items?.length">
                    <td colspan="5" class="empty-row">No line items</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="total-row">
            <span class="total-label">Total Cost:</span>
            <span class="total-value">TSh {{ Number(viewingPO.total_cost || 0).toLocaleString('en-TZ') }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showViewModal = false">Close</button>
          <button
            v-if="viewingPO?.status === 'ordered'"
            class="btn btn-success"
            @click="showViewModal = false; confirmReceive(viewingPO)"
          >
            <i class="fas fa-truck-loading"></i> Receive
          </button>
        </div>
      </div>
    </div>

    <!-- Receive Confirmation Modal -->
    <div class="modal-overlay" v-if="showReceiveModal" @click.self="showReceiveModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3><i class="fas fa-exclamation-triangle" style="color: #f39c12;"></i> Confirm Receive</h3>
          <button class="modal-close" @click="showReceiveModal = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to receive this PO? This will update inventory.</p>
          <p class="po-ref" v-if="receivingPO">{{ receivingPO.po_number }} &mdash; {{ receivingPO.supplier_name }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showReceiveModal = false">Cancel</button>
          <button class="btn btn-success" :disabled="submitting" @click="doReceive">
            <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
            {{ submitting ? 'Receiving...' : 'Yes, Receive PO' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal-overlay" v-if="showDeleteModal" @click.self="showDeleteModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3><i class="fas fa-exclamation-triangle" style="color: #e74c3c;"></i> Delete Purchase Order</h3>
          <button class="modal-close" @click="showDeleteModal = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete this draft purchase order? This action cannot be undone.</p>
          <p class="po-ref" v-if="deletingPO">{{ deletingPO.po_number }} &mdash; {{ deletingPO.supplier_name }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showDeleteModal = false">Cancel</button>
          <button class="btn btn-danger" :disabled="submitting" @click="doDelete">
            <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
            {{ submitting ? 'Deleting...' : 'Delete PO' }}
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
import { purchaseOrderApi, productManageApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import TablePagination from '@/components/TablePagination.vue'

const loading = ref(true)
const submitting = ref(false)
const toastMsg = ref('')
const purchaseOrders = ref([])
const allVariants = ref([])
const statusFilter = ref('')

const currentPage = ref(1)
const totalPages = ref(1)
const pageInfo = ref({ from: 0, to: 0, total: 0 })

const showCreateModal = ref(false)
const showViewModal = ref(false)
const showReceiveModal = ref(false)
const showDeleteModal = ref(false)

const viewingPO = ref(null)
const receivingPO = ref(null)
const deletingPO = ref(null)

const form = reactive({
  supplier_name: '',
  supplier_contact: '',
  expected_date: '',
  notes: '',
  line_items: [
    { product_variant_id: '', quantity: 1, unit_cost: 0 }
  ]
})

const statusTabs = computed(() => {
  const all = purchaseOrders.value.length
  const draft = purchaseOrders.value.filter(p => p.status === 'draft').length
  const ordered = purchaseOrders.value.filter(p => p.status === 'ordered').length
  const received = purchaseOrders.value.filter(p => p.status === 'received').length
  return [
    { label: 'All', value: '', count: all },
    { label: 'Draft', value: 'draft', count: draft },
    { label: 'Ordered', value: 'ordered', count: ordered },
    { label: 'Received', value: 'received', count: received }
  ]
})

const formTotalCost = computed(() => {
  return form.line_items.reduce((sum, item) => sum + (item.quantity || 0) * (item.unit_cost || 0), 0)
})

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-TZ')
}

function showToast(msg) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 3000)
}

function filterByStatus(status) {
  statusFilter.value = status
  currentPage.value = 1
  loadPOs()
}

function goToPage(page) {
  currentPage.value = page
  loadPOs()
}

function resetForm() {
  form.supplier_name = ''
  form.supplier_contact = ''
  form.expected_date = ''
  form.notes = ''
  form.line_items = [{ product_variant_id: '', quantity: 1, unit_cost: 0 }]
}

function openCreateModal() {
  resetForm()
  showCreateModal.value = true
}

function addLineItem() {
  form.line_items.push({ product_variant_id: '', quantity: 1, unit_cost: 0 })
}

function removeLineItem(index) {
  form.line_items.splice(index, 1)
}

async function loadPOs() {
  loading.value = true
  try {
    const params = { page: currentPage.value, per_page: 15 }
    if (statusFilter.value) params.status = statusFilter.value
    const res = await purchaseOrderApi.getAll(params)
    purchaseOrders.value = res.data.data || []
    totalPages.value = res.data.last_page || 1
    pageInfo.value = {
      from: res.data.from || 0,
      to: res.data.to || 0,
      total: res.data.total || 0
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadVariants() {
  try {
    const res = await productManageApi.getAll({ all: 1 })
    const products = res.data.data || []
    const variants = []
    for (const product of products) {
      for (const v of product.variants || []) {
        variants.push({ ...v, product: { name: product.name } })
      }
    }
    allVariants.value = variants
  } catch (e) {
    console.error(e)
  }
}

async function submitPO() {
  if (!form.supplier_name.trim()) return
  const validItems = form.line_items.filter(i => i.product_variant_id && i.quantity > 0)
  if (validItems.length === 0) return

  submitting.value = true
  try {
    await purchaseOrderApi.create({
      supplier_name: form.supplier_name.trim(),
      supplier_contact: form.supplier_contact.trim() || null,
      expected_date: form.expected_date || null,
      notes: form.notes.trim() || null,
      line_items: validItems.map(i => ({
        product_variant_id: i.product_variant_id,
        quantity: i.quantity,
        unit_cost: i.unit_cost
      }))
    })
    showCreateModal.value = false
    showToast('Purchase order created')
    await loadPOs()
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

function viewPO(po) {
  viewingPO.value = po
  showViewModal.value = true
}

function confirmReceive(po) {
  receivingPO.value = po
  showReceiveModal.value = true
}

function confirmDelete(po) {
  deletingPO.value = po
  showDeleteModal.value = true
}

async function doReceive() {
  submitting.value = true
  try {
    await purchaseOrderApi.receive(receivingPO.value.id)
    showReceiveModal.value = false
    showToast('Purchase order received — inventory updated')
    await loadPOs()
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

async function doDelete() {
  submitting.value = true
  try {
    await purchaseOrderApi.delete(deletingPO.value.id)
    showDeleteModal.value = false
    showToast('Purchase order deleted')
    await loadPOs()
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadPOs(), loadVariants()])
})
</script>

<style scoped>
.dashboard-page { padding: 32px 0; }
.dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.dash-header h1 { font-size: 24px; font-weight: 700; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; color: #666; text-decoration: none; font-size: 13px; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-success { background: #27ae60; color: #fff; }
.btn-success:hover { background: #219a52; }
.btn-success:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-danger { background: #e74c3c; color: #fff; }
.btn-danger:hover { background: #c0392b; }
.btn-danger:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-outline { padding: 10px 20px; border: 1px solid #ddd; border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px; font-weight: 500; color: #666; transition: all 0.2s; }
.btn-outline:hover { border-color: #999; color: #333; }
.btn-sm { padding: 7px 12px; font-size: 12px; }

.status-tabs { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
.tab-btn { padding: 8px 18px; border: 1px solid #e0e0e0; border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px; font-weight: 500; color: #666; transition: all 0.2s; display: inline-flex; align-items: center; gap: 6px; }
.tab-btn:hover { border-color: #e74c3c; color: #e74c3c; }
.tab-btn.active { background: #e74c3c; color: #fff; border-color: #e74c3c; }
.tab-btn.active .tab-count { background: rgba(255,255,255,0.25); color: #fff; }
.tab-count { background: #f0f0f0; color: #888; font-size: 11px; padding: 1px 7px; border-radius: 10px; font-weight: 600; }

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
.status-cancelled { background: #f8d7da; color: #721c24; }

.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 13px; color: #666; transition: all 0.2s; }
.btn-icon:hover { border-color: #e74c3c; color: #e74c3c; }
.btn-success-icon { color: #27ae60; border-color: #d5f5e3; }
.btn-success-icon:hover { background: #f0fff4; border-color: #27ae60; color: #27ae60; }
.btn-danger-icon { color: #e74c3c; border-color: #fadbd8; }
.btn-danger-icon:hover { background: #fef5f5; border-color: #e74c3c; }
.actions-cell { white-space: nowrap; display: flex; gap: 6px; }

.empty-state { text-align: center; padding: 60px 20px; }
.empty-state i { font-size: 48px; color: #ddd; margin-bottom: 16px; display: block; }
.empty-state h3 { font-size: 20px; margin-bottom: 8px; }
.empty-state p { color: #888; font-size: 14px; }

/* Modal styles */
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

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.form-group { display: flex; flex-direction: column; }
.form-group label { font-size: 12px; font-weight: 600; color: #555; margin-bottom: 6px; }
.form-group input, .form-group select { padding: 10px 12px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 14px; font-family: inherit; transition: border-color 0.2s; }
.form-group input:focus, .form-group select:focus { outline: none; border-color: #e74c3c; }
.required { color: #e74c3c; }

.line-items-section { margin-top: 8px; }
.line-items-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 10px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.section-header h4 { margin: 0; }

.line-table th { font-size: 11px; }
.line-table td { padding: 8px 12px; }
.variant-select { width: 100%; padding: 8px 10px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 13px; font-family: inherit; background: #fff; }
.variant-select:focus { outline: none; border-color: #e74c3c; }
.num-input { width: 100%; padding: 8px 10px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 13px; font-family: inherit; }
.num-input:focus { outline: none; border-color: #e74c3c; }

.total-row { display: flex; justify-content: flex-end; align-items: center; gap: 12px; margin-top: 16px; padding-top: 16px; border-top: 2px solid #f0f0f0; }
.total-label { font-size: 14px; font-weight: 600; color: #555; }
.total-value { font-size: 20px; font-weight: 700; color: #e74c3c; font-family: 'JetBrains Mono', monospace; }

.po-detail-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.po-detail { display: flex; flex-direction: column; }
.detail-label { font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 4px; }
.detail-value { font-size: 14px; color: #333; }

.po-ref { font-weight: 600; color: #333; margin-top: 8px !important; }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #2c3e50; color: #fff; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 2000; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); animation: slideUp 0.3s ease; }
.toast i { color: #27ae60; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .header-actions { flex-wrap: wrap; }
  .status-tabs { flex-wrap: wrap; }
  .form-row { grid-template-columns: 1fr; }
  .modal-card { margin: 10px; }
  .modal-lg { max-width: 100%; }
  .po-detail-grid { grid-template-columns: 1fr 1fr; }
  .line-table th:nth-child(1),
  .line-table td:nth-child(1) { min-width: 160px; }
}
</style>
