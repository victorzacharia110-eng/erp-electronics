<template>
  <div class="container page">
    <div class="page-header">
      <div>
        <h1>{{ $t('employees.title') }}</h1>
        <p class="subtitle">{{ $t('employees.subtitle') }}</p>
      </div>
      <button class="btn btn-primary" @click="showAddModal = true"><i class="fas fa-user-plus"></i> {{ $t('employees.addEmployee') }}</button>
    </div>

    <SkeletonLoader v-if="loading" type="list" :count="4" />

    <div v-else-if="employees.length === 0" class="empty-state card">
      <div class="empty-icon"><i class="fas fa-users"></i></div>
      <h3>{{ $t('employees.noEmployees') }}</h3>
      <p>{{ $t('employees.noEmployeesDesc') }}</p>
      <button class="btn btn-primary" @click="showAddModal = true"><i class="fas fa-user-plus"></i> {{ $t('employees.addFirst') }}</button>
    </div>

    <div v-else>
      <div class="summary-bar">
        <span><strong>{{ employees.length }}</strong> {{ $t('employees.totalEmployees') }}</span>
        <span><strong>{{ employees.filter(e => e.is_active).length }}</strong> {{ $t('employees.active') }}</span>
        <span><strong>{{ employees.filter(e => !e.is_active).length }}</strong> {{ $t('employees.inactive') }}</span>
      </div>

      <div class="filters-bar" v-if="employees.length > 0">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input v-model="search" type="text" :placeholder="$t('common.searchPlaceholder')" @input="onSearch" />
        </div>
      </div>

      <div class="employees-list">
        <div v-for="emp in displayItems" :key="emp.id" class="employee-card card">
          <div class="emp-avatar"><i class="fas fa-user"></i></div>
          <div class="emp-info">
            <h3>{{ emp.name }}</h3>
            <p class="emp-email">{{ emp.email }}</p>
            <p class="emp-meta" v-if="emp.phone"><i class="fas fa-phone"></i> {{ emp.phone }}</p>
            <p class="emp-meta" v-if="emp.nida_number || emp.voting_id_number"><i class="fas fa-id-card"></i> {{ emp.nida_number || emp.voting_id_number }}</p>
            <p class="emp-meta" v-if="emp.employee_profile?.branch"><i class="fas fa-store"></i> {{ emp.employee_profile.branch.name }}</p>
            <p class="emp-meta"><i class="fas fa-file-contract"></i> {{ emp.documents_count || 0 }} docs · {{ emp.guarantors_count || 0 }} {{ $t('employees.addModal.wadhamini') }}</p>
          </div>
          <div class="emp-details-row">
            <div class="emp-status">
              <span :class="['status-dot', emp.is_active ? 'active' : 'inactive']"></span>
              {{ emp.is_active ? $t('common.active') : $t('common.inactive') }}
            </div>
            <div class="emp-date">
              <span class="label">{{ $t('common.joined') }}</span>
              <span>{{ new Date(emp.created_at).toLocaleDateString() }}</span>
            </div>
            <div class="emp-pw-status">
              <span class="label">{{ $t('common.password') }}</span>
              <span :class="emp.password_changed_at ? 'pw-changed' : 'pw-default'">
                {{ emp.password_changed_at ? $t('employees.changed') : $t('employees.defaultNeedsChange') }}
              </span>
            </div>
          </div>
          <div class="emp-actions">
            <button class="btn-icon" :title="$t('common.edit')" @click="openEdit(emp)"><i class="fas fa-edit"></i></button>
            <button class="btn-icon" :title="emp.is_active ? $t('employees.deactivate') : $t('employees.activate')" @click="toggleStatus(emp)">
              <i :class="emp.is_active ? 'fas fa-user-slash' : 'fas fa-user-check'"></i>
            </button>
            <button class="btn-icon danger" :title="$t('common.delete')" @click="confirmDelete(emp)"><i class="fas fa-trash"></i></button>
          </div>
        </div>
      </div>

      <TablePagination
        v-if="employees.length > 15"
        :current-page="currentPage" :total-pages="totalPages"
        :from="pageInfo.from" :to="pageInfo.to" :total="pageInfo.total"
        :show-all="showAll"
        @page="goToPage" @toggle-all="toggleShowAll"
      />
    </div>

    <div class="modal-overlay" v-if="showAddModal" @click.self="closeAddModal">
      <div class="modal-card card add-employee-modal">
        <h2><i class="fas fa-user-plus"></i> {{ $t('employees.addModal.title') }}</h2>
        <p class="modal-desc">{{ $t('employees.defaultPasswordDesc') }}</p>
        <form @submit.prevent="addEmployee" novalidate>
          <div class="form-group" :class="{ 'has-error': addErrors.name }">
            <label>{{ $t('employees.addModal.name') }} *</label>
            <input v-model="newEmp.name" type="text" :placeholder="$t('employees.addModal.namePlaceholder')" @blur="validateAddField('name')" @input="validateAddField('name')" />
            <span class="field-error" v-if="addErrors.name"><i class="fas fa-exclamation-triangle"></i> {{ addErrors.name }}</span>
          </div>
          <div class="form-group" :class="{ 'has-error': addErrors.email }">
            <label>{{ $t('employees.addModal.email') }} *</label>
            <input v-model="newEmp.email" type="email" :placeholder="$t('employees.addModal.emailPlaceholder')" @blur="validateAddField('email')" @input="validateAddField('email')" />
            <span class="field-error" v-if="addErrors.email"><i class="fas fa-exclamation-triangle"></i> {{ addErrors.email }}</span>
          </div>
          <div class="form-group" :class="{ 'has-error': addErrors.phone }">
            <label>{{ $t('employees.addModal.phone') }} *</label>
            <input v-model="newEmp.phone" type="tel" :placeholder="$t('employees.addModal.phonePlaceholder')" @blur="validateAddField('phone')" @input="validateAddField('phone')" />
            <span class="field-error" v-if="addErrors.phone"><i class="fas fa-exclamation-triangle"></i> {{ addErrors.phone }}</span>
          </div>
          <div class="form-row">
            <div class="form-group" :class="{ 'has-error': addErrors.nida_number }">
              <label>{{ $t('employees.addModal.nida') }}</label>
              <input v-model="newEmp.nida_number" type="text" :placeholder="$t('employees.addModal.nidaPlaceholder')" @input="validateAddField('nida_number')" />
            </div>
            <div class="form-group" :class="{ 'has-error': addErrors.voting_id_number }">
              <label>{{ $t('employees.addModal.votingId') }}</label>
              <input v-model="newEmp.voting_id_number" type="text" :placeholder="$t('employees.addModal.votingIdPlaceholder')" @input="validateAddField('voting_id_number')" />
            </div>
          </div>
          <p class="id-hint"><i class="fas fa-info-circle"></i> {{ $t('employees.addModal.idEither') }}</p>
          <div class="form-group" v-if="branches.length > 0">
            <label>{{ $t('branches.branchName') }}</label>
            <select v-model="newEmp.branch_id" class="form-select">
              <option value="">{{ $t('branches.noBranches') }}</option>
              <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
          </div>

          <div class="wadhamini-box" :class="{ 'has-error': addErrors.guarantors }">
            <div class="wadhamini-head">
              <div>
                <strong>{{ $t('employees.addModal.wadhamini') }} *</strong>
                <p>{{ $t('employees.addModal.wadhaminiRequired') }}</p>
              </div>
              <button type="button" class="btn btn-outline btn-sm" @click="showGuarantorModal = true">
                <i class="fas fa-users"></i>
                {{ newEmp.guarantors.length > 0 ? $t('employees.addModal.editWadhamini') : $t('employees.addModal.fillWadhamini') }}
                <span class="badge-count" v-if="newEmp.guarantors.length > 0">{{ newEmp.guarantors.length }}</span>
              </button>
            </div>
            <div v-if="newEmp.guarantors.length === 0" class="wadhamini-empty">{{ $t('employees.addModal.emptyGuarantors') }}</div>
            <div v-for="(g, i) in newEmp.guarantors" :key="i" class="wadhamini-item">
              <div class="wadhamini-info">
                <strong>{{ g.full_name }}</strong>
                <span class="muted">{{ g.relationship }}</span>
              </div>
              <span class="muted">{{ g.phone }}</span>
              <button type="button" class="btn-icon danger" :title="$t('common.delete')" @click="removeGuarantor(i)"><i class="fas fa-trash"></i></button>
            </div>
            <span class="field-error" v-if="addErrors.guarantors"><i class="fas fa-exclamation-triangle"></i> {{ addErrors.guarantors }}</span>
          </div>

          <div class="form-group attachments-group">
            <label>{{ $t('employees.addModal.attachments') }}</label>
            <p class="attachments-desc">{{ $t('employees.addModal.attachmentsDesc') }}</p>
            <label class="file-drop">
              <input type="file" multiple accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" @change="onFilesSelected" />
              <i class="fas fa-cloud-upload-alt"></i>
              <span>{{ $t('employees.addModal.chooseFiles') }}</span>
            </label>
            <div v-if="newEmp.attachments.length === 0" class="no-files">{{ $t('employees.addModal.noFiles') }}</div>
            <div v-for="(f, i) in newEmp.attachments" :key="i" class="file-item">
              <i class="fas fa-file-alt"></i>
              <span class="file-name">{{ f.file.name }}</span>
              <select v-model="f.type" class="form-select file-type-select">
                <option value="contract">{{ $t('employees.addModal.typeContract') }}</option>
                <option value="background_check">{{ $t('employees.addModal.typeBackground') }}</option>
                <option value="other">{{ $t('employees.addModal.typeOther') }}</option>
              </select>
              <button type="button" class="btn-icon danger" :title="$t('common.delete')" @click="removeFile(i)"><i class="fas fa-trash"></i></button>
            </div>
          </div>
          <div class="default-pw-note" v-if="newEmp.name.trim()">
            <i class="fas fa-info-circle"></i>
            {{ $t('employees.defaultPassword') }} <strong>{{ newEmp.name.trim().toUpperCase() }}</strong>
          </div>
          <div class="server-errors" v-if="addServerErrors.length > 0">
            <div v-for="(msg, i) in addServerErrors" :key="i" class="server-error"><i class="fas fa-exclamation-circle"></i> {{ msg }}</div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="closeAddModal">{{ $t('common.cancel') }}</button>
            <button type="submit" class="btn btn-primary" :disabled="addLoading || !canAdd">
              <i class="fas fa-plus"></i> {{ addLoading ? $t('employees.addModal.creating') : $t('employees.addModal.createBtn') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" v-if="showEditModal" @click.self="closeEditModal">
      <div class="modal-card card add-employee-modal">
        <h2><i class="fas fa-user-edit"></i> {{ $t('employees.editModal.title') }}</h2>
        <form @submit.prevent="saveEmployee" novalidate>
          <div class="form-group" :class="{ 'has-error': editErrors.name }">
            <label>{{ $t('employees.addModal.name') }} *</label>
            <input v-model="editEmp.name" type="text" :placeholder="$t('employees.addModal.namePlaceholder')" @blur="validateEditField('name')" @input="validateEditField('name')" />
            <span class="field-error" v-if="editErrors.name"><i class="fas fa-exclamation-triangle"></i> {{ editErrors.name }}</span>
          </div>
          <div class="form-group" :class="{ 'has-error': editErrors.email }">
            <label>{{ $t('employees.addModal.email') }} *</label>
            <input v-model="editEmp.email" type="email" :placeholder="$t('employees.addModal.emailPlaceholder')" @blur="validateEditField('email')" @input="validateEditField('email')" />
            <span class="field-error" v-if="editErrors.email"><i class="fas fa-exclamation-triangle"></i> {{ editErrors.email }}</span>
          </div>
          <div class="form-group" :class="{ 'has-error': editErrors.phone }">
            <label>{{ $t('employees.addModal.phone') }} *</label>
            <input v-model="editEmp.phone" type="tel" :placeholder="$t('employees.addModal.phonePlaceholder')" @blur="validateEditField('phone')" @input="validateEditField('phone')" />
            <span class="field-error" v-if="editErrors.phone"><i class="fas fa-exclamation-triangle"></i> {{ editErrors.phone }}</span>
          </div>
          <div class="form-row">
            <div class="form-group" :class="{ 'has-error': editErrors.nida_number }">
              <label>{{ $t('employees.addModal.nida') }}</label>
              <input v-model="editEmp.nida_number" type="text" :placeholder="$t('employees.addModal.nidaPlaceholder')" @input="validateEditField('nida_number')" />
            </div>
            <div class="form-group" :class="{ 'has-error': editErrors.voting_id_number }">
              <label>{{ $t('employees.addModal.votingId') }}</label>
              <input v-model="editEmp.voting_id_number" type="text" :placeholder="$t('employees.addModal.votingIdPlaceholder')" @input="validateEditField('nida_number')" />
            </div>
          </div>
          <p class="id-hint"><i class="fas fa-info-circle"></i> {{ $t('employees.addModal.idEither') }}</p>
          <div class="form-row">
            <div class="form-group" v-if="branches.length > 0">
              <label>{{ $t('branches.branchName') }}</label>
              <select v-model="editEmp.branch_id" class="form-select">
                <option value="">{{ $t('employees.editModal.noBranch') }}</option>
                <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>{{ $t('employees.editModal.position') }}</label>
              <input v-model="editEmp.position" type="text" :placeholder="$t('employees.editModal.positionPlaceholder')" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>{{ $t('employees.editModal.department') }}</label>
              <input v-model="editEmp.department" type="text" :placeholder="$t('employees.editModal.departmentPlaceholder')" />
            </div>
            <div class="form-group">
              <label>{{ $t('employees.editModal.commissionRate') }}</label>
              <input v-model="editEmp.commission_rate" type="number" min="0" max="100" step="0.01" :placeholder="$t('employees.editModal.commissionRatePlaceholder')" />
            </div>
          </div>

          <div class="wadhamini-box" :class="{ 'has-error': editErrors.guarantors }">
            <div class="wadhamini-head">
              <div>
                <strong>{{ $t('employees.addModal.wadhamini') }}</strong>
                <p>{{ $t('employees.editModal.guarantorsInfo') }}</p>
              </div>
              <button type="button" class="btn btn-outline btn-sm" @click="showGuarantorModal = true">
                <i class="fas fa-users"></i>
                {{ editEmp.guarantors.length > 0 ? $t('employees.addModal.editWadhamini') : $t('employees.addModal.fillWadhamini') }}
                <span class="badge-count" v-if="editEmp.guarantors.length > 0">{{ editEmp.guarantors.length }}</span>
              </button>
            </div>
            <div v-if="editEmp.guarantors.length === 0" class="wadhamini-empty">{{ $t('employees.addModal.emptyGuarantors') }}</div>
            <div v-for="(g, i) in editEmp.guarantors" :key="i" class="wadhamini-item">
              <div class="wadhamini-info">
                <strong>{{ g.full_name }}</strong>
                <span class="muted">{{ g.relationship }}</span>
              </div>
              <span class="muted">{{ g.phone }}</span>
              <button type="button" class="btn-icon danger" :title="$t('common.delete')" @click="removeGuarantor(i)"><i class="fas fa-trash"></i></button>
            </div>
          </div>
          <div class="server-errors" v-if="editServerErrors.length > 0">
            <div v-for="(msg, i) in editServerErrors" :key="i" class="server-error"><i class="fas fa-exclamation-circle"></i> {{ msg }}</div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="closeEditModal">{{ $t('common.cancel') }}</button>
            <button type="submit" class="btn btn-primary" :disabled="editLoading || !canEdit">
              <i class="fas fa-save"></i> {{ editLoading ? $t('employees.editModal.saving') : $t('employees.editModal.saveBtn') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" v-if="showGuarantorModal" @click.self="showGuarantorModal = false">
      <div class="modal-card card guarantor-modal">
        <h2><i class="fas fa-users"></i> {{ $t('employees.addModal.wadhamini') }}</h2>
        <p class="modal-desc">{{ $t('employees.addModal.wadhaminiRequired') }}</p>
        <form @submit.prevent="addGuarantor">
          <div class="form-group" :class="{ 'has-error': guarantorErrors.full_name }">
            <label>{{ $t('employees.addModal.guarantorName') }} *</label>
            <input v-model="guarantorForm.full_name" type="text" :placeholder="$t('employees.addModal.guarantorNamePlaceholder')" />
            <span class="field-error" v-if="guarantorErrors.full_name"><i class="fas fa-exclamation-triangle"></i> {{ guarantorErrors.full_name }}</span>
          </div>
          <div class="form-group" :class="{ 'has-error': guarantorErrors.phone }">
            <label>{{ $t('employees.addModal.guarantorPhone') }} *</label>
            <input v-model="guarantorForm.phone" type="tel" :placeholder="$t('employees.addModal.guarantorPhonePlaceholder')" />
            <span class="field-error" v-if="guarantorErrors.phone"><i class="fas fa-exclamation-triangle"></i> {{ guarantorErrors.phone }}</span>
          </div>
          <div class="form-group" :class="{ 'has-error': guarantorErrors.relationship }">
            <label>{{ $t('employees.addModal.guarantorRelationship') }} *</label>
            <input v-model="guarantorForm.relationship" type="text" :placeholder="$t('employees.addModal.guarantorRelationshipPlaceholder')" />
            <span class="field-error" v-if="guarantorErrors.relationship"><i class="fas fa-exclamation-triangle"></i> {{ guarantorErrors.relationship }}</span>
          </div>
          <div class="form-group">
            <label>{{ $t('employees.addModal.guarantorAddress') }}</label>
            <input v-model="guarantorForm.address" type="text" :placeholder="$t('employees.addModal.guarantorAddressPlaceholder')" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="showGuarantorModal = false">{{ $t('common.cancel') }}</button>
            <button type="submit" class="btn btn-primary"><i class="fas fa-plus"></i> {{ $t('employees.addModal.addGuarantor') }}</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" v-if="deleteTarget" @click.self="deleteTarget = null">
      <div class="modal-card card confirm-modal">
        <div class="confirm-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <h2>{{ $t('employees.confirmDelete') }}?</h2>
        <p>{{ $t('employees.confirmDeleteDesc') }}</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="deleteTarget = null">{{ $t('common.cancel') }}</button>
          <button class="btn btn-danger" @click="deleteEmployee" :disabled="deleting"><i class="fas fa-trash"></i> {{ deleting ? $t('common.loading') : $t('common.delete') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { employeeApi, branchApi } from '@/api'
import { useTablePagination } from '@/composables/useTablePagination'
import TablePagination from '@/components/TablePagination.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const { t } = useI18n()

const employees = ref([])
const branches = ref([])
const { search, currentPage, showAll, displayItems, totalPages, pageInfo, onSearch, goToPage, toggleShowAll } = useTablePagination(employees, ['name', 'email', 'phone'])
const loading = ref(true)
const showAddModal = ref(false)
const newEmp = ref({ name: '', email: '', phone: '', nida_number: '', voting_id_number: '', branch_id: '', guarantors: [], attachments: [] })
const addErrors = ref({})
const addServerErrors = ref([])
const addLoading = ref(false)
const showGuarantorModal = ref(false)
const guarantorForm = ref({ full_name: '', phone: '', relationship: '', address: '' })
const guarantorErrors = ref({})
const editTarget = ref(null)
const showEditModal = ref(false)
const editEmp = ref({ name: '', email: '', phone: '', nida_number: '', voting_id_number: '', branch_id: '', position: '', department: '', commission_rate: '', guarantors: [] })
const editErrors = ref({})
const editServerErrors = ref([])
const editLoading = ref(false)
const deleteTarget = ref(null)
const deleting = ref(false)

const canAdd = computed(() =>
  newEmp.value.name.trim().length >= 2 &&
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newEmp.value.email) &&
  newEmp.value.phone.trim().length >= 3 &&
  (newEmp.value.nida_number.trim() || newEmp.value.voting_id_number.trim()) &&
  newEmp.value.guarantors.length > 0
)

const canEdit = computed(() =>
  editTarget.value !== null &&
  editEmp.value.name.trim().length >= 2 &&
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(editEmp.value.email) &&
  editEmp.value.phone.trim().length >= 3 &&
  (editEmp.value.nida_number.trim() || editEmp.value.voting_id_number.trim())
)

function validateAddField(field) {
  if (field === 'name') {
    if (!newEmp.value.name.trim()) addErrors.value.name = t('employees.nameRequired')
    else if (newEmp.value.name.trim().length < 2) addErrors.value.name = t('employees.nameTooShort')
    else delete addErrors.value.name
  }
  if (field === 'email') {
    if (!newEmp.value.email.trim()) addErrors.value.email = t('employees.emailRequired')
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newEmp.value.email)) addErrors.value.email = t('employees.emailInvalid')
    else delete addErrors.value.email
  }
  if (field === 'phone') {
    if (!newEmp.value.phone.trim()) addErrors.value.phone = t('employees.addModal.phoneRequired')
    else delete addErrors.value.phone
  }
  if (field === 'nida_number' || field === 'voting_id_number') {
    if (!newEmp.value.nida_number.trim() && !newEmp.value.voting_id_number.trim()) {
      addErrors.value.nida_number = t('employees.addModal.idEither')
      addErrors.value.voting_id_number = t('employees.addModal.idEither')
    } else {
      delete addErrors.value.nida_number
      delete addErrors.value.voting_id_number
    }
  }
}

function validateEditField(field) {
  if (field === 'name') {
    if (!editEmp.value.name.trim()) editErrors.value.name = t('employees.nameRequired')
    else if (editEmp.value.name.trim().length < 2) editErrors.value.name = t('employees.nameTooShort')
    else delete editErrors.value.name
  }
  if (field === 'email') {
    if (!editEmp.value.email.trim()) editErrors.value.email = t('employees.emailRequired')
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(editEmp.value.email)) editErrors.value.email = t('employees.emailInvalid')
    else delete editErrors.value.email
  }
  if (field === 'phone') {
    if (!editEmp.value.phone.trim()) editErrors.value.phone = t('employees.addModal.phoneRequired')
    else delete editErrors.value.phone
  }
  if (field === 'nida_number' || field === 'voting_id_number') {
    if (!editEmp.value.nida_number.trim() && !editEmp.value.voting_id_number.trim()) {
      editErrors.value.nida_number = t('employees.addModal.idEither')
      editErrors.value.voting_id_number = t('employees.addModal.idEither')
    } else {
      delete editErrors.value.nida_number
      delete editErrors.value.voting_id_number
    }
  }
}

function addGuarantor() {
  guarantorErrors.value = {}
  const g = guarantorForm.value
  if (!g.full_name.trim()) guarantorErrors.value.full_name = t('employees.addModal.guarantorNameRequired')
  if (!g.phone.trim()) guarantorErrors.value.phone = t('employees.addModal.guarantorPhoneRequired')
  if (!g.relationship.trim()) guarantorErrors.value.relationship = t('employees.addModal.guarantorRelationshipRequired')
  if (Object.keys(guarantorErrors.value).length) return
  activeGuarantorList().push({ ...g, address: g.address.trim() })
  guarantorForm.value = { full_name: '', phone: '', relationship: '', address: '' }
}

function activeGuarantorList() {
  return showEditModal.value ? editEmp.value.guarantors : newEmp.value.guarantors
}

function removeGuarantor(i) {
  activeGuarantorList().splice(i, 1)
}

function onFilesSelected(e) {
  const files = Array.from(e.target.files || [])
  files.forEach(f => newEmp.value.attachments.push({ file: f, type: 'other' }))
  e.target.value = ''
}

function removeFile(i) {
  newEmp.value.attachments.splice(i, 1)
}

async function loadEmployees() {
  loading.value = true
  try {
    const [empRes, brRes] = await Promise.all([employeeApi.getAll(), branchApi.getAll()])
    employees.value = empRes.data.data || []
    branches.value = brRes.data || []
  } catch { employees.value = [] }
  loading.value = false
}

async function addEmployee() {
  addServerErrors.value = []
  validateAddField('name')
  validateAddField('email')
  validateAddField('phone')
  validateAddField('nida_number')
  if (newEmp.value.guarantors.length === 0) addErrors.value.guarantors = t('employees.addModal.wadhaminiRequired')
  else delete addErrors.value.guarantors
  if (Object.keys(addErrors.value).length > 0) return

  addLoading.value = true
  try {
    const fd = new FormData()
    fd.append('name', newEmp.value.name)
    fd.append('email', newEmp.value.email)
    fd.append('phone', newEmp.value.phone)
    if (newEmp.value.nida_number.trim()) fd.append('nida_number', newEmp.value.nida_number.trim())
    if (newEmp.value.voting_id_number.trim()) fd.append('voting_id_number', newEmp.value.voting_id_number.trim())
    if (newEmp.value.branch_id) fd.append('branch_id', newEmp.value.branch_id)
    newEmp.value.guarantors.forEach((g, i) => {
      fd.append(`guarantors[${i}][full_name]`, g.full_name)
      fd.append(`guarantors[${i}][phone]`, g.phone)
      fd.append(`guarantors[${i}][relationship]`, g.relationship)
      if (g.address) fd.append(`guarantors[${i}][address]`, g.address)
    })
    newEmp.value.attachments.forEach((a, i) => {
      fd.append(`attachments[${i}]`, a.file)
      fd.append(`document_types[${i}]`, a.type)
    })
    await employeeApi.create(fd)
    closeAddModal()
    await loadEmployees()
  } catch (e) {
    if (e.response?.data?.errors) {
      addServerErrors.value = Object.entries(e.response.data.errors).map(([, arr]) => arr[0])
    } else {
      addServerErrors.value = [e.response?.data?.message || t('employees.addFailed')]
    }
  }
  addLoading.value = false
}

function closeAddModal() {
  showAddModal.value = false
  newEmp.value = { name: '', email: '', phone: '', nida_number: '', voting_id_number: '', branch_id: '', guarantors: [], attachments: [] }
  addErrors.value = {}
  addServerErrors.value = []
  showGuarantorModal.value = false
  guarantorForm.value = { full_name: '', phone: '', relationship: '', address: '' }
  guarantorErrors.value = {}
}

function openEdit(emp) {
  editTarget.value = emp
  editEmp.value = {
    name: emp.name,
    email: emp.email,
    phone: emp.phone,
    nida_number: emp.nida_number || '',
    voting_id_number: emp.voting_id_number || '',
    branch_id: emp.employee_profile?.branch_id || '',
    position: emp.employee_profile?.position || '',
    department: emp.employee_profile?.department || '',
    commission_rate: emp.employee_profile?.commission_rate ?? '',
    guarantors: (emp.guarantors || []).map(g => ({
      full_name: g.full_name,
      phone: g.phone,
      relationship: g.relationship,
      address: g.address || '',
    })),
  }
  editErrors.value = {}
  editServerErrors.value = []
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
  editTarget.value = null
  editEmp.value = { name: '', email: '', phone: '', nida_number: '', voting_id_number: '', branch_id: '', position: '', department: '', commission_rate: '', guarantors: [] }
  editErrors.value = {}
  editServerErrors.value = []
  showGuarantorModal.value = false
  guarantorForm.value = { full_name: '', phone: '', relationship: '', address: '' }
  guarantorErrors.value = {}
}

async function saveEmployee() {
  editServerErrors.value = []
  validateEditField('name')
  validateEditField('email')
  validateEditField('phone')
  validateEditField('nida_number')
  if (Object.keys(editErrors.value).length > 0) return

  editLoading.value = true
  try {
    const payload = {
      name: editEmp.value.name,
      email: editEmp.value.email,
      phone: editEmp.value.phone,
      nida_number: editEmp.value.nida_number.trim() || null,
      voting_id_number: editEmp.value.voting_id_number.trim() || null,
      branch_id: editEmp.value.branch_id || null,
      position: editEmp.value.position.trim() || null,
      department: editEmp.value.department.trim() || null,
      commission_rate: editEmp.value.commission_rate === '' ? null : editEmp.value.commission_rate,
      guarantors: editEmp.value.guarantors.map(({ full_name, phone, relationship, address }) => ({
        full_name,
        phone,
        relationship,
        address: address || '',
      })),
    }
    await employeeApi.update(editTarget.value.id, payload)
    closeEditModal()
    await loadEmployees()
  } catch (e) {
    if (e.response?.data?.errors) {
      editServerErrors.value = Object.entries(e.response.data.errors).map(([, arr]) => arr[0])
    } else {
      editServerErrors.value = [e.response?.data?.message || t('employees.editFailed')]
    }
  }
  editLoading.value = false
}

async function toggleStatus(emp) {
  try {
    const res = await employeeApi.toggleStatus(emp.id)
    emp.is_active = res.data.user.is_active
  } catch { /* empty */ }
}

function confirmDelete(emp) { deleteTarget.value = emp }

async function deleteEmployee() {
  deleting.value = true
  try {
    await employeeApi.delete(deleteTarget.value.id)
    employees.value = employees.value.filter(e => e.id !== deleteTarget.value.id)
    deleteTarget.value = null
  } catch { /* empty */ }
  deleting.value = false
}

onMounted(loadEmployees)
</script>

<style scoped>
.page { padding: 32px 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; }
.page-header h1 { font-size: 26px; margin-bottom: 4px; }
.subtitle { color: #888; font-size: 14px; }

.empty-state { text-align: center; padding: 60px 24px; }
.empty-icon { width: 80px; height: 80px; background: #f5f5f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; }
.empty-icon i { font-size: 32px; color: #ccc; }
.empty-state h3 { font-size: 18px; margin-bottom: 8px; }
.empty-state p { color: #888; font-size: 14px; max-width: 400px; margin: 0 auto 20px; line-height: 1.6; }

.summary-bar { display: flex; gap: 24px; margin-bottom: 20px; font-size: 14px; color: #666; flex-wrap: wrap; }
.summary-bar strong { color: #333; }

.employees-list { display: flex; flex-direction: column; gap: 12px; }

.employee-card { display: flex; align-items: center; gap: 16px; padding: 20px; }
.emp-avatar { width: 48px; height: 48px; background: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #999; font-size: 20px; flex-shrink: 0; }
.emp-info { flex: 1; min-width: 0; }
.emp-info h3 { font-size: 15px; font-weight: 600; margin-bottom: 2px; }
.emp-email { font-size: 13px; color: #888; }
.emp-meta { font-size: 12px; color: #aaa; margin-top: 2px; }
.emp-meta i { width: 14px; }
.emp-details-row { display: flex; gap: 16px; align-items: center; }
.emp-status { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 500; min-width: 80px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.active { background: #27ae60; }
.status-dot.inactive { background: #e74c3c; }
.emp-date, .emp-pw-status { text-align: center; min-width: 100px; }
.label { display: block; font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 4px; }
.emp-date span:last-child { font-size: 13px; }
.pw-changed { font-size: 12px; color: #27ae60; font-weight: 500; }
.pw-default { font-size: 12px; color: #e67e22; font-weight: 500; }
.emp-actions { display: flex; gap: 6px; }
.btn-icon { width: 36px; height: 36px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 14px; color: #666; transition: all 0.2s; }
.btn-icon:hover { border-color: #e74c3c; color: #e74c3c; background: #fef5f5; }
.btn-icon.danger:hover { background: #e74c3c; color: #fff; border-color: #e74c3c; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; }
.btn-outline:hover { border-color: #999; }
.btn-danger { background: #e74c3c; color: #fff; }
.btn-danger:hover { background: #c0392b; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 24px; }
.modal-card { width: 100%; max-width: 460px; padding: 32px; }
.modal-card.add-employee-modal { max-width: 580px; max-height: 90vh; overflow-y: auto; }
.modal-card.guarantor-modal { max-width: 480px; }
.modal-card h2 { font-size: 20px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.modal-card h2 i { color: #e74c3c; }
.modal-desc { color: #888; font-size: 13px; margin-bottom: 20px; line-height: 1.5; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.id-hint { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #999; margin: -8px 0 16px; }
.id-hint i { color: #2980b9; }

.wadhamini-box { border: 2px dashed #d5c7f0; background: #fbf9ff; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
.wadhamini-box.has-error { border-color: #e74c3c; }
.wadhamini-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
.wadhamini-head strong { font-size: 14px; }
.wadhamini-head p { font-size: 12px; color: #888; margin: 2px 0 0; }
.badge-count { display: inline-flex; align-items: center; justify-content: center; min-width: 20px; height: 20px; padding: 0 6px; background: #8e44ad; color: #fff; border-radius: 10px; font-size: 11px; font-weight: 700; }
.btn-sm { padding: 8px 14px; font-size: 13px; }
.wadhamini-empty { font-size: 13px; color: #999; padding: 6px 0; }
.wadhamini-item { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-top: 1px solid #f0ebfb; font-size: 13px; }
.wadhamini-info { flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.wadhamini-info .muted { margin-left: 0; }

.attachments-desc { font-size: 12px; color: #999; margin: -8px 0 12px; }
.file-drop { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 20px; border: 2px dashed #ddd; border-radius: 8px; cursor: pointer; color: #888; transition: all 0.2s; margin-bottom: 10px; }
.file-drop:hover { border-color: #e74c3c; color: #e74c3c; }
.file-drop i { font-size: 24px; }
.file-drop input[type="file"] { display: none; }
.no-files { font-size: 13px; color: #999; padding: 4px 0 8px; }
.file-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-top: 1px solid #f5f5f5; font-size: 13px; }
.file-item > i { color: #e74c3c; }
.file-name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-type-select { width: 150px; flex-shrink: 0; padding: 8px 10px; font-size: 12px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
.optional { color: #aaa; font-weight: 400; font-size: 12px; }
.form-group input { width: 100%; padding: 12px 14px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; font-family: 'Inter', sans-serif; box-sizing: border-box; }
.form-group input:focus { outline: none; border-color: #e74c3c; }
.form-select { width: 100%; padding: 12px 14px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; font-family: 'Inter', sans-serif; background: #fff; box-sizing: border-box; }
.form-select:focus { outline: none; border-color: #e74c3c; }
.form-group.has-error input { border-color: #e74c3c; background: #fef8f8; }
.field-error { display: flex; align-items: center; gap: 6px; margin-top: 6px; font-size: 12px; color: #e74c3c; font-weight: 500; }
.field-error i { font-size: 11px; }
.default-pw-note { padding: 12px; background: #fef9e7; border: 1px solid #fdebd0; border-radius: 6px; font-size: 13px; color: #7d6608; margin-bottom: 16px; }
.default-pw-note i { margin-right: 4px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; }

.confirm-modal { text-align: center; }
.confirm-icon { width: 64px; height: 64px; background: #fef5f5; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
.confirm-icon i { font-size: 28px; color: #e74c3c; }
.confirm-modal p { color: #666; font-size: 14px; margin-bottom: 8px; }

.server-errors { margin-bottom: 12px; }
.server-error { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #fef5f5; border: 1px solid #fdd; border-radius: 6px; color: #c0392b; font-size: 13px; font-weight: 500; margin-bottom: 6px; }

.filters-bar { margin-bottom: 16px; }
.search-box { display: flex; align-items: center; gap: 10px; background: #f8f9fa; border: 1px solid #eee; border-radius: 6px; padding: 10px 14px; max-width: 400px; }
.search-box i { color: #999; }
.search-box input { flex: 1; border: none; background: none; font-size: 14px; outline: none; font-family: inherit; }

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .employee-card { flex-direction: column; align-items: flex-start; gap: 12px; }
  .emp-info { width: 100%; }
  .emp-status { min-width: auto; }
  .emp-date, .emp-pw-status { min-width: auto; text-align: left; }
  .emp-date .label, .emp-pw-status .label { display: inline; }
  .emp-date span:last-child, .emp-pw-status span:last-child { display: inline; }
  .emp-details-row { display: flex; flex-wrap: wrap; gap: 12px; width: 100%; align-items: center; }
  .emp-actions { width: 100%; justify-content: flex-end; border-top: 1px solid #f0f0f0; padding-top: 10px; }
  .form-row { grid-template-columns: 1fr; }
  .wadhamini-head { flex-direction: column; align-items: flex-start; }
}
</style>
