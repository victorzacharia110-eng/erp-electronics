<template>
  <div class="sa-profile-page">
    <div class="content-header">
      <div>
        <h3><i class="fas fa-user-circle" style="color: #e74c3c; margin-right: 8px;"></i>{{ $t('superadminProfile.title') }}</h3>
        <p class="muted">{{ $t('superadminProfile.subtitle') }}</p>
      </div>
    </div>

    <div class="profile-grid">
      <div class="card profile-card">
        <h4><i class="fas fa-id-card"></i> {{ $t('superadminProfile.accountInfo') }}</h4>
        <form @submit.prevent="updateProfile" novalidate>
          <div class="form-group">
            <label>{{ $t('account.name') }}</label>
            <input v-model="form.name" type="text" required />
          </div>
          <div class="form-group">
            <label>{{ $t('account.email') }}</label>
            <input v-model="form.email" type="email" required />
          </div>
          <div class="form-group">
            <label>{{ $t('account.phone') }}</label>
            <PhoneInput v-model="form.phone" name="phone" placeholder="7XX XXX XXX" />
          </div>
          <div class="meta-row">
            <span class="meta-item"><i class="fas fa-shield-halved"></i> {{ $t('superadminProfile.role') }}: <strong>Superadmin</strong></span>
            <span class="meta-item" v-if="authStore.user?.created_at"><i class="fas fa-calendar-plus"></i> {{ $t('superadminProfile.joined') }}: <strong>{{ formatDate(authStore.user.created_at) }}</strong></span>
          </div>
          <div v-if="errorMsg" class="server-error"><i class="fas fa-exclamation-circle"></i> {{ errorMsg }}</div>
          <div v-if="successMsg" class="success-msg"><i class="fas fa-check-circle"></i> {{ successMsg }}</div>
          <button type="submit" class="btn btn-primary" :disabled="saving">
            <i class="fas fa-save"></i> {{ saving ? $t('common.saving') : $t('superadminProfile.updateProfile') }}
          </button>
        </form>
      </div>

      <div class="card profile-card">
        <h4><i class="fas fa-key"></i> {{ $t('superadminProfile.changePassword') }}</h4>
        <p class="muted desc">Password must be at least 8 characters with uppercase, lowercase, numbers and symbols.</p>
        <ChangePasswordModal v-if="showPwModal" @close="showPwModal = false" />
        <button v-else class="btn btn-outline" @click="showPwModal = true">
          <i class="fas fa-key"></i> {{ $t('superadminProfile.changePassword') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import ChangePasswordModal from '@/components/ChangePasswordModal.vue'
import PhoneInput from '@/components/PhoneInput.vue'

const authStore = useAuthStore()
const { t } = useI18n()

const form = ref({ name: '', email: '', phone: '' })
const saving = ref(false)
const successMsg = ref('')
const errorMsg = ref('')
const showPwModal = ref(false)

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-TZ', { year: 'numeric', month: 'long', day: 'numeric' })
}

async function updateProfile() {
  saving.value = true
  successMsg.value = ''
  errorMsg.value = ''
  try {
    await authStore.updateProfile({ name: form.value.name, email: form.value.email, phone: form.value.phone })
    successMsg.value = t('superadminProfile.profileUpdated')
    setTimeout(() => successMsg.value = '', 3000)
  } catch (e) {
    errorMsg.value = e.response?.data?.message || t('superadminProfile.updateFailed')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try { await authStore.fetchProfile() } catch { /* empty */ }
  form.value.name = authStore.user?.name || ''
  form.value.email = authStore.user?.email || ''
  form.value.phone = authStore.user?.phone || ''
})
</script>

<style scoped>
.sa-profile-page { padding: 4px 0; }
.content-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.content-header h3 { font-size: 22px; font-weight: 700; }
.content-header .muted { color: #888; font-size: 14px; margin-top: 4px; }
.profile-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start; }
.profile-card { padding: 24px; }
.profile-card h4 { font-size: 16px; font-weight: 600; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; }
.profile-card h4 i { color: #e74c3c; }
.profile-card .desc { margin-bottom: 16px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; color: #555; margin-bottom: 6px; }
.form-group input { width: 100%; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; box-sizing: border-box; font-family: inherit; }
.form-group input:focus { outline: none; border-color: #e74c3c; }
.meta-row { display: flex; flex-wrap: wrap; gap: 16px; margin: 8px 0 20px; }
.meta-item { font-size: 13px; color: #888; display: inline-flex; align-items: center; gap: 6px; }
.meta-item i { color: #e74c3c; }
.server-error { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #fef5f5; border: 1px solid #fdd; border-radius: 6px; color: #c0392b; font-size: 13px; font-weight: 500; margin-bottom: 12px; }
.success-msg { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #eafaf1; border: 1px solid #d5f5e3; border-radius: 6px; color: #27ae60; font-size: 13px; font-weight: 500; margin-bottom: 12px; }
.card { background: #fff; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 13px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; }
.btn-outline:hover { border-color: #999; }
@media (max-width: 768px) { .profile-grid { grid-template-columns: 1fr; } }
</style>
