<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <span class="logo-icon"><i class="fas fa-bolt"></i></span>
        <h1>{{ $t('sso.signingIn') }}</h1>
        <p>{{ $t('sso.signingInSubtitle') }}</p>
        <div v-if="error" class="server-error">
          <i class="fas fa-exclamation-circle"></i> {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const error = ref('')

function dashboardFor(role) {
  switch (role) {
    case 'superadmin':
      return '/superadmin'
    case 'owner':
      return '/owner'
    case 'employee':
      return '/employee'
    case 'customer':
      return '/customer'
    default:
      return '/'
  }
}

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const ssoError = params.get('sso_error')

  if (ssoError) {
    error.value = t(`sso.errors.${ssoError}`)
    return
  }

  const hashParams = new URLSearchParams(window.location.hash.slice(1))
  const token = hashParams.get('token')

  if (!token) {
    error.value = t('sso.errors.missingToken')
    return
  }

  try {
    const user = await authStore.ssoLogin(token)
    const redirect = params.get('redirect')
    router.replace(redirect || dashboardFor(user?.role))
  } catch {
    error.value = t('sso.errors.connectionFailed')
  }
})
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
}

.auth-header {
  text-align: center;
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
  margin-top: 16px;
  text-align: left;
}

.server-error i {
  font-size: 12px;
  flex-shrink: 0;
}
</style>
