<template>
  <div class="superadmin-layout">
    <div class="sa-sidebar-overlay" :class="{ visible: sidebarMobileOpen }" @click="sidebarMobileOpen = false"></div>
    <aside class="sa-sidebar" :class="{ collapsed: sidebarCollapsed, 'mobile-open': sidebarMobileOpen }">
      <div class="sa-logo" @click="sidebarCollapsed = !sidebarCollapsed">
        <span class="sa-logo-icon"><i class="fas fa-shield-halved"></i></span>
        <span class="sa-logo-text" v-show="!sidebarCollapsed">ERP Admin</span>
      </div>
      <nav class="sa-nav">
        <router-link to="/superadmin" class="sa-nav-link" :class="{ active: $route.name === 'superadmin-dashboard' }" @click="sidebarMobileOpen = false">
          <i class="fas fa-gauge-high"></i>
          <span v-show="!sidebarCollapsed">Dashboard</span>
        </router-link>
        <router-link to="/superadmin/owners" class="sa-nav-link" :class="{ active: $route.path.startsWith('/superadmin/owners') }" @click="sidebarMobileOpen = false">
          <i class="fas fa-store"></i>
          <span v-show="!sidebarCollapsed">Owner Management</span>
        </router-link>
        <router-link to="/superadmin/inbox" class="sa-nav-link" :class="{ active: $route.path.startsWith('/superadmin/inbox') }" @click="sidebarMobileOpen = false">
          <i class="fas fa-envelope"></i>
          <span v-show="!sidebarCollapsed">Inbox</span>
          <span v-if="unreadCount > 0" class="nav-badge" v-show="!sidebarCollapsed">{{ unreadCount }}</span>
        </router-link>
        <router-link to="/superadmin/home-content" class="sa-nav-link" :class="{ active: $route.path.startsWith('/superadmin/home-content') }" @click="sidebarMobileOpen = false">
          <i class="fas fa-house"></i>
          <span v-show="!sidebarCollapsed">Home Content</span>
        </router-link>
      </nav>
      <div class="sa-sidebar-footer">
        <router-link to="/" class="sa-nav-link" @click="sidebarMobileOpen = false">
          <i class="fas fa-arrow-left"></i>
          <span v-show="!sidebarCollapsed">Back to Store</span>
        </router-link>
        <button @click="handleLogout" class="sa-nav-link logout-btn">
          <i class="fas fa-right-from-bracket"></i>
          <span v-show="!sidebarCollapsed">Logout</span>
        </button>
      </div>
    </aside>
    <div class="sa-main">
      <header class="sa-header">
        <div class="sa-header-left">
          <button class="sa-hamburger" @click="toggleSidebar">
            <span></span><span></span><span></span>
          </button>
          <h2>{{ pageTitle }}</h2>
        </div>
        <div class="sa-header-right">
          <span class="sa-badge"><i class="fas fa-shield-halved"></i> Superadmin</span>
          <span class="sa-user">{{ authStore.user?.name }}</span>
        </div>
      </header>
      <main class="sa-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { conversationApi } from '@/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const sidebarCollapsed = ref(false)
const sidebarMobileOpen = ref(false)
const unreadCount = ref(0)

const pageTitle = computed(() => {
  const titles = {
    'superadmin-dashboard': 'Dashboard',
    'superadmin-owners': 'Owner Management',
    'superadmin-owner-detail': 'Owner Details',
    'superadmin-branding': 'Brand Settings',
    'superadmin-inbox': 'Inbox',
    'superadmin-home-content': 'Home Content',
  }
  return titles[route.name] || 'Dashboard'
})

function toggleSidebar() {
  if (window.innerWidth <= 768) {
    sidebarMobileOpen.value = !sidebarMobileOpen.value
  } else {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
}

let pollTimer = null
async function pollUnread() {
  try {
    const res = await conversationApi.getUnreadCount()
    unreadCount.value = res.data.unread_count
  } catch { /* empty */ }
}

onMounted(() => {
  pollUnread()
  pollTimer = setInterval(pollUnread, 15000)
})
onUnmounted(() => { clearInterval(pollTimer) })

async function handleLogout() {
  clearInterval(pollTimer)
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.superadmin-layout {
  display: flex;
  min-height: 100vh;
  background: #f0f2f5;
}

.sa-sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.sa-sidebar-overlay.visible {
  opacity: 1;
}

.sa-sidebar {
  width: 260px;
  background: #1a1a2e;
  color: #fff;
  display: flex;
  flex-direction: column;
  transition: width 0.2s ease;
  flex-shrink: 0;
  z-index: 1000;
}

.sa-sidebar.collapsed {
  width: 72px;
}

.sa-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  cursor: pointer;
}

.sa-logo-icon {
  width: 36px;
  height: 36px;
  background: #e74c3c;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.sa-logo-text {
  font-size: 18px;
  font-weight: 700;
  white-space: nowrap;
}

.sa-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sa-nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  border: none;
  background: none;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
}

.sa-nav-link:hover {
  background: rgba(255,255,255,0.08);
  color: #fff;
}

.sa-nav-link.active {
  background: #e74c3c;
  color: #fff;
}

.nav-badge {
  background: #e74c3c;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
  margin-left: auto;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}

.sa-nav-link i {
  width: 20px;
  text-align: center;
  font-size: 16px;
  flex-shrink: 0;
}

.sa-sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

.logout-btn {
  width: 100%;
  color: rgba(255,255,255,0.5);
}

.logout-btn:hover {
  color: #e74c3c !important;
  background: rgba(231,76,60,0.1) !important;
}

.sa-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

.sa-header {
  background: #fff;
  border-bottom: 1px solid #eee;
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sa-header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sa-header h2 {
  font-size: 20px;
  font-weight: 700;
}

.sa-header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sa-badge {
  background: #fef5f5;
  color: #e74c3c;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.sa-user {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.sa-content {
  flex: 1;
  padding: 32px;
}

.sa-hamburger {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
}

.sa-hamburger span {
  display: block;
  width: 22px;
  height: 2px;
  background: #333;
  border-radius: 2px;
  transition: all 0.3s;
}

@media (max-width: 768px) {
  .sa-sidebar-overlay {
    display: block;
    pointer-events: none;
  }

  .sa-sidebar-overlay.visible {
    pointer-events: auto;
  }

  .sa-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 260px;
    transform: translateX(-100%);
    transition: transform 0.3s ease, width 0.2s ease;
  }

  .sa-sidebar.mobile-open {
    transform: translateX(0);
  }

  .sa-sidebar.collapsed {
    width: 260px;
  }

  .sa-sidebar .sa-logo-text,
  .sa-sidebar .sa-nav-link span,
  .sa-sidebar-footer span {
    display: block !important;
  }

  .sa-hamburger {
    display: flex;
  }

  .sa-header {
    padding: 16px;
  }

  .sa-badge {
    display: none;
  }

  .sa-content {
    padding: 16px;
  }
}

@media (min-width: 769px) {
  .sa-hamburger {
    display: none !important;
  }
}
</style>
