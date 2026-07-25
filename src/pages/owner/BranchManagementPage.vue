<template>
  <div class="container page">
    <div class="page-header">
      <div>
        <h1>{{ $t('branches.title') }}</h1>
        <p class="subtitle">{{ $t('branches.subtitle') }}</p>
      </div>
      <button class="btn btn-primary" @click="showAddModal = true"><i class="fas fa-plus"></i> {{ $t('branches.addBranch') }}</button>
    </div>

    <SkeletonLoader v-if="loading" type="list" :count="3" />

    <div v-else-if="branches.length === 0" class="empty-state card">
      <div class="empty-icon"><i class="fas fa-store"></i></div>
      <h3>{{ $t('branches.noBranches') }}</h3>
      <p>{{ $t('branches.noBranchesDesc') }}</p>
      <button class="btn btn-primary" @click="showAddModal = true"><i class="fas fa-plus"></i> {{ $t('branches.addFirst') }}</button>
    </div>

    <div v-else>
      <div class="summary-bar">
        <span><strong>{{ branches.length }}</strong> {{ $t('branches.totalBranches') }}</span>
        <span><strong>{{ branches.filter(b => b.is_active).length }}</strong> {{ $t('common.active') }}</span>
        <span><strong>{{ branches.filter(b => !b.is_active).length }}</strong> {{ $t('common.inactive') }}</span>
      </div>

      <div class="branches-grid">
        <div v-for="branch in branches" :key="branch.id" class="branch-card card" :class="{ inactive: !branch.is_active }">
          <div class="branch-header">
            <div class="branch-icon"><i class="fas fa-store"></i></div>
            <div class="branch-info">
              <h3>
                {{ branch.name }}
                <span v-if="branch.is_default" class="default-badge">{{ $t('branches.default') }}</span>
              </h3>
              <p class="branch-location" v-if="branch.city || branch.address">
                <i class="fas fa-map-marker-alt"></i>
                [{{ branch.city }}{{ branch.city && branch.address ? ', ' : '' }}{{ branch.address }}]
              </p>
              <p class="branch-phone" v-if="branch.phone"><i class="fas fa-phone"></i> {{ branch.phone }}</p>
            </div>
            <div class="branch-stats">
              <div class="stat">
                <span class="stat-value">{{ branch.orders_count ?? 0 }}</span>
                <span class="stat-label">{{ $t('branches.orders') }}</span>
              </div>
              <div class="stat">
                <span class="stat-value">{{ branch.employees_count ?? 0 }}</span>
                <span class="stat-label">{{ $t('branches.employees') }}</span>
              </div>
            </div>
          </div>
          <div class="branch-actions">
            <button v-if="!branch.is_default" class="btn btn-sm btn-outline" @click="setDefault(branch)" :title="$t('branches.setDefault')">
              <i class="fas fa-star"></i> {{ $t('branches.setDefault') }}
            </button>
            <button class="btn btn-sm btn-outline" @click="editBranch(branch)"><i class="fas fa-edit"></i> {{ $t('common.edit') }}</button>
            <button class="btn-icon" :title="branch.is_active ? $t('common.deactivate') : $t('common.activate')" @click="toggleActive(branch)">
              <i :class="branch.is_active ? 'fas fa-pause' : 'fas fa-play'"></i>
            </button>
            <button v-if="!branch.is_default" class="btn-icon danger" :title="$t('common.delete')" @click="confirmDelete(branch)"><i class="fas fa-trash"></i></button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal-overlay" v-if="showAddModal" @click.self="closeModal">
      <div class="modal-card card">
        <h2><i class="fas fa-store"></i> {{ editingBranch ? $t('branches.editBranch') : $t('branches.addBranch') }}</h2>
        <form @submit.prevent="saveBranch" novalidate>
          <div class="form-group" :class="{ 'has-error': formErrors.name }">
            <label>{{ $t('branches.branchName') }} *</label>
            <input v-model="formData.name" type="text" :placeholder="$t('branches.branchNamePlaceholder')" @blur="validateField('name')" @input="validateField('name')" />
            <span class="field-error" v-if="formErrors.name"><i class="fas fa-exclamation-triangle"></i> {{ formErrors.name }}</span>
          </div>
          <div class="form-group">
            <label>{{ $t('branches.city') }}</label>
            <input v-model="formData.city" type="text" :placeholder="$t('branches.cityPlaceholder')" />
          </div>
          <div class="form-group">
            <label>{{ $t('branches.address') }}</label>
            <input v-model="formData.address" type="text" :placeholder="$t('branches.addressPlaceholder')" />
          </div>
          <div class="form-group">
            <label>{{ $t('branches.phone') }}</label>
            <input v-model="formData.phone" type="tel" :placeholder="$t('branches.phonePlaceholder')" />
          </div>
          <div class="server-errors" v-if="serverErrors.length > 0">
            <div v-for="(msg, i) in serverErrors" :key="i" class="server-error"><i class="fas fa-exclamation-circle"></i> {{ msg }}</div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="closeModal">{{ $t('common.cancel') }}</button>
            <button type="submit" class="btn btn-primary" :disabled="saving || !canSave">
              <i class="fas fa-save"></i> {{ saving ? $t('common.saving') : (editingBranch ? $t('common.save') : $t('common.create')) }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" v-if="deleteTarget" @click.self="deleteTarget = null">
      <div class="modal-card card confirm-modal">
        <div class="confirm-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <h2>{{ $t('branches.confirmDelete') }}</h2>
        <p>{{ $t('branches.confirmDeleteDesc') }}</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="deleteTarget = null">{{ $t('common.cancel') }}</button>
          <button class="btn btn-danger" @click="deleteBranch" :disabled="deleting"><i class="fas fa-trash"></i> {{ deleting ? $t('common.loading') : $t('common.delete') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { branchApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const { t } = useI18n()

const branches = ref([])
const loading = ref(true)
const showAddModal = ref(false)
const editingBranch = ref(null)
const formData = ref({ name: '', city: '', address: '', phone: '' })
const formErrors = ref({})
const serverErrors = ref([])
const saving = ref(false)
const deleteTarget = ref(null)
const deleting = ref(false)

const canSave = computed(() => formData.value.name.trim().length >= 2)

function validateField(field) {
  if (field === 'name') {
    if (!formData.value.name.trim()) formErrors.value.name = t('branches.errors.nameRequired')
    else if (formData.value.name.trim().length < 2) formErrors.value.name = t('branches.errors.nameMinLength')
    else delete formErrors.value.name
  }
}

async function loadBranches() {
  loading.value = true
  try {
    const res = await branchApi.getAll()
    branches.value = res.data
  } catch { branches.value = [] }
  loading.value = false
}

function editBranch(branch) {
  editingBranch.value = branch
  formData.value = { name: branch.name, city: branch.city || '', address: branch.address || '', phone: branch.phone || '' }
  showAddModal.value = true
}

function closeModal() {
  showAddModal.value = false
  editingBranch.value = null
  formData.value = { name: '', city: '', address: '', phone: '' }
  formErrors.value = {}
  serverErrors.value = []
}

async function saveBranch() {
  validateField('name')
  if (formErrors.value.name) return
  serverErrors.value = []
  saving.value = true
  try {
    if (editingBranch.value) {
      await branchApi.update(editingBranch.value.id, formData.value)
    } else {
      await branchApi.create(formData.value)
    }
    closeModal()
    await loadBranches()
  } catch (e) {
    if (e.response?.data?.errors) {
      serverErrors.value = Object.entries(e.response.data.errors).map(([, arr]) => arr[0])
    } else {
      serverErrors.value = [e.response?.data?.message || t('branches.errors.saveFailed')]
    }
  }
  saving.value = false
}

async function setDefault(branch) {
  try {
    await branchApi.setDefault(branch.id)
    await loadBranches()
  } catch { /* empty */ }
}

async function toggleActive(branch) {
  try {
    await branchApi.update(branch.id, { is_active: !branch.is_active })
    branch.is_active = !branch.is_active
  } catch { /* empty */ }
}

function confirmDelete(branch) { deleteTarget.value = branch }

async function deleteBranch() {
  deleting.value = true
  try {
    await branchApi.delete(deleteTarget.value.id)
    branches.value = branches.value.filter(b => b.id !== deleteTarget.value.id)
    deleteTarget.value = null
  } catch { /* empty */ }
  deleting.value = false
}

onMounted(loadBranches)
</script>

<style scoped>
.page { padding: 32px 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; }
.page-header h1 { font-size: 26px; margin-bottom: 4px; }
.subtitle { color: #888; font-size: 14px; }

.empty-state { text-align: center; padding: 60px 24px; }
.empty-icon { width: 80px; height: 80px; background: #f5f5f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; }
.empty-icon i { font-size: 32px; color: #ccc; }
.empty-state h3 { font-size: 18px; margin-bottom: 8px; }
.empty-state p { color: #888; font-size: 14px; max-width: 400px; margin: 0 auto 20px; line-height: 1.6; }

.summary-bar { display: flex; gap: 24px; margin-bottom: 20px; font-size: 14px; color: #666; }
.summary-bar strong { color: #333; }

.branches-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 16px; }
.branch-card { padding: 20px; }
.branch-card.inactive { opacity: 0.6; }
.branch-header { display: flex; gap: 14px; align-items: flex-start; margin-bottom: 16px; }
.branch-icon { width: 48px; height: 48px; background: #f0f0f0; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #e74c3c; font-size: 20px; flex-shrink: 0; }
.branch-info { flex: 1; min-width: 0; }
.branch-info h3 { font-size: 16px; font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; }
.default-badge { font-size: 11px; background: #fef9e7; color: #b7950b; border: 1px solid #fdebd0; padding: 2px 8px; border-radius: 10px; font-weight: 500; }
.branch-location, .branch-phone { font-size: 13px; color: #888; margin-top: 2px; }
.branch-location i, .branch-phone i { width: 14px; color: #aaa; }
.branch-stats { display: flex; gap: 16px; flex-shrink: 0; }
.stat { text-align: center; }
.stat-value { display: block; font-size: 18px; font-weight: 700; color: #333; }
.stat-label { font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.3px; }
.branch-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-sm { padding: 6px 12px; font-size: 12px; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; }
.btn-outline:hover { border-color: #999; }
.btn-danger { background: #e74c3c; color: #fff; }
.btn-danger:hover { background: #c0392b; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 13px; color: #666; transition: all 0.2s; }
.btn-icon:hover { border-color: #e74c3c; color: #e74c3c; background: #fef5f5; }
.btn-icon.danger:hover { background: #e74c3c; color: #fff; border-color: #e74c3c; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 24px; }
.modal-card { width: 100%; max-width: 460px; padding: 32px; }
.modal-card h2 { font-size: 20px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.modal-card h2 i { color: #e74c3c; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
.form-group input { width: 100%; padding: 12px 14px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; font-family: 'Inter', sans-serif; box-sizing: border-box; }
.form-group input:focus { outline: none; border-color: #e74c3c; }
.form-group.has-error input { border-color: #e74c3c; background: #fef8f8; }
.field-error { display: flex; align-items: center; gap: 6px; margin-top: 6px; font-size: 12px; color: #e74c3c; font-weight: 500; }
.field-error i { font-size: 11px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; }

.confirm-modal { text-align: center; }
.confirm-icon { width: 64px; height: 64px; background: #fef5f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
.confirm-icon i { font-size: 28px; color: #e74c3c; }
.confirm-modal p { color: #666; font-size: 14px; margin-bottom: 8px; }

.server-errors { margin-bottom: 12px; }
.server-error { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #fef5f5; border: 1px solid #fdd; border-radius: 6px; color: #c0392b; font-size: 13px; font-weight: 500; margin-bottom: 6px; }

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .branches-grid { grid-template-columns: 1fr; }
  .branch-header { flex-wrap: wrap; }
  .branch-stats { width: 100%; justify-content: flex-start; }
}
</style>
