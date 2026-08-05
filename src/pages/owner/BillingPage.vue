<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-credit-card" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('billing.title') }}</h1>
        <p>{{ $t('billing.subtitle') }}</p>
      </div>
      <router-link to="/owner" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.backToDashboard') }}</router-link>
    </div>

    <SkeletonLoader v-if="loading" type="list" :count="3" />

    <template v-else>
      <div class="card current-card">
        <div class="current-info">
          <div>
            <h3><i class="fas fa-gem" style="color: #e74c3c;"></i> {{ $t('billing.currentPlan') }}</h3>
            <p class="current-plan-name">{{ currentPlanName }}</p>
          </div>
          <span :class="['status-badge', `status-${current?.subscription_status || 'none'}`]">{{ currentStatusLabel }}</span>
        </div>
        <div class="current-details">
          <div class="detail-item"><span class="detail-label">{{ $t('billing.expires') }}</span><span class="detail-value">{{ expiresLabel }}</span></div>
          <div class="detail-item"><span class="detail-label">{{ $t('billing.productsLimit') }}</span><span class="detail-value">{{ current?.max_products ?? '—' }}</span></div>
          <div class="detail-item"><span class="detail-label">{{ $t('billing.employeesLimit') }}</span><span class="detail-value">{{ current?.max_employees ?? '—' }}</span></div>
        </div>
      </div>

      <div class="section">
        <div class="section-header">
          <div>
            <h3 class="section-title"><i class="fas fa-box-open" style="color: #e74c3c;"></i> {{ $t('billing.choosePlan') }}</h3>
            <p class="section-desc">{{ $t('billing.choosePlanDesc') }}</p>
          </div>
        </div>
        <div class="plans-grid">
          <div v-for="key in planKeys" :key="key" :class="['plan-card', { selected: selectedPlan === key, current: isCurrentPlan(key) }]">
            <div class="plan-head">
              <span class="plan-name">{{ planName(key) }}</span>
              <span v-if="isCurrentPlan(key)" class="plan-current">{{ $t('billing.current') }}</span>
            </div>
            <div class="plan-price">
              <span class="price">{{ formatPrice(plans[key]?.price_monthly) }}</span>
              <span class="per-month">{{ $t('billing.perMonth') }}</span>
            </div>
            <ul class="plan-features">
              <li><i class="fas fa-check"></i> {{ $t('billing.maxProductsLabel', { count: plans[key]?.max_products }) }}</li>
              <li><i class="fas fa-check"></i> {{ $t('billing.maxEmployeesLabel', { count: plans[key]?.max_employees }) }}</li>
            </ul>
            <button v-if="!isCurrentPlan(key) && key !== 'free'" class="btn btn-primary btn-block" @click="selectPlan(key)">
              {{ $t('billing.select') }}
            </button>
            <span v-else-if="key === 'free'" class="free-note">{{ $t('billing.freeNote') }}</span>
            <span v-else class="plan-current-btn">{{ $t('billing.current') }}</span>
          </div>
        </div>
      </div>

      <div v-if="selectedPlan && selectedPlan !== 'free'" class="card payment-card">
        <h3 class="section-title"><i class="fas fa-wallet" style="color: #e74c3c;"></i> {{ $t('billing.paymentDetails') }}</h3>
        <div class="form-row">
          <div class="form-group">
            <label>{{ $t('billing.billingPeriod') }}</label>
            <div class="month-chips">
              <button v-for="m in monthsOptions" :key="m" :class="['month-chip', { active: selectedMonths === m }]" @click="selectedMonths = m">
                {{ m }} {{ $t('billing.monthsShort') }}
              </button>
            </div>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>{{ $t('billing.paymentMethod') }}</label>
            <div class="provider-chips">
              <button v-for="p in providers" :key="p.id" :class="['provider-chip', { active: selectedProvider === p.slug }]" @click="selectedProvider = p.slug">
                <i :class="p.icon || 'fas fa-mobile-screen'"></i> {{ p.name }}
              </button>
              <p v-if="!providers.length" class="empty-msg">{{ $t('billing.noProviders') }}</p>
            </div>
          </div>
        </div>
        <div v-if="needsPhone" class="form-row">
          <div class="form-group">
            <label>{{ $t('billing.phoneNumber') }}</label>
            <PhoneInput v-model="phoneNumber" name="phone_number" placeholder="7XX XXX XXX" />
          </div>
        </div>
        <div class="total-row">
          <span class="total-label">{{ $t('billing.totalDue') }}</span>
          <span class="total-value">TSh {{ formatPrice(totalDue) }}</span>
        </div>
        <button class="btn btn-primary btn-lg" :disabled="paying" @click="payNow">
          <i class="fas fa-check-circle"></i> {{ paying ? $t('common.saving') : $t('billing.payNow') }}
        </button>
        <p class="hint">{{ $t('billing.payHint') }}</p>
      </div>

      <div class="card">
        <div class="section-header">
          <div>
            <h3 class="section-title"><i class="fas fa-clock-rotate-left" style="color: #e74c3c;"></i> {{ $t('billing.history') }}</h3>
            <p class="section-desc">{{ $t('billing.historyDesc') }}</p>
          </div>
        </div>
        <div v-if="history.length" class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>{{ $t('billing.date') }}</th>
                <th>{{ $t('billing.plan') }}</th>
                <th>{{ $t('billing.period') }}</th>
                <th>{{ $t('billing.provider') }}</th>
                <th>{{ $t('billing.amount') }}</th>
                <th>{{ $t('billing.status') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="h in history" :key="h.id">
                <td>{{ formatDate(h.created_at) }}</td>
                <td>{{ planName(h.plan) }}</td>
                <td>{{ h.months }} {{ $t('billing.monthsShort') }}</td>
                <td>{{ providerName(h.provider) }}</td>
                <td>TSh {{ formatPrice(h.amount) }}</td>
                <td><span :class="['status-badge', `status-${h.status}`]">{{ paymentStatusLabel(h.status) }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="empty-msg">{{ $t('billing.noPayments') }}</p>
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
import { subscriptionApi, paymentProviderApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import PhoneInput from '@/components/PhoneInput.vue'

const { t } = useI18n()

const loading = ref(true)
const current = ref(null)
const plans = ref({})
const monthsOptions = ref([1, 3, 6, 12])
const providers = ref([])
const selectedPlan = ref(null)
const selectedMonths = ref(3)
const selectedProvider = ref(null)
const phoneNumber = ref('')
const history = ref([])
const paying = ref(false)
const toastMsg = ref('')

const planKeys = computed(() => ['free', 'starter', 'pro', 'enterprise'].filter(k => plans.value[k]))

function cap(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : ''
}

function planName(key) {
  const map = { free: t('billing.free'), starter: t('billing.starter'), pro: t('billing.pro'), enterprise: t('billing.enterprise') }
  return map[key] || key
}

function providerName(slug) {
  const p = providers.value.find(x => x.slug === slug)
  return p ? p.name : slug
}

function paymentStatusLabel(s) {
  return t(`billing.status${cap(s)}`)
}

const currentPlanName = computed(() => planName(current.value?.subscription_plan))
const currentStatusLabel = computed(() => t(`billing.status${cap(current.value?.subscription_status || 'none')}`))

const expiresLabel = computed(() => {
  if (!current.value?.subscription_expires_at) return t('billing.expiresNever')
  return new Date(current.value.subscription_expires_at).toLocaleDateString()
})

const needsPhone = computed(() => ['mpesa', 'airtel', 'mixx_by_yas', 'halopesa'].includes(selectedProvider.value))

const totalDue = computed(() => {
  if (!selectedPlan.value || selectedPlan.value === 'free' || !plans.value[selectedPlan.value]) return 0
  return Number(plans.value[selectedPlan.value].price_monthly) * selectedMonths.value
})

function isCurrentPlan(key) {
  return current.value?.subscription_plan === key && current.value?.subscription_status === 'active'
}

function selectPlan(key) {
  selectedPlan.value = key
  if (key === 'free' || selectedProvider.value) return
  if (providers.value.length) selectedProvider.value = providers.value[0].slug
}

function formatPrice(v) { return Number(v || 0).toLocaleString('en-TZ') }
function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }
function showToast(msg) { toastMsg.value = msg; setTimeout(() => toastMsg.value = '', 4000) }

async function payNow() {
  if (!selectedPlan.value || selectedPlan.value === 'free') return
  if (!selectedProvider.value) { showToast(t('billing.chooseProvider')); return }
  if (needsPhone.value && !phoneNumber.value.trim()) { showToast(t('billing.enterPhone')); return }
  paying.value = true
  try {
    const res = await subscriptionApi.pay({
      plan: selectedPlan.value,
      months: selectedMonths.value,
      provider: selectedProvider.value,
      phone_number: needsPhone.value ? phoneNumber.value.trim() : null,
    })
    showToast(res.data.message || t('billing.paymentInitiated'))
    await loadData()
    if (res.data.activated) {
      selectedPlan.value = null
      phoneNumber.value = ''
    }
  } catch (err) {
    showToast(err.response?.data?.message || t('billing.paymentFailed'))
  } finally { paying.value = false }
}

async function loadData() {
  const [plansRes, historyRes] = await Promise.all([subscriptionApi.getPlans(), subscriptionApi.getHistory()])
  current.value = plansRes.data.current
  plans.value = plansRes.data.plans
  monthsOptions.value = plansRes.data.months_options || [1, 3, 6, 12]
  history.value = historyRes.data || []
}

onMounted(async () => {
  try {
    await Promise.all([
      loadData(),
      paymentProviderApi.getEnabled().then(r => providers.value = r.data).catch(() => {}),
    ])
    if (providers.value.length) selectedProvider.value = providers.value[0].slug
  } catch { /* empty */ }
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

.current-card { padding: 24px; margin-bottom: 24px; }
.current-info { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.current-info h3 { font-size: 17px; display: flex; align-items: center; gap: 8px; }
.current-plan-name { font-size: 22px; font-weight: 700; color: #2c3e50; margin: 8px 0 0; }
.current-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
.detail-item { background: #f8f9fa; border: 1px solid #eee; border-radius: 8px; padding: 12px 14px; display: flex; flex-direction: column; gap: 4px; }
.detail-label { font-size: 12px; color: #888; }
.detail-value { font-size: 16px; font-weight: 700; color: #2c3e50; }

.status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 5px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.status-active, .status-completed { background: #eafaf1; color: #27ae60; }
.status-trial { background: #eef4fd; color: #3498db; }
.status-suspended { background: #fef5f5; color: #e74c3c; }
.status-expired { background: #f6f6f6; color: #888; }
.status-pending { background: #fef9e7; color: #d4ac0d; }
.status-failed, .status-none { background: #fef5f5; color: #e74c3c; }

.section { margin-bottom: 24px; }
.section-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.section-title { font-size: 17px; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
.section-desc { font-size: 13px; color: #888; margin: 0; }

.plans-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
.plan-card { border: 2px solid #eee; border-radius: 12px; padding: 20px; background: #fff; display: flex; flex-direction: column; gap: 12px; transition: all 0.2s; }
.plan-card:hover { border-color: #e74c3c; transform: translateY(-2px); }
.plan-card.selected { border-color: #e74c3c; box-shadow: 0 6px 20px rgba(231, 76, 60, 0.12); }
.plan-card.current { border-color: #27ae60; }
.plan-head { display: flex; justify-content: space-between; align-items: center; }
.plan-name { font-size: 16px; font-weight: 700; }
.plan-current { background: #eafaf1; color: #27ae60; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 20px; }
.plan-current-btn { text-align: center; font-size: 12px; color: #27ae60; font-weight: 600; }
.plan-price { display: flex; align-items: baseline; gap: 6px; }
.price { font-size: 26px; font-weight: 800; color: #2c3e50; }
.per-month { font-size: 12px; color: #888; }
.plan-features { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.plan-features li { font-size: 13px; color: #555; display: flex; align-items: center; gap: 8px; }
.plan-features i { color: #27ae60; }
.free-note { text-align: center; font-size: 12px; color: #888; }
.btn-block { width: 100%; }

.payment-card { padding: 24px; margin-bottom: 24px; }
.form-row { margin-bottom: 16px; }
.form-group label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 8px; color: #555; }
.form-group input { width: 100%; max-width: 360px; padding: 10px 14px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; font-family: inherit; }
.form-group input:focus { outline: none; border-color: #e74c3c; }

.month-chips, .provider-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.month-chip, .provider-chip { padding: 9px 16px; border: 1px solid #ddd; border-radius: 8px; background: #fff; cursor: pointer; font-size: 13px; font-weight: 600; font-family: inherit; color: #333; transition: all 0.2s; display: inline-flex; align-items: center; gap: 6px; }
.month-chip:hover, .provider-chip:hover { border-color: #e74c3c; }
.month-chip.active, .provider-chip.active { background: #e74c3c; border-color: #e74c3c; color: #fff; }

.total-row { display: flex; justify-content: space-between; align-items: center; padding: 16px 0; border-top: 1px solid #eee; margin: 8px 0 16px; }
.total-label { font-size: 14px; font-weight: 600; color: #555; }
.total-value { font-size: 24px; font-weight: 800; color: #e74c3c; }
.btn-lg { padding: 12px 28px; font-size: 14px; }
.hint { font-size: 12px; color: #888; margin-top: 10px; }

.btn { padding: 10px 16px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s; font-family: inherit; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th, .data-table td { padding: 12px 14px; text-align: left; border-bottom: 1px solid #eee; }
.data-table th { color: #888; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.4px; }
.data-table tbody tr:hover { background: #fafafa; }

.empty-msg { text-align: center; color: #999; font-size: 14px; padding: 24px; }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #2c3e50; color: #fff; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 2000; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); animation: slideUp 0.3s ease; }
.toast i { color: #27ae60; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

@media (max-width: 768px) {
  .plans-grid { grid-template-columns: 1fr; }
  .dash-header { flex-direction: column; align-items: flex-start; gap: 12px; }
}
</style>
