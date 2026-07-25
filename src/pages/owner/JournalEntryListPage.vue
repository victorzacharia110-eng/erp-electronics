<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-journal-whills" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('accounting.journal.title') }}</h1>
        <p>{{ $t('accounting.journal.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <router-link to="/owner/accounting/journal/new" class="btn btn-primary"><i class="fas fa-plus"></i> {{ $t('accounting.journal.newEntry') }}</router-link>
        <router-link to="/owner/accounting" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.back') }}</router-link>
      </div>
    </div>

    <div class="filter-row">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input v-model="search" :placeholder="$t('common.searchPlaceholder')" @input="loadEntries" />
      </div>
      <select v-model="statusFilter" @change="loadEntries" class="filter-select">
        <option value="">{{ $t('accounting.allStatuses') }}</option>
        <option value="draft">{{ $t('accounting.statuses.draft') }}</option>
        <option value="posted">{{ $t('accounting.statuses.posted') }}</option>
        <option value="voided">{{ $t('accounting.statuses.voided') }}</option>
      </select>
    </div>

    <SkeletonLoader v-if="loading" type="table" :count="5" />
    <template v-else>
      <div class="card table-wrap">
        <table class="sa-table">
          <thead>
            <tr>
              <th>{{ $t('accounting.journal.reference') }}</th>
              <th>{{ $t('accounting.journal.date') }}</th>
              <th>{{ $t('accounting.journal.description') }}</th>
              <th>{{ $t('accounting.journal.debit') }}</th>
              <th>{{ $t('accounting.journal.credit') }}</th>
              <th>{{ $t('accounting.journal.status') }}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in entries" :key="entry.id">
              <td class="code-cell">{{ entry.reference }}</td>
              <td>{{ formatDate(entry.date) }}</td>
              <td>{{ entry.description }}</td>
              <td class="amount-cell">TSh {{ formatPrice(entry.total_debit) }}</td>
              <td class="amount-cell">TSh {{ formatPrice(entry.total_credit) }}</td>
              <td>
                <span :class="['status-badge', `status-${entry.status}`]">{{ entry.status }}</span>
              </td>
              <td class="actions-cell">
                <router-link :to="`/owner/accounting/journal/${entry.id}`" class="btn-icon" :title="$t('common.edit')">
                  <i class="fas fa-eye"></i>
                </router-link>
              </td>
            </tr>
            <tr v-if="entries.length === 0">
              <td colspan="7" class="empty-row">{{ $t('accounting.journal.noEntries') }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <TablePagination
        v-if="totalPages > 1"
        :current-page="currentPage" :total-pages="totalPages"
        :from="pageInfo.from" :to="pageInfo.to" :total="pageInfo.total"
        @page-change="goToPage"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { journalApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import TablePagination from '@/components/TablePagination.vue'

const loading = ref(true)
const entries = ref([])
const search = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const pageInfo = ref({ from: 0, to: 0, total: 0 })

function formatPrice(v) { return Number(v || 0).toLocaleString('en-TZ') }
function formatDate(d) { return new Date(d).toLocaleDateString('en-TZ') }

async function loadEntries() {
  loading.value = true
  try {
    const params = { page: currentPage.value, per_page: 15 }
    if (search.value) params.search = search.value
    if (statusFilter.value) params.status = statusFilter.value
    const res = await journalApi.getAll(params)
    entries.value = res.data.data || []
    totalPages.value = res.data.last_page || 1
    pageInfo.value = {
      from: res.data.from || 0,
      to: res.data.to || 0,
      total: res.data.total || 0,
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  currentPage.value = page
  loadEntries()
}

onMounted(loadEntries)
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

.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.table-wrap { overflow-x: auto; }
.sa-table { width: 100%; border-collapse: collapse; }
.sa-table th { padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 1px solid #f0f0f0; background: #fafafa; }
.sa-table td { padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.code-cell { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #555; }
.amount-cell { text-align: right; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.empty-row { text-align: center; color: #aaa; padding: 32px; }

.status-badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.status-draft { background: #fef9e7; color: #7d6608; }
.status-posted { background: #f0fff4; color: #1e8449; }
.status-voided { background: #f8d7da; color: #721c24; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 13px; color: #666; text-decoration: none; transition: all 0.2s; }
.btn-icon:hover { border-color: #e74c3c; color: #e74c3c; }
.actions-cell { white-space: nowrap; }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .header-actions { flex-wrap: wrap; }
  .filter-row { flex-direction: column; }
  .search-box { max-width: 100%; }
}
</style>
