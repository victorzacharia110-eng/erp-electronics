<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-plus-circle" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('accounting.journal.newEntry') }}</h1>
        <p>{{ $t('accounting.journal.newEntryDesc') }}</p>
      </div>
      <div class="header-actions">
        <router-link to="/owner/accounting/journal" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.back') }}</router-link>
      </div>
    </div>

    <div class="card form-card">
      <div class="form-row">
        <div class="form-group">
          <label>{{ $t('accounting.journal.date') }}</label>
          <input v-model="form.date" type="date" />
        </div>
        <div class="form-group">
          <label>{{ $t('accounting.journal.description') }}</label>
          <input v-model="form.description" type="text" :placeholder="$t('accounting.journal.descriptionPlaceholder')" />
        </div>
      </div>

      <div class="lines-section">
        <div class="lines-header">
          <h3>{{ $t('accounting.journal.lineItems') }}</h3>
        </div>
        <div class="table-wrap">
          <table class="lines-table">
            <thead>
              <tr>
                <th>{{ $t('accounting.journal.account') }}</th>
                <th>{{ $t('accounting.journal.description') }}</th>
                <th class="amount-col">{{ $t('accounting.journal.debit') }}</th>
                <th class="amount-col">{{ $t('accounting.journal.credit') }}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(line, idx) in form.lines" :key="idx">
                <td>
                  <select v-model="line.account_id" class="line-select">
                    <option value="">{{ $t('accounting.journal.selectAccount') }}</option>
                    <optgroup v-for="group in accountGroups" :key="group.type" :label="group.label">
                      <option v-for="acc in group.accounts" :key="acc.id" :value="acc.id">
                        {{ acc.formatted_code }} - {{ acc.name }}
                      </option>
                    </optgroup>
                  </select>
                </td>
                <td><input v-model="line.description" type="text" :placeholder="$t('accounting.journal.lineDesc')" /></td>
                <td class="amount-col"><input v-model.number="line.debit" type="number" min="0" step="0.01" class="amount-input" /></td>
                <td class="amount-col"><input v-model.number="line.credit" type="number" min="0" step="0.01" class="amount-input" /></td>
                <td>
                  <button v-if="form.lines.length > 2" class="btn-icon danger" @click="removeLine(idx)" :title="$t('common.delete')">
                    <i class="fas fa-times"></i>
                  </button>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="2"><strong>{{ $t('accounting.journal.totals') }}</strong></td>
                <td class="amount-col"><strong :class="{ 'text-red': !isBalanced }">TSh {{ formatPrice(totalDebit) }}</strong></td>
                <td class="amount-col"><strong :class="{ 'text-red': !isBalanced }">TSh {{ formatPrice(totalCredit) }}</strong></td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>
        <button class="btn btn-outline add-line-btn" @click="addLine"><i class="fas fa-plus"></i> {{ $t('accounting.journal.addLine') }}</button>
      </div>

      <div v-if="!isBalanced && totalDebit > 0" class="balance-warning">
        <i class="fas fa-exclamation-triangle"></i> {{ $t('accounting.journal.mustBalance') }}
      </div>

      <div v-if="error" class="field-error"><i class="fas fa-exclamation-circle"></i> {{ error }}</div>

      <div class="form-actions">
        <router-link to="/owner/accounting/journal" class="btn btn-outline">{{ $t('common.cancel') }}</router-link>
        <button class="btn btn-primary" @click="saveDraft" :disabled="saving">
          <i class="fas fa-save"></i> {{ saving ? $t('common.saving') : $t('accounting.journal.saveDraft') }}
        </button>
        <button class="btn btn-success" @click="saveAndPost" :disabled="saving || !isBalanced || totalDebit === 0">
          <i class="fas fa-check-circle"></i> {{ $t('accounting.journal.saveAndPost') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { accountApi, journalApi } from '@/api'

const router = useRouter()
const saving = ref(false)
const accounts = ref([])
const error = ref('')

const form = ref({
  date: new Date().toISOString().split('T')[0],
  description: '',
  lines: [
    { account_id: '', description: '', debit: 0, credit: 0 },
    { account_id: '', description: '', debit: 0, credit: 0 },
  ],
})

function formatPrice(v) { return Number(v || 0).toLocaleString('en-TZ') }

const totalDebit = computed(() => form.value.lines.reduce((s, l) => s + (Number(l.debit) || 0), 0))
const totalCredit = computed(() => form.value.lines.reduce((s, l) => s + (Number(l.credit) || 0), 0))
const isBalanced = computed(() => Math.abs(totalDebit.value - totalCredit.value) < 0.01 && totalDebit.value > 0)

const accountGroups = computed(() => {
  const types = ['asset', 'liability', 'equity', 'revenue', 'expense']
  const typeLabels = { asset: 'Assets', liability: 'Liabilities', equity: 'Equity', revenue: 'Revenue', expense: 'Expenses' }
  return types
    .map(type => ({ type, label: typeLabels[type], accounts: accounts.value.filter(a => a.type === type && a.is_active) }))
    .filter(g => g.accounts.length > 0)
})

function addLine() {
  form.value.lines.push({ account_id: '', description: '', debit: 0, credit: 0 })
}

function removeLine(idx) {
  form.value.lines.splice(idx, 1)
}

function validate() {
  if (!form.value.date) return 'Date is required'
  if (!form.value.description.trim()) return 'Description is required'
  for (let i = 0; i < form.value.lines.length; i++) {
    if (!form.value.lines[i].account_id) return `Line ${i + 1}: account is required`
  }
  if (!isBalanced.value) return 'Debits and credits must be equal'
  if (totalDebit.value === 0) return 'Total must be greater than zero'
  return null
}

async function saveDraft() {
  const v = validate()
  if (v) { error.value = v; return }
  saving.value = true
  error.value = ''
  try {
    const res = await journalApi.create(form.value)
    router.push(`/owner/accounting/journal/${res.data.id}`)
  } catch (e) {
    error.value = e.response?.data?.message || 'Failed to create'
  } finally {
    saving.value = false
  }
}

async function saveAndPost() {
  const v = validate()
  if (v) { error.value = v; return }
  saving.value = true
  error.value = ''
  try {
    const res = await journalApi.create(form.value)
    await journalApi.post(res.data.id)
    router.push(`/owner/accounting/journal/${res.data.id}`)
  } catch (e) {
    error.value = e.response?.data?.message || 'Failed to create'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const res = await accountApi.getAll({ with_children: true })
    accounts.value = res.data
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.dash-header h1 { font-size: 24px; font-weight: 700; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; color: #666; text-decoration: none; font-size: 13px; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.form-card { padding: 32px; }
.form-row { display: grid; grid-template-columns: 1fr 2fr; gap: 16px; margin-bottom: 24px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
.form-group input, .form-group select { width: 100%; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; box-sizing: border-box; }
.form-group input:focus, .form-group select:focus { outline: none; border-color: #e74c3c; }

.lines-section { margin-bottom: 24px; }
.lines-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.lines-header h3 { font-size: 15px; font-weight: 600; }
.table-wrap { overflow-x: auto; }
.lines-table { width: 100%; border-collapse: collapse; }
.lines-table th { padding: 10px 12px; text-align: left; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 2px solid #f0f0f0; background: #fafafa; }
.lines-table td { padding: 8px; border-bottom: 1px solid #f5f5f5; }
.lines-table tfoot td { border-top: 2px solid #e0e0e0; padding: 12px; }
.amount-col { text-align: right; min-width: 120px; }
.line-select { width: 100%; padding: 8px 10px; border: 1px solid #e0e0e0; border-radius: 4px; font-size: 13px; background: #fff; }
.amount-input { width: 100%; padding: 8px 10px; border: 1px solid #e0e0e0; border-radius: 4px; font-size: 13px; text-align: right; }
.amount-input:focus, .line-select:focus { outline: none; border-color: #e74c3c; }
.lines-table td input[type="text"] { width: 100%; padding: 8px 10px; border: 1px solid #e0e0e0; border-radius: 4px; font-size: 13px; }

.add-line-btn { margin-top: 12px; }

.balance-warning { background: #fef9e7; border: 1px solid #fdebd0; border-radius: 6px; padding: 10px 16px; color: #7d6608; font-size: 13px; font-weight: 500; margin-bottom: 16px; }
.balance-warning i { margin-right: 6px; }
.text-red { color: #e74c3c; }
.field-error { display: flex; align-items: center; gap: 6px; margin-top: 8px; font-size: 12px; color: #e74c3c; font-weight: 500; }

.form-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; text-decoration: none; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-success { background: #27ae60; color: #fff; }
.btn-success:hover { background: #219a52; }
.btn-success:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; }
.btn-outline:hover { border-color: #999; }
.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 13px; color: #666; transition: all 0.2s; }
.btn-icon.danger:hover { background: #e74c3c; color: #fff; border-color: #e74c3c; }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .form-row { grid-template-columns: 1fr; }
  .form-actions { flex-wrap: wrap; }
}
</style>
