<template>
  <div class="owner-mgmt">
    <div class="page-header">
      <div>
        <h1>Owner Management</h1>
        <p class="subtitle">Manage store owners, subscriptions, and access</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModal = true"><i class="fas fa-user-plus"></i> Add Owner</button>
    </div>

    <div v-if="trialExpiredOwners.length" class="trial-alert">
      <div class="trial-alert-icon"><i class="fas fa-hourglass-end"></i></div>
      <div class="trial-alert-body">
        <strong>Trial period ended</strong>
        <p>The following store(s) were deactivated automatically because their trial period ended.
          Would you like to extend their trial?</p>
        <ul>
          <li v-for="o in trialExpiredOwners" :key="o.id">
            <router-link :to="`/superadmin/owners/${o.id}`">{{ o.name }}</router-link>
            <span class="trial-alert-meta">{{ o.email }} · expired {{ new Date(o.owner_profile.subscription_expires_at).toLocaleDateString() }}</span>
            <button class="btn btn-primary btn-sm" @click="extendTrial(o)">
              <i class="fas fa-plus-circle"></i> Extend trial (30 days)
            </button>
          </li>
        </ul>
      </div>
    </div>

    <SkeletonLoader v-if="loading" type="table" />

    <div v-else-if="owners.length === 0" class="empty-state card">
      <div class="empty-icon"><i class="fas fa-store"></i></div>
      <h3>No owners registered yet</h3>
      <p>Create your first store owner to get started.</p>
      <button class="btn btn-primary" @click="showCreateModal = true"><i class="fas fa-user-plus"></i> Add Owner</button>
    </div>

    <template v-else>
      <div class="summary-bar">
        <span><strong>{{ owners.length }}</strong> Total owners</span>
        <span><strong>{{ owners.filter(o => o.owner_profile?.is_active).length }}</strong> Active</span>
        <span><strong>{{ owners.filter(o => !o.owner_profile?.is_active).length }}</strong> Inactive</span>
      </div>

      <div class="filters-bar">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input v-model="search" type="text" placeholder="Search by name, email, or phone..." @input="onSearch" />
        </div>
        <div class="sort-box">
          <label class="sort-label"><i class="fas fa-arrow-down-wide-short"></i> Sort by</label>
          <select v-model="sortKey" class="sort-select">
            <option value="name">Name (A-Z)</option>
            <option value="name_desc">Name (Z-A)</option>
            <option value="email">Email (A-Z)</option>
            <option value="created_at">Newest First</option>
            <option value="created_at_asc">Oldest First</option>
            <option value="plan">Plan</option>
          </select>
        </div>
      </div>

      <div class="table-wrap">
        <table class="sa-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Joined</th>
              <th>Status</th>
              <th>Plan</th>
              <th>Expires</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="owner in displayItems" :key="owner.id">
              <td><strong>{{ owner.name }}</strong></td>
              <td>{{ owner.email }}</td>
              <td>{{ owner.phone || '-' }}</td>
              <td class="muted">{{ new Date(owner.created_at).toLocaleDateString() }}</td>
              <td>
                <span :class="['status-badge', owner.owner_profile?.is_active ? 'active' : 'inactive']">
                  {{ owner.owner_profile?.is_active ? 'Active' : 'Inactive' }}
                </span>
                <span v-if="isTrialExpired(owner)" class="trial-expired-badge">
                  <i class="fas fa-hourglass-end"></i> Trial ended
                </span>
              </td>
              <td>
                <span :class="['plan-badge', `plan-${owner.owner_profile?.subscription_plan || 'free'}`]">
                  {{ owner.owner_profile?.subscription_plan || 'free' }}
                </span>
              </td>
              <td class="muted">
                {{ owner.owner_profile?.subscription_expires_at
                  ? new Date(owner.owner_profile.subscription_expires_at).toLocaleDateString()
                  : '-' }}
              </td>
              <td class="actions-cell">
                <router-link :to="`/superadmin/owners/${owner.id}`" class="btn-icon" title="View Details">
                  <i class="fas fa-eye"></i>
                </router-link>
                <router-link :to="`/superadmin/branding/${owner.id}`" class="btn-icon" title="Branding">
                  <i class="fas fa-palette"></i>
                </router-link>
                <button class="btn-icon" title="Reset Password" @click="openPasswordModal(owner)">
                  <i class="fas fa-key"></i>
                </button>
                <button class="btn-icon" :class="owner.owner_profile?.is_active ? 'warn' : 'success'"
                  @click="toggleOwner(owner.id)" :title="owner.owner_profile?.is_active ? 'Deactivate' : 'Activate'">
                  <i :class="owner.owner_profile?.is_active ? 'fas fa-ban' : 'fas fa-check'"></i>
                </button>
                <button class="btn-icon danger" @click="confirmDelete(owner)" title="Delete">
                  <i class="fas fa-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <TablePagination
        :current-page="currentPage" :total-pages="totalPages"
        :from="pageInfo.from" :to="pageInfo.to" :total="pageInfo.total"
        :show-all="showAll"
        @page="goToPage" @toggle-all="toggleShowAll"
      />
    </template>

    <div class="modal-overlay" v-if="showCreateModal" @click.self="closeCreateModal">
      <div class="modal-card">
        <h3><i class="fas fa-user-plus"></i> Create New Owner</h3>
        <p class="modal-desc">A secure default password will be generated. The owner will be prompted to change it on first login.</p>
        <form @submit.prevent="createOwner">
          <div class="form-group" :class="{ 'has-error': addErrors.name }">
            <label>Full Name *</label>
            <input v-model="newOwner.name" type="text" placeholder="e.g. John Doe" @blur="validateAddField('name')" @input="validateAddField('name')" />
            <span class="field-error" v-if="addErrors.name"><i class="fas fa-exclamation-triangle"></i> {{ addErrors.name }}</span>
          </div>
          <div class="form-group" :class="{ 'has-error': addErrors.email }">
            <label>Email *</label>
            <input v-model="newOwner.email" type="email" placeholder="e.g. john@example.com" @blur="validateAddField('email')" @input="validateAddField('email')" />
            <span class="field-error" v-if="addErrors.email"><i class="fas fa-exclamation-triangle"></i> {{ addErrors.email }}</span>
          </div>
          <div class="form-group">
            <label>Phone *</label>
            <input v-model="newOwner.phone" type="tel" placeholder="+255700000000" />
          </div>
          <div class="default-pw-note" v-if="newOwner.name.trim()">
            <i class="fas fa-info-circle"></i>
            Default password: <strong>{{ newOwner.name.trim().toUpperCase() }}@###</strong> (random numbers will be appended)
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
          <div class="server-errors" v-if="addServerErrors.length > 0">
            <div v-for="(msg, i) in addServerErrors" :key="i" class="server-error"><i class="fas fa-exclamation-circle"></i> {{ msg }}</div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="closeCreateModal">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="creating || !canAdd">
              <i class="fas fa-plus"></i> {{ creating ? 'Creating...' : 'Create Owner' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" v-if="deleteTarget" @click.self="deleteTarget = null">
      <div class="modal-card confirm-modal">
        <div class="confirm-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <h3>Delete Owner</h3>
        <p>Are you sure you want to delete <strong>{{ deleteTarget.name }}</strong>? This cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="deleteTarget = null">Cancel</button>
          <button class="btn btn-danger" @click="deleteOwner" :disabled="deleting">
            <i class="fas fa-trash"></i> {{ deleting ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>

    <ResetOwnerPasswordModal
      v-if="passwordTarget"
      :owner-id="passwordTarget.id"
      :owner-name="passwordTarget.name"
      @close="passwordTarget = null"
      @updated="onPasswordUpdated"
    />

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas fa-check-circle"></i> {{ toastMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { superadminApi } from '@/api'
import { useTablePagination } from '@/composables/useTablePagination'
import TablePagination from '@/components/TablePagination.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import ResetOwnerPasswordModal from '@/components/ResetOwnerPasswordModal.vue'

const loading = ref(true)
const owners = ref([])
const sortKey = ref('created_at')
const showCreateModal = ref(false)
const creating = ref(false)
const deleteTarget = ref(null)
const deleting = ref(false)
const toastMsg = ref('')
const addErrors = ref({})
const addServerErrors = ref([])
const passwordTarget = ref(null)

function isTrialExpired(owner) {
  return owner.owner_profile?.deactivation_reason === 'trial_expired'
}

const trialExpiredOwners = computed(() =>
  owners.value.filter(isTrialExpired)
)

async function extendTrial(owner, days = 30) {
  try {
    const res = await superadminApi.extendTrial(owner.id, { days })
    toastMsg.value = res.data.message || 'Trial extended'
    await loadData()
  } catch {
    toastMsg.value = 'Failed to extend trial'
  }
  setTimeout(() => toastMsg.value = '', 3000)
}

const newOwner = ref({
  name: '',
  email: '',
  phone: '',
  max_products: 50,
  max_employees: 5,
  subscription_plan: 'starter',
})

const canAdd = computed(() =>
  newOwner.value.name.trim().length >= 2 &&
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newOwner.value.email) &&
  newOwner.value.phone.trim().length > 0
)

function validateAddField(field) {
  if (field === 'name') {
    if (!newOwner.value.name.trim()) addErrors.value.name = 'Please enter the owner name.'
    else if (newOwner.value.name.trim().length < 2) addErrors.value.name = 'Name must be at least 2 characters.'
    else delete addErrors.value.name
  }
  if (field === 'email') {
    if (!newOwner.value.email.trim()) addErrors.value.email = 'Please enter an email address.'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newOwner.value.email)) addErrors.value.email = 'Please enter a valid email.'
    else delete addErrors.value.email
  }
}

const sortedOwners = computed(() => {
  const list = [...owners.value]
  const key = sortKey.value
  const desc = key.endsWith('_desc')
  const field = desc ? key.replace('_desc', '') : key

  list.sort((a, b) => {
    let valA, valB
    if (field === 'plan') {
      valA = a.owner_profile?.subscription_plan || 'free'
      valB = b.owner_profile?.subscription_plan || 'free'
    } else if (field === 'created_at') {
      valA = new Date(a.created_at).getTime()
      valB = new Date(b.created_at).getTime()
      return desc ? valA - valB : valB - valA
    } else {
      valA = (a[field] || '').toString().toLowerCase()
      valB = (b[field] || '').toString().toLowerCase()
    }
    if (valA < valB) return desc ? 1 : -1
    if (valA > valB) return desc ? -1 : 1
    return 0
  })
  return list
})

const { search, currentPage, showAll, displayItems, totalPages, pageInfo, onSearch, goToPage, toggleShowAll } =
  useTablePagination(sortedOwners, ['name', 'email', 'phone'])

async function loadData() {
  try {
    const res = await superadminApi.getOwners()
    owners.value = res.data
  } catch { /* empty */ }
  loading.value = false
}

async function createOwner() {
  addServerErrors.value = []
  creating.value = true
  try {
    const res = await superadminApi.createOwner(newOwner.value)
    showCreateModal.value = false
    const pw = res.data.default_password
    toastMsg.value = `Owner created! Default password: ${pw}`
    closeCreateModal()
    await loadData()
  } catch (e) {
    if (e.response?.data?.errors) {
      addServerErrors.value = Object.entries(e.response.data.errors).map(([, arr]) => arr[0])
    } else {
      addServerErrors.value = [e.response?.data?.message || 'Failed to create owner']
    }
  }
  creating.value = false
  setTimeout(() => toastMsg.value = '', 6000)
}

function closeCreateModal() {
  showCreateModal.value = false
  newOwner.value = { name: '', email: '', phone: '', max_products: 50, max_employees: 5, subscription_plan: 'starter' }
  addErrors.value = {}
  addServerErrors.value = []
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

function confirmDelete(owner) { deleteTarget.value = owner }

async function deleteOwner() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await superadminApi.deleteOwner(deleteTarget.value.id)
    toastMsg.value = 'Owner deleted'
    deleteTarget.value = null
    await loadData()
  } catch {
    toastMsg.value = 'Failed to delete'
  }
  deleting.value = false
  setTimeout(() => toastMsg.value = '', 3000)
}

function openPasswordModal(owner) {
  passwordTarget.value = owner
}

function onPasswordUpdated() {
  passwordTarget.value = null
  toastMsg.value = 'Password updated'
  setTimeout(() => toastMsg.value = '', 3000)
}

onMounted(loadData)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.page-header h1 { font-size: 26px; margin-bottom: 4px; }
.subtitle { color: #888; font-size: 14px; }

.trial-alert {
  display: flex;
  gap: 16px;
  background: #fff8e6;
  border: 1px solid #f5d78e;
  border-left: 4px solid #f39c12;
  border-radius: 10px;
  padding: 18px 20px;
  margin-bottom: 24px;
}
.trial-alert-icon { color: #f39c12; font-size: 24px; flex-shrink: 0; }
.trial-alert-body strong { color: #8a6d1a; font-size: 15px; }
.trial-alert-body p { color: #8a6d1a; font-size: 13px; margin: 4px 0 12px; line-height: 1.5; }
.trial-alert-body ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 8px; }
.trial-alert-body li { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; font-size: 13px; }
.trial-alert-body li a { color: #b57f0a; font-weight: 600; text-decoration: none; }
.trial-alert-body li a:hover { text-decoration: underline; }
.trial-alert-meta { color: #b08c3a; font-size: 12px; }

.trial-expired-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
  background: #fef3e2;
  color: #b57f0a;
  border: 1px solid #f5d78e;
  border-radius: 20px;
  padding: 2px 10px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.empty-state { text-align: center; padding: 60px 24px; }
.empty-icon { width: 80px; height: 80px; background: #f5f5f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; }
.empty-icon i { font-size: 32px; color: #ccc; }
.empty-state h3 { font-size: 18px; margin-bottom: 8px; }
.empty-state p { color: #888; font-size: 14px; max-width: 400px; margin: 0 auto 20px; line-height: 1.6; }

.summary-bar { display: flex; gap: 24px; margin-bottom: 20px; font-size: 14px; color: #666; flex-wrap: wrap; }
.summary-bar strong { color: #333; }

.filters-bar { display: flex; gap: 16px; align-items: center; margin-bottom: 16px; flex-wrap: wrap; }

.search-box { display: flex; align-items: center; gap: 10px; background: #f8f9fa; border: 1px solid #eee; border-radius: 6px; padding: 10px 14px; flex: 1; max-width: 400px; }
.search-box i { color: #999; }
.search-box input { flex: 1; border: none; background: none; font-size: 14px; outline: none; font-family: inherit; }

.sort-box { display: flex; align-items: center; gap: 8px; }
.sort-label { font-size: 13px; color: #888; font-weight: 500; display: flex; align-items: center; gap: 6px; white-space: nowrap; }
.sort-select { padding: 8px 12px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 13px; font-family: 'Inter', sans-serif; background: #fff; cursor: pointer; color: #333; }
.sort-select:focus { outline: none; border-color: #e74c3c; }

.table-wrap { overflow-x: auto; }

.sa-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 10px;
  border: 1px solid #eee;
  overflow: hidden;
}

.sa-table th {
  text-align: left;
  padding: 14px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #fafafa;
  border-bottom: 2px solid #eee;
  white-space: nowrap;
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

.plan-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.plan-free { background: #e9ecef; color: #6c757d; }
.plan-starter { background: #eaf4ff; color: #2980b9; }
.plan-pro { background: #fef9e7; color: #f39c12; }
.plan-enterprise { background: #eafaf1; color: #27ae60; }

.muted { color: #999; font-size: 13px; }

.actions-cell { display: flex; gap: 6px; }

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
.btn-icon.danger { color: #e74c3c; }
.btn-icon.danger:hover { background: #fef5f5; }

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
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; }
.btn-outline:hover { border-color: #999; }
.btn-danger { background: #e74c3c; color: #fff; }
.btn-danger:hover { background: #c0392b; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
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
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-card h3 i { color: #e74c3c; }
.modal-desc { color: #888; font-size: 13px; margin-bottom: 20px; line-height: 1.5; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
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
.form-group select:focus { outline: none; border-color: #e74c3c; }
.form-group.has-error input { border-color: #e74c3c; background: #fef8f8; }
.field-error { display: flex; align-items: center; gap: 6px; margin-top: 6px; font-size: 12px; color: #e74c3c; font-weight: 500; }
.field-error i { font-size: 11px; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.default-pw-note { padding: 12px; background: #fef9e7; border: 1px solid #fdebd0; border-radius: 6px; font-size: 13px; color: #7d6608; margin-bottom: 16px; }
.default-pw-note i { margin-right: 4px; }

.server-errors { margin-bottom: 12px; }
.server-error { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #fef5f5; border: 1px solid #fdd; border-radius: 6px; color: #c0392b; font-size: 13px; font-weight: 500; margin-bottom: 6px; }

.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px; }

.confirm-modal { text-align: center; }
.confirm-icon { width: 64px; height: 64px; background: #fef5f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
.confirm-icon i { font-size: 28px; color: #e74c3c; }
.confirm-modal p { color: #666; font-size: 14px; margin-bottom: 8px; }

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
  .page-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .filters-bar { flex-direction: column; }
  .search-box { max-width: 100%; }
  .form-row { grid-template-columns: 1fr; }
}
</style>
