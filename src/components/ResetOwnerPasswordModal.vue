<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card card">
      <div class="modal-header">
        <h2><i class="fas fa-key"></i> {{ title }}</h2>
        <p>{{ subtitle }}</p>
      </div>

      <!-- Mode selector -->
      <div class="mode-tabs">
        <button :class="['mode-tab', { active: mode === 'reset' }]" @click="mode = 'reset'">
          <i class="fas fa-undo"></i> Reset to Default
        </button>
        <button :class="['mode-tab', { active: mode === 'custom' }]" @click="mode = 'custom'">
          <i class="fas fa-edit"></i> Set Custom Password
        </button>
      </div>

      <!-- Reset mode -->
      <div v-if="mode === 'reset'" class="mode-content">
        <div class="info-box">
          <i class="fas fa-info-circle"></i>
          <div>
            <strong>Reset Password</strong>
            <p>This will reset the owner's password to a new auto-generated password. The owner will be forced to change it on next login.</p>
          </div>
        </div>

        <div v-if="resetResult" class="result-box">
          <div class="result-header">
            <i class="fas fa-check-circle"></i> Password Reset Successfully
          </div>
          <div class="password-display">
            <label>New Password:</label>
            <div class="password-copy">
              <code>{{ resetResult.default_password }}</code>
              <button type="button" class="copy-btn" @click="copyPassword" :title="copied ? 'Copied!' : 'Copy'">
                <i :class="copied ? 'fas fa-check' : 'fas fa-copy'"></i>
              </button>
            </div>
          </div>
          <p class="result-note"><i class="fas fa-exclamation-triangle"></i> Share this password securely with the owner. They will need to change it on login.</p>
        </div>

        <div class="modal-actions" v-if="!resetResult">
          <button class="btn btn-outline" @click="$emit('close')">Cancel</button>
          <button class="btn btn-primary" @click="resetPassword" :disabled="loading">
            <i class="fas fa-undo"></i> {{ loading ? 'Resetting...' : 'Reset Password' }}
          </button>
        </div>
        <div class="modal-actions" v-else>
          <button class="btn btn-primary" @click="$emit('updated'); $emit('close')">Done</button>
        </div>
      </div>

      <!-- Custom mode -->
      <div v-if="mode === 'custom'" class="mode-content">
        <form @submit.prevent="setCustomPassword">
          <div class="form-group" :class="{ 'has-error': errors.password }">
            <label>New Password</label>
            <div class="password-input-wrap">
              <input v-model="form.password" :type="showPw ? 'text' : 'password'"
                placeholder="Enter new password" @input="validateField('password')" />
              <button type="button" class="pw-toggle" @click="showPw = !showPw">
                <i :class="showPw ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <div class="password-rules" v-if="form.password.length > 0">
              <span :class="pwRules.length ? 'valid' : 'invalid'">
                <i :class="pwRules.length ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> At least 8 characters
              </span>
              <span :class="pwRules.uppercase ? 'valid' : 'invalid'">
                <i :class="pwRules.uppercase ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> One uppercase letter (A-Z)
              </span>
              <span :class="pwRules.lowercase ? 'valid' : 'invalid'">
                <i :class="pwRules.lowercase ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> One lowercase letter (a-z)
              </span>
              <span :class="pwRules.number ? 'valid' : 'invalid'">
                <i :class="pwRules.number ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> One number (0-9)
              </span>
              <span :class="pwRules.symbol ? 'valid' : 'invalid'">
                <i :class="pwRules.symbol ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> One special character (!@#$%^&*)
              </span>
            </div>
            <span class="field-error" v-if="errors.password">
              <i class="fas fa-exclamation-triangle"></i> {{ errors.password }}
            </span>
          </div>

          <div class="form-group" :class="{ 'has-error': errors.password_confirmation }">
            <label>Confirm Password</label>
            <div class="password-input-wrap">
              <input v-model="form.password_confirmation" :type="showConfirm ? 'text' : 'password'"
                placeholder="Confirm new password" @input="validateField('password_confirmation')" />
              <button type="button" class="pw-toggle" @click="showConfirm = !showConfirm">
                <i :class="showConfirm ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <span class="field-error" v-if="errors.password_confirmation">
              <i class="fas fa-exclamation-triangle"></i> {{ errors.password_confirmation }}
            </span>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.force_change_on_login" />
              <span>Force owner to change password on next login</span>
            </label>
          </div>

          <div class="server-errors" v-if="serverErrors.length > 0">
            <div v-for="(msg, i) in serverErrors" :key="i" class="server-error">
              <i class="fas fa-exclamation-circle"></i> {{ msg }}
            </div>
          </div>

          <div class="success-msg" v-if="successMsg">
            <i class="fas fa-check-circle"></i> {{ successMsg }}
          </div>

          <div class="modal-actions" v-if="!successMsg">
            <button type="button" class="btn btn-outline" @click="$emit('close')">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="loading || !canSubmit">
              <i class="fas fa-save"></i> {{ loading ? 'Saving...' : 'Set Password' }}
            </button>
          </div>
          <div class="modal-actions" v-else>
            <button type="button" class="btn btn-primary" @click="$emit('close')">Done</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { superadminApi } from '@/api'

const props = defineProps({
  ownerId: { type: [Number, String], required: true },
  ownerName: { type: String, default: '' },
})

const emit = defineEmits(['close', 'updated'])

const title = computed(() => `Password: ${props.ownerName || 'Owner'}`)
const subtitle = computed(() => 'Reset or set a new password for this owner account.')

const mode = ref('reset')
const loading = ref(false)
const showPw = ref(false)
const showConfirm = ref(false)
const copied = ref(false)
const resetResult = ref(null)
const successMsg = ref('')
const serverErrors = ref([])
const errors = ref({})

const form = ref({
  password: '',
  password_confirmation: '',
  force_change_on_login: true,
})

const pwRules = computed(() => ({
  length: form.value.password.length >= 8,
  uppercase: /[A-Z]/.test(form.value.password),
  lowercase: /[a-z]/.test(form.value.password),
  number: /[0-9]/.test(form.value.password),
  symbol: /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?`~]/.test(form.value.password),
}))

const allPwValid = computed(() => Object.values(pwRules.value).every(Boolean))

const canSubmit = computed(() =>
  form.value.password &&
  form.value.password_confirmation &&
  form.value.password === form.value.password_confirmation &&
  allPwValid.value
)

function validateField(field) {
  if (field === 'password') {
    if (!form.value.password) errors.value.password = 'Please enter a new password.'
    else if (!allPwValid.value) errors.value.password = 'Password does not meet all requirements.'
    else delete errors.value.password
  }
  if (field === 'password_confirmation') {
    if (!form.value.password_confirmation) errors.value.password_confirmation = 'Please confirm the password.'
    else if (form.value.password !== form.value.password_confirmation) errors.value.password_confirmation = 'Passwords do not match.'
    else delete errors.value.password_confirmation
  }
}

async function resetPassword() {
  loading.value = true
  serverErrors.value = []
  try {
    const res = await superadminApi.resetOwnerPassword(props.ownerId)
    resetResult.value = res.data
  } catch (e) {
    serverErrors.value = [e.response?.data?.message || 'Failed to reset password']
  }
  loading.value = false
}

async function setCustomPassword() {
  errors.value = {}
  validateField('password')
  validateField('password_confirmation')
  if (errors.value.password || errors.value.password_confirmation) return

  loading.value = true
  serverErrors.value = []
  try {
    await superadminApi.setOwnerPassword(props.ownerId, form.value)
    successMsg.value = 'Password updated successfully!'
    emit('updated')
  } catch (e) {
    if (e.response?.data?.errors) {
      serverErrors.value = Object.entries(e.response.data.errors).map(([, arr]) => arr[0])
    } else {
      serverErrors.value = [e.response?.data?.message || 'Failed to set password']
    }
  }
  loading.value = false
}

function copyPassword() {
  if (resetResult.value?.default_password) {
    navigator.clipboard.writeText(resetResult.value.default_password)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
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
  max-width: 480px;
  padding: 32px;
}

.modal-header {
  margin-bottom: 20px;
}

.modal-header h2 {
  font-size: 20px;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-header h2 i { color: #e74c3c; }

.modal-header p {
  color: #888;
  font-size: 13px;
  line-height: 1.5;
}

.mode-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.mode-tab {
  flex: 1;
  padding: 10px 14px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s;
  font-family: 'Inter', sans-serif;
}

.mode-tab:hover { border-color: #ccc; }
.mode-tab.active { border-color: #e74c3c; color: #e74c3c; background: #fef5f5; }

.mode-content { min-height: 120px; }

.info-box {
  display: flex;
  gap: 12px;
  padding: 14px;
  background: #f0f7ff;
  border: 1px solid #d6e8f7;
  border-radius: 8px;
  margin-bottom: 20px;
}

.info-box > i { color: #2980b9; font-size: 18px; margin-top: 2px; }
.info-box strong { display: block; font-size: 14px; margin-bottom: 4px; color: #333; }
.info-box p { font-size: 13px; color: #666; margin: 0; line-height: 1.5; }

.result-box {
  background: #eafaf1;
  border: 1px solid #d5f5e3;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #27ae60;
  margin-bottom: 16px;
}

.password-display { margin-bottom: 12px; }
.password-display label { font-size: 12px; font-weight: 600; color: #555; text-transform: uppercase; letter-spacing: 0.3px; display: block; margin-bottom: 6px; }

.password-copy {
  display: flex;
  align-items: center;
  background: #fff;
  border: 2px solid #d5f5e3;
  border-radius: 6px;
  overflow: hidden;
}

.password-copy code {
  flex: 1;
  padding: 10px 14px;
  font-size: 16px;
  font-weight: 700;
  color: #333;
  letter-spacing: 1px;
  user-select: all;
}

.copy-btn {
  padding: 10px 14px;
  border: none;
  background: none;
  cursor: pointer;
  color: #27ae60;
  font-size: 16px;
}

.copy-btn:hover { color: #1e8449; }

.result-note {
  font-size: 12px;
  color: #7d6608;
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
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

.form-group input[type="text"],
.form-group input[type="password"] {
  width: 100%;
  padding: 10px 14px;
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

.pw-toggle:hover { color: #333; }

.field-error {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  font-size: 12px;
  color: #e74c3c;
  font-weight: 500;
}

.field-error i { font-size: 11px; }

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

.password-rules span.valid { color: #27ae60; }
.password-rules span.invalid { color: #bbb; }
.password-rules span i { font-size: 11px; width: 14px; }

.checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #e74c3c;
  cursor: pointer;
}

.server-errors { margin-bottom: 12px; }

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

.server-error i { font-size: 12px; flex-shrink: 0; }

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

.success-msg i { font-size: 12px; }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
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
  transition: all 0.2s;
}

.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; }
.btn-outline:hover { border-color: #999; }
</style>
