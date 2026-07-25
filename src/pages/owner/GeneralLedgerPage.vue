<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-list-alt" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('accounting.reports.generalLedger') }}</h1>
      </div>
      <div class="header-actions">
        <router-link to="/owner/accounting" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.back') }}</router-link>
      </div>
    </div>

    <div class="card filters-card">
      <div class="filter-row">
        <div class="form-group">
          <label>{{ $t('accounting.journal.account') }}</label>
          <select v-model="accountId" @change="loadLedger" class="form-select">
            <option value="">{{ $t('accounting.reports.selectAccount') }}</option>
            <option v-for="acc in accounts" :key="acc.id" :value="acc.id">
              {{ acc.formatted_code }} - {{ acc.name }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>{{ $t('accounting.reports.from') }}</label>
          <input v-model="from" type="date" @change="loadLedger" />
        </div>
        <div class="form-group">
          <label>{{ $t('accounting.reports.to') }}</label>
          <input v-model="to" type="date" @change="loadLedger" />
        </div>
      </div>
    </div>

    <SkeletonLoader v-if="loading" type="table" :count="5" />
    <template v-else-if="accountId">
      <div class="card">
        <div v-if="data.account" class="ledger-header">
          <strong>{{ data.account.code }} {{ data.account.name }}</strong>
          <span :class="['type-tag', data.account.type]">{{ data.account.type }}</span>
        </div>
        <div class="table-wrap">
          <table class="sa-table">
            <thead>
              <tr>
                <th>{{ $t('accounting.journal.date') }}</th>
                <th>{{ $t('accounting.journal.reference') }}</th>
                <th>{{ $t('accounting.journal.description') }}</th>
                <th class="amount-col">{{ $t('accounting.journal.debit') }}</th>
                <th class="amount-col">{{ $t('accounting.journal.credit') }}</th>
                <th class="amount-col">{{ $t('accounting.reports.balance') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in data.entries" :key="entry.id">
                <td>{{ formatDate(entry.date) }}</td>
                <td class="code-cell">{{ entry.reference }}</td>
                <td>{{ entry.description }}</td>
                <td class="amount-col">{{ entry.debit > 0 ? formatPrice(entry.debit) : '-' }}</td>
                <td class="amount-col">{{ entry.credit > 0 ? formatPrice(entry.credit) : '-' }}</td>
                <td class="amount-col" :class="{ 'text-red': entry.balance < 0 }">
                  TSh {{ formatPrice(Math.abs(entry.balance)) }}
                </td>
              </tr>
              <tr v-if="data.entries.length === 0">
                <td colspan="6" class="empty-row">{{ $t('accounting.reports.noEntries') }}</td>
              </tr>
            </tbody>
            <tfoot v-if="data.entries.length > 0">
              <tr>
                <td colspan="3"><strong>{{ $t('accounting.reports.closingBalance') }}</strong></td>
                <td class="amount-col"><strong>TSh {{ formatPrice(totalDebit) }}</strong></td>
                <td class="amount-col"><strong>TSh {{ formatPrice(totalCredit) }}</strong></td>
                <td class="amount-col"><strong :class="{ 'text-red': data.closing_balance < 0 }">TSh {{ formatPrice(Math.abs(data.closing_balance)) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { accountApi, accountingReportApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const loading = ref(false)
const accounts = ref([])
const accountId = ref('')
const from = ref('')
const to = ref(new Date().toISOString().split('T')[0])
const data = ref({ account: null, entries: [], closing_balance: 0 })

function formatPrice(v) { return Number(v || 0).toLocaleString('en-TZ') }
function formatDate(d) { return new Date(d).toLocaleDateString('en-TZ') }

const totalDebit = computed(() => data.value.entries.reduce((s, e) => s + e.debit, 0))
const totalCredit = computed(() => data.value.entries.reduce((s, e) => s + e.credit, 0))

async function loadLedger() {
  if (!accountId.value) return
  loading.value = true
  try {
    const params = { account_id: accountId.value }
    if (from.value) params.from = from.value
    if (to.value) params.to = to.value
    const res = await accountingReportApi.getGeneralLedger(params)
    data.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const res = await accountApi.getAll()
    accounts.value = res.data
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.dash-header h1 { font-size: 24px; font-weight: 700; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; color: #666; text-decoration: none; font-size: 13px; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); overflow: hidden; }
.filters-card { padding: 20px; margin-bottom: 20px; overflow: visible; }
.filter-row { display: flex; gap: 16px; flex-wrap: wrap; }
.form-group { flex: 1; min-width: 150px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: #666; }
.form-group input, .form-select { width: 100%; padding: 10px 12px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 14px; box-sizing: border-box; }
.form-group input:focus, .form-select:focus { outline: none; border-color: #e74c3c; }

.ledger-header { padding: 16px 20px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; gap: 8px; }
.type-tag { display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: 600; text-transform: uppercase; }
.type-tag.asset { background: #eef6ff; color: #3498db; }
.type-tag.liability { background: #fef5f5; color: #e74c3c; }
.type-tag.equity { background: #f5f0ff; color: #9b59b6; }
.type-tag.revenue { background: #f0fff4; color: #27ae60; }
.type-tag.expense { background: #fef9e7; color: #f39c12; }

.table-wrap { overflow-x: auto; }
.sa-table { width: 100%; border-collapse: collapse; }
.sa-table th { padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 2px solid #f0f0f0; background: #fafafa; }
.sa-table td { padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.sa-table tfoot td { border-top: 2px solid #e0e0e0; background: #fafafa; }
.amount-col { text-align: right; font-family: 'JetBrains Mono', monospace; }
.code-cell { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #555; }
.text-red { color: #e74c3c; }
.empty-row { text-align: center; color: #aaa; padding: 32px; }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .filter-row { flex-direction: column; }
}
</style>
