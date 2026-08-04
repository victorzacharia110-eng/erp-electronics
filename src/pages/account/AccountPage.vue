<template>
  <div class="account-page container">
    <h1 class="page-title">{{ $t('account.title') }}</h1>
    <SkeletonLoader v-if="loading" type="text" :count="1" />

    <div v-else class="account-layout">
      <div class="card form-section">
        <h2><i class="fas fa-user-pen"></i> {{ $t('account.profile') }}</h2>
        <form @submit.prevent="updateProfile">
          <div class="form-group"><label>{{ $t('account.name') }}</label><input v-model="form.name" type="text" /></div>
          <div class="form-group"><label>{{ $t('account.email') }}</label><input v-model="form.email" type="email" /></div>
          <div class="form-group"><label>{{ $t('account.phone') }}</label><input v-model="form.phone" type="tel" /></div>
          <template v-if="authStore.isOwner">
            <div class="form-group"><label>Store Name</label><input v-model="form.brand_store_name" type="text" disabled /></div>
            <div class="form-group"><label>Tagline</label><input v-model="form.brand_tagline" type="text" disabled /></div>
            <div class="form-group"><label>Brand Color</label><input v-model="form.brand_color" type="text" disabled /></div>
            <div class="form-group"><label>Secondary Color</label><input v-model="form.brand_color_secondary" type="text" disabled /></div>
            <p v-if="form.brand_color" class="color-preview">
              <span class="color-swatch" :style="{ background: form.brand_color }"></span>
              {{ form.brand_color }}
            </p>
            <div class="divider"></div>
            <div class="form-group"><label><i class="fab fa-whatsapp"></i> {{ $t('account.whatsappNumber') }}</label><input v-model="form.whatsapp_number" type="tel" :placeholder="'+255 700 000 000'" /></div>
            <div class="form-group"><label>{{ $t('account.whatsappMessage') }}</label><textarea v-model="form.whatsapp_default_message" rows="2" maxlength="500"></textarea></div>
            <p class="help-text"><i class="fas fa-info-circle"></i> {{ $t('account.whatsappHelp') }}</p>
          </template>
          <button type="submit" class="btn btn-primary btn-sm" :disabled="saving"><i class="fas fa-save"></i> {{ saving ? t('common.saving') : t('account.updateProfile') }}</button>
          <p v-if="message" class="success"><i class="fas fa-check-circle"></i> {{ message }}</p>
        </form>
      </div>
      <div class="card form-section">
        <h2><i class="fas fa-location-dot"></i> {{ $t('account.addresses') }}</h2>
        <div v-for="addr in addresses" :key="addr.id" class="address-card">
          <div><strong>{{ addr.label || $t('account.address') }}</strong><p>{{ addr.street }}, {{ addr.city }}, {{ addr.country }}</p></div>
          <button class="remove-btn" @click="deleteAddress(addr.id)"><i class="fas fa-trash"></i></button>
        </div>
        <button @click="showAddForm = !showAddForm" class="btn btn-outline btn-sm" style="margin-top:12px"><i class="fas" :class="showAddForm ? 'fa-times' : 'fa-plus'"></i> {{ showAddForm ? t('common.cancel') : t('account.addAddress') }}</button>
        <form v-if="showAddForm" @submit.prevent="addAddress" class="add-form">
          <div class="form-group"><label>{{ $t('account.addressLabel') }}</label><input v-model="newAddress.label" type="text" :placeholder="$t('account.addressLabelPlaceholder')" /></div>
          <div class="form-group"><label>{{ $t('account.addressStreet') }}</label><input v-model="newAddress.street" type="text" required /></div>
          <div class="form-group"><label>{{ $t('account.addressCity') }}</label><input v-model="newAddress.city" type="text" required /></div>
          <div class="form-group"><label>{{ $t('account.addressCountry') }}</label><input v-model="newAddress.country" type="text" /></div>
          <button type="submit" class="btn btn-primary btn-sm"><i class="fas fa-save"></i> {{ $t('common.save') }}</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
const { t } = useI18n()
import { addressApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
const authStore = useAuthStore()
const loading = ref(true)
const form = ref({ name: '', email: '', phone: '', brand_store_name: '', brand_tagline: '', brand_color: '', brand_color_secondary: '', whatsapp_number: '', whatsapp_default_message: '' })
const addresses = ref([])
const newAddress = ref({ label: '', street: '', city: '', country: 'Tanzania' })
const showAddForm = ref(false)
const saving = ref(false)
const message = ref('')
onMounted(async () => { try { await authStore.fetchProfile(); form.value.name = authStore.user?.name || ''; form.value.email = authStore.user?.email || ''; form.value.phone = authStore.user?.phone || ''; if (authStore.isOwner) { const p = authStore.user?.owner_profile; form.value.brand_store_name = p?.brand_store_name || ''; form.value.brand_tagline = p?.brand_tagline || ''; form.value.brand_color = p?.brand_color || ''; form.value.brand_color_secondary = p?.brand_color_secondary || ''; form.value.whatsapp_number = p?.whatsapp_number || ''; form.value.whatsapp_default_message = p?.whatsapp_default_message || '' }; const r = await addressApi.getAll(); addresses.value = r.data } finally { loading.value = false } })
async function updateProfile() { saving.value = true; message.value = ''; try { await authStore.updateProfile(form.value); message.value = t('account.profileUpdated') } finally { saving.value = false } }
async function addAddress() { const r = await addressApi.create(newAddress.value); addresses.value.push(r.data); newAddress.value = { label: '', street: '', city: '', country: 'Tanzania' }; showAddForm.value = false }
async function deleteAddress(id) { await addressApi.delete(id); addresses.value = addresses.value.filter(a => a.id !== id) }
</script>

<style scoped>
.account-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start; }
.form-section { padding: 24px; }
.form-section h2 { font-size: 18px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
.form-section h2 i { color: #e74c3c; }
.success { color: #27ae60; margin-top: 12px; font-size: 14px; display: flex; align-items: center; gap: 8px; }
.address-card { display: flex; align-items: center; justify-content: space-between; padding: 14px; border: 1px solid #eee; border-radius: 8px; margin-bottom: 8px; }
.address-card strong { display: block; margin-bottom: 4px; }
.address-card p { font-size: 13px; color: #888; }
.remove-btn { color: #ccc; padding: 8px; }
.remove-btn:hover { color: #e74c3c; }
.add-form { margin-top: 16px; }
.color-preview { display: flex; align-items: center; gap: 8px; margin-top: 4px; font-size: 13px; color: #666; }
.color-swatch { display: inline-block; width: 20px; height: 20px; border-radius: 4px; border: 1px solid #ddd; }
.divider { border-top: 1px solid #eee; margin: 16px 0; }
.help-text { font-size: 12px; color: #888; display: flex; align-items: flex-start; gap: 6px; margin-top: 4px; }
.help-text i { color: #25d366; margin-top: 2px; }
.form-group textarea { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; font-family: inherit; resize: vertical; }
@media (max-width: 768px) { .account-layout { grid-template-columns: 1fr; } }
</style>
