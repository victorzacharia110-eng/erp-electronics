<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-store" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('storeSettings.title') }}</h1>
        <p>{{ $t('storeSettings.subtitle') }}</p>
      </div>
      <router-link to="/owner" class="back-btn"><i class="fas fa-arrow-left"></i> {{ $t('common.backToDashboard') }}</router-link>
    </div>

    <SkeletonLoader v-if="loading" type="list" :count="3" />

    <template v-else>
      <div v-if="businesses.length === 0" class="card empty-msg">{{ $t('storeSettings.noBusiness') }}</div>

      <template v-else>
        <div v-if="businesses.length > 1" class="business-select">
          <label>{{ $t('storeSettings.selectBusiness') }}</label>
          <select v-model="selectedId" class="form-select" @change="loadSelected">
            <option v-for="b in businesses" :key="b.id" :value="b.id">{{ b.store_name }}</option>
          </select>
        </div>

        <div class="settings-grid">
          <div class="card settings-card">
            <h3 class="section-title"><i class="fab fa-whatsapp"></i> {{ $t('storeSettings.whatsapp') }}</h3>
            <p class="section-desc">{{ $t('storeSettings.whatsappDesc') }}</p>
            <div class="form-group">
              <label>{{ $t('storeSettings.whatsappNumber') }}</label>
              <PhoneInput v-model="form.whatsapp_number" name="whatsapp_number" placeholder="7XX XXX XXX" />
            </div>
            <div class="form-group">
              <label>{{ $t('storeSettings.whatsappMessage') }}</label>
              <textarea v-model="form.whatsapp_default_message" rows="3" :placeholder="$t('storeSettings.whatsappMessagePlaceholder')"></textarea>
              <p v-if="whatsappPreview" class="hint"><i class="fab fa-whatsapp"></i> {{ whatsappPreview }}</p>
            </div>
          </div>

          <div class="card settings-card">
            <h3 class="section-title"><i class="fas fa-address-book"></i> {{ $t('storeSettings.contact') }}</h3>
            <p class="section-desc">{{ $t('storeSettings.contactDesc') }}</p>
            <div class="form-row">
              <div class="form-group"><label>{{ $t('storeSettings.contactPhone') }}</label><PhoneInput v-model="form.contact_phone" name="contact_phone" placeholder="7XX XXX XXX" /></div>
              <div class="form-group"><label>{{ $t('storeSettings.contactEmail') }}</label><input v-model="form.contact_email" type="email" :placeholder="$t('storeSettings.contactEmailPlaceholder')" /></div>
            </div>
            <div class="form-group"><label>{{ $t('storeSettings.address') }}</label><input v-model="form.address" type="text" :placeholder="$t('storeSettings.addressPlaceholder')" /></div>
          </div>

          <div class="card settings-card">
            <h3 class="section-title"><i class="fas fa-share-nodes"></i> {{ $t('storeSettings.social') }}</h3>
            <p class="section-desc">{{ $t('storeSettings.socialDesc') }}</p>
            <div class="form-group">
              <label><i class="fab fa-facebook"></i> Facebook</label>
              <input v-model="form.facebook_url" type="url" placeholder="https://facebook.com/yourstore" />
            </div>
            <div class="form-group">
              <label><i class="fab fa-instagram"></i> Instagram</label>
              <input v-model="form.instagram_url" type="url" placeholder="https://instagram.com/yourstore" />
            </div>
            <div class="form-group">
              <label><i class="fab fa-x-twitter"></i> X / Twitter</label>
              <input v-model="form.twitter_url" type="url" placeholder="https://x.com/yourstore" />
            </div>
            <div class="form-group">
              <label><i class="fab fa-tiktok"></i> TikTok</label>
              <input v-model="form.tiktok_url" type="url" placeholder="https://tiktok.com/@yourstore" />
            </div>
            <div class="form-group">
              <label><i class="fab fa-youtube"></i> YouTube</label>
              <input v-model="form.youtube_url" type="url" placeholder="https://youtube.com/@yourstore" />
            </div>
          </div>

          <button class="btn btn-primary" @click="save" :disabled="saving">
            <i class="fas fa-save"></i> {{ saving ? $t('common.saving') : $t('storeSettings.save') }}
          </button>
        </div>
      </template>
    </template>

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas fa-check-circle"></i> {{ toastMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { businessApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import PhoneInput from '@/components/PhoneInput.vue'
import { useBusinessStore } from '@/stores/business'

const { t } = useI18n()
const businessStore = useBusinessStore()
const loading = ref(true)
const saving = ref(false)
const toastMsg = ref('')
const businesses = ref([])
const selectedId = ref(null)

const form = ref({
  whatsapp_number: '',
  whatsapp_default_message: '',
  contact_phone: '',
  contact_email: '',
  address: '',
  facebook_url: '',
  instagram_url: '',
  twitter_url: '',
  tiktok_url: '',
  youtube_url: '',
})

const whatsappPreview = computed(() => {
  const digits = (form.value.whatsapp_number || '').replace(/[^\d]/g, '')
  if (!digits) return ''
  const msg = form.value.whatsapp_default_message?.trim() || t('storeSettings.defaultMessage', { store: currentBusiness.value?.store_name || '' })
  return `wa.me/${digits}?text=${encodeURIComponent(msg)}`
})

const currentBusiness = computed(() => businesses.value.find((b) => String(b.id) === String(selectedId.value)) || null)

function fill(b) {
  form.value = {
    whatsapp_number: b.whatsapp_number || '',
    whatsapp_default_message: b.whatsapp_default_message || '',
    contact_phone: b.contact_phone || '',
    contact_email: b.contact_email || '',
    address: b.address || '',
    facebook_url: b.social?.facebook || '',
    instagram_url: b.social?.instagram || '',
    twitter_url: b.social?.twitter || '',
    tiktok_url: b.social?.tiktok || '',
    youtube_url: b.social?.youtube || '',
  }
}

function loadSelected() {
  const b = currentBusiness.value
  if (b) fill(b)
}

function showToast(msg) { toastMsg.value = msg; setTimeout(() => toastMsg.value = '', 3000) }

async function save() {
  saving.value = true
  try {
    const b = currentBusiness.value
    if (!b) return
    const payload = {}
    for (const key of Object.keys(form.value)) {
      payload[key] = form.value[key].trim() === '' ? null : form.value[key].trim()
    }
    const res = await businessApi.update(b.id, payload)
    const updated = businesses.value.map((x) => String(x.id) === String(b.id) ? res.data : x)
    businesses.value = updated
    businessStore.syncBusiness(res.data)
    showToast(t('storeSettings.saved'))
  } catch (err) {
    showToast(err.response?.data?.message || t('storeSettings.saveError'))
  } finally { saving.value = false }
}

onMounted(async () => {
  try {
    const res = await businessApi.mine()
    businesses.value = res.data.data || []
    if (businesses.value.length) {
      selectedId.value = businesses.value[0].id
      fill(businesses.value[0])
    }
  } catch { /* empty */ }
  loading.value = false
})
</script>

<style scoped>
.dashboard-page { padding: 32px 0; }
.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.dash-header h1 { font-size: 26px; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 16px; border: 1px solid #ddd; border-radius: 6px; text-decoration: none; color: #333; font-size: 13px; font-weight: 500; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.business-select { margin-bottom: 20px; display: flex; align-items: center; gap: 12px; }
.business-select label { font-size: 13px; font-weight: 600; color: #555; }
.form-select { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; font-family: inherit; background: #fff; }

.settings-grid { display: flex; flex-direction: column; gap: 20px; max-width: 700px; }
.settings-card { padding: 24px; }
.section-title { font-size: 17px; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
.section-title i { color: #e74c3c; }
.section-desc { font-size: 13px; color: #888; margin-bottom: 16px; }

.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 4px; color: #555; }
.form-group label i { width: 16px; color: #e74c3c; }
.form-group input, .form-group textarea { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; font-family: inherit; box-sizing: border-box; }
.form-group textarea { resize: vertical; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: #e74c3c; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.hint { font-size: 12px; color: #27ae60; word-break: break-all; margin-top: 6px; }

.btn { padding: 12px 20px; border: none; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s; font-family: inherit; align-self: flex-start; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.empty-msg { text-align: center; color: #999; font-size: 14px; padding: 32px; }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #2c3e50; color: #fff; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 2000; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); animation: slideUp 0.3s ease; }
.toast i { color: #27ae60; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

@media (max-width: 768px) {
  .form-row { grid-template-columns: 1fr; }
}
</style>
