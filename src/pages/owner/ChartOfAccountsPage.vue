<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-book" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('accounting.chartOfAccounts.title') }}</h1>
        <p>{{ $t('accounting.chartOfAccounts.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showCreateModal = true"><i class="fas fa-plus"></i> {{ $t('accounting.chartOfAccounts.newAccount') }}</button>
        <router-link to="/owner/accounting" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.back') }}</router-link>
      </div>
    </div>

    <SkeletonLoader v-if="loading" type="table" :count="5" />
    <template v-else>
      <div class="filter-row">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input v-model="search" :placeholder="$t('common.searchPlaceholder')" />
        </div>
        <select v-model="typeFilter" class="filter-select">
          <option value="">{{ $t('accounting.allTypes') }}</option>
          <option value="asset">{{ $t('accounting.types.asset') }}</option>
          <option value="liability">{{ $t('accounting.types.liability') }}</option>
          <option value="equity">{{ $t('accounting.types.equity') }}</option>
          <option value="revenue">{{ $t('accounting.types.revenue') }}</option>
          <option value="expense">{{ $t('accounting.types.expense') }}</option>
        </select>
      </div>

      <div v-for="group in filteredAccounts" :key="group.type" class="account-group card">
        <h3 class="group-header">
          <span :class="['type-dot', group.type]"></span>
          {{ $t(`accounting.types.${group.type}`) }}
          <span class="group-total">TSh {{ formatPrice(group.total) }}</span>
        </h3>
        <div class="table-wrap">
          <table class="sa-table">
            <thead>
              <tr>
                <th>{{ $t('accounting.chartOfAccounts.code') }}</th>
                <th>{{ $t('accounting.chartOfAccounts.accountName') }}</th>
                <th>{{ $t('accounting.chartOfAccounts.balance') }}</th>
                <th>{{ $t('accounting.chartOfAccounts.status') }}</th>
                <th>{{ $t('accounting.chartOfAccounts.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="acc in group.accounts" :key="acc.id" :class="{ 'system-row': acc.is_system }">
                <td class="code-cell">{{ acc.formatted_code }}</td>
                <td>
                  <strong>{{ acc.name }}</strong>
                  <span v-if="acc.description" class="muted">{{ acc.description }}</span>
                </td>
                <td class="balance-cell" :class="{ 'negative': acc.balance < 0 }">
                  TSh {{ formatPrice(Math.abs(acc.balance)) }}
                </td>
                <td>
                  <span :class="['status-dot-label', acc.is_active ? 'active' : 'inactive']">
                    {{ acc.is_active ? $t('common.active') : $t('common.inactive') }}
                  </span>
                </td>
                <td class="actions-cell">
                  <button v-if="!acc.is_system" class="btn-icon" @click="editAccount(acc)" :title="$t('common.edit')">
                    <i class="fas fa-pen"></i>
                  </button>
                  <button v-if="!acc.is_system" class="btn-icon danger" @click="confirmDelete(acc)" :title="$t('common.delete')">
                    <i class="fas fa-trash"></i>
                  </button>
                  <span v-if="acc.is_system" class="system-badge">System</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Create/Edit Modal -->
    <div class="modal-overlay" v-if="showCreateModal || editingAccount" @click.self="closeModal">
      <div class="modal-card">
        <h2><i class="fas" :class="editingAccount ? 'fa-pen' : 'fa-plus-circle'"></i> {{ editingAccount ? $t('accounting.chartOfAccounts.editAccount') : $t('accounting.chartOfAccounts.newAccount') }}</h2>
        <div class="form-group">
          <label>{{ $t('accounting.chartOfAccounts.code') }}</label>
          <input v-model="form.code" type="text" maxlength="10" :disabled="editingAccount" />
        </div>
        <div class="form-group">
          <label>{{ $t('accounting.chartOfAccounts.accountName') }}</label>
          <input v-model="form.name" type="text" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>{{ $t('accounting.chartOfAccounts.type') }}</label>
            <select v-model="form.type">
              <option value="asset">{{ $t('accounting.types.asset') }}</option>
              <option value="liability">{{ $t('accounting.types.liability') }}</option>
              <option value="equity">{{ $t('accounting.types.equity') }}</option>
              <option value="revenue">{{ $t('accounting.types.revenue') }}</option>
              <option value="expense">{{ $t('accounting.types.expense') }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>{{ $t('accounting.chartOfAccounts.normalBalance') }}</label>
            <select v-model="form.normal_balance">
              <option value="debit">{{ $t('accounting.debit') }}</option>
              <option value="credit">{{ $t('accounting.credit') }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>{{ $t('accounting.chartOfAccounts.description') }} {{ $t('common.optional') }}</label>
          <input v-model="form.description" type="text" />
        </div>
        <div v-if="error" class="field-error"><i class="fas fa-exclamation-circle"></i> {{ error }}</div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="closeModal">{{ $t('common.cancel') }}</button>
          <button class="btn btn-primary" @click="saveAccount" :disabled="saving">
            {{ saving ? $t('common.saving') : $t('common.save') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div class="modal-overlay" v-if="deletingAccount" @click.self="deletingAccount = null">
      <div class="modal-card confirm-modal">
        <div class="confirm-icon"><i class="fas fa-trash"></i></div>
        <h2>{{ $t('accounting.chartOfAccounts.deleteAccount') }}</h2>
        <p class="modal-desc">{{ $t('accounting.chartOfAccounts.deleteConfirm', { name: deletingAccount?.name }) }}</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="deletingAccount = null">{{ $t('common.cancel') }}</button>
          <button class="btn btn-danger" @click="doDelete">{{ $t('common.delete') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { accountApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const loading = ref(true)
const saving = ref(false)
const accounts = ref([])
const search = ref('')
const typeFilter = ref('')
const showCreateModal = ref(false)
const editingAccount = ref(null)
const deletingAccount = ref(null)
const error = ref('')

const form = ref({ code: '', name: '', type: 'asset', normal_balance: 'debit', description: '' })

function formatPrice(v) {
  return Number(v || 0).toLocaleString('en-TZ')
}

const filteredAccounts = computed(() => {
  let filtered = accounts.value
  if (typeFilter.value) {
    filtered = filtered.filter(a => a.type === typeFilter.value)
  }
  if (search.value) {
    const s = search.value.toLowerCase()
    filtered = filtered.filter(a => a.name.toLowerCase().includes(s) || a.code.includes(s))
  }
  const groups = {}
  const typeOrder = ['asset', 'liability', 'equity', 'revenue', 'expense']
  for (const type of typeOrder) {
    const typeAccounts = filtered.filter(a => a.type === type)
    if (typeAccounts.length > 0) {
      groups[type] = {
        type,
        accounts: typeAccounts,
        total: typeAccounts.reduce((s, a) => s + Math.abs(a.balance || 0), 0),
      }
    }
  }
  return groups
})

async function loadAccounts() {
  try {
    const res = await accountApi.getAll()
    accounts.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function editAccount(acc) {
  editingAccount.value = acc
  form.value = { code: acc.code, name: acc.name, type: acc.type, normal_balance: acc.normal_balance, description: acc.description || '' }
}

function closeModal() {
  showCreateModal.value = false
  editingAccount.value = null
  form.value = { code: '', name: '', type: 'asset', normal_balance: 'debit', description: '' }
  error.value = ''
}

async function saveAccount() {
  error.value = ''
  if (!form.value.code || !form.value.name) {
    error.value = 'Code and name are required'
    return
  }
  saving.value = true
  try {
    if (editingAccount.value) {
      await accountApi.update(editingAccount.value.id, {
        name: form.value.name,
        description: form.value.description,
      })
    } else {
      await accountApi.create(form.value)
    }
    closeModal()
    await loadAccounts()
  } catch (e) {
    error.value = e.response?.data?.message || 'Failed to save'
  } finally {
    saving.value = false
  }
}

function confirmDelete(acc) {
  deletingAccount.value = acc
}

async function doDelete() {
  try {
    await accountApi.delete(deletingAccount.value.id)
    deletingAccount.value = null
    await loadAccounts()
  } catch (e) {
    error.value = e.response?.data?.message || 'Failed to delete'
    deletingAccount.value = null
  }
}

onMounted(loadAccounts)
</script>

<style scoped>
.dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.dash-header h1 { font-size: 24px; font-weight: 700; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; color: #666; text-decoration: none; font-size: 13px; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.filter-row { display: flex; gap: 12px; margin-bottom: 20px; }
.search-box { display: flex; align-items: center; gap: 8px; border: 1px solid #e0e0e0; border-radius: 6px; padding: 0 12px; background: #fff; flex: 1; max-width: 300px; }
.search-box i { color: #999; }
.search-box input { border: none; outline: none; padding: 10px 0; font-size: 14px; width: 100%; }
.filter-select { padding: 10px 14px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 14px; background: #fff; }

.account-group { margin-bottom: 20px; }
.group-header { display: flex; align-items: center; gap: 8px; padding: 16px 20px; border-bottom: 1px solid #f0f0f0; font-size: 15px; font-weight: 600; }
.group-total { margin-left: auto; font-size: 14px; color: #888; font-weight: 400; }
.type-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.type-dot.asset { background: #3498db; }
.type-dot.liability { background: #e74c3c; }
.type-dot.equity { background: #9b59b6; }
.type-dot.revenue { background: #27ae60; }
.type-dot.expense { background: #f39c12; }

.table-wrap { overflow-x: auto; }
.sa-table { width: 100%; border-collapse: collapse; }
.sa-table th { padding: 10px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 1px solid #f0f0f0; background: #fafafa; }
.sa-table td { padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.code-cell { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #555; }
.balance-cell { font-weight: 600; text-align: right; }
.balance-cell.negative { color: #e74c3c; }
.muted { display: block; font-size: 12px; color: #999; margin-top: 2px; }
.system-row { background: #fafafa; }
.system-badge { font-size: 11px; color: #999; background: #f0f0f0; padding: 2px 8px; border-radius: 4px; }

.status-dot-label { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 500; }
.status-dot-label::before { content: ''; width: 6px; height: 6px; border-radius: 50%; }
.status-dot-label.active::before { background: #27ae60; }
.status-dot-label.inactive::before { background: #e74c3c; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; }
.btn-outline:hover { border-color: #999; }
.btn-danger { background: #e74c3c; color: #fff; }
.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 13px; color: #666; transition: all 0.2s; }
.btn-icon:hover { border-color: #e74c3c; color: #e74c3c; }
.btn-icon.danger:hover { background: #e74c3c; color: #fff; border-color: #e74c3c; }
.actions-cell { white-space: nowrap; display: flex; gap: 4px; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 24px; }
.modal-card { width: 100%; max-width: 480px; background: #fff; border-radius: 12px; padding: 32px; }
.modal-card h2 { font-size: 20px; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; }
.modal-card h2 i { color: #e74c3c; }
.modal-desc { color: #888; font-size: 13px; margin-bottom: 20px; line-height: 1.5; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
.form-group input, .form-group select { width: 100%; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; box-sizing: border-box; }
.form-group input:focus, .form-group select:focus { outline: none; border-color: #e74c3c; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.field-error { display: flex; align-items: center; gap: 6px; margin-top: 8px; font-size: 12px; color: #e74c3c; font-weight: 500; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; }

.confirm-modal { text-align: center; }
.confirm-icon { width: 64px; height: 64px; background: #fef5f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
.confirm-icon i { font-size: 28px; color: #e74c3c; }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .header-actions { flex-wrap: wrap; }
  .filter-row { flex-direction: column; }
  .search-box { max-width: 100%; }
  .form-row { grid-template-columns: 1fr; }
}
</style>
