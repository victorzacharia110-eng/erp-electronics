<template>
  <div class="store-layout" :style="{ '--brand': brandColor, '--brand-dark': brandColorDark }">
    <header class="site-header">
      <div class="top-bar">
        <div class="container top-bar-inner">
          <div class="top-bar-left" v-if="!isDirectory && (contactPhone || contactEmail || contactAddress)">
            <span v-if="contactPhone"><i class="fas fa-phone"></i> {{ contactPhone }}</span>
            <span v-if="contactEmail"><i class="fas fa-envelope"></i> {{ contactEmail }}</span>
            <span v-if="contactAddress"><i class="fas fa-location-dot"></i> {{ contactAddress }}</span>
          </div>
          <div class="top-bar-right" v-if="!isDirectory && socialLinks.length">
            <a v-for="s in socialLinks" :key="s.platform" :href="s.url" target="_blank" rel="noopener" :aria-label="s.platform" :title="s.platform">
              <i :class="s.icon"></i>
            </a>
          </div>
        </div>
      </div>

      <div class="main-header">
        <div class="container main-header-inner">
          <router-link :to="homeLink" class="logo" @click="navOpen = false">
            <span class="logo-icon"><i class="fas fa-bolt"></i></span>
            <span class="logo-text">{{ logoTextFirst }}<span v-if="logoTextRest">{{ logoTextRest }}</span></span>
          </router-link>

          <div v-if="!isDirectory" class="search-bar">
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="$t('search.placeholder')"
              @keyup.enter="handleSearch"
            />
            <button @click="handleSearch" class="search-btn">
              <i class="fas fa-search"></i>
            </button>
          </div>

          <div class="header-actions">
            <router-link v-if="!isDirectory" :to="storeLink('/cart')" class="action-link cart-link" :class="{ 'cart-bump': cartBump }">
              <i class="fas fa-shopping-cart"></i>
              <span class="cart-count" v-if="cartStore.itemCount > 0">{{ cartStore.itemCount }}</span>
              <span class="action-label">{{ $t('nav.cart') }}</span>
            </router-link>

            <router-link v-if="isDirectory && authStore.isAuthenticated" :to="dashboardRoute" class="action-link">
              <i class="fas fa-gauge-high"></i>
              <span class="action-label">{{ $t('nav.dashboard') }}</span>
            </router-link>

            <template v-if="authStore.isAuthenticated">
              <router-link v-if="!isDirectory && (authStore.isOwner || authStore.isCustomer)" :to="inboxRoute" class="action-link inbox-link">
                <i class="fas fa-envelope"></i>
                <span class="cart-count msg-count" v-if="unreadMsgCount > 0">{{ unreadMsgCount }}</span>
                <span class="action-label">{{ $t('nav.inbox') }}</span>
              </router-link>
              <router-link v-if="!isDirectory" :to="dashboardRoute" class="action-link">
                <i class="fas fa-gauge-high"></i>
                <span class="action-label">{{ $t('nav.dashboard') }}</span>
              </router-link>
              <button @click="handleLogout" class="action-link logout-btn">
                <i class="fas fa-right-from-bracket"></i>
                <span class="action-label">{{ $t('nav.logout') }}</span>
              </button>
            </template>
            <template v-else>
              <router-link to="/login" class="action-link">
                <i class="fas fa-user"></i>
                <span class="action-label">{{ $t('nav.login') }}</span>
              </router-link>
            </template>

            <button class="lang-switch" @click="toggleLocale" :title="locale === 'sw' ? $t('topBar.switchToEnglish') : $t('topBar.switchToSwahili')">
              {{ locale === 'sw' ? 'EN' : 'SW' }}
            </button>
          </div>

          <button v-if="!isDirectory" class="hamburger" :class="{ active: navOpen }" @click="navOpen = !navOpen">
            <span></span><span></span><span></span>
          </button>
        </div>

        <div v-if="!isDirectory" class="mobile-dropdown" :class="{ open: navOpen }">
          <div class="mobile-dropdown-inner">
            <div class="mobile-search">
              <input
                v-model="searchQuery"
                type="text"
                :placeholder="$t('search.placeholder')"
                @keyup.enter="handleSearch(); navOpen = false"
              />
              <button @click="handleSearch(); navOpen = false" class="search-btn">
                <i class="fas fa-search"></i>
              </button>
            </div>

            <router-link :to="homeLink" class="mobile-link" @click="navOpen = false">
              <i class="fas fa-home"></i> {{ $t('nav.home') }}
            </router-link>
            <router-link :to="storeLink('/products')" class="mobile-link" @click="navOpen = false">
              <i class="fas fa-box-open"></i> {{ $t('nav.products') }}
            </router-link>
            <router-link
              v-for="cat in productStore.categories.slice(0, 5)"
              :key="cat.id"
              :to="storeLink(`/category/${cat.slug}`)"
              class="mobile-link"
              @click="navOpen = false"
            >
              <i class="fas fa-tag"></i> {{ cat.translated_name || cat.name }}
            </router-link>

            <div class="mobile-divider"></div>

            <router-link to="/" class="mobile-link" @click="navOpen = false">
              <i class="fas fa-store"></i> {{ $t('directory.badge') }}
            </router-link>

            <router-link :to="storeLink('/cart')" class="mobile-link" @click="navOpen = false">
              <i class="fas fa-shopping-cart"></i> {{ $t('nav.cart') }}
              <span class="mobile-badge" v-if="cartStore.itemCount > 0">{{ cartStore.itemCount }}</span>
            </router-link>

            <template v-if="authStore.isAuthenticated">
              <router-link v-if="authStore.isOwner || authStore.isCustomer" :to="inboxRoute" class="mobile-link" @click="navOpen = false">
                <i class="fas fa-envelope"></i> {{ $t('nav.inbox') }}
                <span class="mobile-badge msg" v-if="unreadMsgCount > 0">{{ unreadMsgCount }}</span>
              </router-link>
              <router-link :to="dashboardRoute" class="mobile-link" @click="navOpen = false">
                <i class="fas fa-gauge-high"></i> {{ $t('nav.dashboard') }}
              </router-link>
              <button @click="handleLogout" class="mobile-link logout">
                <i class="fas fa-right-from-bracket"></i> {{ $t('nav.logout') }}
              </button>
            </template>
            <template v-else>
              <router-link to="/login" class="mobile-link" @click="navOpen = false">
                <i class="fas fa-user"></i> {{ $t('nav.login') }}
              </router-link>
              <router-link to="/register" class="mobile-link" @click="navOpen = false">
                <i class="fas fa-user-plus"></i> {{ $t('nav.register') }}
              </router-link>
            </template>

            <div class="mobile-divider"></div>

            <button class="mobile-link" @click="toggleLocale">
              <i class="fas fa-language"></i>
              {{ locale === 'sw' ? $t('topBar.switchToEnglish') : $t('topBar.switchToSwahili') }}
            </button>
          </div>
        </div>
      </div>

      <nav v-if="!isDirectory" class="main-nav" :class="{ 'mobile-open': navOpen }">
        <div class="container nav-inner">
          <div class="nav-links">
            <router-link :to="homeLink" class="nav-link" @click="navOpen = false">{{ $t('nav.home') }}</router-link>
            <router-link :to="storeLink('/products')" class="nav-link" @click="navOpen = false">{{ $t('nav.products') }}</router-link>
            <router-link
              v-for="cat in productStore.categories.slice(0, 5)"
              :key="cat.id"
              :to="storeLink(`/category/${cat.slug}`)"
              class="nav-link"
              @click="navOpen = false"
            >
              {{ cat.translated_name || cat.name }}
            </router-link>
            <router-link to="/" class="nav-link" @click="navOpen = false">
              <i class="fas fa-store"></i> {{ $t('directory.badge') }}
            </router-link>
          </div>
          <div class="nav-right">
            <span class="nav-text"><i class="fas fa-truck"></i> {{ $t('nav.fastDelivery') }}</span>
          </div>
        </div>
      </nav>
    </header>

    <main>
      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>

    <footer class="site-footer">
      <div class="container footer-grid">
        <div>
          <div class="footer-logo">
            <span class="logo-icon"><i class="fas fa-bolt"></i></span>
            <span class="logo-text">{{ logoTextFirst }}<span v-if="logoTextRest">{{ logoTextRest }}</span></span>
          </div>
          <p class="footer-desc">{{ isDirectory ? $t('footer.description') : (businessStore.current?.tagline || $t('footer.description')) }}</p>
          <div class="footer-social" v-if="!isDirectory && socialLinks.length">
            <a v-for="s in socialLinks" :key="s.platform" :href="s.url" target="_blank" rel="noopener" :aria-label="s.platform" :title="s.platform">
              <i :class="s.icon"></i>
            </a>
          </div>
        </div>
        <div>
          <h4>{{ $t('footer.quickLinks') }}</h4>
          <router-link :to="storeLink('/products')">{{ $t('footer.allProducts') }}</router-link>
          <router-link :to="storeLink('/category/phones')">{{ $t('footer.phones') }}</router-link>
          <router-link :to="storeLink('/category/accessories')">{{ $t('footer.accessories') }}</router-link>
        </div>
        <div>
          <h4>{{ $t('footer.support') }}</h4>
          <a href="#">{{ $t('footer.helpCenter') }}</a>
          <a href="#">{{ $t('footer.shippingInfo') }}</a>
          <a href="#">{{ $t('footer.returnsPolicy') }}</a>
        </div>
        <div>
          <h4>{{ $t('footer.contact') }}</h4>
          <p v-if="!isDirectory && contactPhone"><i class="fas fa-phone"></i> {{ contactPhone }}</p>
          <p v-else><i class="fas fa-phone"></i> {{ $t('topBar.phone') }}</p>
          <p v-if="!isDirectory && contactEmail"><i class="fas fa-envelope"></i> {{ contactEmail }}</p>
          <p v-else><i class="fas fa-envelope"></i> {{ $t('topBar.email') }}</p>
          <p v-if="!isDirectory && contactAddress"><i class="fas fa-location-dot"></i> {{ contactAddress }}</p>
          <p v-else><i class="fas fa-location-dot"></i> {{ $t('topBar.location') }}</p>
          <a v-if="!isDirectory && whatsappUrl" :href="whatsappUrl" target="_blank" rel="noopener" class="footer-whatsapp">
            <i class="fab fa-whatsapp"></i> {{ $t('whatsapp.chat') }}
          </a>
        </div>
      </div>
      <div class="footer-bottom">
        <div class="container">
          <span>{{ $t('footer.copyright') }}</span>
        </div>
      </div>
    </footer>

    <a v-if="whatsappUrl && !isDirectory" :href="whatsappUrl" target="_blank" rel="noopener" class="whatsapp-fab" :aria-label="$t('whatsapp.chat')" :title="$t('whatsapp.chat')">
      <i class="fab fa-whatsapp"></i>
    </a>

    <ChangePasswordModal v-if="authStore.mustChangePassword" @close="authStore.mustChangePassword = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { useProductStore } from '@/stores/products'
import { useBusinessStore } from '@/stores/business'
import { conversationApi } from '@/api'
import ChangePasswordModal from '@/components/ChangePasswordModal.vue'

const route = useRoute()
const router = useRouter()
const { locale } = useI18n()
const authStore = useAuthStore()
const cartStore = useCartStore()
const productStore = useProductStore()
const businessStore = useBusinessStore()

function toggleLocale() {
  locale.value = locale.value === 'sw' ? 'en' : 'sw'
  localStorage.setItem('locale', locale.value)
}

const searchQuery = ref('')
const navOpen = ref(false)
const cartBump = ref(false)
const unreadMsgCount = ref(0)

const businessSlug = computed(() => route.params.businessSlug || null)
const isDirectory = computed(() => route.name === 'home' && !businessSlug.value)

const brandColor = computed(() =>
  businessSlug.value ? businessStore.current?.brand_color || '#e74c3c' : '#e74c3c'
)
const brandColorDark = computed(() =>
  businessSlug.value ? businessStore.current?.brand_color_secondary || '#2c3e50' : '#2c3e50'
)
const storeName = computed(() =>
  businessSlug.value ? businessStore.current?.store_name || 'ElectroShop' : 'ElectroShop'
)
const logoTextFirst = computed(() => storeName.value.split(' ')[0] || 'ElectroShop')
const logoTextRest = computed(() => storeName.value.split(' ').slice(1).join(' '))

const contactPhone = computed(() => businessStore.current?.contact_phone || '')
const contactEmail = computed(() => businessStore.current?.contact_email || '')
const contactAddress = computed(() => businessStore.current?.address || '')

const whatsappUrl = computed(() => {
  const digits = (businessStore.current?.whatsapp_number || '').replace(/[^\d]/g, '')
  if (!digits) return null
  const msg = businessStore.current?.whatsapp_message || 'Hello!'
  return `https://wa.me/${digits}?text=${encodeURIComponent(msg)}`
})

const socialLinks = computed(() => {
  const social = businessStore.current?.social || {}
  const links = []
  if (whatsappUrl.value) links.push({ platform: 'whatsapp', icon: 'fab fa-whatsapp', url: whatsappUrl.value })
  const defs = [
    ['facebook', 'fab fa-facebook-f'],
    ['instagram', 'fab fa-instagram'],
    ['twitter', 'fab fa-x-twitter'],
    ['tiktok', 'fab fa-tiktok'],
    ['youtube', 'fab fa-youtube'],
  ]
  for (const [key, icon] of defs) {
    if (social[key]) links.push({ platform: key, icon, url: social[key] })
  }
  return links
})

function storeLink(path) {
  return businessStore.link(path)
}

const homeLink = computed(() => {
  if (isDirectory.value) return '/'
  return businessStore.link('/')
})

const inboxRoute = computed(() => {
  if (authStore.isOwner) return '/owner/inbox'
  return businessStore.link('/customer/inbox')
})

let msgPollTimer = null
async function pollUnreadMessages() {
  if (!authStore.isAuthenticated) return
  try {
    const res = await conversationApi.getUnreadCount()
    unreadMsgCount.value = res.data.unread_count
  } catch { /* empty */ }
}

let prevCartCount = 0
watch(() => cartStore.itemCount, (newVal) => {
  if (newVal > prevCartCount) {
    cartBump.value = true
    setTimeout(() => cartBump.value = false, 400)
  }
  prevCartCount = newVal
})

const dashboardRoute = computed(() => {
  if (authStore.isSuperadmin) return '/superadmin'
  if (authStore.isOwner) return '/owner'
  if (authStore.isEmployee) return '/employee'
  return businessStore.link('/customer')
})

async function applyBusinessContext() {
  businessStore.setSlugMode(!!businessSlug.value)
  if (businessSlug.value) {
    const found = await businessStore.loadBySlug(businessSlug.value)
    if (!found && route.name === 'store-home') {
      router.replace('/')
      return
    }
  } else {
    await businessStore.fetchDirectory()
    if (authStore.isOwner) {
      await businessStore.fetchMine()
    }
    businessStore.restoreFromStorage()
    businessStore.pickFallback()
  }
}

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchProfile()
  }
  await applyBusinessContext()
  await productStore.fetchCategories()
  if (authStore.isAuthenticated) {
    await cartStore.fetchCart()
    pollUnreadMessages()
    msgPollTimer = setInterval(pollUnreadMessages, 15000)
  }
})

watch(businessSlug, () => {
  applyBusinessContext()
  productStore.fetchCategories()
})

onUnmounted(() => {
  clearInterval(msgPollTimer)
  businessStore.setSlugMode(false)
})

function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push({
      path: businessStore.link('/products'),
      query: { search: searchQuery.value },
    })
  }
}

async function handleLogout() {
  await authStore.logout()
  cartStore.$reset()
  navOpen.value = false
  router.push('/')
}
</script>

<style scoped>
.top-bar {
  background: var(--brand-dark);
  color: #fff;
  font-size: 13px;
  padding: 8px 0;
}

.top-bar-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.top-bar-left {
  display: flex;
  gap: 24px;
}

.top-bar-left span {
  display: flex;
  align-items: center;
  gap: 6px;
  opacity: 0.85;
}

.top-bar-left i {
  color: var(--brand);
}

.top-bar-right {
  display: flex;
  gap: 12px;
}

.top-bar-right a {
  color: #fff;
  opacity: 0.7;
  transition: opacity 0.2s;
  font-size: 14px;
}

.top-bar-right a:hover {
  opacity: 1;
}

.main-header {
  background: #fff;
  padding: 16px 0;
  border-bottom: 1px solid #eee;
  position: relative;
  z-index: 100;
}

.main-header-inner {
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  flex-shrink: 0;
}

.logo-icon {
  color: #fff;
  background: var(--brand);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  font-size: 18px;
}

.logo-text {
  font-size: 24px;
  font-weight: 800;
  color: var(--brand-dark);
}

.logo-text span {
  color: var(--brand);
}

.search-bar {
  flex: 1;
  display: flex;
  max-width: 500px;
}

.search-bar input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #eee;
  border-right: none;
  border-radius: 4px 0 0 4px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
}

.search-bar input:focus {
  outline: none;
  border-color: var(--brand);
}

.search-btn {
  padding: 12px 20px;
  background: var(--brand);
  color: #fff;
  border-radius: 0 4px 4px 0;
  font-size: 16px;
  border: none;
  cursor: pointer;
}

.search-btn:hover {
  background: var(--brand-dark);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.action-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #555;
  font-size: 12px;
  text-decoration: none;
  transition: color 0.2s;
  position: relative;
}

.action-link:hover {
  color: var(--brand);
}

.action-link i {
  font-size: 20px;
}

.action-label {
  font-weight: 500;
}

.cart-link {
  position: relative;
}

.cart-count {
  position: absolute;
  top: -6px;
  right: -8px;
  background: var(--brand);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  min-width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.msg-count {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.inbox-link {
  position: relative;
}

.cart-bump .cart-count {
  animation: cartBounce 0.4s ease;
}

@keyframes cartBounce {
  0% { transform: scale(1); }
  30% { transform: scale(1.4); }
  60% { transform: scale(0.9); }
  100% { transform: scale(1); }
}

.cart-bump i {
  animation: cartIconBump 0.4s ease;
}

@keyframes cartIconBump {
  0% { transform: scale(1); }
  30% { transform: scale(1.15); }
  60% { transform: scale(0.95); }
  100% { transform: scale(1); }
}

.logout-btn {
  cursor: pointer;
  background: none;
  border: none;
  font-family: inherit;
}

.hamburger {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
}

.hamburger span {
  display: block;
  width: 22px;
  height: 2px;
  background: #333;
  border-radius: 2px;
  transition: all 0.3s;
}

.hamburger.active span:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.hamburger.active span:nth-child(2) {
  opacity: 0;
}

.hamburger.active span:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

.main-nav {
  background: var(--brand);
}

.nav-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-links {
  display: flex;
}

.nav-link {
  color: #fff;
  padding: 14px 20px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s;
}

.nav-link:hover {
  background: rgba(0, 0, 0, 0.1);
}

.nav-right {
  display: flex;
  align-items: center;
}

.nav-text {
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  opacity: 0.9;
}

.mobile-dropdown {
  display: none;
  background: #fff;
  border-top: 1px solid #eee;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 99;
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease, opacity 0.3s ease;
  opacity: 0;
}

.mobile-dropdown.open {
  max-height: 80vh;
  overflow-y: auto;
  opacity: 1;
}

.mobile-dropdown-inner {
  padding: 12px 0;
}

.mobile-search {
  display: none;
  padding: 0 16px 12px;
}

.mobile-search input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #eee;
  border-radius: 8px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
}

.mobile-search input:focus {
  outline: none;
  border-color: var(--brand);
}

.mobile-search .search-btn {
  border-radius: 8px;
  margin-top: 8px;
  width: 100%;
  padding: 12px;
}

.mobile-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  color: #333;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  transition: background 0.15s;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
}

.mobile-link:hover {
  background: #f5f5f5;
}

.mobile-link i {
  width: 20px;
  text-align: center;
  color: var(--brand);
  font-size: 16px;
}

.mobile-link.logout {
  color: var(--brand);
}

.mobile-badge {
  margin-left: auto;
  background: var(--brand);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
}

.mobile-badge.msg {
  animation: pulse 2s infinite;
}

.mobile-divider {
  height: 1px;
  background: #eee;
  margin: 8px 16px;
}

footer {
  background: var(--brand-dark);
  color: #ccc;
  padding-top: 48px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr;
  gap: 40px;
  padding-bottom: 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.footer-logo .logo-icon {
  width: 36px;
  height: 36px;
  font-size: 16px;
}

.footer-logo .logo-text {
  color: #fff;
  font-size: 20px;
}

.footer-desc {
  font-size: 13px;
  line-height: 1.7;
  opacity: 0.7;
}

footer h4 {
  color: #fff;
  font-size: 15px;
  margin-bottom: 16px;
}

footer a,
footer p {
  display: block;
  font-size: 13px;
  color: #ccc;
  text-decoration: none;
  margin-bottom: 10px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

footer a:hover {
  opacity: 1;
  color: var(--brand);
}

footer p i {
  color: var(--brand);
  width: 18px;
  margin-right: 4px;
}

.footer-social {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}

.footer-social a {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  opacity: 1;
  margin: 0;
}

.footer-social a:hover {
  background: var(--brand);
  color: #fff;
}

.footer-whatsapp {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 8px 14px;
  border-radius: 6px;
  background: #25d366;
  color: #fff !important;
  font-weight: 600;
  opacity: 1;
}

.footer-whatsapp:hover {
  background: #1da851;
}

.whatsapp-fab {
  position: fixed;
  right: 20px;
  bottom: 20px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #25d366;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  box-shadow: 0 6px 20px rgba(37, 211, 102, 0.45);
  z-index: 500;
  transition: transform 0.2s;
}

.whatsapp-fab:hover {
  transform: scale(1.08);
  color: #fff;
}

.footer-bottom {
  padding: 20px 0;
  text-align: center;
  font-size: 13px;
  opacity: 0.5;
}

.lang-switch {
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  font-weight: 700;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
}
.lang-switch:hover {
  border-color: var(--brand);
  color: var(--brand);
}

@media (max-width: 768px) {
  .top-bar {
    display: none;
  }

  .main-header-inner {
    gap: 6px;
    justify-content: space-between;
  }

  .search-bar {
    display: none;
  }

  .header-actions {
    display: flex;
    gap: 8px;
  }

  .header-actions .action-label {
    display: none;
  }

  .header-actions .action-link {
    gap: 0;
  }

  .logo-text {
    font-size: 17px;
  }

  .logo-icon {
    width: 34px;
    height: 34px;
    font-size: 15px;
  }

  .hamburger {
    display: flex;
  }

  .main-nav {
    display: none;
  }

  .mobile-dropdown {
    display: block;
  }

  .mobile-search {
    display: flex;
    flex-direction: column;
  }

  .footer-grid {
    grid-template-columns: 1fr;
    gap: 28px;
  }
}

@media (min-width: 769px) {
  .mobile-dropdown {
    display: none !important;
  }
}
</style>

<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
