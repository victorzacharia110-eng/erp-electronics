import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token') || null)
  const loading = ref(false)
  const mustChangePassword = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const isCustomer = computed(() => user.value?.role === 'customer')
  const isEmployee = computed(() => user.value?.role === 'employee')
  const isOwner = computed(() => user.value?.role === 'owner')
  const isSuperadmin = computed(() => user.value?.role === 'superadmin')

  async function register(data) {
    loading.value = true
    try {
      const response = await authApi.register(data)
      token.value = response.data.token
      user.value = response.data.user
      localStorage.setItem('auth_token', response.data.token)
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function login(data) {
    loading.value = true
    try {
      const response = await authApi.login(data)
      token.value = response.data.token
      user.value = response.data.user
      mustChangePassword.value = response.data.must_change_password || false
      localStorage.setItem('auth_token', response.data.token)
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      token.value = null
      user.value = null
      mustChangePassword.value = false
      localStorage.removeItem('auth_token')
    }
  }

  async function fetchProfile() {
    if (!token.value) return
    loading.value = true
    try {
      const response = await authApi.getProfile()
      user.value = response.data
      mustChangePassword.value = response.data.must_change_password || false
    } catch {
      token.value = null
      user.value = null
      mustChangePassword.value = false
      localStorage.removeItem('auth_token')
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(data) {
    const response = await authApi.updateProfile(data)
    user.value = response.data
    return response.data
  }

  async function changePassword(data) {
    const response = await authApi.changePassword(data)
    mustChangePassword.value = false
    return response.data
  }

  return {
    user,
    token,
    loading,
    mustChangePassword,
    isAuthenticated,
    isCustomer,
    isEmployee,
    isOwner,
    isSuperadmin,
    register,
    login,
    logout,
    fetchProfile,
    updateProfile,
    changePassword,
  }
}, {
  persist: {
    pick: ['token'],
  },
})
