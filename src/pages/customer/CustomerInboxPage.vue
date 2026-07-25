<template>
  <div class="inbox-page">
    <SkeletonLoader v-if="loading && !activeConversation" type="list" :count="4" />

    <div v-else class="inbox-layout">
      <div class="inbox-sidebar" :class="{ 'show-mobile': showSidebar }">
        <div class="inbox-sidebar-header">
          <h3>{{ $t('inbox.title') }}</h3>
          <button class="btn btn-sm btn-primary" @click="showNewModal = true"><i class="fas fa-plus"></i></button>
          <button class="btn-icon mobile-close" @click="showSidebar = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="inbox-search">
          <i class="fas fa-search"></i>
          <input v-model="search" type="text" :placeholder="$t('inbox.searchPlaceholder')" @input="debouncedLoad" />
        </div>
        <div class="inbox-list">
          <div v-if="conversations.length === 0" class="inbox-empty">
            <i class="fas fa-envelope-open"></i>
            <p>{{ $t('inbox.noConversations') }}</p>
            <button class="btn btn-primary btn-sm" @click="showNewModal = true"><i class="fas fa-plus"></i> {{ $t('inbox.startConversation') }}</button>
          </div>
          <div v-for="conv in conversations" :key="conv.id" class="inbox-item" :class="{ active: activeConversation?.id === conv.id, unread: hasUnread(conv) }" @click="openConversation(conv)">
            <div class="inbox-item-avatar"><i class="fas fa-headset"></i></div>
            <div class="inbox-item-info">
              <div class="inbox-item-top">
                <span class="inbox-item-name">{{ conv.subject }}</span>
                <span class="inbox-item-time">{{ timeAgo(conv.last_message_at || conv.created_at) }}</span>
              </div>
              <span class="inbox-item-subject">{{ conv.last_message?.message || '...' }}</span>
            </div>
            <span v-if="hasUnread(conv)" class="unread-dot"></span>
          </div>
        </div>
      </div>

      <div class="inbox-main">
        <div v-if="!activeConversation" class="inbox-welcome">
          <i class="fas fa-comments"></i>
          <h3>{{ $t('inbox.selectConversation') }}</h3>
          <p>{{ $t('inbox.customerWelcome') }}</p>
        </div>

        <template v-else>
          <div class="inbox-main-header">
            <button class="btn-icon mobile-menu" @click="showSidebar = true"><i class="fas fa-bars"></i></button>
            <div class="header-info">
              <h3>{{ activeConversation.subject }}</h3>
              <span class="header-owner">{{ $t('inbox.storeSupport') }}</span>
            </div>
            <div class="header-actions">
              <span :class="['status-pill', activeConversation.status]">{{ $t(`inbox.statuses.${activeConversation.status}`) }}</span>
            </div>
          </div>

          <div class="messages-area" ref="messagesArea">
            <div v-for="msg in activeConversation.messages" :key="msg.id" class="message-bubble" :class="{ mine: msg.sender_id === authStore.user?.id }">
              <div class="msg-sender">{{ msg.sender?.name }}</div>
              <div class="msg-text">{{ msg.message }}</div>
              <div class="msg-time">{{ new Date(msg.created_at).toLocaleTimeString('en-TZ', { hour: '2-digit', minute: '2-digit' }) }}</div>
            </div>
          </div>

          <div class="message-input-area" v-if="activeConversation.status !== 'closed'">
            <textarea v-model="newMessage" :placeholder="$t('inbox.typeMessage')" rows="2" @keydown.enter.exact.prevent="sendMessage"></textarea>
            <button class="btn btn-primary send-btn" @click="sendMessage" :disabled="!newMessage.trim() || sending">
              <i class="fas" :class="sending ? 'fa-spinner fa-spin' : 'fa-paper-plane'"></i>
            </button>
          </div>
          <div class="closed-notice" v-else>
            <i class="fas fa-lock"></i> {{ $t('inbox.conversationClosed') }}
          </div>
        </template>
      </div>
    </div>

    <div class="modal-overlay" v-if="showNewModal" @click.self="showNewModal = false">
      <div class="modal-card card">
        <h2><i class="fas fa-paper-plane"></i> {{ $t('inbox.newConversation') }}</h2>
        <form @submit.prevent="createConversation" novalidate>
          <div class="form-group">
            <label>{{ $t('inbox.subject') }} *</label>
            <input v-model="newConv.subject" type="text" :placeholder="$t('inbox.subjectPlaceholder')" />
          </div>
          <div class="form-group">
            <label>{{ $t('inbox.message') }} *</label>
            <textarea v-model="newConv.message" rows="4" :placeholder="$t('inbox.messagePlaceholder')"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="showNewModal = false">{{ $t('common.cancel') }}</button>
            <button type="submit" class="btn btn-primary" :disabled="!canCreate || creating">
              <i class="fas fa-paper-plane"></i> {{ creating ? $t('common.sending') : $t('inbox.sendMessage') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { conversationApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const { t } = useI18n()
const authStore = useAuthStore()
const conversations = ref([])
const activeConversation = ref(null)
const loading = ref(true)
const sending = ref(false)
const newMessage = ref('')
const search = ref('')
const showSidebar = ref(true)
const messagesArea = ref(null)
const showNewModal = ref(false)
const creating = ref(false)
const newConv = ref({ subject: '', message: '' })

const canCreate = computed(() => newConv.value.subject.trim() && newConv.value.message.trim())

function hasUnread(conv) {
  if (!authStore.user) return false
  return conv.messages?.some(m => m.sender_id !== authStore.user.id && !m.is_read)
}

function timeAgo(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const mins = Math.floor((now - d) / 60000)
  if (mins < 1) return 'now'
  if (mins < 60) return `${mins}m`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h`
  const days = Math.floor(hrs / 24)
  return `${days}d`
}

let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadConversations, 300)
}

async function loadConversations() {
  loading.value = true
  try {
    const res = await conversationApi.getAll({ search: search.value || undefined })
    conversations.value = res.data.data || []
  } catch { conversations.value = [] }
  loading.value = false
}

async function openConversation(conv) {
  activeConversation.value = conv
  showSidebar.value = false
  try {
    const res = await conversationApi.getOne(conv.id)
    activeConversation.value = res.data
    conv.messages = res.data.messages
  } catch { /* empty */ }
  await nextTick()
  if (messagesArea.value) messagesArea.value.scrollTop = messagesArea.value.scrollHeight
}

async function sendMessage() {
  if (!newMessage.value.trim() || sending.value || !activeConversation.value) return
  sending.value = true
  try {
    const res = await conversationApi.sendMessage(activeConversation.value.id, { message: newMessage.value })
    activeConversation.value.messages.push(res.data)
    newMessage.value = ''
    await nextTick()
    if (messagesArea.value) messagesArea.value.scrollTop = messagesArea.value.scrollHeight
  } catch { /* empty */ }
  sending.value = false
}

async function createConversation() {
  if (!canCreate.value || creating.value) return
  creating.value = true
  try {
    const res = await conversationApi.create({
      subject: newConv.value.subject,
      message: newConv.value.message,
      type: 'customer_owner',
    })
    showNewModal.value = false
    newConv.value = { subject: '', message: '' }
    await loadConversations()
    await openConversation(res.data)
  } catch { /* empty */ }
  creating.value = false
}

let pollTimer = null
async function pollConversations() {
  try {
    const res = await conversationApi.getAll({ search: search.value || undefined })
    conversations.value = res.data.data || []
    if (activeConversation.value) {
      const fresh = await conversationApi.getOne(activeConversation.value.id)
      activeConversation.value = fresh.data
    }
  } catch { /* empty */ }
}

onMounted(() => {
  loadConversations()
  pollTimer = setInterval(pollConversations, 15000)
})
onUnmounted(() => { clearInterval(pollTimer) })
</script>

<style scoped>
.inbox-page { height: calc(100vh - 120px); }
.inbox-layout { display: flex; height: 100%; border-radius: 10px; overflow: hidden; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }

.inbox-sidebar { width: 340px; border-right: 1px solid #eee; display: flex; flex-direction: column; flex-shrink: 0; }
.inbox-sidebar-header { padding: 16px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.inbox-sidebar-header h3 { font-size: 18px; font-weight: 700; flex: 1; }
.mobile-close { display: none; }

.inbox-search { padding: 12px 16px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; gap: 8px; }
.inbox-search i { color: #999; font-size: 13px; }
.inbox-search input { flex: 1; border: none; background: none; font-size: 14px; outline: none; font-family: inherit; }

.inbox-list { flex: 1; overflow-y: auto; }
.inbox-empty { text-align: center; padding: 40px 20px; color: #999; }
.inbox-empty i { font-size: 40px; margin-bottom: 12px; display: block; }
.inbox-empty .btn { margin-top: 16px; }
.inbox-item { display: flex; align-items: center; gap: 12px; padding: 14px 16px; cursor: pointer; border-bottom: 1px solid #f5f5f5; transition: background 0.15s; }
.inbox-item:hover { background: #f8f9fa; }
.inbox-item.active { background: #fef5f5; border-left: 3px solid #e74c3c; }
.inbox-item.unread { background: #fafafa; }
.inbox-item-avatar { width: 40px; height: 40px; background: #eaf2ff; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #2980b9; font-size: 16px; flex-shrink: 0; }
.inbox-item-info { flex: 1; min-width: 0; }
.inbox-item-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }
.inbox-item-name { font-weight: 600; font-size: 14px; }
.inbox-item-time { font-size: 11px; color: #999; flex-shrink: 0; }
.inbox-item-subject { display: block; font-size: 12px; color: #aaa; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.unread-dot { width: 10px; height: 10px; background: #e74c3c; border-radius: 50%; flex-shrink: 0; animation: pulse 2s infinite; }

@keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.3); } }

.inbox-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.inbox-welcome { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #ccc; }
.inbox-welcome i { font-size: 60px; margin-bottom: 16px; }
.inbox-welcome h3 { font-size: 18px; color: #999; margin-bottom: 6px; }
.inbox-welcome p { font-size: 14px; }

.inbox-main-header { padding: 14px 20px; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 12px; }
.mobile-menu { display: none; }
.header-info { flex: 1; }
.header-info h3 { font-size: 16px; font-weight: 600; }
.header-owner { font-size: 13px; color: #888; }
.header-actions { display: flex; gap: 8px; align-items: center; }
.status-pill { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; }
.status-pill.open { background: #eaf2ff; color: #2980b9; }
.status-pill.in_progress { background: #fef9e7; color: #b7950b; }
.status-pill.resolved { background: #eafaf1; color: #27ae60; }
.status-pill.closed { background: #f0f0f0; color: #888; }

.messages-area { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.message-bubble { max-width: 65%; padding: 10px 14px; border-radius: 12px; background: #f0f0f0; align-self: flex-start; }
.message-bubble.mine { background: #e74c3c; color: #fff; align-self: flex-end; }
.msg-sender { font-size: 11px; font-weight: 600; margin-bottom: 4px; opacity: 0.7; }
.message-bubble.mine .msg-sender { display: none; }
.msg-text { font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
.msg-time { font-size: 10px; opacity: 0.6; margin-top: 4px; text-align: right; }

.message-input-area { padding: 12px 16px; border-top: 1px solid #eee; display: flex; gap: 10px; align-items: flex-end; }
.message-input-area textarea { flex: 1; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; font-family: inherit; resize: none; outline: none; }
.message-input-area textarea:focus { border-color: #e74c3c; }
.send-btn { padding: 10px 16px; border-radius: 8px; flex-shrink: 0; }
.closed-notice { padding: 14px 20px; text-align: center; color: #888; font-size: 14px; background: #f8f9fa; border-top: 1px solid #eee; }
.closed-notice i { margin-right: 6px; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-sm { padding: 6px 12px; font-size: 12px; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; }
.btn-outline:hover { border-color: #999; }
.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 13px; color: #666; }
.btn-icon:hover { border-color: #e74c3c; color: #e74c3c; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 24px; }
.modal-card { width: 100%; max-width: 460px; padding: 32px; }
.modal-card h2 { font-size: 20px; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; }
.modal-card h2 i { color: #e74c3c; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
.form-group input, .form-group textarea { width: 100%; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; font-family: 'Inter', sans-serif; box-sizing: border-box; resize: vertical; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: #e74c3c; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; }

@media (max-width: 768px) {
  .inbox-sidebar { position: fixed; left: 0; top: 0; bottom: 0; width: 300px; z-index: 100; transform: translateX(-100%); transition: transform 0.25s ease; background: #fff; }
  .inbox-sidebar.show-mobile { transform: translateX(0); box-shadow: 4px 0 20px rgba(0,0,0,0.15); }
  .mobile-close { display: flex; }
  .mobile-menu { display: flex; }
}
</style>
