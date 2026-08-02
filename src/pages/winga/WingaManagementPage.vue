<template>
  <div class="container page">
    <div class="page-header">
      <div>
        <h1>{{ $t('wingas.title') }}</h1>
        <p class="subtitle">{{ $t('wingas.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <router-link :to="commissionsLink" class="btn btn-outline">
          <i class="fas fa-money-bill-wave"></i> {{ $t('wingas.viewCommissions') }}
        </router-link>
        <button class="btn btn-primary" @click="openAdd"><i class="fas fa-plus"></i> {{ $t('wingas.addWinga') }}</button>
      </div>
    </div>

    <SkeletonLoader v-if="loading" type="list" :count="3" />

    <div v-else-if="wingas.length === 0" class="empty-state card">
      <div class="empty-icon"><i class="fas fa-person-walking-arrow-right"></i></div>
      <h3>{{ $t('wingas.noWingas') }}</h3>
      <p>{{ $t('wingas.noWingasDesc') }}</p>
      <button class="btn btn-primary" @click="openAdd"><i class="fas fa-plus"></i> {{ $t('wingas.addFirst') }}</button>
    </div>

    <div v-else>
      <div class="summary-bar">
        <span><strong>{{ wingas.length }}</strong> {{ $t('wingas.totalWingas') }}</span>
        <span><strong>{{ activeCount }}</strong> {{ $t('common.active') }}</span>
        <span><strong>{{ inactiveCount }}</strong> {{ $t('common.inactive') }}</span>
        <span><strong>{{ pendingCount }}</strong> {{ $t('wingas.pendingCommissions') }}</span>
      </div>

      <div class="wingas-grid">
        <div v-for="winga in wingas" :key="winga.id" class="winga-card card" :class="{ inactive: winga.status !== 'active' }">
          <div class="winga-header">
            <div class="winga-icon"><i class="fas fa-user-tie"></i></div>
            <div class="winga-info">
              <h3>{{ winga.name }}</h3>
              <span class="rate-badge">{{ winga.commission_rate }}%</span>
            </div>
            <span :class="['status-badge', winga.status === 'active' ? 'status-active' : 'status-inactive']">
              {{ winga.status === 'active' ? $t('common.active') : $t('common.inactive') }}
            </span>
          </div>

          <div class="winga-details">
            <div v-if="winga.phone" class="detail-row"><i class="fas fa-phone"></i> {{ winga.phone }}</div>
            <div v-if="winga.tin_number" class="detail-row"><i class="fas fa-receipt"></i> TIN: {{ winga.tin_number }}</div>
            <div v-if="winga.nida_number" class="detail-row"><i class="fas fa-id-card"></i> NIDA: {{ winga.nida_number }}</div>
            <div class="detail-row"><i class="fas fa-store"></i> {{ winga.branch ? winga.branch.name : $t('wingas.noBranch') }}</div>
          </div>

          <div class="winga-footer">
            <div class="pending-chip">
              <i class="fas fa-clock"></i>
              {{ winga.pending_commissions ?? 0 }} {{ $t('wingas.pendingCommissions') }}
            </div>
            <div class="winga-actions">
              <button class="btn btn-sm btn-outline" @click="openEdit(winga)"><i class="fas fa-edit"></i> {{ $t('common.edit') }}</button>
              <button class="btn-icon" :title="winga.status === 'active' ? $t('common.deactivate') : $t('common.activate')" @click="toggleStatus(winga)">
                <i :class="winga.status === 'active' ? 'fas fa-pause' : 'fas fa-play'"></i>
              </button>
              <button class="btn-icon danger" :title="$t('common.delete')" @click="confirmDelete(winga)"><i class="fas fa-trash"></i></button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="modal-overlay" v-if="showModal" @click.self="closeModal">
      <div class="modal-card card">
        <h2><i class="fas fa-user-tie"></i> {{ editingWinga ? $t('wingas.editWinga') : $t('wingas.addWinga') }}</h2>
        <form @submit.prevent="saveWinga" novalidate>
          <div class="form-group" :class="{ 'has-error': formErrors.name }">
            <label>{{ $t('wingas.name') }} *</label>
            <input v-model="formData.name" type="text" :placeholder="$t('wingas.namePlaceholder')" @blur="validateField('name')" @input="validateField('name')" />
            <span class="field-error" v-if="formErrors.name"><i class="fas fa-exclamation-triangle"></i> {{ formErrors.name }}</span>
          </div>
          <div class="form-group">
            <label>{{ $t('wingas.phone') }}</label>
            <input v-model="formData.phone" type="tel" :placeholder="$t('wingas.phonePlaceholder')" />
          </div>
          <div class="form-group">
            <label>{{ $t('wingas.tinNumber') }}</label>
            <input v-model="formData.tin_number" type="text" :placeholder="$t('wingas.tinPlaceholder')" />
          </div>
          <div class="form-group">
            <label>{{ $t('wingas.nidaNumber') }}</label>
            <input v-model="formData.nida_number" type="text" :placeholder="$t('wingas.nidaPlaceholder')" />
          </div>
          <div class="form-group" :class="{ 'has-error': formErrors.commission_rate }">
            <label>{{ $t('wingas.commissionRate') }} *</label>
            <input v-model="formData.commission_rate" type="number" min="0" max="100" step="0.01" @blur="validateField('commission_rate')" @input="validateField('commission_rate')" />
            <span class="field-hint">{{ $t('wingas.commissionRateDesc') }}</span>
            <span class="field-error" v-if="formErrors.commission_rate"><i class="fas fa-exclamation-triangle"></i> {{ formErrors.commission_rate }}</span>
          </div>
          <div class="form-group">
            <label>{{ $t('wingas.branch') }}</label>
            <select v-model="formData.branch_id">
              <option :value="null">{{ $t('wingas.noBranch') }}</option>
              <option v-for="branch in branches" :key="branch.id" :value="branch.id">{{ branch.name }}</option>
            </select>
          </div>
          <div class="server-errors" v-if="serverErrors.length > 0">
            <div v-for="(msg, i) in serverErrors" :key="i" class="server-error"><i class="fas fa-exclamation-circle"></i> {{ msg }}</div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="closeModal">{{ $t('common.cancel') }}</button>
            <button type="submit" class="btn btn-primary" :disabled="saving || !canSave">
              <i class="fas fa-save"></i> {{ saving ? $t('common.saving') : (editingWinga ? $t('common.save') : $t('common.create')) }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" v-if="deleteTarget" @click.self="deleteTarget = null">
      <div class="modal-card card confirm-modal">
        <div class="confirm-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <h2>{{ $t('wingas.confirmDelete') }}</h2>
        <p>{{ $t('wingas.confirmDeleteDesc') }}</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="deleteTarget = null">{{ $t('common.cancel') }}</button>
          <button class="btn btn-danger" @click="deleteWinga" :disabled="deleting"><i class="fas fa-trash"></i> {{ deleting ? $t('common.loading') : $t('common.delete') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { wingaApi, branchApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const { t } = useI18n()
const authStore = useAuthStore()

const wingas = ref([])
const branches = ref([])
const loading = ref(true)
const showModal = ref(false)
const editingWinga = ref(null)
const formData = ref({ name: '', phone: '', tin_number: '', nida_number: '', commission_rate: '', branch_id: null })
const formErrors = ref({})
const serverErrors = ref([])
const saving = ref(false)
const deleteTarget = ref(null)
const deleting = ref(false)

const isOwner = computed(() => authStore.user?.role === 'owner')
const commissionsLink = computed(() => (isOwner.value ? '/owner/winga-commissions' : '/employee/winga-commissions'))

const canSave = computed(() => formData.value.name.trim().length >= 2 && formData.value.commission_rate !== '' && formData.value.commission_rate !== null)

const activeCount = computed(() => wingas.value.filter(w => w.status === 'active').length)
const inactiveCount = computed(() => wingas.value.filter(w => w.status !== 'active').length)
const pendingCount = computed(() => wingas.value.reduce((s, w) => s + Number(w.pending_commissions ?? 0), 0))

function validateField(field) {
  if (field === 'name') {
    if (!formData.value.name.trim()) formErrors.value.name = t('wingas.errors.nameRequired')
    else if (formData.value.name.trim().length < 2) formErrors.value.name = t('wingas.errors.nameMinLength')
    else delete formErrors.value.name
  } else if (field === 'commission_rate') {
    const rate = Number(formData.value.commission_rate)
    if (formData.value.commission_rate === '' || formData.value.commission_rate === null || Number.isNaN(rate)) {
      formErrors.value.commission_rate = t('wingas.errors.rateRequired')
    } else if (rate < 0 || rate > 100) {
      formErrors.value.commission_rate = t('wingas.errors.rateInvalid')
    } else {
      delete formErrors.value.commission_rate
    }
  }
}

async function loadData() {
  loading.value = true
  try {
    const [wingaRes, branchRes] = await Promise.all([
      wingaApi.getAll().catch(() => ({ data: { data: [] } })),
      branchApi.getAll().catch(() => ({ data: [] })),
    ])
    wingas.value = wingaRes.data.data || wingaRes.data || []
    branches.value = Array.isArray(branchRes.data) ? branchRes.data : branchRes.data.data || []
  } catch { /* empty */ }
  loading.value = false
}

function openAdd() {
  editingWinga.value = null
  formData.value = { name: '', phone: '', tin_number: '', nida_number: '', commission_rate: '', branch_id: null }
  formErrors.value = {}
  serverErrors.value = []
  showModal.value = true
}

function openEdit(winga) {
  editingWinga.value = winga
  formData.value = {
    name: winga.name,
    phone: winga.phone || '',
    tin_number: winga.tin_number || '',
    nida_number: winga.nida_number || '',
    commission_rate: winga.commission_rate,
    branch_id: winga.branch_id ?? null,
  }
  formErrors.value = {}
  serverErrors.value = []
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingWinga.value = null
}

async function saveWinga() {
  validateField('name')
  validateField('commission_rate')
  if (formErrors.value.name || formErrors.value.commission_rate) return
  serverErrors.value = []
  saving.value = true
  try {
    const payload = {
      name: formData.value.name.trim(),
      phone: formData.value.phone.trim() || null,
      tin_number: formData.value.tin_number.trim() || null,
      nida_number: formData.value.nida_number.trim() || null,
      commission_rate: Number(formData.value.commission_rate),
      branch_id: formData.value.branch_id || null,
    }
    if (editingWinga.value) {
      await wingaApi.update(editingWinga.value.id, payload)
    } else {
      await wingaApi.create(payload)
    }
    closeModal()
    await loadData()
  } catch (e) {
    if (e.response?.data?.errors) {
      serverErrors.value = Object.entries(e.response.data.errors).map(([, arr]) => arr[0])
    } else {
      serverErrors.value = [e.response?.data?.message || t('wingas.errors.saveFailed')]
    }
  }
  saving.value = false
}

async function toggleStatus(winga) {
  try {
    await wingaApi.toggleStatus(winga.id)
    winga.status = winga.status === 'active' ? 'inactive' : 'active'
  } catch { /* empty */ }
}

function confirmDelete(winga) { deleteTarget.value = winga }

async function deleteWinga() {
  deleting.value = true
  try {
    await wingaApi.delete(deleteTarget.value.id)
    wingas.value = wingas.value.filter(w => w.id !== deleteTarget.value.id)
    deleteTarget.value = null
  } catch { /* empty */ }
  deleting.value = false
}

onMounted(loadData)
</script>

<style scoped>
.page { padding: 32px 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; }
.page-header h1 { font-size: 26px; margin-bottom: 4px; }
.subtitle { color: #888; font-size: 14px; }
.header-actions { display: flex; gap: 10px; align-items: center; }

.empty-state { text-align: center; padding: 60px 24px; }
.empty-icon { width: 80px; height: 80px; background: #f5f5f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; }
.empty-icon i { font-size: 32px; color: #ccc; }
.empty-state h3 { font-size: 18px; margin-bottom: 8px; }
.empty-state p { color: #888; font-size: 14px; max-width: 460px; margin: 0 auto 20px; line-height: 1.6; }

.summary-bar { display: flex; gap: 24px; margin-bottom: 20px; font-size: 14px; color: #666; flex-wrap: wrap; }
.summary-bar strong { color: #333; }

.wingas-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.winga-card { padding: 20px; }
.winga-card.inactive { opacity: 0.6; }
.winga-header { display: flex; gap: 14px; align-items: center; margin-bottom: 14px; }
.winga-icon { width: 46px; height: 46px; background: #fef5f5; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #e74c3c; font-size: 20px; flex-shrink: 0; }
.winga-info { flex: 1; min-width: 0; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.winga-info h3 { font-size: 16px; font-weight: 600; margin: 0; }
.rate-badge { font-size: 12px; background: #fef9e7; color: #b7950b; border: 1px solid #fdebd0; padding: 2px 10px; border-radius: 10px; font-weight: 700; }
.status-badge { padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: capitalize; white-space: nowrap; }
.status-active { background: #f0fff4; color: #1e8449; }
.status-inactive { background: #e9ecef; color: #6c757d; }

.winga-details { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.detail-row { font-size: 13px; color: #666; display: flex; align-items: center; gap: 8px; }
.detail-row i { width: 14px; color: #aaa; }

.winga-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid #f5f5f5; gap: 8px; flex-wrap: wrap; }
.pending-chip { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: #e67e22; background: #fef9e7; padding: 4px 10px; border-radius: 12px; font-weight: 600; }
.winga-actions { display: flex; gap: 6px; align-items: center; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; font-family: 'Inter', sans-serif; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-sm { padding: 6px 12px; font-size: 12px; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #c0392b; }
.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; text-decoration: none; }
.btn-outline:hover { border-color: #999; }
.btn-danger { background: #e74c3c; color: #fff; }
.btn-danger:hover:not(:disabled) { background: #c0392b; }

.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 13px; color: #666; transition: all 0.2s; }
.btn-icon:hover { border-color: #e74c3c; color: #e74c3c; background: #fef5f5; }
.btn-icon.danger:hover { background: #e74c3c; color: #fff; border-color: #e74c3c; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 24px; }
.modal-card { width: 100%; max-width: 480px; padding: 32px; }
.modal-card h2 { font-size: 20px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.modal-card h2 i { color: #e74c3c; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
.form-group input, .form-group select { width: 100%; padding: 12px 14px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; font-family: 'Inter', sans-serif; box-sizing: border-box; }
.form-group input:focus, .form-group select:focus { outline: none; border-color: #e74c3c; }
.form-group.has-error input { border-color: #e74c3c; background: #fef8f8; }
.field-error { display: flex; align-items: center; gap: 6px; margin-top: 6px; font-size: 12px; color: #e74c3c; font-weight: 500; }
.field-error i { font-size: 11px; }
.field-hint { display: block; margin-top: 6px; font-size: 12px; color: #999; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; }

.confirm-modal { text-align: center; }
.confirm-icon { width: 64px; height: 64px; background: #fef5f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
.confirm-icon i { font-size: 28px; color: #e74c3c; }
.confirm-modal p { color: #666; font-size: 14px; margin-bottom: 8px; }

.server-errors { margin-bottom: 12px; }
.server-error { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #fef5f5; border: 1px solid #fdd; border-radius: 6px; color: #c0392b; font-size: 13px; font-weight: 500; margin-bottom: 6px; }

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .header-actions { flex-wrap: wrap; }
  .wingas-grid { grid-template-columns: 1fr; }
}
</style>
