<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-chart-line" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('reports.title') }}</h1>
        <p>{{ $t('reports.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-outline" @click="printReport"><i class="fas fa-print"></i> {{ $t('reports.printReport') }}</button>
        <router-link to="/owner" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.back') }}</router-link>
      </div>
    </div>

    <div class="date-nav">
      <button class="nav-btn" @click="prevDay"><i class="fas fa-chevron-left"></i></button>
      <input type="date" v-model="selectedDate" @change="loadReport" class="date-input" />
      <button class="nav-btn" @click="nextDay"><i class="fas fa-chevron-right"></i></button>
      <button class="today-btn" @click="goToday">{{ $t('reports.today') }}</button>
    </div>

    <SkeletonLoader v-if="loading" type="stats" :count="6" />

    <template v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon revenue"><i class="fas fa-dollar-sign"></i></div>
          <div><span class="stat-value">TSh {{ formatPrice(report.total_revenue) }}</span><span class="stat-label">{{ $t('reports.revenue') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orders"><i class="fas fa-shopping-bag"></i></div>
          <div><span class="stat-value">{{ report.total_orders }}</span><span class="stat-label">{{ $t('reports.totalOrders') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon paid"><i class="fas fa-check-circle"></i></div>
          <div><span class="stat-value">{{ report.paid_orders }}</span><span class="stat-label">{{ $t('reports.paid') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon pending"><i class="fas fa-clock"></i></div>
          <div><span class="stat-value">{{ report.pending_orders }}</span><span class="stat-label">{{ $t('reports.processing') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon cancelled"><i class="fas fa-times-circle"></i></div>
          <div><span class="stat-value">{{ report.cancelled_orders }}</span><span class="stat-label">{{ $t('reports.cancelled') }}</span></div>
        </div>
        <div class="stat-card">
          <div class="stat-icon items"><i class="fas fa-box"></i></div>
          <div><span class="stat-value">{{ report.total_items_sold }}</span><span class="stat-label">{{ $t('reports.itemsSold') }}</span></div>
        </div>
      </div>

      <div class="report-grid">
        <div class="card report-section">
          <h2><i class="fas fa-users"></i> {{ $t('reports.employeePerformance') }}</h2>
          <div v-if="!report.employee_stats?.length" class="empty-mini">
            <p>{{ $t('reports.noEmployeeSales') }}</p>
          </div>
          <div v-else class="emp-list">
            <div v-for="(emp, idx) in report.employee_stats" :key="idx" class="emp-row">
              <div class="emp-avatar">{{ emp.name?.charAt(0) || '?' }}</div>
              <div class="emp-info">
                <span class="emp-name">{{ emp.name }}</span>
                <span class="emp-email">{{ emp.email }}</span>
              </div>
              <div class="emp-stats">
                <span class="emp-orders">{{ emp.orders_handled }} {{ $t('reports.ordersHandled') }}</span>
                <span class="emp-revenue">TSh {{ formatPrice(emp.revenue_collected) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="card report-section">
          <h2><i class="fas fa-trophy"></i> {{ $t('reports.topProducts') }}</h2>
          <div v-if="!report.top_products?.length" class="empty-mini">
            <p>{{ $t('reports.noTopProducts') }}</p>
          </div>
          <div v-else class="product-list">
            <div v-for="(prod, idx) in report.top_products" :key="idx" class="product-row">
              <span class="prod-rank">#{{ idx + 1 }}</span>
              <span class="prod-name">{{ prod.name }}</span>
              <span class="prod-qty">{{ prod.quantity_sold }} {{ $t('reports.unitsSold') }}</span>
              <span class="prod-revenue">TSh {{ formatPrice(prod.revenue) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card report-section" id="printable-report">
        <h2><i class="fas fa-calendar-day"></i> {{ $t('reports.summaryFor') }} {{ formatDateFull(selectedDate) }}</h2>
        <div class="print-summary">
          <div class="print-row"><span>{{ $t('reports.revenue') }}</span><span>TSh {{ formatPrice(report.total_revenue) }}</span></div>
          <div class="print-row"><span>{{ $t('reports.totalOrders') }}</span><span>{{ report.total_orders }}</span></div>
          <div class="print-row"><span>{{ $t('reports.paid') }}</span><span>{{ report.paid_orders }}</span></div>
          <div class="print-row"><span>{{ $t('reports.processing') }}</span><span>{{ report.pending_orders }}</span></div>
          <div class="print-row"><span>{{ $t('reports.cancelled') }}</span><span>{{ report.cancelled_orders }}</span></div>
          <div class="print-row"><span>{{ $t('reports.itemsSold') }}</span><span>{{ report.total_items_sold }}</span></div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { reportApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const router = useRouter()
const authStore = useAuthStore()
const selectedDate = ref(new Date().toISOString().split('T')[0])
const report = ref({})
const loading = ref(true)

function formatPrice(v) { return Number(v).toLocaleString('en-TZ') }
function formatDateFull(d) { return new Date(d + 'T00:00:00').toLocaleDateString('en-TZ', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }) }

function prevDay() {
  const d = new Date(selectedDate.value)
  d.setDate(d.getDate() - 1)
  selectedDate.value = d.toISOString().split('T')[0]
  loadReport()
}

function nextDay() {
  const d = new Date(selectedDate.value)
  d.setDate(d.getDate() + 1)
  selectedDate.value = d.toISOString().split('T')[0]
  loadReport()
}

function goToday() {
  selectedDate.value = new Date().toISOString().split('T')[0]
  loadReport()
}

async function loadReport() {
  loading.value = true
  try {
    const res = await reportApi.getDaily(selectedDate.value)
    report.value = res.data
  } catch { /* empty */ }
  loading.value = false
}

function printReport() {
  window.print()
}

onMounted(async () => {
  await authStore.fetchProfile()
  if (authStore.user?.role !== 'owner') {
    router.push('/employee')
    return
  }
  await loadReport()
})
</script>

<style scoped>
.dashboard-page { padding: 32px 0; }
.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.dash-header h1 { font-size: 26px; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 16px; border: 1px solid #ddd; border-radius: 6px; text-decoration: none; color: #333; font-size: 13px; font-weight: 500; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }
.btn-outline { padding: 10px 16px; border: 1px solid #ddd; border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 6px; transition: all 0.2s; }
.btn-outline:hover { border-color: #e74c3c; color: #e74c3c; }

.date-nav { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
.nav-btn { width: 40px; height: 40px; border-radius: 8px; border: 1px solid #ddd; background: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.nav-btn:hover { border-color: #e74c3c; color: #e74c3c; }
.date-input { padding: 10px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; font-family: inherit; cursor: pointer; }
.date-input:focus { outline: none; border-color: #e74c3c; }
.today-btn { padding: 10px 20px; border: 1px solid #e74c3c; border-radius: 8px; background: #fff; color: #e74c3c; font-weight: 600; cursor: pointer; font-size: 13px; transition: all 0.2s; }
.today-btn:hover { background: #e74c3c; color: #fff; }

.stats-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 20px; display: flex; align-items: center; gap: 14px; }
.stat-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.stat-icon.revenue { background: #eafaf1; color: #27ae60; }
.stat-icon.orders { background: #eaf4ff; color: #2980b9; }
.stat-icon.paid { background: #eafaf1; color: #27ae60; }
.stat-icon.pending { background: #fff3cd; color: #856404; }
.stat-icon.cancelled { background: #fef5f5; color: #e74c3c; }
.stat-icon.items { background: #f0e6ff; color: #8e44ad; }
.stat-value { display: block; font-size: 20px; font-weight: 700; color: #333; }
.stat-label { font-size: 12px; color: #888; }

.report-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
.report-section { padding: 24px; }
.report-section h2 { font-size: 17px; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.report-section h2 i { color: #e74c3c; }
.empty-mini { text-align: center; padding: 32px 16px; color: #999; font-size: 14px; }
.empty-mini p { margin: 0; }

.emp-list { display: flex; flex-direction: column; gap: 10px; }
.emp-row { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: #f8f9fa; border-radius: 8px; }
.emp-avatar { width: 40px; height: 40px; border-radius: 50%; background: #e74c3c; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; flex-shrink: 0; }
.emp-info { flex: 1; }
.emp-name { display: block; font-weight: 600; font-size: 14px; }
.emp-email { display: block; font-size: 12px; color: #888; }
.emp-stats { text-align: right; }
.emp-orders { display: block; font-size: 12px; color: #666; }
.emp-revenue { display: block; font-weight: 700; color: #27ae60; font-size: 14px; }

.product-list { display: flex; flex-direction: column; gap: 8px; }
.product-row { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: #f8f9fa; border-radius: 8px; font-size: 14px; }
.prod-rank { font-weight: 700; color: #e74c3c; min-width: 28px; }
.prod-name { flex: 1; font-weight: 500; }
.prod-qty { color: #888; font-size: 13px; min-width: 60px; text-align: right; }
.prod-revenue { font-weight: 600; color: #27ae60; min-width: 100px; text-align: right; }

.print-summary { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.print-row { display: flex; justify-content: space-between; padding: 10px 16px; background: #f8f9fa; border-radius: 6px; font-size: 14px; }
.print-row span:first-child { color: #666; }
.print-row span:last-child { font-weight: 700; color: #333; }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .report-grid { grid-template-columns: 1fr; }
  .dash-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .date-nav { gap: 8px; }
  .date-input { padding: 8px 12px; font-size: 13px; }
  .print-summary { grid-template-columns: 1fr; }
  .product-row { gap: 8px; }
  .prod-qty, .prod-revenue { min-width: auto; }
}

@media print {
  .dash-header, .date-nav, .stats-grid, .report-grid, .back-btn, .btn-outline { display: none !important; }
  .dashboard-page { padding: 0; }
  #printable-report { border: none; box-shadow: none; }
}
</style>
