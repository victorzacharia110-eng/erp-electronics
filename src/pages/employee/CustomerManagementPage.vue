<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-users" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('customers.title') }}</h1>
        <p>{{ $t('customers.subtitle') }}</p>
      </div>
      <router-link to="/employee" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.backToDashboard')
        }}</router-link>
    </div>

    <div class="summary-bar">
      <div class="summary-item"><span class="summary-num">{{ customers.length }}</span><span class="summary-label">{{
        $t('customers.totalCustomers') }}</span></div>
      <div class="summary-item"><span class="summary-num active-num">{{customers.filter(c => c.is_active).length
          }}</span><span class="summary-label">{{ $t('common.active') }}</span></div>
      <div class="summary-item"><span class="summary-num inactive-num">{{customers.filter(c => !c.is_active).length
          }}</span><span class="summary-label">{{ $t('common.inactive') }}</span></div>
    </div>

    <div class="filters-bar card" v-if="!loading && customers.length > 0">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input v-model="search" type="text" :placeholder="$t('common.searchPlaceholder')" @input="onSearch" />
      </div>
    </div>

    <SkeletonLoader v-if="loading" type="table" :count="5" />

    <div v-else-if="customers.length === 0" class="empty-state card">
      <i class="fas fa-users"></i>
      <h3>{{ $t('customers.noCustomers') }}</h3>
      <p>{{ $t('customers.noCustomersDesc') }}</p>
    </div>

    <div v-else class="customers-list">
      <div class="list-header">
        <span class="col-name">{{ $t('customers.name') }}</span>
        <span class="col-email">{{ $t('customers.email') }}</span>
        <span class="col-phone">{{ $t('customers.phone') }}</span>
        <span class="col-orders">{{ $t('customers.orders') }}</span>
        <span class="col-status">{{ $t('customers.status') }}</span>
        <span class="col-date">{{ $t('customers.joined') }}</span>
        <span class="col-actions">{{ $t('customers.actions') }}</span>
      </div>
      <div v-for="customer in displayItems" :key="customer.id" class="list-row">
        <span class="col-name">
          <div class="avatar-circle"><i class="fas fa-user"></i></div>
          <span>{{ customer.name }}</span>
        </span>
        <span class="col-email">{{ customer.email }}</span>
        <span class="col-phone">{{ customer.phone || '—' }}</span>
        <span class="col-orders"><span class="order-count">{{ customer.orders_count }}</span></span>
        <span class="col-status">
          <span :class="['status-pill', customer.is_active ? 'active' : 'inactive']">{{ customer.is_active ?
            $t('common.active') : $t('common.inactive') }}</span>
        </span>
        <span class="col-date">{{ new Date(customer.created_at).toLocaleDateString('en-TZ', {
          day: 'numeric', month:
            'short', year: 'numeric' }) }}</span>
        <span class="col-actions">
          <button class="icon-btn toggle"
            :title="customer.is_active ? $t('customers.deactivate') : $t('customers.activate')"
            @click="toggleCustomer(customer)">
            <i :class="customer.is_active ? 'fas fa-ban' : 'fas fa-check-circle'"></i>
          </button>
          <button class="icon-btn delete" :title="$t('common.delete')" @click="deleteCustomer(customer)">
            <i class="fas fa-trash-alt"></i>
          </button>
        </span>
      </div>
    </div>

    <TablePagination v-if="!loading && customers.length > 15" :current-page="currentPage" :total-pages="totalPages"
      :from="pageInfo.from" :to="pageInfo.to" :total="pageInfo.total" :show-all="showAll" @page="goToPage"
      @toggle-all="toggleShowAll" />

    <div class="modal-overlay" v-if="confirmDialog.show" @click.self="confirmDialog.show = false">
      <div class="modal-content confirm-modal">
        <h3><i class="fas fa-exclamation-triangle"></i> {{ confirmDialog.title }}</h3>
        <p>{{ confirmDialog.message }}</p>
        <div class="modal-actions">
          <button class="btn-outline" @click="confirmDialog.show = false">{{ $t('common.cancel') }}</button>
          <button :class="['btn', confirmDialog.danger ? 'btn-danger' : 'btn-primary']"
            @click="confirmDialog.onConfirm">
            {{ confirmDialog.confirmText }}
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
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { customerApi } from '@/api'
import { useTablePagination } from '@/composables/useTablePagination'
import TablePagination from '@/components/TablePagination.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const { t } = useI18n()

const customers = ref([])
const { search, currentPage, showAll, displayItems, totalPages, pageInfo, onSearch, goToPage, toggleShowAll } = useTablePagination(customers, ['name', 'email', 'phone'])
const loading = ref(true)
const toastMsg = ref('')
const confirmDialog = reactive({ show: false, title: '', message: '', confirmText: 'Confirm', danger: false, onConfirm: () => { } })

function showToast(msg) { toastMsg.value = msg; setTimeout(() => toastMsg.value = '', 3000) }

function toggleCustomer(customer) {
  confirmDialog.title = customer.is_active ? t('customers.deactivate') : t('customers.activate')
  confirmDialog.message = customer.is_active
    ? `Are you sure you want to deactivate ${customer.name}? They will no longer be able to log in.`
    : `Are you sure you want to activate ${customer.name}?`
  confirmDialog.confirmText = customer.is_active ? t('customers.deactivate') : t('customers.activate')
  confirmDialog.danger = customer.is_active
  confirmDialog.onConfirm = async () => {
    confirmDialog.show = false
    try {
      await customerApi.toggleStatus(customer.id)
      customer.is_active = !customer.is_active
      showToast(`${customer.name} ${customer.is_active ? t('common.activated') : t('common.deactivated')}`)
    } catch { /* empty */ }
  }
  confirmDialog.show = true
}

function deleteCustomer(customer) {
  confirmDialog.title = t('customers.confirmDelete')
  confirmDialog.message = t('customers.confirmDeleteDesc')
  confirmDialog.confirmText = t('common.delete')
  confirmDialog.danger = true
  confirmDialog.onConfirm = async () => {
    confirmDialog.show = false
    try {
      await customerApi.delete(customer.id)
      customers.value = customers.value.filter(c => c.id !== customer.id)
      showToast(`${customer.name} ${t('common.hasBeenDeleted')}`)
    } catch { /* empty */ }
  }
  confirmDialog.show = true
}

onMounted(async () => {
  try {
    const res = await customerApi.getAll()
    customers.value = res.data
  } catch { /* empty */ }
  loading.value = false
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

.summary-bar {
  display: flex;
  gap: 32px;
  padding: 20px 28px;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 24px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-num {
  font-size: 22px;
  font-weight: 700;
  color: #333;
}

.summary-label {
  font-size: 12px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.active-num {
  color: #27ae60;
}

.inactive-num {
  color: #e74c3c;
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

.customers-list {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.list-header {
  display: grid;
  grid-template-columns: 2fr 2fr 1.2fr 0.7fr 0.8fr 1fr 0.8fr;
  padding: 14px 20px;
  background: #fafafa;
  border-bottom: 1px solid #eee;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.list-row {
  display: grid;
  grid-template-columns: 2fr 2fr 1.2fr 0.7fr 0.8fr 1fr 0.8fr;
  padding: 14px 20px;
  border-bottom: 1px solid #f5f5f5;
  font-size: 14px;
  align-items: center;
  transition: background 0.15s;
}

.list-row:hover {
  background: #fafafa;
}

.list-row:last-child {
  border-bottom: none;
}

.col-name {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}

.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #eaf4ff;
  color: #2980b9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
}

.col-email {
  color: #666;
  font-size: 13px;
}

.col-phone {
  color: #666;
  font-size: 13px;
}

.col-orders {
  text-align: center;
}

.order-count {
  background: #eaf4ff;
  color: #2980b9;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.col-status {}

.status-pill {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.status-pill.active {
  background: #eafaf1;
  color: #27ae60;
}

.status-pill.inactive {
  background: #fef5f5;
  color: #e74c3c;
}

.col-date {
  color: #888;
  font-size: 13px;
}

.col-actions {
  display: flex;
  gap: 6px;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid #eee;
  background: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  transition: all 0.2s;
  color: #666;
}

.icon-btn.toggle:hover {
  background: #fef5f5;
  border-color: #e74c3c;
  color: #e74c3c;
}

.icon-btn.delete:hover {
  background: #e74c3c;
  border-color: #e74c3c;
  color: #fff;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: #fff;
  border-radius: 10px;
  padding: 28px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.confirm-modal h3 {
  font-size: 18px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.confirm-modal h3 i {
  color: #f39c12;
}

.confirm-modal p {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 24px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-outline {
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-outline:hover {
  border-color: #999;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
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
  background: #e74c3c;
  color: #fff;
}

.btn-danger:hover {
  background: #c0392b;
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

.filters-bar {
  padding: 12px 20px;
  margin-bottom: 16px;
  display: flex;
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
  max-width: 400px;
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

@media (max-width: 768px) {
  .list-header {
    display: none;
  }

  .list-row {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    padding: 16px 20px;
  }

  .col-name {
    grid-column: 1 / -1;
  }

  .col-actions {
    grid-column: 1 / -1;
    justify-content: flex-end;
    margin-top: 4px;
  }

  .summary-bar {
    gap: 20px;
  }
}
</style>
