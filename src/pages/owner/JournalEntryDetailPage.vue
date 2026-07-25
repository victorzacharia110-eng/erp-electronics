<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-file-invoice" style="color: #e74c3c; margin-right: 12px;"></i>{{ entry?.reference || $t('accounting.journal.entryDetail') }}</h1>
        <p v-if="entry">{{ entry.description }}</p>
      </div>
      <div class="header-actions">
        <button v-if="entry?.status === 'draft'" class="btn btn-success" @click="postEntry"><i class="fas fa-check-circle"></i> {{ $t('accounting.journal.post') }}</button>
        <button v-if="entry?.status === 'posted'" class="btn btn-warning" @click="showVoidModal = true"><i class="fas fa-ban"></i> {{ $t('accounting.journal.void') }}</button>
        <button v-if="entry?.status === 'draft'" class="btn btn-danger" @click="showDeleteModal = true"><i class="fas fa-trash"></i> {{ $t('common.delete') }}</button>
        <router-link to="/owner/accounting/journal" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.back') }}</router-link>
      </div>
    </div>

    <SkeletonLoader v-if="loading" type="stats" :count="3" />
    <template v-else-if="entry">
      <div class="entry-meta">
        <div class="meta-item">
          <span class="meta-label">{{ $t('accounting.journal.date') }}</span>
          <span>{{ formatDate(entry.date) }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">{{ $t('accounting.journal.status') }}</span>
          <span :class="['status-badge', `status-${entry.status}`]">{{ entry.status }}</span>
        </div>
        <div class="meta-item" v-if="entry.preparer">
          <span class="meta-label">{{ $t('accounting.journal.preparedBy') }}</span>
          <span>{{ entry.preparer.name }}</span>
        </div>
        <div class="meta-item" v-if="entry.poster">
          <span class="meta-label">{{ $t('accounting.journal.postedBy') }}</span>
          <span>{{ entry.poster.name }}</span>
        </div>
        <div class="meta-item" v-if="entry.voided_by_user">
          <span class="meta-label">{{ $t('accounting.journal.voidedBy') }}</span>
          <span>{{ entry.voided_by_user.name }}</span>
        </div>
        <div class="meta-item" v-if="entry.void_reason">
          <span class="meta-label">{{ $t('accounting.journal.voidReason') }}</span>
          <span class="text-red">{{ entry.void_reason }}</span>
        </div>
      </div>

      <div class="card">
        <div class="table-wrap">
          <table class="sa-table">
            <thead>
              <tr>
                <th>{{ $t('accounting.journal.account') }}</th>
                <th>{{ $t('accounting.journal.description') }}</th>
                <th class="amount-col">{{ $t('accounting.journal.debit') }}</th>
                <th class="amount-col">{{ $t('accounting.journal.credit') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="line in entry.lines" :key="line.id">
                <td><strong>{{ line.account?.formatted_code }} {{ line.account?.name }}</strong></td>
                <td>{{ line.description || '-' }}</td>
                <td class="amount-col">{{ line.debit > 0 ? formatPrice(line.debit) : '-' }}</td>
                <td class="amount-col">{{ line.credit > 0 ? formatPrice(line.credit) : '-' }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="2"><strong>{{ $t('accounting.journal.totals') }}</strong></td>
                <td class="amount-col"><strong>TSh {{ formatPrice(entry.total_debit) }}</strong></td>
                <td class="amount-col"><strong>TSh {{ formatPrice(entry.total_credit) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </template>

    <!-- Void Modal -->
    <div class="modal-overlay" v-if="showVoidModal" @click.self="showVoidModal = false">
      <div class="modal-card">
        <h2><i class="fas fa-ban"></i> {{ $t('accounting.journal.voidEntry') }}</h2>
        <div class="form-group">
          <label>{{ $t('accounting.journal.voidReason') }} *</label>
          <input v-model="voidReason" type="text" :placeholder="$t('accounting.journal.voidReasonPlaceholder')" />
        </div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showVoidModal = false">{{ $t('common.cancel') }}</button>
          <button class="btn btn-danger" @click="doVoid" :disabled="!voidReason">{{ $t('accounting.journal.void') }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Modal -->
    <div class="modal-overlay" v-if="showDeleteModal" @click.self="showDeleteModal = false">
      <div class="modal-card confirm-modal">
        <div class="confirm-icon"><i class="fas fa-trash"></i></div>
        <h2>{{ $t('accounting.journal.deleteEntry') }}</h2>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showDeleteModal = false">{{ $t('common.cancel') }}</button>
          <button class="btn btn-danger" @click="doDelete">{{ $t('common.delete') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { journalApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const entry = ref(null)
const showVoidModal = ref(false)
const showDeleteModal = ref(false)
const voidReason = ref('')

function formatPrice(v) { return Number(v || 0).toLocaleString('en-TZ') }
function formatDate(d) { return new Date(d).toLocaleDateString('en-TZ', { year: 'numeric', month: 'long', day: 'numeric' }) }

async function loadEntry() {
  try {
    const res = await journalApi.getOne(route.params.id)
    entry.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function postEntry() {
  try {
    await journalApi.post(entry.value.id)
    await loadEntry()
  } catch (e) {
    alert(e.response?.data?.message || 'Failed to post')
  }
}

async function doVoid() {
  try {
    await journalApi.void(entry.value.id, { reason: voidReason.value })
    showVoidModal.value = false
    voidReason.value = ''
    await loadEntry()
  } catch (e) {
    alert(e.response?.data?.message || 'Failed to void')
  }
}

async function doDelete() {
  try {
    await journalApi.delete(entry.value.id)
    router.push('/owner/accounting/journal')
  } catch (e) {
    alert(e.response?.data?.message || 'Failed to delete')
    showDeleteModal.value = false
  }
}

onMounted(loadEntry)
</script>

<style scoped>
.dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.dash-header h1 { font-size: 24px; font-weight: 700; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.header-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; color: #666; text-decoration: none; font-size: 13px; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.entry-meta { display: flex; flex-wrap: wrap; gap: 24px; margin-bottom: 24px; padding: 20px; background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.meta-item { min-width: 120px; }
.meta-label { display: block; font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 4px; }
.text-red { color: #e74c3c; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); overflow: hidden; }
.table-wrap { overflow-x: auto; }
.sa-table { width: 100%; border-collapse: collapse; }
.sa-table th { padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 2px solid #f0f0f0; background: #fafafa; }
.sa-table td { padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.sa-table tfoot td { border-top: 2px solid #e0e0e0; background: #fafafa; }
.amount-col { text-align: right; font-family: 'JetBrains Mono', monospace; }

.status-badge { padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.status-draft { background: #fef9e7; color: #7d6608; }
.status-posted { background: #f0fff4; color: #1e8449; }
.status-voided { background: #f8d7da; color: #721c24; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-success { background: #27ae60; color: #fff; }
.btn-success:hover { background: #219a52; }
.btn-warning { background: #f39c12; color: #fff; }
.btn-warning:hover { background: #e67e22; }
.btn-danger { background: #e74c3c; color: #fff; }
.btn-danger:hover { background: #c0392b; }
.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 24px; }
.modal-card { width: 100%; max-width: 420px; background: #fff; border-radius: 12px; padding: 32px; }
.modal-card h2 { font-size: 18px; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.modal-card h2 i { color: #e74c3c; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
.form-group input { width: 100%; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; box-sizing: border-box; }
.form-group input:focus { outline: none; border-color: #e74c3c; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; }
.confirm-modal { text-align: center; }
.confirm-icon { width: 64px; height: 64px; background: #fef5f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
.confirm-icon i { font-size: 28px; color: #e74c3c; }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .header-actions { flex-wrap: wrap; }
  .entry-meta { gap: 16px; }
}
</style>
