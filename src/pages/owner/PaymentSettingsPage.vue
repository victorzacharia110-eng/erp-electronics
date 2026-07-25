<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-gear" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('paymentSettings.title') }}</h1>
        <p>{{ $t('paymentSettings.subtitle') }}</p>
      </div>
      <router-link to="/owner" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.backToDashboard') }}</router-link>
    </div>

    <SkeletonLoader v-if="loading" type="list" :count="3" />

    <template v-else>
    <div class="settings-grid">
      <div class="card settings-card">
        <div class="setting-row">
          <div class="setting-info">
            <h3><i class="fas fa-globe"></i> {{ $t('paymentSettings.clickpesa') }}</h3>
            <p>{{ $t('paymentSettings.clickpesaDesc') }}</p>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" v-model="clickpesaEnabled" @change="saveClickpesa" />
            <span class="slider"></span>
          </label>
        </div>
        <div class="setting-status">
          <span :class="['status-badge', clickpesaEnabled ? 'active' : 'inactive']">
            <i :class="clickpesaEnabled ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i>
            {{ clickpesaEnabled ? $t('paymentSettings.enabled') : $t('paymentSettings.disabled') }}
          </span>
        </div>
      </div>

      <div class="card settings-card">
        <div class="section-header">
          <div>
            <h3 class="section-title"><i class="fas fa-mobile-screen"></i> {{ $t('paymentSettings.mobileMoneyProviders') }}</h3>
            <p class="section-desc">{{ $t('paymentSettings.manageNumbers') }}</p>
          </div>
          <button class="btn btn-primary btn-sm" @click="showAddForm = !showAddForm">
            <i class="fas" :class="showAddForm ? 'fa-times' : 'fa-plus'"></i>
            {{ showAddForm ? $t('common.cancel') : $t('paymentSettings.addProvider') }}
          </button>
        </div>

        <div class="settings-search" v-if="providers.length > 0 && !showAddForm">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input v-model="search" type="text" :placeholder="$t('common.searchPlaceholder')" />
          </div>
        </div>

        <div v-if="showAddForm" class="add-form">
          <div class="form-row">
            <div class="form-group"><label>{{ $t('paymentSettings.name') }}</label><input v-model="newProvider.name" type="text" :placeholder="$t('paymentSettings.namePlaceholder')" /></div>
            <div class="form-group"><label>{{ $t('paymentSettings.slug') }}</label><input v-model="newProvider.slug" type="text" :placeholder="$t('paymentSettings.slugPlaceholder')" /></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>{{ $t('paymentSettings.phoneNumber') }}</label><input v-model="newProvider.number" type="tel" :placeholder="$t('paymentSettings.phoneNumberPlaceholder')" /></div>
            <div class="form-group"><label>{{ $t('paymentSettings.iconClass') }}</label><input v-model="newProvider.icon" type="text" :placeholder="$t('paymentSettings.iconClassPlaceholder')" /></div>
          </div>
          <button class="btn btn-primary btn-sm" @click="addProvider" :disabled="saving">
            <i class="fas fa-save"></i> {{ saving ? $t('common.saving') : $t('paymentSettings.saveProvider') }}
          </button>
        </div>

        <div class="provider-list">
          <div v-for="p in paginatedProviders" :key="p.id" class="provider-item">
            <div class="provider-left">
              <i :class="p.icon" class="provider-icon"></i>
              <div v-if="editingId !== p.id" class="provider-info">
                <span class="provider-name">{{ p.name }}</span>
                <span class="provider-number">{{ p.number || $t('paymentSettings.noNumber') }}</span>
              </div>
              <div v-else class="provider-info edit-fields">
                <input v-model="editForm.name" type="text" class="edit-input" :placeholder="$t('paymentSettings.name')" />
                <input v-model="editForm.number" type="tel" class="edit-input" :placeholder="$t('paymentSettings.phoneNumber')" />
              </div>
            </div>
            <div class="provider-right">
              <label class="toggle-switch small">
                <input type="checkbox" :checked="p.enabled" @change="toggleEnabled(p)" />
                <span class="slider"></span>
              </label>
              <div v-if="editingId !== p.id" class="provider-actions">
                <button class="action-btn edit" @click="startEdit(p)" :title="$t('common.edit')"><i class="fas fa-pen"></i></button>
                <button class="action-btn delete" @click="deleteProvider(p)" :title="$t('common.delete')"><i class="fas fa-trash"></i></button>
              </div>
              <div v-else class="provider-actions">
                <button class="action-btn save" @click="saveEdit(p)" :title="$t('common.save')"><i class="fas fa-check"></i></button>
                <button class="action-btn cancel" @click="editingId = null" :title="$t('common.cancel')"><i class="fas fa-times"></i></button>
              </div>
            </div>
          </div>
          <p v-if="!providers.length" class="empty-msg">{{ $t('paymentSettings.noProviders') }}</p>
        </div>

        <TablePagination
          v-if="providers.length > 15"
          :current-page="currentPage" :total-pages="totalPages"
          :from="pageInfo.from" :to="pageInfo.to" :total="pageInfo.total"
          :show-all="showAll"
          @page="goToPage" @toggle-all="toggleShowAll"
        />
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
import { useI18n } from 'vue-i18n'
import { settingsApi, paymentProviderApi } from '@/api'
import TablePagination from '@/components/TablePagination.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const { t } = useI18n()
const clickpesaEnabled = ref(false)
const providers = ref([])
const toastMsg = ref('')
const saving = ref(false)
const showAddForm = ref(false)
const editingId = ref(null)
const editForm = ref({ name: '', number: '' })
const newProvider = ref({ name: '', slug: '', number: '', icon: 'fas fa-mobile-screen' })
const search = ref('')
const currentPage = ref(1)
const showAll = ref(false)
const PER_PAGE = 15
const loading = ref(true)

const filteredProviders = computed(() => {
  const q = search.value.toLowerCase().trim()
  if (!q) return providers.value
  return providers.value.filter(p =>
    p.name.toLowerCase().includes(q) ||
    (p.number && p.number.includes(q))
  )
})

const paginatedProviders = computed(() => {
  if (showAll.value) return filteredProviders.value
  const start = (currentPage.value - 1) * PER_PAGE
  return filteredProviders.value.slice(start, start + PER_PAGE)
})

const totalPages = computed(() => Math.ceil(filteredProviders.value.length / PER_PAGE))

const pageInfo = computed(() => {
  const total = filteredProviders.value.length
  if (showAll.value) return { from: 1, to: total, total }
  const from = total === 0 ? 0 : (currentPage.value - 1) * PER_PAGE + 1
  const to = Math.min(currentPage.value * PER_PAGE, total)
  return { from, to, total }
})

function goToPage(p) { currentPage.value = p; showAll.value = false }
function toggleShowAll() { showAll.value = !showAll.value }

function showToast(msg) { toastMsg.value = msg; setTimeout(() => toastMsg.value = '', 3000) }

async function saveClickpesa() {
  try {
    await settingsApi.updatePayment({ clickpesa_enabled: clickpesaEnabled.value })
    showToast(t('paymentSettings.saved'))
  } catch { showToast(t('paymentSettings.saveError')) }
}

async function loadProviders() {
  try {
    const res = await paymentProviderApi.manage()
    providers.value = res.data
  } catch { /* empty */ }
}

async function addProvider() {
  saving.value = true
  try {
    await paymentProviderApi.create(newProvider.value)
    newProvider.value = { name: '', slug: '', number: '', icon: 'fas fa-mobile-screen' }
    showAddForm.value = false
    showToast(t('paymentSettings.providerAdded'))
    await loadProviders()
  } catch (err) {
    showToast(err.response?.data?.message || t('paymentSettings.failedToAdd'))
  } finally { saving.value = false }
}

function startEdit(p) {
  editingId.value = p.id
  editForm.value = { name: p.name, number: p.number || '' }
}

async function saveEdit(p) {
  try {
    await paymentProviderApi.update(p.id, editForm.value)
    editingId.value = null
    showToast(t('paymentSettings.providerUpdated'))
    await loadProviders()
  } catch (err) {
    showToast(err.response?.data?.message || t('paymentSettings.failedToUpdate'))
  }
}

async function toggleEnabled(p) {
  try {
    await paymentProviderApi.update(p.id, { enabled: !p.enabled })
    showToast(`${p.name} ${!p.enabled ? t('paymentSettings.enabled') : t('paymentSettings.disabled')}`)
    await loadProviders()
  } catch { showToast(t('paymentSettings.failedToUpdate')) }
}

async function deleteProvider(p) {
  if (!confirm(t('paymentSettings.confirmDelete', { name: p.name }))) return
  try {
    await paymentProviderApi.delete(p.id)
    showToast(t('paymentSettings.providerDeleted', { name: p.name }))
    await loadProviders()
  } catch { showToast(t('paymentSettings.failedToDelete')) }
}

onMounted(async () => {
  try {
    const res = await settingsApi.getPayment()
    clickpesaEnabled.value = res.data.clickpesa_enabled
  } catch { /* empty */ }
  await loadProviders()
  loading.value = false
})
</script>

<style scoped>
.dashboard-page { padding: 32px 0; }
.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.dash-header h1 { font-size: 26px; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 16px; border: 1px solid #ddd; border-radius: 6px; text-decoration: none; color: #333; font-size: 13px; font-weight: 500; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.settings-grid { display: flex; flex-direction: column; gap: 20px; max-width: 700px; }
.settings-card { padding: 24px; }

.setting-row { display: flex; justify-content: space-between; align-items: center; gap: 24px; }
.setting-info h3 { font-size: 17px; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
.setting-info h3 i { color: #e74c3c; }
.setting-info p { font-size: 13px; color: #888; line-height: 1.5; margin: 0; }
.setting-status { margin-top: 12px; }

.status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 5px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.status-badge.active { background: #eafaf1; color: #27ae60; }
.status-badge.inactive { background: #fef5f5; color: #e74c3c; }

.toggle-switch { position: relative; width: 52px; height: 28px; flex-shrink: 0; cursor: pointer; }
.toggle-switch.small { width: 44px; height: 24px; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: #ddd; border-radius: 28px; transition: all 0.3s; }
.slider::before { content: ''; position: absolute; width: 22px; height: 22px; left: 3px; bottom: 3px; background: #fff; border-radius: 50%; transition: all 0.3s; }
.toggle-switch.small .slider::before { width: 18px; height: 18px; }
.toggle-switch input:checked + .slider { background: #27ae60; }
.toggle-switch input:checked + .slider::before { transform: translateX(24px); }
.toggle-switch.small input:checked + .slider::before { transform: translateX(20px); }

.section-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.section-title { font-size: 17px; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
.section-title i { color: #e74c3c; }
.section-desc { font-size: 13px; color: #888; margin: 0; }

.btn { padding: 10px 16px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s; font-family: inherit; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-sm { padding: 8px 14px; font-size: 12px; }

.add-form { background: #f8f9fa; border: 1px solid #eee; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.form-group { margin-bottom: 0; }
.form-group label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 4px; color: #555; }
.form-group input { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; font-family: inherit; }
.form-group input:focus { outline: none; border-color: #e74c3c; }

.provider-list { display: flex; flex-direction: column; gap: 8px; }
.provider-item { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; background: #f8f9fa; border: 1px solid #eee; border-radius: 8px; transition: border-color 0.2s; }
.provider-item:hover { border-color: #ddd; }

.provider-left { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }
.provider-icon { color: #e74c3c; font-size: 18px; width: 24px; text-align: center; flex-shrink: 0; }
.provider-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.provider-name { font-size: 14px; font-weight: 600; color: #333; }
.provider-number { font-size: 16px; font-weight: 700; color: #2c3e50; letter-spacing: 1px; }

.edit-fields { display: flex; flex-direction: column; gap: 6px; flex: 1; }
.edit-input { padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; font-family: inherit; }
.edit-input:focus { outline: none; border-color: #e74c3c; }

.provider-right { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.provider-actions { display: flex; gap: 4px; }
.action-btn { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 12px; transition: all 0.2s; }
.action-btn.edit { color: #3498db; }
.action-btn.edit:hover { background: #3498db; color: #fff; border-color: #3498db; }
.action-btn.delete { color: #e74c3c; }
.action-btn.delete:hover { background: #e74c3c; color: #fff; border-color: #e74c3c; }
.action-btn.save { color: #27ae60; }
.action-btn.save:hover { background: #27ae60; color: #fff; border-color: #27ae60; }
.action-btn.cancel { color: #888; }
.action-btn.cancel:hover { background: #888; color: #fff; border-color: #888; }

.empty-msg { text-align: center; color: #999; font-size: 14px; padding: 24px; }

@media (max-width: 768px) {
  .form-row { grid-template-columns: 1fr; }
  .provider-item { flex-wrap: wrap; gap: 10px; }
  .provider-right { width: 100%; justify-content: flex-end; }
}

.settings-search { margin-bottom: 16px; }
.search-box { display: flex; align-items: center; gap: 10px; background: #f8f9fa; border: 1px solid #eee; border-radius: 6px; padding: 10px 14px; max-width: 400px; }
.search-box i { color: #999; }
.search-box input { flex: 1; border: none; background: none; font-size: 14px; outline: none; font-family: inherit; }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #2c3e50; color: #fff; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 2000; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); animation: slideUp 0.3s ease; }
.toast i { color: #27ae60; }

@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }
</style>
