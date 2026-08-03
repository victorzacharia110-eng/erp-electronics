<template>
  <div class="inbox-page">
    <SkeletonLoader v-if="loading && !activeConversation" type="list" :count="4" />

    <div v-else class="inbox-layout">
      <div class="inbox-sidebar" :class="{ 'show-mobile': showSidebar }">
        <div class="inbox-sidebar-header">
          <h3>Conversations</h3>
          <button class="btn-icon mobile-close" @click="showSidebar = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="inbox-tabs">
          <button :class="['tab-btn', { active: viewMode === 'chats' }]" @click="viewMode = 'chats'; debouncedLoad()">
            <i class="fas fa-comments"></i> Chats
          </button>
          <button :class="['tab-btn', { active: viewMode === 'contacts' }]" @click="viewMode = 'contacts'">
            <i class="fas fa-users"></i> Owners
          </button>
        </div>
        <div class="inbox-search">
          <i class="fas fa-search"></i>
          <input v-model="search" type="text" placeholder="Search conversations..." @input="debouncedLoad" />
        </div>
        <div class="inbox-list">
          <template v-if="viewMode === 'contacts'">
            <div v-if="filteredContacts.length === 0" class="inbox-empty">
              <i class="fas fa-store"></i>
              <p>No owners available</p>
            </div>
            <div v-for="contact in filteredContacts" :key="contact.id" class="inbox-item" @click="openContact(contact)">
              <div class="inbox-item-avatar owner-avatar"><i class="fas fa-store"></i></div>
              <div class="inbox-item-info">
                <div class="inbox-item-top">
                  <span class="inbox-item-name">{{ contact.name }}</span>
                  <span class="inbox-item-time" v-if="!contact.is_active">Inactive</span>
                </div>
                <span class="inbox-item-subject">{{ contact.store_name }}</span>
                <span class="inbox-item-preview">{{ contact.email }}</span>
              </div>
              <i class="fas fa-paper-plane contact-send"></i>
            </div>
          </template>
          <template v-else>
            <div v-if="conversations.length === 0" class="inbox-empty">
              <i class="fas fa-envelope-open"></i>
              <p>No conversations yet</p>
            </div>
            <div v-for="conv in conversations" :key="conv.id" class="inbox-item" :class="{ active: activeConversation?.id === conv.id, unread: hasUnread(conv) }" @click="openConversation(conv)">
              <div class="inbox-item-avatar"><i class="fas fa-store"></i></div>
              <div class="inbox-item-info">
                <div class="inbox-item-top">
                  <span class="inbox-item-name">{{ conv.owner?.name }}</span>
                  <span class="inbox-item-time">{{ timeAgo(conv.last_message_at || conv.created_at) }}</span>
                </div>
                <span class="inbox-item-subject">{{ conv.subject }}</span>
                <span class="inbox-item-preview" v-if="conv.last_message">{{ conv.last_message.message }}</span>
              </div>
              <span v-if="hasUnread(conv)" class="unread-dot"></span>
            </div>
          </template>
        </div>
      </div>

      <div class="inbox-main">
        <div v-if="!activeConversation" class="inbox-welcome">
          <i class="fas fa-comments"></i>
          <h3>Select a conversation</h3>
          <p>Choose a conversation from the sidebar to view messages</p>
        </div>

        <template v-else>
          <div class="inbox-main-header">
            <button class="btn-icon mobile-menu" @click="showSidebar = true"><i class="fas fa-bars"></i></button>
            <div class="header-info">
              <h3>{{ activeConversation.subject }}</h3>
              <span class="header-owner">{{ activeConversation.owner?.name }}</span>
            </div>
            <div class="header-actions">
              <select v-model="activeConversation.status" class="status-select" @change="updateStatus">
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="resolved">Resolved</option>
                <option value="closed">Closed</option>
              </select>
              <button class="btn-icon" title="Owner Details" @click="showOwnerDetails = !showOwnerDetails"><i class="fas fa-info-circle"></i></button>
            </div>
          </div>

          <div class="owner-details-panel" v-if="showOwnerDetails && ownerDetails">
            <div class="detail-row"><i class="fas fa-user"></i><span><strong>{{ ownerDetails.full_name }}</strong></span></div>
            <div class="detail-row"><i class="fas fa-building"></i><span>{{ ownerDetails.company_name }}</span></div>
            <div class="detail-row"><i class="fas fa-crown"></i><span class="plan-badge">{{ ownerDetails.plan }}</span></div>
            <div class="detail-row"><i class="fas fa-store"></i><span>{{ ownerDetails.branch_name }}</span></div>
            <div class="detail-row"><i class="fas fa-phone"></i><span>{{ ownerDetails.phone_number }}</span></div>
            <div class="detail-row"><i class="fas fa-map-marker-alt"></i><span>{{ ownerDetails.location }}</span></div>
          </div>

          <div class="messages-area" ref="messagesArea">
            <div v-for="msg in activeConversation.messages" :key="msg.id" class="message-bubble" :class="{ mine: msg.sender_id === authStore.user?.id }">
              <div class="msg-sender">{{ msg.sender?.name }}</div>
              <div class="msg-text">{{ msg.message }}</div>
              <div class="msg-time">
                <span v-if="msg.sender_id === authStore.user?.id" class="msg-tick" :class="{ read: msg.is_read }" :title="msg.is_read ? $t('inbox.read') : $t('inbox.delivered')">
                  <i :class="msg.is_read ? 'fas fa-check-double' : 'fas fa-check'"></i>
                </span>
                {{ new Date(msg.created_at).toLocaleTimeString('en-TZ', { hour: '2-digit', minute: '2-digit' }) }}
              </div>
            </div>
          </div>

          <div class="message-input-area">
            <textarea v-model="newMessage" placeholder="Type your message..." rows="2" @keydown.enter.exact.prevent="sendMessage"></textarea>
            <button class="btn btn-primary send-btn" @click="sendMessage" :disabled="!newMessage.trim() || sending">
              <i class="fas" :class="sending ? 'fa-spinner fa-spin' : 'fa-paper-plane'"></i>
            </button>
          </div>
        </template>
      </div>
    </div>

    <div class="modal-overlay" v-if="showCompose" @click.self="closeCompose">
      <div class="modal-card card">
        <h2><i class="fas fa-paper-plane"></i> New conversation</h2>
        <p class="compose-target">To: <strong>{{ composeTarget?.name }}</strong> <span v-if="composeTarget?.store_name">({{ composeTarget.store_name }})</span></p>
        <form @submit.prevent="createConversation" novalidate>
          <div class="form-group">
            <label>Subject *</label>
            <input v-model="newConv.subject" type="text" placeholder="What is this about?" />
          </div>
          <div class="form-group">
            <label>Message *</label>
            <textarea v-model="newConv.message" rows="4" placeholder="Type your message..."></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="closeCompose">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="!canCreate || creating">
              <i class="fas fa-paper-plane"></i> {{ creating ? 'Sending...' : 'Send Message' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { conversationApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const authStore = useAuthStore()
const conversations = ref([])
const activeConversation = ref(null)
const ownerDetails = ref(null)
const showOwnerDetails = ref(false)
const loading = ref(true)
const sending = ref(false)
const newMessage = ref('')
const search = ref('')
const showSidebar = ref(true)
const messagesArea = ref(null)
const viewMode = ref('chats')
const contacts = ref([])
const showCompose = ref(false)
const composeTarget = ref(null)
const newConv = ref({ subject: 'Support', message: '' })
const creating = ref(false)

const canCreate = computed(() => newConv.value.subject.trim() && newConv.value.message.trim())

const filteredContacts = computed(() => {
  const q = search.value.toLowerCase().trim()
  if (!q) return contacts.value
  return contacts.value.filter(c =>
    c.name?.toLowerCase().includes(q) ||
    c.store_name?.toLowerCase().includes(q) ||
    c.email?.toLowerCase().includes(q)
  )
})

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
  if (viewMode.value === 'contacts') return
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

async function loadContacts() {
  try {
    const res = await conversationApi.getContacts()
    contacts.value = res.data.data || []
  } catch { contacts.value = [] }
}

async function openContact(contact) {
  showSidebar.value = false
  const existing = conversations.value.find(c => c.owner?.id === contact.id && c.type === 'superadmin_owner')
  if (existing) {
    viewMode.value = 'chats'
    await openConversation(existing)
    return
  }
  composeTarget.value = contact
  newConv.value = { subject: 'Support', message: '' }
  showCompose.value = true
}

function closeCompose() {
  showCompose.value = false
  composeTarget.value = null
}

async function createConversation() {
  if (!canCreate.value || creating.value || !composeTarget.value) return
  creating.value = true
  try {
    const res = await conversationApi.create({
      type: 'superadmin_owner',
      owner_id: composeTarget.value.id,
      subject: newConv.value.subject,
      message: newConv.value.message,
    })
    closeCompose()
    viewMode.value = 'chats'
    await loadConversations()
    await openConversation(res.data)
  } catch { /* empty */ }
  creating.value = false
}

async function openConversation(conv) {
  activeConversation.value = conv
  showSidebar.value = false
  showOwnerDetails.value = false
  ownerDetails.value = null
  try {
    const res = await conversationApi.getOne(conv.id)
    activeConversation.value = res.data
    conv.messages = res.data.messages
    await loadOwnerDetails(conv.id)
  } catch { /* empty */ }
  await nextTick()
  if (messagesArea.value) {
    messagesArea.value.scrollTop = messagesArea.value.scrollHeight
  }
}

async function loadOwnerDetails(convId) {
  try {
    const res = await conversationApi.getOwnerDetails(convId)
    ownerDetails.value = res.data
  } catch { /* empty */ }
}

async function sendMessage() {
  if (!newMessage.value.trim() || sending.value || !activeConversation.value) return
  sending.value = true
  try {
    const res = await conversationApi.sendMessage(activeConversation.value.id, { message: newMessage.value })
    activeConversation.value.messages.push(res.data)
    newMessage.value = ''
    await nextTick()
    if (messagesArea.value) {
      messagesArea.value.scrollTop = messagesArea.value.scrollHeight
    }
  } catch { /* empty */ }
  sending.value = false
}

async function updateStatus() {
  try {
    await conversationApi.updateStatus(activeConversation.value.id, { status: activeConversation.value.status })
  } catch { /* empty */ }
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
  loadContacts()
  pollTimer = setInterval(pollConversations, 15000)
})
onUnmounted(() => { clearInterval(pollTimer) })
</script>

<style scoped>
.inbox-page { height: calc(100vh - 120px); }
.inbox-layout { display: flex; height: 100%; border-radius: 10px; overflow: hidden; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }

.inbox-sidebar { width: 340px; border-right: 1px solid #eee; display: flex; flex-direction: column; flex-shrink: 0; }
.inbox-sidebar-header { padding: 16px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.inbox-sidebar-header h3 { font-size: 18px; font-weight: 700; }
.mobile-close { display: none; }

.inbox-tabs { display: flex; border-bottom: 1px solid #eee; }
.tab-btn { flex: 1; padding: 10px; font-size: 12px; font-weight: 600; border: none; background: none; cursor: pointer; color: #888; border-bottom: 2px solid transparent; transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 4px; font-family: inherit; }
.tab-btn:hover { color: #333; }
.tab-btn.active { color: #e74c3c; border-bottom-color: #e74c3c; }

.owner-avatar { background: #fef5f5; color: #e74c3c; }
.contact-send { color: #e74c3c; font-size: 14px; flex-shrink: 0; }

.inbox-search { padding: 12px 16px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; gap: 8px; }
.inbox-search i { color: #999; font-size: 13px; }
.inbox-search input { flex: 1; border: none; background: none; font-size: 14px; outline: none; font-family: inherit; }

.inbox-list { flex: 1; overflow-y: auto; }
.inbox-empty { text-align: center; padding: 60px 20px; color: #999; }
.inbox-empty i { font-size: 40px; margin-bottom: 12px; display: block; }
.inbox-item { display: flex; align-items: center; gap: 12px; padding: 14px 16px; cursor: pointer; border-bottom: 1px solid #f5f5f5; transition: background 0.15s; }
.inbox-item:hover { background: #f8f9fa; }
.inbox-item.active { background: #fef5f5; border-left: 3px solid #e74c3c; }
.inbox-item.unread { background: #fafafa; }
.inbox-item-avatar { width: 40px; height: 40px; background: #f0f0f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #e74c3c; font-size: 16px; flex-shrink: 0; }
.inbox-item-info { flex: 1; min-width: 0; }
.inbox-item-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }
.inbox-item-name { font-weight: 600; font-size: 14px; }
.inbox-item-time { font-size: 11px; color: #999; flex-shrink: 0; }
.inbox-item-subject { display: block; font-size: 13px; color: #666; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.inbox-item-preview { display: block; font-size: 12px; color: #aaa; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }
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
.status-select { padding: 6px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; font-family: inherit; }

.owner-details-panel { padding: 16px 20px; background: #f8f9fa; border-bottom: 1px solid #eee; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.detail-row { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #555; }
.detail-row i { width: 16px; color: #e74c3c; text-align: center; }
.plan-badge { background: #fef9e7; color: #b7950b; padding: 2px 8px; border-radius: 10px; font-size: 12px; font-weight: 500; }

.messages-area { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.message-bubble { max-width: 65%; padding: 10px 14px; border-radius: 12px; background: #f0f0f0; align-self: flex-start; }
.message-bubble.mine { background: #e74c3c; color: #fff; align-self: flex-end; }
.msg-sender { font-size: 11px; font-weight: 600; margin-bottom: 4px; opacity: 0.7; }
.message-bubble.mine .msg-sender { display: none; }
.msg-text { font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
.msg-time { font-size: 10px; opacity: 0.6; margin-top: 4px; text-align: right; display: flex; align-items: center; justify-content: flex-end; gap: 5px; }
.msg-tick { font-size: 11px; color: rgba(255, 255, 255, 0.7); }
.msg-tick.read { color: #fff; opacity: 1; }

.message-input-area { padding: 12px 16px; border-top: 1px solid #eee; display: flex; gap: 10px; align-items: flex-end; }
.message-input-area textarea { flex: 1; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; font-family: inherit; resize: none; outline: none; }
.message-input-area textarea:focus { border-color: #e74c3c; }
.send-btn { padding: 10px 16px; border-radius: 8px; flex-shrink: 0; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 14px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #eee; background: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 13px; color: #666; }
.btn-icon:hover { border-color: #e74c3c; color: #e74c3c; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 24px; }
.modal-card { width: 100%; max-width: 460px; padding: 32px; }
.modal-card h2 { font-size: 20px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.modal-card h2 i { color: #e74c3c; }
.compose-target { font-size: 13px; color: #666; margin-bottom: 20px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }
.form-group input, .form-group textarea { width: 100%; padding: 10px 14px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 14px; font-family: 'Inter', sans-serif; box-sizing: border-box; resize: vertical; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: #e74c3c; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; }

.btn-outline { background: #fff; color: #333; border: 1px solid #ddd; }
.btn-outline:hover { border-color: #999; }

@media (max-width: 768px) {
  .inbox-sidebar { position: fixed; left: 0; top: 0; bottom: 0; width: 300px; z-index: 100; transform: translateX(-100%); transition: transform 0.25s ease; background: #fff; }
  .inbox-sidebar.show-mobile { transform: translateX(0); box-shadow: 4px 0 20px rgba(0,0,0,0.15); }
  .mobile-close { display: flex; }
  .mobile-menu { display: flex; }
  .owner-details-panel { grid-template-columns: 1fr; }
}
</style>
