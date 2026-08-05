<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-truck" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('suppliers.title') }}</h1>
        <p>{{ $t('suppliers.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" @click="openCreateModal"><i class="fas fa-plus"></i> {{ $t('suppliers.addSupplier') }}</button>
        <router-link to="/owner/accounting" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.back') }}</router-link>
      </div>
    </div>

    <div class="filters-bar" v-if="suppliers.length > 0 || search">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input v-model="search" type="text" :placeholder="$t('suppliers.searchPlaceholder')" />
      </div>
    </div>

    <SkeletonLoader v-if="loading" type="table" :count="5" />

    <div v-else-if="filteredSuppliers.length === 0 && !search" class="empty-state card">
      <i class="fas fa-truck"></i>
      <h3>{{ $t('suppliers.noSuppliersTitle') }}</h3>
      <p>{{ $t('suppliers.noSuppliersDesc') }}</p>
      <button class="btn btn-primary" style="margin-top: 16px;" @click="openCreateModal"><i class="fas fa-plus"></i> {{ $t('suppliers.addSupplier') }}</button>
    </div>

    <div v-else-if="filteredSuppliers.length === 0 && search" class="empty-state card">
      <i class="fas fa-search"></i>
      <h3>{{ $t('suppliers.noResultsTitle') }}</h3>
      <p>{{ $t('suppliers.noResultsDesc', { query: search }) }}</p>
    </div>

    <template v-else>
      <div class="card table-wrap">
        <table class="sa-table">
          <thead>
            <tr>
              <th>{{ $t('suppliers.name') }}</th>
              <th>{{ $t('suppliers.contactPerson') }}</th>
              <th>{{ $t('suppliers.phone') }}</th>
              <th>{{ $t('suppliers.email') }}</th>
              <th>{{ $t('suppliers.city') }}</th>
              <th>{{ $t('suppliers.pos') }}</th>
              <th>{{ $t('suppliers.status') }}</th>
              <th>{{ $t('suppliers.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="supplier in paginatedSuppliers" :key="supplier.id">
              <td class="name-cell"><i class="fas fa-building" style="color: #e74c3c; margin-right: 8px;"></i>{{ supplier.name }}</td>
              <td>{{ supplier.contact_person || '—' }}</td>
              <td>{{ supplier.phone || '—' }}</td>
              <td>{{ supplier.email || '—' }}</td>
              <td>{{ supplier.city || '—' }}</td>
              <td class="count-cell">{{ supplier.purchase_orders_count ?? 0 }}</td>
              <td>
                <span :class="['status-badge', supplier.is_active !== false ? 'status-active' : 'status-inactive']">
                  {{ supplier.is_active !== false ? $t('suppliers.active') : $t('suppliers.inactive') }}
                </span>
              </td>
              <td class="actions-cell">
                <button class="btn-icon" :title="$t('common.edit')" @click="openEditModal(supplier)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon btn-danger-icon" :title="$t('common.delete')" @click="confirmDelete(supplier)">
                  <i class="fas fa-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <TablePagination
        v-if="totalPages > 1"
        :current-page="currentPage"
        :total-pages="totalPages"
        :from="pageInfo.from"
        :to="pageInfo.to"
        :total="pageInfo.total"
        @page-change="goToPage"
      />
    </template>

    <!-- Create / Edit Supplier Modal -->
    <div class="modal-overlay" v-if="showModal" @click.self="closeModal">
      <div class="modal-card modal-lg">
        <div class="modal-header">
          <h3><i class="fas fa-truck"></i> {{ editingSupplier ? $t('suppliers.editSupplier') : $t('suppliers.addSupplier') }}</h3>
          <button class="modal-close" @click="closeModal"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group" :class="{ 'has-error': formErrors.name }">
              <label>{{ $t('suppliers.name') }} <span class="required">*</span></label>
              <input v-model="form.name" type="text" :placeholder="$t('suppliers.namePlaceholder')" @blur="validateField('name')" @input="validateField('name')" />
              <span class="field-error" v-if="formErrors.name"><i class="fas fa-exclamation-triangle"></i> {{ formErrors.name }}</span>
            </div>
            <div class="form-group">
              <label>{{ $t('suppliers.contactPerson') }}</label>
              <input v-model="form.contact_person" type="text" :placeholder="$t('suppliers.contactPersonPlaceholder')" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>{{ $t('suppliers.phone') }}</label>
              <PhoneInput v-model="form.phone" name="phone" placeholder="7XX XXX XXX" />
            </div>
            <div class="form-group">
              <label>{{ $t('suppliers.email') }}</label>
              <input v-model="form.email" type="email" :placeholder="$t('suppliers.emailPlaceholder')" />
            </div>
          </div>
          <div class="form-group">
            <label>{{ $t('suppliers.address') }}</label>
            <input v-model="form.address" type="text" :placeholder="$t('suppliers.addressPlaceholder')" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>{{ $t('suppliers.city') }}</label>
              <input v-model="form.city" type="text" :placeholder="$t('suppliers.cityPlaceholder')" />
            </div>
            <div class="form-group">
              <label>{{ $t('suppliers.country') }}</label>
              <input v-model="form.country" type="text" :placeholder="$t('suppliers.countryPlaceholder')" />
            </div>
          </div>

          <div class="legal-section">
            <h4><i class="fas fa-file-contract"></i> {{ $t('suppliers.tanzanianBusinessDetails') }}</h4>
            <div class="form-row">
              <div class="form-group">
                <label>{{ $t('suppliers.businessType') }}</label>
                <select v-model="form.business_type">
                  <option value="">{{ $t('suppliers.selectBusinessType') }}</option>
                  <option value="sole_proprietorship">{{ $t('suppliers.businessTypeSoleProprietorship') }}</option>
                  <option value="partnership">{{ $t('suppliers.businessTypePartnership') }}</option>
                  <option value="limited_company">{{ $t('suppliers.businessTypeLimitedCompany') }}</option>
                  <option value="other">{{ $t('suppliers.businessTypeOther') }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>{{ $t('suppliers.tinNumber') }}</label>
                <input v-model="form.tin_number" type="text" :placeholder="$t('suppliers.tinNumberPlaceholder')" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>{{ $t('suppliers.vatNumber') }}</label>
                <input v-model="form.vat_number" type="text" :placeholder="$t('suppliers.vatNumberPlaceholder')" />
              </div>
              <div class="form-group">
                <label>{{ $t('suppliers.businessRegistrationNumber') }}</label>
                <input v-model="form.business_registration_number" type="text" :placeholder="$t('suppliers.businessRegistrationNumberPlaceholder')" />
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>{{ $t('suppliers.productsDescription') }}</label>
            <textarea v-model="form.products_description" rows="3" :placeholder="$t('suppliers.productsDescriptionPlaceholder')"></textarea>
          </div>
          <div class="form-group">
            <label>{{ $t('suppliers.notes') }}</label>
            <textarea v-model="form.notes" rows="2" :placeholder="$t('suppliers.notesPlaceholder')"></textarea>
          </div>

          <div class="legal-section">
            <h4><i class="fas fa-folder-open"></i> {{ $t('suppliers.legalDocsTitle') }}</h4>
            <p class="attachments-desc">{{ $t('suppliers.legalDocsDesc') }}</p>

            <template v-if="editingSupplier">
              <div v-if="documents.length === 0" class="no-files">{{ $t('suppliers.noDocuments') }}</div>
              <div v-for="doc in documents" :key="doc.id" class="file-item">
                <i class="fas fa-file-alt"></i>
                <span class="file-name" :title="doc.original_name">{{ doc.original_name }}</span>
                <span class="doc-category">{{ docCategoryLabel(doc.category) }}</span>
                <button type="button" class="btn-icon" :title="$t('suppliers.download')" @click="downloadDoc(doc)"><i class="fas fa-download"></i></button>
                <button type="button" class="btn-icon danger" :title="$t('suppliers.delete')" @click="deleteDoc(doc)"><i class="fas fa-trash"></i></button>
              </div>
              <div class="doc-upload-sep" v-if="documents.length > 0"></div>
            </template>

            <label class="file-drop">
              <input type="file" multiple accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" @change="onFilesSelected" />
              <i class="fas fa-cloud-upload-alt"></i>
              <span>{{ editingSupplier ? $t('suppliers.uploadMoreDocuments') : $t('suppliers.chooseDocuments') }}</span>
            </label>
            <div v-if="newDocs.length === 0" class="no-files">{{ $t('suppliers.noFilesChosen') }}</div>
            <div v-for="(f, i) in newDocs" :key="i" class="file-item">
              <i class="fas fa-file-alt"></i>
              <span class="file-name" :title="f.file.name">{{ f.file.name }}</span>
              <select v-model="f.type" class="form-select file-type-select">
                <option value="contract">{{ $t('suppliers.docCategoryContract') }}</option>
                <option value="business_registration">{{ $t('suppliers.docCategoryBusinessRegistration') }}</option>
                <option value="tin_certificate">{{ $t('suppliers.docCategoryTinCertificate') }}</option>
                <option value="vat_certificate">{{ $t('suppliers.docCategoryVatCertificate') }}</option>
                <option value="business_license">{{ $t('suppliers.docCategoryBusinessLicense') }}</option>
                <option value="certificate_of_incorporation">{{ $t('suppliers.docCategoryIncorporation') }}</option>
                <option value="identification">{{ $t('suppliers.docCategoryIdentification') }}</option>
                <option value="other">{{ $t('suppliers.docCategoryOther') }}</option>
              </select>
              <button type="button" class="btn-icon danger" :title="$t('suppliers.remove')" @click="removeFile(i)"><i class="fas fa-trash"></i></button>
            </div>
          </div>

          <div class="server-errors" v-if="serverErrors.length > 0">
            <div v-for="(msg, i) in serverErrors" :key="i" class="server-error"><i class="fas fa-exclamation-circle"></i> {{ msg }}</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closeModal">{{ $t('suppliers.cancel') }}</button>
          <button class="btn btn-primary" :disabled="saving || !canSave" @click="saveSupplier">
            <i v-if="saving" class="fas fa-spinner fa-spin"></i>
            {{ saving ? $t('suppliers.saving') : (editingSupplier ? $t('suppliers.updateSupplier') : $t('suppliers.createSupplier')) }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal-overlay" v-if="deletingSupplier" @click.self="deletingSupplier = null">
      <div class="modal-card">
        <div class="modal-header">
          <h3><i class="fas fa-exclamation-triangle" style="color: #e74c3c;"></i> {{ $t('suppliers.deleteSupplier') }}</h3>
          <button class="modal-close" @click="deletingSupplier = null"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <p>{{ $t('suppliers.deleteConfirm') }}</p>
          <p class="supplier-ref" v-if="deletingSupplier">{{ deletingSupplier.name }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="deletingSupplier = null">{{ $t('suppliers.cancel') }}</button>
          <button class="btn btn-danger" :disabled="submittingDelete" @click="doDelete">
            <i v-if="submittingDelete" class="fas fa-spinner fa-spin"></i>
            {{ submittingDelete ? $t('suppliers.deleting') : $t('suppliers.deleteSupplier') }}
          </button>
        </div>
      </div>
    </div>

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas fa-check-circle"></i> {{ toastMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { supplierApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import PhoneInput from '@/components/PhoneInput.vue'
import TablePagination from '@/components/TablePagination.vue'

const { t } = useI18n()
const loading = ref(true)
const saving = ref(false)
const submittingDelete = ref(false)
const toastMsg = ref('')

const suppliers = ref([])
const search = ref('')
const currentPage = ref(1)
const perPage = 15

const showModal = ref(false)
const editingSupplier = ref(null)
const deletingSupplier = ref(null)

const documents = ref([])
const newDocs = ref([])

const formErrors = ref({})
const serverErrors = ref([])

const defaultForm = () => ({
  name: '',
  contact_person: '',
  phone: '',
  email: '',
  address: '',
  city: '',
  country: 'Tanzania',
  business_type: '',
  tin_number: '',
  vat_number: '',
  business_registration_number: '',
  products_description: '',
  notes: '',
})

const form = reactive(defaultForm())

const filteredSuppliers = computed(() => {
  if (!search.value.trim()) return suppliers.value
  const q = search.value.toLowerCase()
  return suppliers.value.filter(s =>
    (s.name && s.name.toLowerCase().includes(q)) ||
    (s.contact_person && s.contact_person.toLowerCase().includes(q)) ||
    (s.email && s.email.toLowerCase().includes(q)) ||
    (s.phone && s.phone.toLowerCase().includes(q)) ||
    (s.city && s.city.toLowerCase().includes(q))
  )
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredSuppliers.value.length / perPage)))

const pageInfo = computed(() => {
  const total = filteredSuppliers.value.length
  const from = total === 0 ? 0 : (currentPage.value - 1) * perPage + 1
  const to = Math.min(currentPage.value * perPage, total)
  return { from, to, total }
})

const paginatedSuppliers = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredSuppliers.value.slice(start, start + perPage)
})

const canSave = computed(() => form.name.trim().length >= 2)

function validateField(field) {
  if (field === 'name') {
    if (!form.name.trim()) formErrors.value.name = t('suppliers.nameRequired')
    else if (form.name.trim().length < 2) formErrors.value.name = t('suppliers.nameMinLength')
    else delete formErrors.value.name
  }
}

function goToPage(page) {
  currentPage.value = page
}

function showToast(msg) {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 3000)
}

function openCreateModal() {
  editingSupplier.value = null
  Object.assign(form, defaultForm())
  documents.value = []
  newDocs.value = []
  formErrors.value = {}
  serverErrors.value = []
  showModal.value = true
}

function openEditModal(supplier) {
  editingSupplier.value = supplier
  Object.assign(form, {
    name: supplier.name || '',
    contact_person: supplier.contact_person || '',
    phone: supplier.phone || '',
    email: supplier.email || '',
    address: supplier.address || '',
    city: supplier.city || '',
    country: supplier.country || 'Tanzania',
    business_type: supplier.business_type || '',
    tin_number: supplier.tin_number || '',
    vat_number: supplier.vat_number || '',
    business_registration_number: supplier.business_registration_number || '',
    products_description: supplier.products_description || '',
    notes: supplier.notes || '',
  })
  newDocs.value = []
  documents.value = []
  loadDocuments(supplier.id)
  formErrors.value = {}
  serverErrors.value = []
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingSupplier.value = null
  documents.value = []
  newDocs.value = []
  Object.assign(form, defaultForm())
  formErrors.value = {}
  serverErrors.value = []
}

const docCategoryLabels = {
  contract: t('suppliers.docCategoryContract'),
  business_registration: t('suppliers.docCategoryBusinessRegistration'),
  tin_certificate: t('suppliers.docCategoryTinCertificate'),
  vat_certificate: t('suppliers.docCategoryVatCertificate'),
  business_license: t('suppliers.docCategoryBusinessLicense'),
  certificate_of_incorporation: t('suppliers.docCategoryIncorporation'),
  identification: t('suppliers.docCategoryIdentification'),
  other: t('suppliers.docCategoryOther'),
}

function docCategoryLabel(cat) {
  return docCategoryLabels[cat] || cat || t('suppliers.docCategoryOther')
}

function onFilesSelected(e) {
  const files = Array.from(e.target.files || [])
  files.forEach(f => newDocs.value.push({ file: f, type: 'other' }))
  e.target.value = ''
}

function removeFile(i) {
  newDocs.value.splice(i, 1)
}

async function loadDocuments(id) {
  try {
    const res = await supplierApi.getDocuments(id)
    documents.value = res.data.data || []
  } catch {
    documents.value = []
  }
}

async function deleteDoc(doc) {
  if (!confirm(t('suppliers.deleteConfirm'))) return
  try {
    await supplierApi.deleteDocument(editingSupplier.value.id, doc.id)
    showToast(t('suppliers.documentDeleted'))
    await loadDocuments(editingSupplier.value.id)
  } catch (e) {
    serverErrors.value = [e.response?.data?.message || t('suppliers.deleteDocumentFailed')]
  }
}

async function downloadDoc(doc) {
  try {
    const res = await supplierApi.downloadDocument(editingSupplier.value.id, doc.id)
    const url = URL.createObjectURL(res.data)
    const link = document.createElement('a')
    link.href = url
    link.download = doc.original_name || 'document'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch {
    showToast(t('suppliers.downloadFailed'))
  }
}

async function loadSuppliers() {
  loading.value = true
  try {
    const res = await supplierApi.getAll()
    suppliers.value = res.data.data || res.data || []
  } catch {
    suppliers.value = []
  }
  loading.value = false
}

async function saveSupplier() {
  validateField('name')
  if (formErrors.value.name) return

  serverErrors.value = []
  saving.value = true
  try {
    const payload = {
      name: form.name.trim(),
      contact_person: form.contact_person.trim() || null,
      phone: form.phone.trim() || null,
      email: form.email.trim() || null,
      address: form.address.trim() || null,
      city: form.city.trim() || null,
      country: form.country.trim() || null,
      business_type: form.business_type || null,
      tin_number: form.tin_number.trim() || null,
      vat_number: form.vat_number.trim() || null,
      business_registration_number: form.business_registration_number.trim() || null,
      products_description: form.products_description.trim() || null,
      notes: form.notes.trim() || null,
    }

    if (editingSupplier.value) {
      await supplierApi.update(editingSupplier.value.id, payload)
      if (newDocs.value.length > 0) {
        const fd = new FormData()
        newDocs.value.forEach((a, i) => {
          fd.append(`attachments[${i}]`, a.file)
          fd.append(`document_types[${i}]`, a.type)
        })
        await supplierApi.uploadDocuments(editingSupplier.value.id, fd)
      }
    } else {
      const fd = new FormData()
      Object.entries(payload).forEach(([key, value]) => fd.append(key, value ?? ''))
      newDocs.value.forEach((a, i) => {
        fd.append(`attachments[${i}]`, a.file)
        fd.append(`document_types[${i}]`, a.type)
      })
      await supplierApi.create(fd)
    }
    closeModal()
    showToast(editingSupplier.value ? t('suppliers.updated') : t('suppliers.created'))
    await loadSuppliers()
  } catch (e) {
    if (e.response?.data?.errors) {
      serverErrors.value = Object.entries(e.response.data.errors).map(([, arr]) => arr[0])
    } else {
      serverErrors.value = [e.response?.data?.message || t('suppliers.saveFailed')]
    }
  }
  saving.value = false
}

function confirmDelete(supplier) {
  deletingSupplier.value = supplier
}

async function doDelete() {
  submittingDelete.value = true
  try {
    await supplierApi.delete(deletingSupplier.value.id)
    deletingSupplier.value = null
    showToast(t('suppliers.deleted'))
    await loadSuppliers()
  } catch (e) {
    serverErrors.value = [e.response?.data?.message || t('suppliers.deleteFailed')]
  }
  submittingDelete.value = false
}

onMounted(loadSuppliers)
</script>

<style scoped>
.dashboard-page { padding: 32px 0; }
.dash-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.dash-header h1 { font-size: 24px; font-weight: 700; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; color: #666; text-decoration: none; font-size: 13px; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.filters-bar { margin-bottom: 16px; }
.search-box { display: flex; align-items: center; gap: 10px; background: #f8f9fa; border: 1px solid #eee; border-radius: 6px; padding: 10px 14px; max-width: 400px; }
.search-box i { color: #999; }
.search-box input { flex: 1; border: none; background: none; font-size: 14px; outline: none; font-family: inherit; }

.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.table-wrap { overflow-x: auto; }
.sa-table { width: 100%; border-collapse: collapse; }
.sa-table th { padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 1px solid #f0f0f0; background: #fafafa; }
.sa-table td { padding: 12px 16px; font-size: 13px; border-bottom: 1px solid #f5f5f5; }
.name-cell { font-weight: 600; }
.count-cell { text-align: center; font-weight: 600; }
.empty-row { text-align: center; color: #aaa; padding: 32px; }

.status-badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.status-active { background: #f0fff4; color: #1e8449; }
.status-inactive { background: #f8d7da; color: #721c24; }

.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 13px; color: #666; transition: all 0.2s; }
.btn-icon:hover { border-color: #e74c3c; color: #e74c3c; }
.btn-danger-icon { color: #e74c3c; border-color: #fadbd8; }
.btn-danger-icon:hover { background: #fef5f5; border-color: #e74c3c; }
.actions-cell { white-space: nowrap; display: flex; gap: 6px; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-danger { background: #e74c3c; color: #fff; }
.btn-danger:hover { background: #c0392b; }
.btn-danger:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-outline { padding: 10px 20px; border: 1px solid #ddd; border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px; font-weight: 500; color: #666; transition: all 0.2s; }
.btn-outline:hover { border-color: #999; color: #333; }

.empty-state { text-align: center; padding: 60px 20px; }
.empty-state i { font-size: 48px; color: #ddd; margin-bottom: 16px; display: block; }
.empty-state h3 { font-size: 20px; margin-bottom: 8px; }
.empty-state p { color: #888; font-size: 14px; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 2000; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: #fff; border-radius: 10px; width: 100%; max-width: 480px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); max-height: 90vh; display: flex; flex-direction: column; }
.modal-lg { max-width: 600px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; }
.modal-header h3 { font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 8px; margin: 0; }
.modal-header h3 i { color: #e74c3c; }
.modal-close { background: none; border: none; cursor: pointer; font-size: 18px; color: #999; padding: 4px; transition: color 0.2s; }
.modal-close:hover { color: #333; }
.modal-body { padding: 24px; overflow-y: auto; flex: 1; }
.modal-body p { color: #555; font-size: 14px; line-height: 1.6; margin: 0 0 8px; }
.modal-footer { display: flex; gap: 12px; justify-content: flex-end; padding: 16px 24px; border-top: 1px solid #f0f0f0; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.form-row:last-of-type { margin-bottom: 0; }
.form-group { display: flex; flex-direction: column; margin-bottom: 16px; }
.form-row .form-group { margin-bottom: 0; }
.form-group label { font-size: 12px; font-weight: 600; color: #555; margin-bottom: 6px; }
.form-group input, .form-group select, .form-group textarea { padding: 10px 12px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 14px; font-family: inherit; transition: border-color 0.2s; resize: vertical; }
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: #e74c3c; }
.form-group.has-error input { border-color: #e74c3c; background: #fef8f8; }
.field-error { display: flex; align-items: center; gap: 6px; margin-top: 6px; font-size: 12px; color: #e74c3c; font-weight: 500; }
.field-error i { font-size: 11px; }
.required { color: #e74c3c; }

.legal-section { border: 1px solid #eee; border-radius: 8px; padding: 16px; margin-bottom: 16px; background: #fafafa; }
.legal-section h4 { font-size: 13px; font-weight: 700; color: #333; display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.legal-section h4 i { color: #e74c3c; }

.attachments-desc { font-size: 12px; color: #999; margin: -4px 0 12px; line-height: 1.5; }
.file-drop { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 20px; border: 2px dashed #ddd; border-radius: 8px; cursor: pointer; color: #888; transition: all 0.2s; margin-bottom: 10px; }
.file-drop:hover { border-color: #e74c3c; color: #e74c3c; }
.file-drop i { font-size: 24px; }
.file-drop input[type="file"] { display: none; }
.no-files { font-size: 13px; color: #999; padding: 4px 0 8px; }
.file-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-top: 1px solid #f5f5f5; font-size: 13px; }
.file-item > i { color: #e74c3c; flex-shrink: 0; }
.file-name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-type-select { width: 210px; flex-shrink: 0; padding: 8px 10px; font-size: 12px; }
.doc-category { flex-shrink: 0; font-size: 11px; font-weight: 600; color: #555; background: #f0f0f0; border-radius: 4px; padding: 2px 8px; text-transform: uppercase; letter-spacing: 0.3px; }
.doc-upload-sep { height: 1px; background: #f0f0f0; margin: 8px 0 12px; }
.btn-icon.danger { color: #e74c3c; }
.btn-icon.danger:hover { background: #fef5f5; border-color: #e74c3c; }

.supplier-ref { font-weight: 600; color: #333; margin-top: 8px !important; }

.server-errors { margin-bottom: 12px; }
.server-error { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #fef5f5; border: 1px solid #fdd; border-radius: 6px; color: #c0392b; font-size: 13px; font-weight: 500; margin-bottom: 6px; }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #2c3e50; color: #fff; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 2000; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); animation: slideUp 0.3s ease; }
.toast i { color: #27ae60; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; gap: 12px; }
  .header-actions { flex-wrap: wrap; }
  .form-row { grid-template-columns: 1fr; }
  .modal-card { margin: 10px; }
  .modal-lg { max-width: 100%; }
  .sa-table th:nth-child(4),
  .sa-table td:nth-child(4),
  .sa-table th:nth-child(5),
  .sa-table td:nth-child(5) { display: none; }
}
</style>
