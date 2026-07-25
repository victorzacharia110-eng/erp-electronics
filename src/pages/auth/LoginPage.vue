<template>
  <div class="auth-page">
    <div class="auth-card card">
      <div class="auth-header">
        <span class="logo-icon"><i class="fas fa-bolt"></i></span>
        <h1>{{ $t('auth.loginTitle') }}</h1>
        <p>{{ $t('auth.loginSubtitle') }}</p>
      </div>
      <form @submit.prevent="handleLogin" novalidate>
        <div class="form-group" :class="{ 'has-error': errors.email }">
          <label>{{ $t('auth.email') }}</label>
          <input v-model="form.email" type="email" :placeholder="$t('auth.emailPlaceholder')" @blur="touch('email')"
            @input="validateField('email')" />
          <span class="field-error" v-if="errors.email"><i class="fas fa-exclamation-triangle"></i> {{ errors.email
            }}</span>
        </div>

        <div class="form-group" :class="{ 'has-error': errors.password }">
          <label>{{ $t('common.password') }}</label>
          <div class="password-input-wrap">
            <input v-model="form.password" :type="showPw ? 'text' : 'password'"
              :placeholder="$t('auth.passwordPlaceholder')" @blur="touch('password')"
              @input="validateField('password')" />
            <button type="button" class="pw-toggle" @click="showPw = !showPw"><i
                :class="showPw ? 'fas fa-eye-slash' : 'fas fa-eye'"></i></button>
          </div>
          <span class="field-error" v-if="errors.password"><i class="fas fa-exclamation-triangle"></i> {{
            errors.password }}</span>
        </div>

        <div class="server-errors" v-if="serverErrors.length > 0">
          <div v-for="(msg, i) in serverErrors" :key="i" class="server-error"><i class="fas fa-exclamation-circle"></i>
            {{ msg }}</div>
        </div>

        <button type="submit" class="btn btn-primary full-width" :disabled="loading"><i
            class="fas fa-right-to-bracket"></i> {{ loading ? t('auth.signInLoading') : t('auth.signIn') }}</button>
      </form>
      <p class="auth-link">{{ $t('auth.noAccount') }} <router-link to="/register">{{ $t('auth.registerHere')
          }}</router-link></p>
      <p class="auth-link home-link"><router-link to="/"><i class="fas fa-arrow-left"></i> {{ $t('common.backToHome')
          }}</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({ email: '', password: '' })
const errors = ref({})
const serverErrors = ref([])
const touched = ref({})
const loading = ref(false)
const showPw = ref(false)

function touch(field) { touched.value[field] = true }

function validateField(field) {
  if (!touched.value[field] && !form.value[field]) return

  switch (field) {
    case 'email':
      if (!form.value.email.trim()) errors.value.email = t('auth.validation.emailRequired')
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) errors.value.email = t('auth.validation.emailInvalid')
      else delete errors.value.email
      break

    case 'password':
      if (!form.value.password) errors.value.password = t('auth.validation.passwordRequired')
      else delete errors.value.password
      break
  }
}

function validateAll() {
  ;['email', 'password'].forEach(f => { touched.value[f] = true; validateField(f) })
  return !errors.value.email && !errors.value.password
}

async function handleLogin() {
  serverErrors.value = []
  if (!validateAll()) return

  loading.value = true
  try {
    await authStore.login(form.value)
    const redirect = route.query.redirect
    if (redirect) {
      router.push(redirect)
    } else if (authStore.isSuperadmin) {
      router.push('/superadmin')
    } else {
      router.push('/')
    }
  } catch (e) {
    if (e.response?.data?.message) {
      const msg = e.response.data.message
      if (msg === 'Invalid credentials') serverErrors.value = [t('auth.serverErrors.invalidCredentials')]
      else if (msg === 'Account is deactivated') serverErrors.value = [t('auth.serverErrors.deactivated')]
      else serverErrors.value = [msg]
    } else {
      serverErrors.value = [t('auth.serverErrors.connectionFailed')]
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  padding: 40px;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-header .logo-icon {
  display: inline-flex;
  color: #fff;
  background: #e74c3c;
  border-radius: 10px;
  justify-content: center;
  align-items: center;
  width: 48px;
  height: 48px;
  font-size: 20px;
  margin-bottom: 16px;
}

.auth-header h1 {
  font-size: 24px;
  margin-bottom: 8px;
}

.auth-header p {
  color: #888;
  font-size: 14px;
}

.full-width {
  width: 100%;
  justify-content: center;
  padding: 14px;
  margin-top: 8px;
}

.auth-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #888;
}

.auth-link a {
  color: #e74c3c;
  font-weight: 600;
}

.home-link {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
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
</style>
