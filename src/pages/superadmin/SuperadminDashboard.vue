<template>
  <div class="sa-dashboard">
    <SkeletonLoader v-if="loading" type="stats" :count="4" />
    <template v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon owners"><i class="fas fa-store"></i></div>
          <div>
            <span class="stat-value">{{ stats.total_owners }}</span>
            <span class="stat-label">Total Owners</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon active"><i class="fas fa-check-circle"></i></div>
          <div>
            <span class="stat-value">{{ stats.active_owners }}</span>
            <span class="stat-label">Active Owners</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon employees"><i class="fas fa-users"></i></div>
          <div>
            <span class="stat-value">{{ stats.total_employees }}</span>
            <span class="stat-label">Total Employees</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon customers"><i class="fas fa-user-group"></i></div>
          <div>
            <span class="stat-value">{{ stats.total_customers }}</span>
            <span class="stat-label">Total Customers</span>
          </div>
        </div>
      </div>

      <div class="sa-grid">
        <div class="card sa-section">
          <h3><i class="fas fa-chart-pie"></i> Subscriptions</h3>
          <div class="sub-list">
            <div class="sub-item" v-for="(count, status) in stats.subscriptions" :key="status">
              <span :class="['sub-badge', `sub-${status}`]">{{ status }}</span>
              <span class="sub-count">{{ count }}</span>
            </div>
            <div v-if="Object.keys(stats.subscriptions || {}).length === 0" class="empty-text">
              No subscription data
            </div>
          </div>
        </div>

        <div class="card sa-section">
          <h3><i class="fas fa-dollar-sign"></i> Revenue</h3>
          <div class="revenue-display">
            <span class="revenue-amount">TSh {{ formatPrice(stats.total_revenue) }}</span>
            <span class="revenue-label">Total platform revenue</span>
          </div>
        </div>
      </div>

      <div class="card sa-section">
        <div class="section-header">
          <h3><i class="fas fa-tags"></i> Subscription Plans</h3>
          <button class="btn btn-primary btn-sm" @click="openPlansEditor">
            <i class="fas fa-pen"></i> Edit Plans
          </button>
        </div>
        <div class="plans-list">
          <div v-for="(plan, key) in plans" :key="key" class="plan-item">
            <span class="plan-item-name">{{ cap(key) }}</span>
            <span class="plan-item-price">TSh {{ formatPrice(plan.price_monthly) }}/mo</span>
            <span class="plan-item-limits">{{ plan.max_products }} products · {{ plan.max_employees }} employees</span>
          </div>
        </div>
      </div>

      <div class="card sa-section">
        <div class="section-header">
          <h3><i class="fas fa-store"></i> All Owners</h3>
          <button class="btn btn-primary btn-sm" @click="showCreateModal = true">
            <i class="fas fa-plus"></i> Add Owner
          </button>
        </div>
        <div v-if="owners.length === 0" class="empty-state">
          <i class="fas fa-store"></i>
          <p>No owners yet</p>
        </div>
        <div v-else class="table-wrap">
        <table class="sa-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Status</th>
              <th>Subscription</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="owner in owners" :key="owner.id">
              <td><strong>{{ owner.name }}</strong></td>
              <td>{{ owner.email }}</td>
              <td>
                <span :class="['status-badge', owner.owner_profile?.is_active ? 'active' : 'inactive']">
                  {{ owner.owner_profile?.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <span :class="['sub-badge', `sub-${owner.owner_profile?.subscription_status || 'trial'}`]">
                  {{ owner.owner_profile?.subscription_status || 'trial' }}
                </span>
              </td>
              <td class="actions-cell">
                <router-link :to="`/superadmin/owners/${owner.id}`" class="btn-icon" title="View Details">
                  <i class="fas fa-eye"></i>
                </router-link>
                <router-link :to="`/superadmin/branding/${owner.id}`" class="btn-icon" title="Branding">
                  <i class="fas fa-palette"></i>
                </router-link>
                <button class="btn-icon" :class="owner.owner_profile?.is_active ? 'warn' : 'success'"
                  @click="toggleOwner(owner.id)" :title="owner.owner_profile?.is_active ? 'Deactivate' : 'Activate'">
                  <i :class="owner.owner_profile?.is_active ? 'fas fa-ban' : 'fas fa-check'"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
    </template>

    <div class="modal-overlay" v-if="showCreateModal" @click.self="showCreateModal = false">
      <div class="modal-card">
        <h3><i class="fas fa-store"></i> Create New Owner</h3>
        <p class="modal-desc">Default password will be the owner's full name in uppercase. They will be prompted to change it on first login.</p>
        <form @submit.prevent="createOwner">
          <div class="form-group">
            <label>Full Name</label>
            <input v-model="newOwner.name" type="text" placeholder="John Doe" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="newOwner.email" type="email" placeholder="john@example.com" required />
          </div>
          <div class="form-group">
            <label>Phone</label>
            <input v-model="newOwner.phone" type="text" placeholder="+255700000000" required />
          </div>
          <div class="default-pw-note" v-if="newOwner.name.trim()">
            <i class="fas fa-info-circle"></i>
            Default password: <strong>{{ newOwner.name.trim().toUpperCase() }}</strong>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Max Products</label>
              <input v-model.number="newOwner.max_products" type="number" min="1" />
            </div>
            <div class="form-group">
              <label>Max Employees</label>
              <input v-model.number="newOwner.max_employees" type="number" min="1" />
            </div>
          </div>
          <div class="form-group">
            <label>Plan</label>
            <select v-model="newOwner.subscription_plan">
              <option value="free">Free</option>
              <option value="starter">Starter</option>
              <option value="pro">Pro</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showCreateModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="creating">
              {{ creating ? 'Creating...' : 'Create Owner' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" v-if="showPlansModal" @click.self="showPlansModal = false">
      <div class="modal-card">
        <h3><i class="fas fa-tags"></i> Edit Subscription Plans</h3>
        <p class="modal-desc">Prices are in Tanzanian Shillings per month. These values are used when owners pay for their subscription.</p>
        <form @submit.prevent="savePlans">
          <div v-for="key in ['starter', 'pro', 'enterprise']" :key="key" class="plan-editor-block">
            <h4>{{ cap(key) }}</h4>
            <div class="form-row">
              <div class="form-group">
                <label>Price (TSh/month)</label>
                <input v-model.number="plansForm[key].price_monthly" type="number" min="0" />
              </div>
              <div class="form-group">
                <label>Max Products</label>
                <input v-model.number="plansForm[key].max_products" type="number" min="0" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Max Employees</label>
                <input v-model.number="plansForm[key].max_employees" type="number" min="0" />
              </div>
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="showPlansModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="savingPlans">
              {{ savingPlans ? 'Saving...' : 'Save Plans' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas fa-check-circle"></i> {{ toastMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { superadminApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const loading = ref(true)
const stats = ref({})
const owners = ref([])
const showCreateModal = ref(false)
const creating = ref(false)
const toastMsg = ref('')
const plans = ref({})
const showPlansModal = ref(false)
const savingPlans = ref(false)
const plansForm = ref({ starter: {}, pro: {}, enterprise: {} })

const newOwner = ref({
  name: '',
  email: '',
  phone: '',
  max_products: 50,
  max_employees: 5,
  subscription_plan: 'starter',
})

function cap(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : ''
}

function formatPrice(v) {
  return Number(v || 0).toLocaleString('en-TZ')
}

async function loadData() {
  try {
    const [statsRes, ownersRes, plansRes] = await Promise.all([
      superadminApi.getStats(),
      superadminApi.getOwners(),
      superadminApi.getSubscriptionPlans(),
    ])
    stats.value = statsRes.data
    owners.value = ownersRes.data
    plans.value = plansRes.data
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

function openPlansEditor() {
  plansForm.value = {
    starter: { ...plans.value.starter },
    pro: { ...plans.value.pro },
    enterprise: { ...plans.value.enterprise },
  }
  showPlansModal.value = true
}

async function savePlans() {
  savingPlans.value = true
  try {
    const res = await superadminApi.updateSubscriptionPlans(plansForm.value)
    plans.value = res.data.plans
    showPlansModal.value = false
    toastMsg.value = res.data.message || 'Plans updated'
  } catch (e) {
    toastMsg.value = e.response?.data?.message || 'Failed to update plans'
  }
  savingPlans.value = false
  setTimeout(() => toastMsg.value = '', 3000)
}

async function createOwner() {
  creating.value = true
  try {
    const res = await superadminApi.createOwner(newOwner.value)
    showCreateModal.value = false
    const pw = res.data.default_password
    toastMsg.value = `Owner created! Default password: ${pw}`
    newOwner.value = { name: '', email: '', phone: '', max_products: 50, max_employees: 5, subscription_plan: 'starter' }
    await loadData()
  } catch (e) {
    toastMsg.value = e.response?.data?.message || 'Failed to create owner'
  }
  creating.value = false
  setTimeout(() => toastMsg.value = '', 6000)
}

async function toggleOwner(id) {
  try {
    const res = await superadminApi.toggleActive(id)
    toastMsg.value = res.data.message
    await loadData()
  } catch {
    toastMsg.value = 'Failed to toggle owner'
  }
  setTimeout(() => toastMsg.value = '', 3000)
}

onMounted(loadData)
</script>

<style scoped>
.sa-dashboard {
  max-width: 1200px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 10px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-icon.owners { background: #fef5f5; color: #e74c3c; }
.stat-icon.active { background: #eafaf1; color: #27ae60; }
.stat-icon.employees { background: #eaf4ff; color: #2980b9; }
.stat-icon.customers { background: #fef9e7; color: #f39c12; }

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
}

.stat-label {
  font-size: 13px;
  color: #888;
}

.sa-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.sa-section {
  padding: 24px;
}

.sa-section h3 {
  font-size: 16px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sa-section h3 i {
  color: #e74c3c;
}

.sub-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sub-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
}

.sub-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.sub-trial { background: #fff3cd; color: #856404; }
.sub-active { background: #d4edda; color: #155724; }
.sub-suspended { background: #f8d7da; color: #721c24; }
.sub-expired { background: #e9ecef; color: #6c757d; }

.sub-count {
  font-size: 18px;
  font-weight: 700;
}

.revenue-display {
  text-align: center;
  padding: 24px;
}

.revenue-amount {
  display: block;
  font-size: 28px;
  font-weight: 800;
  color: #27ae60;
  margin-bottom: 8px;
}

.revenue-label {
  color: #888;
  font-size: 13px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin-bottom: 0;
}

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
  letter-spacing: 0.5px;
  border-bottom: 2px solid #eee;
}

.sa-table td {
  padding: 14px 16px;
  font-size: 14px;
  border-bottom: 1px solid #f5f5f5;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active { background: #d4edda; color: #155724; }
.status-badge.inactive { background: #f8d7da; color: #721c24; }

.actions-cell {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid #eee;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #555;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-icon:hover { border-color: #e74c3c; color: #e74c3c; }
.btn-icon.success { color: #27ae60; }
.btn-icon.warn { color: #e67e22; }

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
  transition: all 0.2s;
}

.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-ghost { background: transparent; border: 1px solid #ddd; color: #555; }
.btn-ghost:hover { border-color: #999; }
.btn-sm { padding: 8px 14px; font-size: 13px; }

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: #fff;
  border-radius: 12px;
  padding: 32px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-card h3 {
  font-size: 18px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-card h3 i { color: #e74c3c; }

.modal-desc { color: #888; font-size: 13px; margin-bottom: 20px; line-height: 1.5; }

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 14px;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.default-pw-note { padding: 12px; background: #fef9e7; border: 1px solid #fdebd0; border-radius: 6px; font-size: 13px; color: #7d6608; margin-bottom: 16px; }
.default-pw-note i { margin-right: 4px; }

.plans-list { display: flex; flex-direction: column; gap: 12px; }
.plan-item { display: flex; align-items: center; gap: 16px; padding: 12px 14px; background: #f8f9fa; border: 1px solid #eee; border-radius: 8px; flex-wrap: wrap; }
.plan-item-name { font-weight: 700; font-size: 14px; min-width: 90px; }
.plan-item-price { font-weight: 800; color: #e74c3c; font-size: 14px; }
.plan-item-limits { color: #888; font-size: 13px; margin-left: auto; }

.plan-editor-block { border: 1px solid #eee; border-radius: 8px; padding: 16px; margin-bottom: 16px; background: #fafafa; }
.plan-editor-block h4 { margin: 0 0 12px; font-size: 14px; text-transform: uppercase; letter-spacing: 0.3px; color: #555; }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.empty-state {
  text-align: center;
  padding: 48px;
  color: #999;
}

.empty-state i { font-size: 36px; color: #ddd; margin-bottom: 12px; display: block; }
.empty-text { text-align: center; padding: 24px; color: #999; font-size: 14px; }

.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
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
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}

.toast i { color: #27ae60; }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .sa-grid { grid-template-columns: 1fr; }
  .form-row { grid-template-columns: 1fr; }
}
</style>
