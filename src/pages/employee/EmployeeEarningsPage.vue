<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-coins" style="color: #e74c3c; margin-right: 12px;"></i>My Earnings</h1>
        <p>Track your commission earnings and payout history</p>
      </div>
      <router-link to="/employee" class="back-btn"><i class="fas fa-arrow-left"></i> Back to Dashboard</router-link>
    </div>

    <SkeletonLoader v-if="loading" type="stats" :count="4" />

    <template v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon sales"><i class="fas fa-chart-line"></i></div>
          <div>
            <span class="stat-value">TSh {{ formatPrice(data.total_profit) }}</span>
            <span class="stat-label">Total Profit Generated</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orders"><i class="fas fa-receipt"></i></div>
          <div>
            <span class="stat-value">{{ data.total_orders }}</span>
            <span class="stat-label">Total Orders</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon pending"><i class="fas fa-hourglass-half"></i></div>
          <div>
            <span class="stat-value">TSh {{ formatPrice(data.pending_total) }}</span>
            <span class="stat-label">Pending Commission</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon paid"><i class="fas fa-check-circle"></i></div>
          <div>
            <span class="stat-value">TSh {{ formatPrice(data.paid_total) }}</span>
            <span class="stat-label">Paid Commission</span>
          </div>
        </div>
      </div>

      <div class="card table-section">
        <div class="section-header-row">
          <h2><i class="fas fa-clock"></i> Recent Commissions</h2>
        </div>

        <div v-if="data.recent.length === 0" class="empty-mini">
          <i class="fas fa-inbox"></i>
          <p>No commissions recorded yet</p>
        </div>

        <div v-else class="table-wrap">
          <table class="sa-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Order</th>
                <th>Sale Amount</th>
                <th>Rate</th>
                <th>Commission</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in data.recent" :key="item.id">
                <td>{{ formatDate(item.created_at) }}</td>
                <td><span class="order-link">{{ item.order?.order_number || '—' }}</span></td>
                <td>TSh {{ formatPrice(item.profit_amount) }}</td>
                <td>{{ item.commission_rate }}%</td>
                <td class="commission-amount">TSh {{ formatPrice(item.commission_amount) }}</td>
                <td><span :class="['status-badge', `status-${item.status}`]">{{ item.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { commissionApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const loading = ref(true)
const data = reactive({
  pending_total: 0,
  paid_total: 0,
  total_sales: 0,
  total_orders: 0,
  recent: [],
})

function formatPrice(v) {
  return Number(v).toLocaleString('en-TZ')
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-TZ', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(async () => {
  try {
    const res = await commissionApi.getMyEarnings()
    const d = res.data
    data.pending_total = d.pending_total || 0
    data.paid_total = d.paid_total || 0
    data.total_sales = d.total_sales || 0
    data.total_orders = d.total_orders || 0
    data.recent = d.recent || []
  } catch { /* empty */ }
  loading.value = false
})
</script>

<style scoped>
.dashboard-page {
  padding: 32px 0;
}

.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dash-header h1 {
  font-size: 26px;
}

.dash-header p {
  color: #888;
  font-size: 14px;
  margin-top: 4px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  text-decoration: none;
  color: #333;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.back-btn:hover {
  border-color: #e74c3c;
  color: #e74c3c;
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
  border-radius: 8px;
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
  flex-shrink: 0;
}

.stat-icon.sales {
  background: #eaf4ff;
  color: #2980b9;
}

.stat-icon.orders {
  background: #fef9e7;
  color: #f39c12;
}

.stat-icon.pending {
  background: #fff3cd;
  color: #856404;
}

.stat-icon.paid {
  background: #eafaf1;
  color: #27ae60;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #333;
}

.stat-label {
  font-size: 13px;
  color: #888;
}

.table-section {
  padding: 24px;
}

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header-row h2 {
  font-size: 17px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.section-header-row h2 i {
  color: #e74c3c;
}

.table-wrap {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.sa-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.sa-table thead th {
  text-align: left;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 2px solid #eee;
  font-size: 12px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.sa-table tbody td {
  padding: 14px 16px;
  border-bottom: 1px solid #f5f5f5;
  vertical-align: middle;
}

.sa-table tbody tr:hover {
  background: #fafafa;
}

.sa-table tbody tr:last-child td {
  border-bottom: none;
}

.order-link {
  font-weight: 600;
  color: #2980b9;
}

.commission-amount {
  font-weight: 700;
  color: #27ae60;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: capitalize;
  white-space: nowrap;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-paid {
  background: #d4edda;
  color: #155724;
}

.empty-mini {
  text-align: center;
  padding: 48px 24px;
  color: #999;
  font-size: 14px;
}

.empty-mini i {
  font-size: 36px;
  color: #ddd;
  margin-bottom: 12px;
  display: block;
}

.empty-mini p {
  margin: 0;
}

@media (max-width: 768px) {
  .dash-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 16px;
  }

  .table-section {
    padding: 16px;
  }

  .sa-table {
    font-size: 13px;
  }

  .sa-table thead th,
  .sa-table tbody td {
    padding: 10px 12px;
  }
}
</style>
