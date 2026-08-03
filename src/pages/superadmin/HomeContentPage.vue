<template>
  <div class="home-content-page">
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i> Loading...
    </div>

    <template v-else>
      <div class="content-header">
        <div>
          <h3>{{ $t('homeContent.title') }}</h3>
          <p class="muted">{{ $t('homeContent.subtitle') }}</p>
        </div>
        <button class="btn btn-primary btn-sm" @click="saveAll" :disabled="saving">
          <i class="fas fa-save"></i>
          {{ saving ? $t('homeContent.saving') : $t('homeContent.saveAll') }}
        </button>
      </div>

      <div v-for="section in sections" :key="section.key" class="card content-section">
        <h4><i :class="section.icon"></i> {{ $t(`homeContent.sections.${section.key}`) }}</h4>
        <div class="locale-header">
          <span class="locale-tag en">{{ $t('homeContent.en') }}</span>
          <span class="locale-tag sw">{{ $t('homeContent.sw') }}</span>
        </div>
        <div v-for="field in section.fields" :key="field" class="form-group">
          <label>{{ $t(`homeContent.fields.${field}`) }}</label>
          <div class="lang-row">
            <input v-model="form.en[field]" type="text" :placeholder="$t('homeContent.enPlaceholder')" />
            <input v-model="form.sw[field]" type="text" :placeholder="$t('homeContent.swPlaceholder')" />
          </div>
        </div>
      </div>

      <div class="save-footer">
        <button class="btn btn-primary" @click="saveAll" :disabled="saving">
          <i class="fas fa-save"></i>
          {{ saving ? $t('homeContent.saving') : $t('homeContent.saveAll') }}
        </button>
      </div>
    </template>

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas" :class="toastError ? 'fa-circle-xmark' : 'fa-check-circle'"></i> {{ toastMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { superadminApi } from '@/api'

const loading = ref(true)
const saving = ref(false)
const toastMsg = ref('')
const toastError = ref(false)

const form = ref({ en: {}, sw: {} })

const sections = [
  {
    key: 'hero',
    icon: 'fas fa-star',
    fields: ['heroBadge', 'heroTitle', 'heroTitleHighlight', 'heroDesc', 'shopNow', 'viewCatalog'],
  },
  {
    key: 'features',
    icon: 'fas fa-truck-fast',
    fields: ['freeDelivery', 'freeDeliveryDesc', 'securePayment', 'securePaymentDesc', 'easyReturns', 'easyReturnsDesc', 'support247', 'support247Desc'],
  },
  {
    key: 'categories',
    icon: 'fas fa-layer-group',
    fields: ['shopByCategory', 'browseCategories', 'productsCount', 'categoriesComingSoon'],
  },
  {
    key: 'newArrivals',
    icon: 'fas fa-box-open',
    fields: ['newArrivals', 'newArrivalsDesc', 'noProductsYet', 'viewMoreProducts'],
  },
  {
    key: 'promo',
    icon: 'fas fa-fire',
    fields: ['hotDeals', 'hotDealsTitle', 'hotDealsDesc', 'shopTheSale'],
  },
  {
    key: 'hotSelling',
    icon: 'fas fa-chart-line',
    fields: ['hotSelling', 'hotSellingDesc', 'viewAllProducts'],
  },
  {
    key: 'cta',
    icon: 'fas fa-bullhorn',
    fields: ['createAccount', 'createAccountDesc', 'register', 'mobileMoney', 'mobileMoneyDesc', 'fastDeliveryTitle', 'fastDeliveryDesc'],
  },
  {
    key: 'directory',
    icon: 'fas fa-store',
    fields: ['dirBadge', 'dirTitle', 'dirSubtitle', 'dirProductsCount', 'dirVisitStore', 'dirEmpty', 'dirNew', 'dirNewArrivals'],
  },
]

async function loadContent() {
  try {
    const res = await superadminApi.getHomeContent()
    form.value = {
      en: { ...(res.data.en || {}) },
      sw: { ...(res.data.sw || {}) },
    }
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

async function saveAll() {
  saving.value = true
  toastMsg.value = ''
  try {
    await superadminApi.updateHomeContent({
      en: form.value.en,
      sw: form.value.sw,
    })
    toastError.value = false
    toastMsg.value = 'Home content saved'
    await loadContent()
  } catch {
    toastError.value = true
    toastMsg.value = 'Failed to save home content'
  }
  saving.value = false
  setTimeout(() => (toastMsg.value = ''), 3000)
}

onMounted(loadContent)
</script>

<style scoped>
.home-content-page { max-width: 1000px; }

.loading-state {
  text-align: center;
  padding: 64px;
  color: #888;
  font-size: 16px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.content-header h3 { font-size: 22px; }
.muted { color: #888; font-size: 14px; }

.content-section {
  padding: 24px;
  margin-bottom: 20px;
}

.content-section h4 {
  font-size: 15px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.content-section h4 i { color: #e74c3c; }

.locale-header {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 8px;
}

.locale-tag {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  text-align: center;
  padding: 3px 0;
  border-radius: 4px;
}

.locale-tag.en { background: #eef2ff; color: #4f46e5; }
.locale-tag.sw { background: #f0fdf4; color: #16a34a; }

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

.lang-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.lang-row input {
  width: 100%;
  padding: 8px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  box-sizing: border-box;
}

.lang-row input:focus {
  outline: none;
  border-color: #e74c3c;
}

.save-footer {
  text-align: right;
  margin-bottom: 24px;
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

.toast i.fa-check-circle { color: #27ae60; }
.toast i.fa-circle-xmark { color: #e74c3c; }

@media (max-width: 768px) {
  .content-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .lang-row { grid-template-columns: 1fr; }
  .locale-header { grid-template-columns: 1fr 1fr; }
}
</style>
