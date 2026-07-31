import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const IDLE_TIMEOUT_SECONDS = 15 * 60
const WARNING_AT_SECONDS = 60
const HIDDEN_GRACE_SECONDS = 10 * 60
const LAST_ACTIVE_KEY = 'session_last_active'

const ACTIVITY_EVENTS = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll', 'click', 'wheel']

export const useSessionStore = defineStore('session', () => {
  const authStore = useAuthStore()

  const remaining = ref(IDLE_TIMEOUT_SECONDS)
  const showWarning = ref(false)
  const warningSeconds = computed(() => Math.max(0, Math.min(WARNING_AT_SECONDS, remaining.value)))

  let timer = null
  let hiddenSince = null
  let lastWrite = 0
  let running = false
  let terminating = false

  function persistActivity() {
    const now = Date.now()
    if (now - lastWrite > 10000) {
      lastWrite = now
      localStorage.setItem(LAST_ACTIVE_KEY, String(now))
    }
  }

  function handleActivity() {
    if (!running) return
    persistActivity()
    remaining.value = IDLE_TIMEOUT_SECONDS
    showWarning.value = false
  }

  function tick() {
    if (!authStore.isAuthenticated) return
    remaining.value -= 1
    if (remaining.value <= WARNING_AT_SECONDS && remaining.value > 0) {
      showWarning.value = true
    }
    if (remaining.value <= 0) {
      terminate()
    }
  }

  function onVisibilityChange() {
    if (document.hidden) {
      hiddenSince = Date.now()
      return
    }
    if (hiddenSince === null) return
    const awaySeconds = Math.floor((Date.now() - hiddenSince) / 1000)
    hiddenSince = null
    if (awaySeconds > HIDDEN_GRACE_SECONDS) {
      terminate()
      return
    }
    handleActivity()
  }

  async function terminate() {
    if (terminating) return
    terminating = true
    stop()
    try {
      await authStore.logout()
    } catch {
      authStore.$patch({ token: null, user: null, mustChangePassword: false })
      localStorage.removeItem('auth_token')
    } finally {
      router.push({ name: 'login' })
    }
  }

  function start() {
    if (running) return
    running = true
    terminating = false
    remaining.value = IDLE_TIMEOUT_SECONDS

    const lastActive = parseInt(localStorage.getItem(LAST_ACTIVE_KEY) || '0', 10)
    if (lastActive && Date.now() - lastActive > IDLE_TIMEOUT_SECONDS * 1000) {
      terminate()
      return
    }

    lastWrite = Date.now()
    localStorage.setItem(LAST_ACTIVE_KEY, String(lastWrite))
    ACTIVITY_EVENTS.forEach((ev) => window.addEventListener(ev, handleActivity, { passive: true }))
    document.addEventListener('visibilitychange', onVisibilityChange)
    timer = setInterval(tick, 1000)
  }

  function stop() {
    running = false
    localStorage.removeItem(LAST_ACTIVE_KEY)
    ACTIVITY_EVENTS.forEach((ev) => window.removeEventListener(ev, handleActivity))
    document.removeEventListener('visibilitychange', onVisibilityChange)
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    showWarning.value = false
  }

  return {
    remaining,
    showWarning,
    warningSeconds,
    start,
    stop,
    activity: handleActivity,
  }
})
