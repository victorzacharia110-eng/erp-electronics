<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-truck" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('shippingSettings.title') }}</h1>
        <p>{{ $t('shippingSettings.subtitle') }}</p>
      </div>
      <router-link to="/owner" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.backToDashboard') }}</router-link>
    </div>

    <div class="settings-grid">
      <div class="card settings-card">
        <div class="section-header">
          <div>
            <h3 class="section-title"><i class="fas fa-route"></i> {{ $t('shippingSettings.routes') }}</h3>
          </div>
          <button class="btn btn-primary btn-sm" @click="openAddForm">
            <i class="fas fa-plus"></i> {{ $t('shippingSettings.addRoute') }}
          </button>
        </div>

        <div v-if="showForm" class="add-form">
          <div class="form-row">
            <div class="form-group"><label>{{ $t('shippingSettings.routeName') }}</label><input v-model="form.name" type="text" :placeholder="$t('shippingSettings.routeNamePlaceholder')" /></div>
            <div class="form-group"><label>{{ $t('shippingSettings.baseCost') }} (TSh)</label><input v-model.number="form.base_cost" type="number" min="0" :placeholder="$t('shippingSettings.baseCostPlaceholder')" /></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>{{ $t('shippingSettings.fromCity') }}</label><input v-model="form.from_city" type="text" :placeholder="$t('shippingSettings.fromCityPlaceholder')" /></div>
            <div class="form-group"><label>{{ $t('shippingSettings.toCity') }}</label><input v-model="form.to_city" type="text" :placeholder="$t('shippingSettings.toCityPlaceholder')" /></div>
          </div>

          <div class="rules-section">
            <h4><i class="fas fa-list-ol"></i> {{ $t('shippingSettings.valueRules') }}</h4>
            <div v-for="(rule, idx) in form.value_rules" :key="idx" class="rule-row">
              <div class="form-group"><label>{{ $t('shippingSettings.minValue') }}</label><input v-model.number="rule.min_value" type="number" min="0" :placeholder="$t('shippingSettings.minValuePlaceholder')" /></div>
              <div class="form-group"><label>{{ $t('shippingSettings.maxValue') }}</label><input v-model.number="rule.max_value" type="number" min="0" :placeholder="$t('shippingSettings.maxValuePlaceholder')" /></div>
              <div class="form-group"><label>{{ $t('shippingSettings.shippingCost') }}</label><input v-model.number="rule.adjusted_cost" type="number" min="0" :placeholder="$t('shippingSettings.shippingCostPlaceholder')" /></div>
              <button class="action-btn delete rule-delete" @click="form.value_rules.splice(idx, 1)" :title="$t('common.delete')"><i class="fas fa-trash"></i></button>
            </div>
            <button class="btn btn-outline btn-sm" @click="form.value_rules.push({ min_value: null, max_value: null, adjusted_cost: null })">
              <i class="fas fa-plus"></i> {{ $t('shippingSettings.addRule') }}
            </button>
          </div>

          <div class="form-actions">
            <button class="btn btn-outline btn-sm" @click="cancelForm">{{ $t('common.cancel') }}</button>
            <button class="btn btn-primary btn-sm" @click="saveRoute" :disabled="saving">
              <i class="fas fa-save"></i> {{ saving ? $t('common.saving') : $t('common.save') }}
            </button>
          </div>
        </div>

        <div class="settings-search" v-if="routes.length > 0 && !showForm">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input v-model="search" type="text" :placeholder="$t('common.searchPlaceholder')" />
          </div>
        </div>

        <div class="route-list">
        <SkeletonLoader v-if="loading" type="list" :count="3" />
        <div v-else-if="!routes.length" class="empty-msg">
            <i class="fas fa-route"></i>
            <p>{{ $t('shippingSettings.noRoutes') }}</p>
          </div>
          <div v-else-if="!paginatedRoutes.length" class="empty-msg">
            <i class="fas fa-search"></i>
            <p>{{ $t('common.noResults') }}</p>
          </div>
          <div v-for="route in paginatedRoutes" :key="route.id" class="route-item">
            <div class="route-info">
              <span class="route-name">{{ route.name }}</span>
              <span class="route-cities">
                <i class="fas fa-map-marker-alt"></i> {{ route.from_city }} <i class="fas fa-arrow-right route-arrow"></i> {{ route.to_city }}
              </span>
              <span class="route-base">TSh {{ formatPrice(route.base_cost) }}</span>
            </div>
            <div v-if="route.value_rules && route.value_rules.length" class="route-rules">
              <div v-for="(vr, i) in route.value_rules" :key="i" class="rule-tag">
                {{ vr.min_value != null ? formatPrice(vr.min_value) : '0' }} – {{ vr.max_value != null ? formatPrice(vr.max_value) : $t('shippingSettings.unlimited') }} → TSh {{ vr.adjusted_cost != null ? formatPrice(vr.adjusted_cost) : formatPrice(route.base_cost) }}
              </div>
            </div>
            <div class="route-actions">
              <button class="action-btn edit" @click="editRoute(route)" :title="$t('common.edit')"><i class="fas fa-pen"></i></button>
              <button class="action-btn delete" @click="deleteRoute(route)" :title="$t('common.delete')"><i class="fas fa-trash"></i></button>
            </div>
          </div>
        </div>

        <TablePagination
          v-if="filteredRoutes.length > 15"
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { shippingRuleApi } from '@/api'
import TablePagination from '@/components/TablePagination.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const { t } = useI18n()
const routes = ref([])
const loading = ref(true)
const saving = ref(false)
const showForm = ref(false)
const editingId = ref(null)
const toastMsg = ref('')
const search = ref('')
const currentPage = ref(1)
const showAll = ref(false)
const PER_PAGE = 15

const defaultForm = { name: '', from_city: '', to_city: '', base_cost: 5000, value_rules: [] }
const form = ref({ ...defaultForm })

const filteredRoutes = computed(() => {
  const q = search.value.toLowerCase().trim()
  if (!q) return routes.value
  return routes.value.filter(r =>
    r.name.toLowerCase().includes(q) ||
    r.from_city.toLowerCase().includes(q) ||
    r.to_city.toLowerCase().includes(q)
  )
})

const paginatedRoutes = computed(() => {
  if (showAll.value) return filteredRoutes.value
  const start = (currentPage.value - 1) * PER_PAGE
  return filteredRoutes.value.slice(start, start + PER_PAGE)
})
const totalPages = computed(() => Math.ceil(filteredRoutes.value.length / PER_PAGE))
const pageInfo = computed(() => {
  const total = filteredRoutes.value.length
  if (showAll.value) return { from: 1, to: total, total }
  const from = total === 0 ? 0 : (currentPage.value - 1) * PER_PAGE + 1
  const to = Math.min(currentPage.value * PER_PAGE, total)
  return { from, to, total }
})
function goToPage(p) { currentPage.value = p; showAll.value = false }
function toggleShowAll() { showAll.value = !showAll.value }

function formatPrice(v) { return Number(v).toLocaleString('en-TZ') }

function showToast(msg) { toastMsg.value = msg; setTimeout(() => toastMsg.value = '', 3000) }

function openAddForm() {
  editingId.value = null
  form.value = { ...defaultForm, value_rules: [] }
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  editingId.value = null
  form.value = { ...defaultForm, value_rules: [] }
}

function editRoute(route) {
  editingId.value = route.id
  form.value = {
    name: route.name,
    from_city: route.from_city,
    to_city: route.to_city,
    base_cost: route.base_cost,
    value_rules: (route.value_rules || []).map(r => ({
      min_value: r.min_value,
      max_value: r.max_value,
      adjusted_cost: r.adjusted_cost,
    })),
  }
  showForm.value = true
}

async function loadRoutes() {
  loading.value = true
  try {
    const res = await shippingRuleApi.getAll()
    routes.value = res.data
  } catch { /* empty */ }
  loading.value = false
}

async function saveRoute() {
  saving.value = true
  try {
    const payload = {
      name: form.value.name,
      from_city: form.value.from_city,
      to_city: form.value.to_city,
      base_cost: form.value.base_cost,
      value_rules: form.value.value_rules,
    }
    if (editingId.value) {
      await shippingRuleApi.update(editingId.value, payload)
      showToast(t('shippingSettings.routeUpdated'))
    } else {
      await shippingRuleApi.create(payload)
      showToast(t('shippingSettings.routeAdded'))
    }
    cancelForm()
    await loadRoutes()
  } catch (err) {
    showToast(err.response?.data?.message || t('shippingSettings.addFailed'))
  }
  saving.value = false
}

async function deleteRoute(route) {
  if (!confirm(t('shippingSettings.deleteRouteConfirm'))) return
  try {
    await shippingRuleApi.delete(route.id)
    showToast(t('shippingSettings.routeDeleted'))
    await loadRoutes()
  } catch {
    showToast(t('shippingSettings.deleteFailed'))
  }
}

onMounted(loadRoutes)
</script>

<style scoped>
.dashboard-page { padding: 32px 0; }
.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.dash-header h1 { font-size: 26px; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 16px; border: 1px solid #ddd; border-radius: 6px; text-decoration: none; color: #333; font-size: 13px; font-weight: 500; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.settings-grid { display: flex; flex-direction: column; gap: 20px; max-width: 800px; }
.settings-card { padding: 24px; }

.section-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.section-title { font-size: 17px; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
.section-title i { color: #e74c3c; }

.btn { padding: 10px 16px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s; font-family: inherit; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: #fff; border: 1px solid #ddd; color: #555; }
.btn-outline:hover { border-color: #e74c3c; color: #e74c3c; }
.btn-sm { padding: 8px 14px; font-size: 12px; }

.add-form { background: #f8f9fa; border: 1px solid #eee; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.form-group { margin-bottom: 0; }
.form-group label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 4px; color: #555; }
.form-group input { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; font-family: inherit; }
.form-group input:focus { outline: none; border-color: #e74c3c; }

.rules-section { margin-top: 16px; padding-top: 16px; border-top: 1px solid #eee; }
.rules-section h4 { font-size: 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; color: #555; }
.rules-section h4 i { color: #e74c3c; }
.rule-row { display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 8px; align-items: end; margin-bottom: 8px; }
.rule-delete { align-self: end; margin-bottom: 4px; }

.form-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px; }

.route-list { display: flex; flex-direction: column; gap: 8px; }
.route-item { display: flex; flex-direction: column; gap: 6px; padding: 16px; background: #f8f9fa; border: 1px solid #eee; border-radius: 8px; transition: border-color 0.2s; }
.route-item:hover { border-color: #ddd; }

.route-info { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.route-name { font-weight: 600; font-size: 14px; color: #333; }
.route-cities { font-size: 13px; color: #888; display: flex; align-items: center; gap: 6px; }
.route-cities i { color: #e74c3c; font-size: 11px; }
.route-arrow { font-size: 10px; color: #ccc; }
.route-base { margin-left: auto; font-weight: 700; color: #e74c3c; font-size: 15px; }

.route-rules { display: flex; flex-wrap: wrap; gap: 6px; }
.rule-tag { font-size: 11px; background: #eaf4ff; color: #2980b9; padding: 4px 10px; border-radius: 12px; font-weight: 500; }

.route-actions { display: flex; gap: 4px; }
.action-btn { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 12px; transition: all 0.2s; }
.action-btn.edit { color: #3498db; }
.action-btn.edit:hover { background: #3498db; color: #fff; border-color: #3498db; }
.action-btn.delete { color: #e74c3c; }
.action-btn.delete:hover { background: #e74c3c; color: #fff; border-color: #e74c3c; }

.loading-msg, .empty-msg { text-align: center; color: #999; font-size: 14px; padding: 32px 16px; }
.empty-msg i { font-size: 28px; color: #ddd; margin-bottom: 12px; display: block; }
.empty-msg p { margin: 0; }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #2c3e50; color: #fff; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 2000; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); animation: slideUp 0.3s ease; }
.toast i { color: #27ae60; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

@media (max-width: 768px) {
  .form-row, .rule-row { grid-template-columns: 1fr; }
}

.settings-search { margin-bottom: 16px; }
.search-box { display: flex; align-items: center; gap: 10px; background: #f8f9fa; border: 1px solid #eee; border-radius: 6px; padding: 10px 14px; max-width: 400px; }
.search-box i { color: #999; }
.search-box input { flex: 1; border: none; background: none; font-size: 14px; outline: none; font-family: inherit; }
</style>
