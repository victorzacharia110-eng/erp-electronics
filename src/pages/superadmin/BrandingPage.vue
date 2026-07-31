<template>
  <div class="branding-page">
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i> Loading...
    </div>
    <template v-else-if="owner">
      <div class="detail-header">
        <div>
          <h3>Branding: {{ owner.name }}</h3>
          <p class="muted">{{ owner.email }}</p>
        </div>
        <router-link :to="`/superadmin/owners/${owner.id}`" class="btn btn-ghost btn-sm">
          <i class="fas fa-arrow-left"></i> Back to Details
        </router-link>
      </div>

      <div class="branding-grid">
        <div class="card brand-section">
          <h4><i class="fas fa-store"></i> Store Identity</h4>
          <form @submit.prevent="saveBranding">
            <div class="form-group">
              <label>Store Name</label>
              <input v-model="brandForm.brand_store_name" type="text" placeholder="ElectroShop" />
            </div>
            <div class="form-group">
              <label>Tagline</label>
              <input v-model="brandForm.brand_tagline" type="text" placeholder="Your trusted electronics store" />
            </div>
            <button type="submit" class="btn btn-primary btn-sm" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save Identity' }}
            </button>
          </form>
        </div>

        <div class="card brand-section">
          <h4><i class="fas fa-palette"></i> Colors</h4>
          <form @submit.prevent="saveBranding">
            <div class="form-group">
              <label>Primary Color</label>
              <div class="color-input-row">
                <input v-model="brandForm.brand_color" type="color" />
                <input v-model="brandForm.brand_color" type="text" placeholder="#e74c3c" />
              </div>
            </div>
            <div class="form-group">
              <label>Secondary Color</label>
              <div class="color-input-row">
                <input v-model="brandForm.brand_color_secondary" type="color" />
                <input v-model="brandForm.brand_color_secondary" type="text" placeholder="#2c3e50" />
              </div>
            </div>
            <button type="submit" class="btn btn-primary btn-sm" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save Colors' }}
            </button>
          </form>
        </div>

        <div class="card brand-section">
          <h4><i class="fas fa-image"></i> Logo</h4>
          <div class="logo-preview" v-if="owner.owner_profile?.brand_logo_path">
            <img :src="`/branding/${owner.owner_profile.brand_logo_path}`" alt="Brand logo" />
          </div>
          <div class="logo-preview empty-logo" v-else>
            <i class="fas fa-image"></i>
            <p>No logo uploaded</p>
          </div>
          <form @submit.prevent="uploadLogo" class="upload-form">
            <input type="file" ref="fileInput" accept="image/*" @change="onFileSelect" style="display:none" />
            <button type="button" class="btn btn-ghost btn-sm" @click="$refs.fileInput.click()">
              <i class="fas fa-upload"></i> Choose Image
            </button>
            <button v-if="selectedFile" type="submit" class="btn btn-primary btn-sm" :disabled="uploading">
              {{ uploading ? 'Uploading...' : 'Upload Logo' }}
            </button>
            <span v-if="selectedFile" class="file-name">{{ selectedFile.name }}</span>
          </form>
        </div>
      </div>

      <div class="card brand-section preview-section">
        <h4><i class="fas fa-eye"></i> Preview</h4>
        <div class="preview-frame" :style="{
          '--brand-color': brandForm.brand_color,
          '--brand-secondary': brandForm.brand_color_secondary
        }">
          <div class="preview-header">
            <div class="preview-logo">
              <span class="preview-icon" :style="{ background: brandForm.brand_color }"><i class="fas fa-bolt"></i></span>
              <span class="preview-name">{{ brandForm.brand_store_name || 'ElectroShop' }}</span>
            </div>
          </div>
          <div class="preview-nav" :style="{ background: brandForm.brand_color }">
            <span>Home</span>
            <span>Products</span>
            <span>Contact</span>
          </div>
          <div class="preview-body">
            <p class="preview-tagline">{{ brandForm.brand_tagline || 'Your tagline here' }}</p>
          </div>
        </div>
      </div>
    </template>

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas fa-check-circle"></i> {{ toastMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { superadminApi } from '@/api'

const route = useRoute()
const loading = ref(true)
const owner = ref(null)
const saving = ref(false)
const uploading = ref(false)
const selectedFile = ref(null)
const toastMsg = ref('')

const brandForm = ref({
  brand_store_name: '',
  brand_tagline: '',
  brand_color: '#e74c3c',
  brand_color_secondary: '#2c3e50',
})

async function loadData() {
  try {
    const res = await superadminApi.getOwner(route.params.id)
    owner.value = res.data.owner
    const profile = owner.value.owner_profile
    if (profile) {
      brandForm.value = {
        brand_store_name: profile.brand_store_name || '',
        brand_tagline: profile.brand_tagline || '',
        brand_color: profile.brand_color || '#e74c3c',
        brand_color_secondary: profile.brand_color_secondary || '#2c3e50',
      }
    }
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

async function saveBranding() {
  saving.value = true
  try {
    await superadminApi.updateBranding(route.params.id, brandForm.value)
    toastMsg.value = 'Branding updated'
    await loadData()
  } catch {
    toastMsg.value = 'Failed to update branding'
  }
  saving.value = false
  setTimeout(() => toastMsg.value = '', 3000)
}

function onFileSelect(e) {
  selectedFile.value = e.target.files[0]
}

async function uploadLogo() {
  if (!selectedFile.value) return
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('logo', selectedFile.value)
    await superadminApi.uploadBrandingLogo(route.params.id, formData)
    toastMsg.value = 'Logo uploaded'
    selectedFile.value = null
    await loadData()
  } catch {
    toastMsg.value = 'Failed to upload logo'
  }
  uploading.value = false
  setTimeout(() => toastMsg.value = '', 3000)
}

onMounted(loadData)
</script>

<style scoped>
.branding-page { max-width: 1000px; }

.loading-state {
  text-align: center;
  padding: 64px;
  color: #888;
  font-size: 16px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.detail-header h3 { font-size: 22px; }
.muted { color: #888; font-size: 14px; }

.branding-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.brand-section {
  padding: 24px;
}

.brand-section h4 {
  font-size: 15px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-section h4 i { color: #e74c3c; }

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #555;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.form-group input[type="text"] {
  width: 100%;
  padding: 8px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  box-sizing: border-box;
}

.form-group input[type="text"]:focus {
  outline: none;
  border-color: #e74c3c;
}

.color-input-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.color-input-row input[type="color"] {
  width: 40px;
  height: 40px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  padding: 2px;
}

.color-input-row input[type="text"] {
  flex: 1;
}

.logo-preview {
  width: 100%;
  height: 120px;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  overflow: hidden;
}

.logo-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.empty-logo {
  flex-direction: column;
  color: #ccc;
  gap: 8px;
}

.empty-logo i { font-size: 28px; }
.empty-logo p { font-size: 13px; margin: 0; }

.upload-form {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-name {
  font-size: 12px;
  color: #888;
}

.preview-section {
  margin-bottom: 24px;
}

.preview-frame {
  border: 2px solid #eee;
  border-radius: 10px;
  overflow: hidden;
}

.preview-header {
  background: #fff;
  padding: 14px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
}

.preview-logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
}

.preview-name {
  font-size: 18px;
  font-weight: 800;
  color: #2c3e50;
}

.preview-nav {
  display: flex;
  gap: 0;
}

.preview-nav span {
  color: #fff;
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 600;
}

.preview-body {
  padding: 24px;
  background: #fafafa;
}

.preview-tagline {
  font-size: 14px;
  color: #888;
  font-style: italic;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: 'Inter', sans-serif;
}

.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-ghost { background: transparent; border: 1px solid #ddd; color: #555; }
.btn-ghost:hover { border-color: #999; }
.btn-sm { padding: 8px 14px; font-size: 13px; }

.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: #2c3e50;
  color: #fff;
  padding: 14px 24px;
  border-radius: 8px;
  font-size: 14px;
  z-index: 2000;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}

.toast i { color: #27ae60; }

@media (max-width: 768px) {
  .branding-grid { grid-template-columns: 1fr; }
}
</style>
