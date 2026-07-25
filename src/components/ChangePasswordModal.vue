<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card card">
      <div class="modal-header">
        <h2><i class="fas fa-key"></i> {{ $t('changePassword.title') }}</h2>
        <p>{{ $t('changePassword.subtitle') }}</p>
      </div>
      <form @submit.prevent="handleChange" novalidate>
        <div class="form-group" :class="{ 'has-error': errors.current_password }">
          <label>{{ $t('changePassword.currentPassword') }}</label>
          <div class="password-input-wrap">
            <input v-model="form.current_password" :type="showCurrent ? 'text' : 'password'"
              :placeholder="$t('changePassword.currentPasswordPlaceholder')" @blur="touch('current_password')"
              @input="validateField('current_password')" />
            <button type="button" class="pw-toggle" @click="showCurrent = !showCurrent"><i
                :class="showCurrent ? 'fas fa-eye-slash' : 'fas fa-eye'"></i></button>
          </div>
          <span class="field-error" v-if="errors.current_password"><i class="fas fa-exclamation-triangle"></i> {{
            errors.current_password }}</span>
        </div>

        <div class="form-group" :class="{ 'has-error': errors.password }">
          <label>{{ $t('changePassword.newPassword') }}</label>
          <div class="password-input-wrap">
            <input v-model="form.password" :type="showPw ? 'text' : 'password'"
              :placeholder="$t('changePassword.newPasswordPlaceholder')" @blur="touch('password')" @input="validateField('password')" />
            <button type="button" class="pw-toggle" @click="showPw = !showPw"><i
                :class="showPw ? 'fas fa-eye-slash' : 'fas fa-eye'"></i></button>
          </div>
          <div class="password-rules" v-if="form.password.length > 0">
            <span :class="pwRules.length ? 'valid' : 'invalid'"><i
                :class="pwRules.length ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> {{ $t('changePassword.passwordRules.length') }}</span>
            <span :class="pwRules.uppercase ? 'valid' : 'invalid'"><i
                :class="pwRules.uppercase ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> {{ $t('changePassword.passwordRules.uppercase') }}</span>
            <span :class="pwRules.lowercase ? 'valid' : 'invalid'"><i
                :class="pwRules.lowercase ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> {{ $t('changePassword.passwordRules.lowercase') }}</span>
            <span :class="pwRules.number ? 'valid' : 'invalid'"><i
                :class="pwRules.number ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> {{ $t('changePassword.passwordRules.number') }}</span>
            <span :class="pwRules.symbol ? 'valid' : 'invalid'"><i
                :class="pwRules.symbol ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> {{ $t('changePassword.passwordRules.symbol') }}</span>
          </div>
          <span class="field-error" v-if="errors.password"><i class="fas fa-exclamation-triangle"></i> {{
            errors.password }}</span>
        </div>

        <div class="form-group" :class="{ 'has-error': errors.password_confirmation }">
          <label>{{ $t('changePassword.confirmNewPassword') }}</label>
          <div class="password-input-wrap">
            <input v-model="form.password_confirmation" :type="showConfirm ? 'text' : 'password'"
              :placeholder="$t('changePassword.confirmNewPasswordPlaceholder')" @blur="touch('password_confirmation')"
              @input="validateField('password_confirmation')" />
            <button type="button" class="pw-toggle" @click="showConfirm = !showConfirm"><i
                :class="showConfirm ? 'fas fa-eye-slash' : 'fas fa-eye'"></i></button>
          </div>
          <span class="field-error" v-if="errors.password_confirmation"><i class="fas fa-exclamation-triangle"></i> {{
            errors.password_confirmation }}</span>
        </div>

        <div class="server-errors" v-if="serverErrors.length > 0">
          <div v-for="(msg, i) in serverErrors" :key="i" class="server-error"><i class="fas fa-exclamation-circle"></i>
            {{ msg }}</div>
        </div>

        <div class="success-msg" v-if="success"><i class="fas fa-check-circle"></i> {{ success }}</div>

        <button type="submit" class="btn btn-primary full-width" :disabled="loading || !canSubmit">
          <i class="fas fa-save"></i> {{ loading ? $t('changePassword.updating') : $t('changePassword.updateBtn') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

const emit = defineEmits(['close'])
const authStore = useAuthStore()
const { t } = useI18n()

const form = ref({ current_password: '', password: '', password_confirmation: '' })
const errors = ref({})
const serverErrors = ref([])
const success = ref('')
const touched = ref({})
const loading = ref(false)
const showCurrent = ref(false)
const showPw = ref(false)
const showConfirm = ref(false)

function touch(field) { touched.value[field] = true }

const pwRules = computed(() => ({
  length: form.value.password.length >= 8,
  uppercase: /[A-Z]/.test(form.value.password),
  lowercase: /[a-z]/.test(form.value.password),
  number: /[0-9]/.test(form.value.password),
  symbol: /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?`~]/.test(form.value.password),
}))

const allPwValid = computed(() => Object.values(pwRules.value).every(Boolean))

const canSubmit = computed(() => {
  return form.value.current_password && form.value.password && form.value.password_confirmation && allPwValid.value && form.value.password === form.value.password_confirmation
})

function validateField(field) {
  switch (field) {
    case 'current_password':
      if (!form.value.current_password) errors.value.current_password = t('changePassword.validation.currentPasswordRequired')
      else delete errors.value.current_password
      break
    case 'password':
      if (!form.value.password) errors.value.password = t('changePassword.validation.newPasswordRequired')
      else if (!allPwValid.value) errors.value.password = t('changePassword.validation.passwordInvalid')
      else delete errors.value.password
      break
    case 'password_confirmation':
      if (!form.value.password_confirmation) errors.value.password_confirmation = t('changePassword.validation.passwordConfirmRequired')
      else if (form.value.password !== form.value.password_confirmation) errors.value.password_confirmation = t('changePassword.validation.passwordMismatch')
      else delete errors.value.password_confirmation
      break
  }
}

function validateAll() {
  ;['current_password', 'password', 'password_confirmation'].forEach(f => { touched.value[f] = true; validateField(f) })
  return !errors.value.current_password && !errors.value.password && !errors.value.password_confirmation
}

async function handleChange() {
  serverErrors.value = []
  success.value = ''
  if (!validateAll()) return

  loading.value = true
  try {
    await authStore.changePassword(form.value)
    success.value = t('changePassword.updatedSuccess')
    setTimeout(() => emit('close'), 1500)
  } catch (e) {
    if (e.response?.data?.message) {
      const msg = e.response.data.message
      if (msg === 'Current password is incorrect') serverErrors.value = [t('changePassword.currentPasswordIncorrect')]
      else serverErrors.value = [msg]
    } else {
      serverErrors.value = [t('changePassword.updateFailed')]
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

.modal-card {
  width: 100%;
  max-width: 440px;
  padding: 32px;
}

.modal-header {
  margin-bottom: 24px;
}

.modal-header h2 {
  font-size: 20px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-header h2 i {
  color: #e74c3c;
}

.modal-header p {
  color: #888;
  font-size: 13px;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
}

.form-group input {
  width: 100%;
  padding: 12px 14px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #e74c3c;
}

.form-group.has-error input {
  border-color: #e74c3c;
  background: #fef8f8;
}

.password-input-wrap {
  position: relative;
}

.password-input-wrap input {
  padding-right: 44px;
}

.pw-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 16px;
}

.pw-toggle:hover {
  color: #333;
}

.field-error {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  font-size: 12px;
  color: #e74c3c;
  font-weight: 500;
}

.field-error i {
  font-size: 11px;
}

.password-rules {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-top: 10px;
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

.password-rules span {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: color 0.2s;
}

.password-rules span.valid {
  color: #27ae60;
}

.password-rules span.invalid {
  color: #bbb;
}

.password-rules span i {
  font-size: 11px;
  width: 14px;
}

.full-width {
  width: 100%;
  justify-content: center;
  padding: 14px;
  margin-top: 8px;
}

.server-errors {
  margin-bottom: 12px;
}

.server-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #fef5f5;
  border: 1px solid #fdd;
  border-radius: 6px;
  color: #c0392b;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
}

.server-error i {
  font-size: 12px;
  flex-shrink: 0;
}

.success-msg {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #eafaf1;
  border: 1px solid #d5f5e3;
  border-radius: 6px;
  color: #27ae60;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 12px;
}

.success-msg i {
  font-size: 12px;
}
</style>
