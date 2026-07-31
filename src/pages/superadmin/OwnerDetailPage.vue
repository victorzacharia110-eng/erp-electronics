<template>
  <div class="owner-detail">
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i> Loading owner details...
    </div>
    <template v-else-if="owner">
      <div class="detail-header">
        <div>
          <h3>{{ owner.name }}</h3>
          <p class="muted">{{ owner.email }} | {{ owner.phone || 'No phone' }}</p>
        </div>
        <span :class="['status-badge', owner.owner_profile?.is_active ? 'active' : 'inactive']">
          {{ owner.owner_profile?.is_active ? 'Active' : 'Inactive' }}
        </span>
      </div>

      <div class="detail-grid">
        <div class="card detail-section">
          <h4><i class="fas fa-chart-bar"></i> Stats</h4>
          <div class="stat-rows">
            <div class="stat-row">
              <span>Total Orders</span>
              <strong>{{ ownerStats.total_orders }}</strong>
            </div>
            <div class="stat-row">
              <span>Total Revenue</span>
              <strong>TSh {{ formatPrice(ownerStats.total_revenue) }}</strong>
            </div>
            <div class="stat-row">
              <span>Products</span>
              <strong>{{ ownerStats.product_count }}</strong>
            </div>
            <div class="stat-row">
              <span>Employees</span>
              <strong>{{ ownerStats.employee_count }}</strong>
            </div>
          </div>
        </div>

        <div class="card detail-section">
          <h4><i class="fas fa-credit-card"></i> Subscription</h4>
          <form @submit.prevent="saveSubscription">
            <div class="form-group">
              <label>Status</label>
              <select v-model="subForm.subscription_status">
                <option value="trial">Trial</option>
                <option value="active">Active</option>
                <option value="suspended">Suspended</option>
                <option value="expired">Expired</option>
              </select>
            </div>
            <div class="form-group">
              <label>Plan</label>
              <select v-model="subForm.subscription_plan">
                <option value="free">Free</option>
                <option value="starter">Starter</option>
                <option value="pro">Pro</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </div>
            <div class="form-group">
              <label>Expires At</label>
              <input v-model="subForm.subscription_expires_at" type="date" />
            </div>
            <button type="submit" class="btn btn-primary btn-sm" :disabled="savingSub">
              {{ savingSub ? 'Saving...' : 'Save Subscription' }}
            </button>
          </form>
        </div>

        <div class="card detail-section">
          <h4><i class="fas fa-sliders"></i> Limits</h4>
          <form @submit.prevent="saveLimits">
            <div class="form-group">
              <label>Max Products</label>
              <input v-model.number="limitsForm.max_products" type="number" min="1" />
            </div>
            <div class="form-group">
              <label>Max Employees</label>
              <input v-model.number="limitsForm.max_employees" type="number" min="1" />
            </div>
            <button type="submit" class="btn btn-primary btn-sm" :disabled="savingLimits">
              {{ savingLimits ? 'Saving...' : 'Save Limits' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Password Management -->
      <div class="card detail-section">
        <h4><i class="fas fa-shield-alt"></i> Password Management</h4>
        <div v-if="pwLoading" class="loading-inline">
          <i class="fas fa-spinner fa-spin"></i> Loading password status...
        </div>
        <template v-else-if="pwStatus">
          <div class="pw-status-grid">
            <div class="pw-stat-item">
              <span class="pw-stat-label">Status</span>
              <span :class="['pw-stat-value', pwStatus.must_change_password ? 'warning' : 'ok']">
                {{ pwStatus.must_change_password ? 'Must Change' : 'OK' }}
              </span>
            </div>
            <div class="pw-stat-item">
              <span class="pw-stat-label">Last Changed</span>
              <span class="pw-stat-value">
                {{ pwStatus.days_since_last_change !== null ? pwStatus.days_since_last_change + ' days ago' : 'Never' }}
              </span>
            </div>
            <div class="pw-stat-item">
              <span class="pw-stat-label">Account</span>
              <span :class="['pw-stat-value', pwStatus.is_account_locked ? 'danger' : 'ok']">
                {{ pwStatus.is_account_locked ? 'Locked' : 'Unlocked' }}
              </span>
            </div>
            <div class="pw-stat-item">
              <span class="pw-stat-label">Failed Attempts</span>
              <span class="pw-stat-value">{{ pwStatus.failed_login_attempts }}</span>
            </div>
          </div>
          <div class="pw-actions">
            <button class="btn btn-primary btn-sm" @click="showPasswordModal = true">
              <i class="fas fa-key"></i> Reset / Set Password
            </button>
            <button v-if="pwStatus.must_change_password" class="btn btn-warning btn-sm" @click="forceChange" :disabled="forcingChange">
              <i class="fas fa-exclamation-triangle"></i> {{ forcingChange ? 'Forcing...' : 'Force Change on Login' }}
            </button>
            <button v-if="pwStatus.is_account_locked" class="btn btn-success btn-sm" @click="unlockAccount" :disabled="unlocking">
              <i class="fas fa-unlock"></i> {{ unlocking ? 'Unlocking...' : 'Unlock Account' }}
            </button>
          </div>
        </template>
      </div>

      <div class="card detail-section">
        <h4><i class="fas fa-receipt"></i> Recent Orders</h4>
        <div v-if="!owner.orders?.length" class="empty-text">No orders yet</div>
        <div v-else class="table-wrap">
        <table class="sa-table">
          <thead>
            <tr>
              <th>Order #</th>
              <th>Date</th>
              <th>Status</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in owner.orders" :key="order.id">
              <td><strong>{{ order.order_number }}</strong></td>
              <td>{{ new Date(order.created_at).toLocaleDateString() }}</td>
              <td>
                <span :class="['status-badge', `status-${order.status}`]">
                  {{ order.status }}
                </span>
              </td>
              <td>TSh {{ Number(order.total).toLocaleString('en-TZ') }}</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
    </template>

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas fa-check-circle"></i> {{ toastMsg }}
    </div>

    <ResetOwnerPasswordModal
      v-if="showPasswordModal"
      :owner-id="route.params.id"
      :owner-name="owner?.name"
      @close="showPasswordModal = false"
      @updated="onPasswordUpdated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { superadminApi } from '@/api'
import ResetOwnerPasswordModal from '@/components/ResetOwnerPasswordModal.vue'

const route = useRoute()
const loading = ref(true)
const owner = ref(null)
const ownerStats = ref({})
const toastMsg = ref('')

const showPasswordModal = ref(false)
const pwStatus = ref(null)
const pwLoading = ref(true)
const forcingChange = ref(false)
const unlocking = ref(false)

const subForm = ref({
  subscription_status: 'trial',
  subscription_plan: 'starter',
  subscription_expires_at: '',
})

const limitsForm = ref({
  max_products: 50,
  max_employees: 5,
})

const savingSub = ref(false)
const savingLimits = ref(false)

function formatPrice(v) {
  return Number(v || 0).toLocaleString('en-TZ')
}

async function loadData() {
  try {
    const res = await superadminApi.getOwner(route.params.id)
    owner.value = res.data.owner
    ownerStats.value = res.data.stats

    const profile = owner.value.owner_profile
    if (profile) {
      subForm.value = {
        subscription_status: profile.subscription_status || 'trial',
        subscription_plan: profile.subscription_plan || 'starter',
        subscription_expires_at: profile.subscription_expires_at
          ? profile.subscription_expires_at.split('T')[0]
          : '',
      }
      limitsForm.value = {
        max_products: profile.max_products || 50,
        max_employees: profile.max_employees || 5,
      }
    }
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

async function saveSubscription() {
  savingSub.value = true
  try {
    await superadminApi.updateSubscription(route.params.id, subForm.value)
    toastMsg.value = 'Subscription updated'
    await loadData()
  } catch {
    toastMsg.value = 'Failed to update subscription'
  }
  savingSub.value = false
  setTimeout(() => toastMsg.value = '', 3000)
}

async function saveLimits() {
  savingLimits.value = true
  try {
    await superadminApi.updateLimits(route.params.id, limitsForm.value)
    toastMsg.value = 'Limits updated'
    await loadData()
  } catch {
    toastMsg.value = 'Failed to update limits'
  }
  savingLimits.value = false
  setTimeout(() => toastMsg.value = '', 3000)
}

async function loadPasswordStatus() {
  pwLoading.value = true
  try {
    const res = await superadminApi.getPasswordStatus(route.params.id)
    pwStatus.value = res.data.password_status
  } catch { /* empty */ }
  pwLoading.value = false
}

async function forceChange() {
  forcingChange.value = true
  try {
    await superadminApi.forcePasswordChange(route.params.id)
    toastMsg.value = 'Owner will be forced to change password on next login'
    await loadPasswordStatus()
  } catch {
    toastMsg.value = 'Failed to force password change'
  }
  forcingChange.value = false
  setTimeout(() => toastMsg.value = '', 3000)
}

async function unlockAccount() {
  unlocking.value = true
  try {
    await superadminApi.unlockOwnerAccount(route.params.id)
    toastMsg.value = 'Account unlocked'
    await loadPasswordStatus()
  } catch {
    toastMsg.value = 'Failed to unlock account'
  }
  unlocking.value = false
  setTimeout(() => toastMsg.value = '', 3000)
}

function onPasswordUpdated() {
  showPasswordModal.value = false
  loadPasswordStatus()
  toastMsg.value = 'Password updated'
  setTimeout(() => toastMsg.value = '', 3000)
}

onMounted(async () => {
  await loadData()
  await loadPasswordStatus()
})
</script>

<style scoped>
.owner-detail { max-width: 1200px; }

.loading-state {
  text-align: center;
  padding: 64px;
  color: #888;
  font-size: 16px;
}

.loading-state i { margin-right: 8px; }

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.detail-header h3 { font-size: 22px; }

.muted { color: #888; font-size: 14px; }

.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.detail-section {
  padding: 24px;
}

.detail-section h4 {
  font-size: 15px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-section h4 i { color: #e74c3c; }

.stat-rows { display: flex; flex-direction: column; gap: 12px; }

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 14px;
}

.stat-row span { color: #888; }
.stat-row strong { color: #333; }

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #555;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #e74c3c;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: 'Inter', sans-serif;
}

.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { padding: 8px 14px; font-size: 13px; }

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.active { background: #d4edda; color: #155724; }
.status-badge.inactive { background: #f8d7da; color: #721c24; }
.status-badge.status-pending { background: #fff3cd; color: #856404; }
.status-badge.status-paid { background: #d4edda; color: #155724; }
.status-badge.status-processing { background: #cce5ff; color: #004085; }
.status-badge.status-shipped { background: #e2d5f1; color: #563d7c; }
.status-badge.status-delivered { background: #d4edda; color: #155724; }
.status-badge.status-cancelled { background: #f8d7da; color: #721c24; }

.table-wrap { overflow-x: auto; }

.sa-table {
  width: 100%;
  border-collapse: collapse;
}

.sa-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  border-bottom: 2px solid #eee;
}

.sa-table td {
  padding: 12px 16px;
  font-size: 14px;
  border-bottom: 1px solid #f5f5f5;
}

.empty-text { text-align: center; padding: 24px; color: #999; font-size: 14px; }

.loading-inline {
  text-align: center;
  padding: 20px;
  color: #888;
  font-size: 14px;
}

.loading-inline i { margin-right: 6px; }

.pw-status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.pw-stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pw-stat-label {
  font-size: 12px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.pw-stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.pw-stat-value.warning { color: #e67e22; }
.pw-stat-value.danger { color: #e74c3c; }
.pw-stat-value.ok { color: #27ae60; }

.pw-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-warning { background: #e67e22; color: #fff; }
.btn-warning:hover { background: #d35400; }
.btn-success { background: #27ae60; color: #fff; }
.btn-success:hover { background: #1e8449; }

.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: #2c3e50;
  color: #fff;
  padding: 14px 24px;
  border-radius: 8px;
  font-size: 14px;
  z-index: 2000;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}

.toast i { color: #27ae60; }

@media (max-width: 768px) {
  .detail-grid { grid-template-columns: 1fr; }
}
</style>
