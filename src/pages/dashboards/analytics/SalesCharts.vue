<template>
  <div class="sales-charts">
    <div class="charts-header">
      <h2><i class="fas fa-chart-line"></i> {{ $t('analytics.salesOverview') }}</h2>
      <div class="chart-controls">
        <select v-model="selectedPeriod" class="period-select">
          <option value="6">6 {{ $t('analytics.months') }}</option>
          <option value="12">12 {{ $t('analytics.months') }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="chart-loading"><i class="fas fa-spinner fa-spin"></i> {{ $t('common.loading') }}</div>

    <div v-else class="charts-grid">
      <div class="chart-card card">
        <h3><i class="fas fa-coins"></i> {{ $t('analytics.revenueVsProfit') }}</h3>
        <div class="chart-wrap">
          <Bar v-if="revenueChartReady" :data="revenueChartData" :options="barOptions" />
        </div>
      </div>

      <div class="chart-card card">
        <h3><i class="fas fa-shopping-bag"></i> {{ $t('analytics.ordersTrend') }}</h3>
        <div class="chart-wrap">
          <Line v-if="ordersChartReady" :data="ordersChartData" :options="lineOptions" />
        </div>
      </div>

      <div class="chart-card card">
        <h3><i class="fas fa-boxes-stacked"></i> {{ $t('analytics.itemsSold') }}</h3>
        <div class="chart-wrap">
          <Bar v-if="itemsChartReady" :data="itemsChartData" :options="barOptions" />
        </div>
      </div>

      <div class="chart-card card">
        <h3><i class="fas fa-tags"></i> {{ $t('analytics.categoryRevenue') }}</h3>
        <div class="chart-wrap">
          <Doughnut v-if="categoryChartReady" :data="categoryChartData" :options="doughnutOptions" />
        </div>
      </div>
    </div>

    <div class="summary-cards" v-if="summary">
      <div class="mini-stat">
        <span class="mini-val">TSh {{ formatPrice(summary.total_revenue) }}</span>
        <span class="mini-label">{{ $t('analytics.totalRevenue') }}</span>
      </div>
      <div class="mini-stat">
        <span class="mini-val profit">TSh {{ formatPrice(summary.total_profit) }}</span>
        <span class="mini-label">{{ $t('analytics.totalProfit') }}</span>
      </div>
      <div class="mini-stat">
        <span class="mini-val">{{ summary.total_orders }}</span>
        <span class="mini-label">{{ $t('analytics.totalOrders') }}</span>
      </div>
      <div class="mini-stat">
        <span class="mini-val">{{ summary.profit_margin }}%</span>
        <span class="mini-label">{{ $t('analytics.profitMargin') }}</span>
      </div>
      <div class="mini-stat">
        <span class="mini-val" :class="summary.revenue_growth >= 0 ? 'growth-pos' : 'growth-neg'">
          {{ summary.revenue_growth >= 0 ? '+' : '' }}{{ summary.revenue_growth }}%
        </span>
        <span class="mini-label">{{ $t('analytics.revenueGrowth') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Bar, Line, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, ArcElement, Tooltip, Legend, Filler
} from 'chart.js'
import { analyticsApi } from '@/api'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Tooltip, Legend, Filler)

const emit = defineEmits(['loaded'])

const loading = ref(true)
const selectedPeriod = ref('12')
const monthlyData = ref([])
const categoryData = ref([])
const summary = ref(null)

const revenueChartReady = computed(() => monthlyData.value.length > 0)
const ordersChartReady = computed(() => monthlyData.value.length > 0)
const itemsChartReady = computed(() => monthlyData.value.length > 0)
const categoryChartReady = computed(() => categoryData.value.length > 0)

const labels = computed(() => monthlyData.value.map(d => d.label))

const revenueChartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: 'Revenue',
      data: monthlyData.value.map(d => d.revenue),
      backgroundColor: 'rgba(231, 76, 60, 0.8)',
      borderRadius: 4,
    },
    {
      label: 'Profit',
      data: monthlyData.value.map(d => d.profit),
      backgroundColor: 'rgba(39, 174, 96, 0.8)',
      borderRadius: 4,
    },
  ],
}))

const ordersChartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: 'Orders',
      data: monthlyData.value.map(d => d.order_count),
      borderColor: '#3498db',
      backgroundColor: 'rgba(52, 152, 219, 0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 4,
      pointBackgroundColor: '#3498db',
    },
    {
      label: 'Cancelled',
      data: monthlyData.value.map(d => d.cancelled_count),
      borderColor: '#e74c3c',
      backgroundColor: 'rgba(231, 76, 60, 0.1)',
      fill: true,
      tension: 0.3,
      pointRadius: 4,
      pointBackgroundColor: '#e74c3c',
    },
  ],
}))

const itemsChartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: 'Items Sold',
      data: monthlyData.value.map(d => d.items_sold),
      backgroundColor: 'rgba(155, 89, 182, 0.8)',
      borderRadius: 4,
    },
  ],
}))

const categoryChartData = computed(() => {
  const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#34495e']
  return {
    labels: categoryData.value.map(c => c.category),
    datasets: [{
      data: categoryData.value.map(c => c.revenue),
      backgroundColor: colors.slice(0, categoryData.value.length),
    }],
  }
})

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'top', labels: { font: { size: 11 } } } },
  scales: {
    y: { beginAtZero: true, ticks: { callback: v => v >= 1000000 ? (v / 1000000).toFixed(1) + 'M' : v >= 1000 ? (v / 1000).toFixed(0) + 'K' : v } },
    x: { ticks: { font: { size: 10 }, maxRotation: 45 } },
  },
}

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'top', labels: { font: { size: 11 } } } },
  scales: {
    y: { beginAtZero: true },
    x: { ticks: { font: { size: 10 }, maxRotation: 45 } },
  },
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'right', labels: { font: { size: 11 } } } },
}

function formatPrice(v) { return Number(v || 0).toLocaleString('en-TZ') }

async function loadData() {
  loading.value = true
  try {
    const res = await analyticsApi.getSales(parseInt(selectedPeriod.value))
    monthlyData.value = res.data.monthly || []
    categoryData.value = res.data.category_breakdown || []
    summary.value = res.data.summary || null
    emit('loaded', res.data)
  } catch { /* empty */ }
  loading.value = false
}

watch(selectedPeriod, loadData)
onMounted(loadData)
</script>

<style scoped>
.sales-charts {
  margin-bottom: 32px;
}

.charts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.charts-header h2 {
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.charts-header h2 i {
  color: #e74c3c;
}

.period-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  font-family: inherit;
  background: #fff;
  cursor: pointer;
}

.period-select:focus {
  outline: none;
  border-color: #e74c3c;
}

.chart-loading {
  text-align: center;
  padding: 60px 20px;
  color: #888;
}

.chart-loading i {
  color: #e74c3c;
  margin-right: 8px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  padding: 20px;
}

.chart-card h3 {
  font-size: 15px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #333;
}

.chart-card h3 i {
  color: #e74c3c;
  font-size: 14px;
}

.chart-wrap {
  height: 260px;
  position: relative;
}

.summary-cards {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.mini-stat {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px 20px;
  flex: 1;
  min-width: 140px;
  text-align: center;
}

.mini-val {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
}

.mini-val.profit {
  color: #27ae60;
}

.mini-val.growth-pos {
  color: #27ae60;
}

.mini-val.growth-neg {
  color: #e74c3c;
}

.mini-label {
  font-size: 12px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .summary-cards {
    flex-direction: column;
  }
}
</style>
