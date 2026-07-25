<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i :class="isEdit ? 'fas fa-pen' : 'fas fa-plus'" style="color: #e74c3c; margin-right: 12px;"></i>{{ isEdit ? $t('productForm.editTitle') : $t('productForm.newTitle') }}</h1>
        <p>{{ isEdit ? $t('productForm.editSubtitle') : $t('productForm.newSubtitle') }}</p>
      </div>
      <router-link to="/owner/products" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.backToProducts') }}</router-link>
    </div>

    <form @submit.prevent="handleSubmit" class="form-layout">
      <div class="form-main">
        <div class="card form-section">
          <h2><i class="fas fa-info-circle"></i> {{ $t('productForm.basicInfo') }}</h2>
          <div class="form-grid">
            <div class="form-group full">
              <label>{{ $t('productForm.productName') }}</label>
              <input v-model="form.name" type="text" placeholder="e.g. Samsung Galaxy A15" required />
              <span class="field-error" v-if="errors.name">{{ errors.name }}</span>
            </div>
            <div class="form-group">
              <label>{{ $t('productForm.sku') }}</label>
              <input v-model="form.sku" type="text" placeholder="e.g. SAM-GAL-A15" required />
              <span class="field-error" v-if="errors.sku">{{ errors.sku }}</span>
            </div>
            <div class="form-group">
              <label>{{ $t('productForm.brand') }}</label>
              <input v-model="form.brand" type="text" placeholder="e.g. Samsung" />
            </div>
            <div class="form-group">
              <label>{{ $t('productForm.category') }}</label>
              <select v-model="form.category_id" required>
                <option value="">{{ $t('productForm.selectCategory') }}</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
              <span class="field-error" v-if="errors.category_id">{{ errors.category_id }}</span>
            </div>
            <div class="form-group">
              <label>{{ $t('productForm.status') }}</label>
              <select v-model="form.is_active">
                <option :value="true">{{ $t('productForm.active') }}</option>
                <option :value="false">{{ $t('productForm.inactive') }}</option>
              </select>
            </div>
          </div>
          <div class="form-group full">
            <label>{{ $t('productForm.description') }}</label>
            <textarea v-model="form.description" rows="4" placeholder="Product description..."></textarea>
          </div>
        </div>

        <div class="card form-section">
          <h2><i class="fas fa-dollar-sign"></i> {{ $t('productForm.pricing') }}</h2>
          <div class="form-grid">
            <div class="form-group">
              <label>{{ $t('productForm.sellingPrice') }}</label>
              <input v-model.number="form.price" type="number" min="0" placeholder="0" required />
              <span class="field-error" v-if="errors.price">{{ errors.price }}</span>
            </div>
            <div class="form-group">
              <label>{{ $t('productForm.costPrice') }}</label>
              <input v-model.number="form.cost_price" type="number" min="0" placeholder="0" />
            </div>
          </div>
        </div>

        <div class="card form-section">
          <h2><i class="fas fa-layer-group"></i> {{ $t('productForm.variants') }}</h2>
          <p class="section-desc">Add one or more variants (color, storage, quantity).</p>
          <div v-for="(variant, idx) in form.variants" :key="idx" class="variant-row">
            <div class="variant-fields">
              <div class="form-group">
                <label>{{ $t('productForm.variantSku') }}</label>
                <input v-model="variant.sku" type="text" required placeholder="e.g. SAM-A15-BLK" />
              </div>
              <div class="form-group">
                <label>{{ $t('productForm.variantColor') }}</label>
                <input v-model="variant.color" type="text" placeholder="e.g. Black" />
              </div>
              <div class="form-group">
                <label>{{ $t('productForm.variantStorage') }}</label>
                <input v-model="variant.storage" type="text" placeholder="e.g. 128GB" />
              </div>
              <div class="form-group">
                <label>{{ $t('productForm.variantPrice') }}</label>
                <input v-model.number="variant.price" type="number" min="0" required />
              </div>
              <div class="form-group">
                <label>{{ $t('productForm.variantCost') }}</label>
                <input v-model.number="variant.cost_price" type="number" min="0" />
              </div>
              <div class="form-group">
                <label>{{ $t('productForm.variantStock') }}</label>
                <input v-model.number="variant.quantity" type="number" min="0" required />
              </div>
              <button v-if="form.variants.length > 1" type="button" class="remove-variant" @click="form.variants.splice(idx, 1)">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
          <button type="button" class="add-variant-btn" @click="addVariant">
            <i class="fas fa-plus"></i> {{ $t('productForm.addVariant') }}
          </button>
        </div>
      </div>

      <div class="form-sidebar">
        <div class="card form-section">
          <h2><i class="fas fa-image"></i> {{ $t('productForm.image') }}</h2>
          <div class="image-upload" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
            <input ref="fileInput" type="file" accept="image/*" @change="handleFileChange" style="display:none" />
            <img v-if="imagePreview" :src="imagePreview" class="preview-img" />
            <div v-else class="upload-placeholder">
              <i class="fas fa-cloud-arrow-up"></i>
              <p>{{ $t('productForm.dragDrop') }}</p>
            </div>
          </div>
          <div class="image-url-input">
            <label>{{ $t('productForm.imageUrl') }}</label>
            <input v-model="form.image_url" type="url" :placeholder="$t('productForm.imageUrlPlaceholder')" @input="imagePreview = form.image_url" />
          </div>
          <button v-if="imagePreview" type="button" class="remove-image-btn" @click="removeImage">
            <i class="fas fa-trash"></i> {{ $t('productForm.removeImage') }}
          </button>
        </div>

        <div class="card form-section">
          <h2><i class="fas fa-save"></i> {{ $t('common.save') }}</h2>
          <button type="submit" class="btn btn-primary save-btn" :disabled="saving">
            <i :class="saving ? 'fas fa-spinner fa-spin' : 'fas fa-check'"></i>
            {{ saving ? $t('productForm.saving') : (isEdit ? $t('productForm.updateProduct') : $t('productForm.createProduct')) }}
          </button>
          <div v-if="serverErrors.length" class="server-errors">
            <div v-for="(err, i) in serverErrors" :key="i"><i class="fas fa-exclamation-circle"></i> {{ err }}</div>
          </div>
        </div>
      </div>
    </form>

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas fa-check-circle"></i> {{ toastMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { productManageApi, categoryApi } from '@/api'
import { imageUrl } from '@/utils/image'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const isEdit = computed(() => !!route.params.id)

const categories = ref([])
const saving = ref(false)
const toastMsg = ref('')
const fileInput = ref(null)
const imagePreview = ref('')
const imageFile = ref(null)
const serverErrors = ref([])
const errors = reactive({})

const form = reactive({
  name: '',
  sku: '',
  description: '',
  price: null,
  cost_price: null,
  category_id: '',
  brand: '',
  is_active: true,
  image_url: '',
  remove_image: false,
  variants: [
    { sku: '', color: '', storage: '', price: null, cost_price: null, quantity: 0 },
  ],
})

function addVariant() {
  form.variants.push({ sku: '', color: '', storage: '', price: null, cost_price: null, quantity: 0 })
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    imageFile.value = file
    imagePreview.value = URL.createObjectURL(file)
    form.image_url = ''
  }
}

function handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    imageFile.value = file
    imagePreview.value = URL.createObjectURL(file)
    form.image_url = ''
  }
}

function removeImage() {
  imageFile.value = null
  imagePreview.value = ''
  form.image_url = ''
  form.remove_image = true
}

function validate() {
  Object.keys(errors).forEach(k => delete errors[k])
  if (!form.name) errors.name = t('productForm.errors.nameRequired')
  if (!form.sku) errors.sku = t('productForm.errors.skuRequired')
  if (!form.category_id) errors.category_id = t('productForm.errors.categoryRequired')
  if (!form.price || form.price <= 0) errors.price = t('productForm.errors.priceInvalid')
  return Object.keys(errors).length === 0
}

async function handleSubmit() {
  if (!validate()) return
  saving.value = true
  serverErrors.value = []

  const fd = new FormData()
  fd.append('name', form.name)
  fd.append('sku', form.sku)
  fd.append('description', form.description || '')
  fd.append('price', form.price)
  if (form.cost_price) fd.append('cost_price', form.cost_price)
  fd.append('category_id', form.category_id)
  fd.append('brand', form.brand || '')
  fd.append('is_active', form.is_active ? '1' : '0')

  if (imageFile.value) {
    fd.append('image_file', imageFile.value)
  } else if (form.image_url) {
    fd.append('image_url', form.image_url)
  }
  if (form.remove_image) fd.append('remove_image', '1')

  form.variants.forEach((v, i) => {
    fd.append(`variants[${i}][sku]`, v.sku)
    fd.append(`variants[${i}][color]`, v.color || '')
    fd.append(`variants[${i}][storage]`, v.storage || '')
    fd.append(`variants[${i}][price]`, v.price)
    if (v.cost_price) fd.append(`variants[${i}][cost_price]`, v.cost_price)
    fd.append(`variants[${i}][quantity]`, v.quantity)
  })

  try {
    if (isEdit.value) {
      await productManageApi.update(route.params.id, fd)
      toastMsg.value = t('productForm.updatedSuccessfully')
    } else {
      await productManageApi.create(fd)
      toastMsg.value = t('productForm.createdSuccessfully')
    }
    setTimeout(() => router.push('/owner/products'), 1000)
  } catch (e) {
    if (e.response?.data?.errors) {
      serverErrors.value = Object.values(e.response.data.errors).flat()
    } else {
      serverErrors.value = [e.response?.data?.message || t('common.somethingWentWrong')]
    }
  }
  saving.value = false
}

onMounted(async () => {
  const catRes = await categoryApi.getAll()
  categories.value = catRes.data

  if (isEdit.value) {
    try {
      const res = await productManageApi.getById(route.params.id)
      const p = res.data
      form.name = p.name
      form.sku = p.sku
      form.description = p.description || ''
      form.price = p.price
      form.cost_price = p.cost_price
      form.category_id = p.category_id
      form.brand = p.brand || ''
      form.is_active = p.is_active
      form.image_url = p.image || ''
      imagePreview.value = imageUrl(p.image) || ''
      if (p.variants?.length) {
        form.variants = p.variants.map(v => ({
          sku: v.sku,
          color: v.color || '',
          storage: v.storage || '',
          price: v.price,
          cost_price: v.cost_price,
          quantity: v.inventory?.quantity_on_hand || 0,
        }))
      }
    } catch { router.push('/owner/products') }
  }
})
</script>

<style scoped>
.dashboard-page { padding: 32px 0; }
.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.dash-header h1 { font-size: 26px; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 16px; border: 1px solid #ddd; border-radius: 6px; text-decoration: none; color: #333; font-size: 13px; font-weight: 500; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.form-layout { display: grid; grid-template-columns: 1fr 320px; gap: 24px; align-items: start; }
.form-main { display: flex; flex-direction: column; gap: 20px; }
.form-sidebar { position: sticky; top: 100px; display: flex; flex-direction: column; gap: 20px; }

.form-section { padding: 24px; }
.form-section h2 { font-size: 17px; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.form-section h2 i { color: #e74c3c; }
.section-desc { font-size: 13px; color: #888; margin-bottom: 16px; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { margin-bottom: 14px; }
.form-group.full { grid-column: 1 / -1; }
.form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: #555; }
.form-group input, .form-group select, .form-group textarea {
  width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; font-family: inherit; transition: border-color 0.2s;
}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: #e74c3c; }
.field-error { font-size: 12px; color: #e74c3c; margin-top: 4px; display: block; }

.variant-row { border: 1px solid #eee; border-radius: 8px; padding: 16px; margin-bottom: 12px; position: relative; }
.variant-fields { display: grid; grid-template-columns: repeat(3, 1fr) auto auto auto auto; gap: 12px; align-items: end; }
.variant-fields .form-group { margin-bottom: 0; }
.remove-variant { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #999; transition: all 0.2s; }
.remove-variant:hover { background: #fef5f5; border-color: #e74c3c; color: #e74c3c; }
.add-variant-btn { width: 100%; padding: 12px; border: 2px dashed #ddd; border-radius: 8px; background: #fff; cursor: pointer; font-size: 14px; font-weight: 500; color: #666; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s; }
.add-variant-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.image-upload { width: 100%; aspect-ratio: 1; border: 2px dashed #ddd; border-radius: 8px; display: flex; align-items: center; justify-content: center; cursor: pointer; overflow: hidden; transition: border-color 0.2s; margin-bottom: 12px; }
.image-upload:hover { border-color: #e74c3c; }
.preview-img { width: 100%; height: 100%; object-fit: cover; }
.upload-placeholder { text-align: center; color: #999; }
.upload-placeholder i { font-size: 36px; margin-bottom: 8px; display: block; color: #ddd; }
.upload-placeholder p { font-size: 13px; }
.image-url-input { margin-bottom: 12px; }
.image-url-input label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 4px; color: #888; }
.image-url-input input { width: 100%; padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; }
.image-url-input input:focus { outline: none; border-color: #e74c3c; }
.remove-image-btn { width: 100%; padding: 8px; border: 1px solid #e74c3c; border-radius: 6px; background: #fff; color: #e74c3c; cursor: pointer; font-size: 12px; font-weight: 500; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s; }
.remove-image-btn:hover { background: #fef5f5; }

.save-btn { width: 100%; padding: 14px; font-size: 15px; display: flex; align-items: center; justify-content: center; gap: 8px; }
.btn-primary { background: #e74c3c; color: #fff; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.server-errors { margin-top: 12px; padding: 12px; background: #fef5f5; border: 1px solid #e74c3c; border-radius: 6px; font-size: 13px; color: #c0392b; }
.server-errors div { display: flex; align-items: center; gap: 6px; padding: 3px 0; }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #2c3e50; color: #fff; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 2000; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); animation: slideUp 0.3s ease; }
.toast i { color: #27ae60; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

@media (max-width: 768px) {
  .form-layout { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .variant-fields { grid-template-columns: 1fr 1fr; }
  .form-sidebar { position: static; }
}
</style>
