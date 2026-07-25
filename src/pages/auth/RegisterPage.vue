<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-header">
        <span class="logo-icon"><i class="fas fa-bolt"></i></span>
        <h1>{{ $t('auth.registerTitle') }}</h1>
        <p>{{ $t('auth.registerSubtitle') }}</p>
      </div>
      <form @submit.prevent="handleRegister" novalidate>
        <div class="form-group" :class="{ 'has-error': errors.name }">
          <label>{{ $t('auth.fullName') }}</label>
          <input v-model="form.name" type="text" :placeholder="$t('auth.fullNamePlaceholder')" @blur="touch('name')" @input="validateField('name')" />
          <span class="field-error" v-if="errors.name"><i class="fas fa-exclamation-triangle"></i> {{ errors.name }}</span>
        </div>

        <div class="form-group" :class="{ 'has-error': errors.email }">
          <label>{{ $t('auth.email') }}</label>
          <input v-model="form.email" type="email" :placeholder="$t('auth.emailPlaceholder')" @blur="touch('email')" @input="validateField('email')" />
          <span class="field-error" v-if="errors.email"><i class="fas fa-exclamation-triangle"></i> {{ errors.email }}</span>
        </div>

        <div class="form-group" :class="{ 'has-error': errors.phone }">
          <label>{{ $t('auth.phone') }}</label>
          <input v-model="form.phone" type="tel" :placeholder="$t('auth.phonePlaceholder')" @blur="touch('phone')" @input="validateField('phone')" />
          <span class="field-error" v-if="errors.phone"><i class="fas fa-exclamation-triangle"></i> {{ errors.phone }}</span>
        </div>

        <div class="form-group" :class="{ 'has-error': errors.password }">
          <label>{{ $t('common.password') }}</label>
          <div class="password-input-wrap">
            <input v-model="form.password" :type="showPw ? 'text' : 'password'" :placeholder="$t('auth.createPassword')" @blur="touch('password')" @input="validateField('password')" />
            <button type="button" class="pw-toggle" @click="showPw = !showPw"><i :class="showPw ? 'fas fa-eye-slash' : 'fas fa-eye'"></i></button>
          </div>
          <div class="password-rules" v-if="form.password.length > 0">
            <span :class="pwRules.length ? 'valid' : 'invalid'"><i :class="pwRules.length ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> {{ $t('auth.passwordRules.length') }}</span>
            <span :class="pwRules.uppercase ? 'valid' : 'invalid'"><i :class="pwRules.uppercase ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> {{ $t('auth.passwordRules.uppercase') }}</span>
            <span :class="pwRules.lowercase ? 'valid' : 'invalid'"><i :class="pwRules.lowercase ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> {{ $t('auth.passwordRules.lowercase') }}</span>
            <span :class="pwRules.number ? 'valid' : 'invalid'"><i :class="pwRules.number ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> {{ $t('auth.passwordRules.number') }}</span>
            <span :class="pwRules.symbol ? 'valid' : 'invalid'"><i :class="pwRules.symbol ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> {{ $t('auth.passwordRules.symbol') }}</span>
          </div>
          <span class="field-error" v-if="errors.password"><i class="fas fa-exclamation-triangle"></i> {{ errors.password }}</span>
        </div>

        <div class="form-group" :class="{ 'has-error': errors.password_confirmation }">
          <label>{{ $t('auth.confirmPassword') }}</label>
          <div class="password-input-wrap">
            <input v-model="form.password_confirmation" :type="showConfirm ? 'text' : 'password'" :placeholder="$t('auth.reenterPassword')" @blur="touch('password_confirmation')" @input="validateField('password_confirmation')" />
            <button type="button" class="pw-toggle" @click="showConfirm = !showConfirm"><i :class="showConfirm ? 'fas fa-eye-slash' : 'fas fa-eye'"></i></button>
          </div>
          <span class="field-error" v-if="errors.password_confirmation"><i class="fas fa-exclamation-triangle"></i> {{ errors.password_confirmation }}</span>
        </div>

        <div class="server-errors" v-if="serverErrors.length > 0">
          <div v-for="(msg, i) in serverErrors" :key="i" class="server-error"><i class="fas fa-exclamation-circle"></i> {{ msg }}</div>
        </div>

        <button type="submit" class="btn btn-primary full-width" :disabled="loading">
          <i class="fas fa-user-plus"></i> {{ loading ? t('auth.createAccountLoading') : t('auth.createAccountBtn') }}
        </button>
      </form>
      <p class="auth-link">{{ $t('auth.hasAccount') }} <router-link to="/login">{{ $t('auth.loginHere') }}</router-link></p>
      <p class="auth-link home-link"><router-link to="/"><i class="fas fa-arrow-left"></i> {{ $t('common.backToHome') }}</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const form = ref({ name: '', email: '', phone: '', password: '', password_confirmation: '' })
const errors = ref({})
const serverErrors = ref([])
const touched = ref({})
const loading = ref(false)
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

function validateField(field) {
  if (!touched.value[field] && !form.value[field]) return

  const v = form.value
  switch (field) {
    case 'name':
      if (!v.name.trim()) errors.value.name = t('auth.validation.nameRequired')
      else if (v.name.trim().length < 2) errors.value.name = t('auth.validation.nameTooShort')
      else if (v.name.trim().length > 255) errors.value.name = t('auth.validation.nameTooLong')
      else delete errors.value.name
      break

    case 'email':
      if (!v.email.trim()) errors.value.email = t('auth.validation.emailRequired')
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.email)) errors.value.email = t('auth.validation.emailInvalid')
      else delete errors.value.email
      break

    case 'phone':
      if (!v.phone.trim()) errors.value.phone = t('auth.validation.phoneRequired')
      else if (!/^[+]?[\d\s\-()]{7,20}$/.test(v.phone)) errors.value.phone = t('auth.validation.phoneInvalid')
      else delete errors.value.phone
      break

    case 'password':
      if (!v.password) errors.value.password = t('auth.validation.passwordRequired')
      else if (!allPwValid.value) errors.value.password = t('auth.validation.passwordInvalid')
      else delete errors.value.password
      break

    case 'password_confirmation':
      if (!v.password_confirmation) errors.value.password_confirmation = t('auth.validation.passwordConfirmRequired')
      else if (v.password !== v.password_confirmation) errors.value.password_confirmation = t('auth.validation.passwordMismatch')
      else delete errors.value.password_confirmation
      break
  }
}

function validateAll() {
  const fields = ['name', 'email', 'phone', 'password', 'password_confirmation']
  fields.forEach(f => { touched.value[f] = true; validateField(f) })
  return fields.every(f => !errors.value[f])
}

async function handleRegister() {
  serverErrors.value = []
  if (!validateAll()) return

  loading.value = true
  try {
    await authStore.register(form.value)
    router.push('/')
  } catch (e) {
    if (e.response?.data?.errors) {
      const msgs = e.response.data.errors
      serverErrors.value = Object.entries(msgs).map(([field, arr]) => {
        const label = { name: 'Name', email: 'Email', phone: 'Phone', password: 'Password', password_confirmation: 'Password confirmation' }[field] || field
        return `${label}: ${arr[0]}`
      })
    } else {
      serverErrors.value = [e.response?.data?.message || t('auth.serverErrors.registrationFailed')]
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f8f9fa; padding: 24px; }
.auth-card { width: 100%; max-width: 480px; padding: 40px; }
.auth-header { text-align: center; margin-bottom: 32px; }
.auth-header .logo-icon { display: inline-flex; color: #fff; background: #e74c3c; border-radius: 10px; justify-content: center; align-items: center; width: 48px; height: 48px; font-size: 20px; margin-bottom: 16px; }
.auth-header h1 { font-size: 24px; margin-bottom: 8px; }
.auth-header p { color: #888; font-size: 14px; }
.optional { color: #aaa; font-weight: 400; font-size: 12px; }
.full-width { width: 100%; justify-content: center; padding: 14px; margin-top: 12px; }
.auth-link { text-align: center; margin-top: 20px; font-size: 14px; color: #888; }
.auth-link a { color: #e74c3c; font-weight: 600; }
.home-link { margin-top: 12px; padding-top: 12px; border-top: 1px solid #f0f0f0; }

.form-group { margin-bottom: 18px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; color: #333; margin-bottom: 6px; }
.form-group input { width: 100%; padding: 12px 14px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; font-family: 'Inter', sans-serif; transition: border-color 0.2s; box-sizing: border-box; }
.form-group input:focus { outline: none; border-color: #e74c3c; }
.form-group.has-error input { border-color: #e74c3c; background: #fef8f8; }

.password-input-wrap { position: relative; }
.password-input-wrap input { padding-right: 44px; }
.pw-toggle { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #999; cursor: pointer; font-size: 16px; }
.pw-toggle:hover { color: #333; }

.field-error { display: flex; align-items: center; gap: 6px; margin-top: 6px; font-size: 12px; color: #e74c3c; font-weight: 500; }
.field-error i { font-size: 11px; }

.password-rules { display: flex; flex-direction: column; gap: 5px; margin-top: 10px; padding: 12px; background: #fafafa; border-radius: 6px; border: 1px solid #f0f0f0; }
.password-rules span { font-size: 12px; display: flex; align-items: center; gap: 6px; transition: color 0.2s; }
.password-rules span.valid { color: #27ae60; }
.password-rules span.invalid { color: #bbb; }
.password-rules span i { font-size: 11px; width: 14px; }

.server-errors { margin-bottom: 12px; }
.server-error { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #fef5f5; border: 1px solid #fdd; border-radius: 6px; color: #c0392b; font-size: 13px; font-weight: 500; margin-bottom: 6px; }
.server-error i { font-size: 12px; flex-shrink: 0; }
</style>
