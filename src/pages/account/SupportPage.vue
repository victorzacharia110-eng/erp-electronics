<template>
  <div class="support-page container">
    <h1 class="page-title"><i class="fas fa-headset"></i> {{ $t('support.title') }}</h1>

    <SkeletonLoader v-if="loading" type="list" :count="3" />

    <div v-if="!loading && !showForm && !selectedMessage" class="support-layout">
      <div class="card support-section">
        <div class="section-header">
          <h2><i class="fas fa-inbox"></i> {{ $t('support.myMessages') }}</h2>
          <button class="btn btn-primary btn-sm" @click="showForm = true">
            <i class="fas fa-plus"></i> {{ $t('support.newMessage') }}
          </button>
        </div>
        <div v-if="messages.length === 0" class="empty-state">
          <i class="fas fa-envelope-open"></i>
          <p>{{ $t('support.noMessages') }}</p>
          <p class="muted">{{ $t('support.noMessagesHint') }}</p>
        </div>
        <div v-for="msg in messages" :key="msg.id" class="message-list-item" @click="viewMessage(msg)">
          <div class="msg-header">
            <span :class="['msg-status', `status-${msg.status}`]">{{ $t(`support.statuses.${msg.status}`) }}</span>
            <span class="msg-category">{{ $t(`support.categories.${msg.category}`) }}</span>
            <span class="msg-date">{{ new Date(msg.created_at).toLocaleDateString() }}</span>
          </div>
          <h3>{{ msg.subject }}</h3>
          <p class="msg-preview">{{ msg.message.substring(0, 120) }}{{ msg.message.length > 120 ? '...' : '' }}</p>
          <div v-if="msg.order_id" class="msg-order">
            <i class="fas fa-receipt"></i> {{ msg.order?.order_number || $t('common.order') }}
          </div>
          <div v-if="msg.admin_reply" class="msg-reply-badge">
            <i class="fas fa-reply"></i> {{ $t('support.hasReply') }}
          </div>
        </div>
      </div>

      <div class="card support-sidebar">
        <h3><i class="fas fa-info-circle"></i> {{ $t('support.needHelp') }}</h3>
        <p>{{ $t('support.helpDesc') }}</p>
        <div class="help-topics">
          <div class="help-topic" @click="quickMessage('payment_issue')">
            <i class="fas fa-credit-card"></i>
            <span>{{ $t('support.topicPayment') }}</span>
          </div>
          <div class="help-topic" @click="quickMessage('order_status')">
            <i class="fas fa-clock"></i>
            <span>{{ $t('support.topicOrderStatus') }}</span>
          </div>
          <div class="help-topic" @click="quickMessage('delivery')">
            <i class="fas fa-truck"></i>
            <span>{{ $t('support.topicDelivery') }}</span>
          </div>
          <div class="help-topic" @click="quickMessage('refund')">
            <i class="fas fa-undo"></i>
            <span>{{ $t('support.topicRefund') }}</span>
          </div>
        </div>
        <div class="account-reminder">
          <i class="fas fa-bell"></i>
          <p>{{ $t('support.accountReminder') }}</p>
        </div>
      </div>
    </div>

    <div v-if="!loading && showForm" class="card support-form-card">
      <div class="section-header">
        <h2><i class="fas fa-paper-plane"></i> {{ $t('support.composeMessage') }}</h2>
        <button class="btn btn-outline btn-sm" @click="cancelForm"><i class="fas fa-times"></i> {{ $t('common.cancel') }}</button>
      </div>
      <form @submit.prevent="sendMessage" class="support-form">
        <div class="form-group">
          <label>{{ $t('support.category') }}</label>
          <select v-model="newMessage.category">
            <option value="payment_issue">{{ $t('support.categories.payment_issue') }}</option>
            <option value="order_status">{{ $t('support.categories.order_status') }}</option>
            <option value="delivery">{{ $t('support.categories.delivery') }}</option>
            <option value="refund">{{ $t('support.categories.refund') }}</option>
            <option value="general">{{ $t('support.categories.general') }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>{{ $t('support.orderRef') }}</label>
          <select v-model="newMessage.order_id">
            <option :value="null">{{ $t('support.noOrderRef') }}</option>
            <option v-for="o in recentOrders" :key="o.id" :value="o.id">{{ o.order_number }} — TSh {{ Number(o.total).toLocaleString('en-TZ') }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>{{ $t('support.subject') }}</label>
          <input v-model="newMessage.subject" type="text" required :placeholder="$t('support.subjectPlaceholder')" />
        </div>
        <div class="form-group">
          <label>{{ $t('support.message') }}</label>
          <textarea v-model="newMessage.message" rows="5" required :placeholder="$t('support.messagePlaceholder')"></textarea>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="sending">
          <i class="fas" :class="sending ? 'fa-spinner fa-spin' : 'fa-paper-plane'"></i>
          {{ sending ? $t('common.saving') : $t('support.sendMessage') }}
        </button>
        <p v-if="formError" class="form-error"><i class="fas fa-exclamation-circle"></i> {{ formError }}</p>
        <p v-if="formSuccess" class="form-success"><i class="fas fa-check-circle"></i> {{ formSuccess }}</p>
      </form>
    </div>

    <div v-if="!loading && selectedMessage" class="card support-detail-card">
      <div class="section-header">
        <button class="btn btn-outline btn-sm" @click="selectedMessage = null"><i class="fas fa-arrow-left"></i> {{ $t('common.back') }}</button>
        <span :class="['msg-status', `status-${selectedMessage.status}`]">{{ $t(`support.statuses.${selectedMessage.status}`) }}</span>
      </div>
      <h2>{{ selectedMessage.subject }}</h2>
      <div class="detail-meta">
        <span><i class="fas fa-tag"></i> {{ $t(`support.categories.${selectedMessage.category}`) }}</span>
        <span><i class="fas fa-calendar"></i> {{ new Date(selectedMessage.created_at).toLocaleString() }}</span>
        <span v-if="selectedMessage.order_id"><i class="fas fa-receipt"></i> {{ selectedMessage.order?.order_number }}</span>
      </div>
      <div class="message-bubble customer">
        <p>{{ selectedMessage.message }}</p>
      </div>
      <div v-if="selectedMessage.admin_reply" class="message-bubble admin">
        <div class="bubble-header"><i class="fas fa-headset"></i> {{ $t('support.supportReply') }} <span class="reply-time">{{ new Date(selectedMessage.replied_at).toLocaleString() }}</span></div>
        <p>{{ selectedMessage.admin_reply }}</p>
      </div>
      <p v-else class="waiting-reply"><i class="fas fa-hourglass-half"></i> {{ $t('support.waitingReply') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { supportApi, orderApi } from '@/api'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const { t } = useI18n()
const messages = ref([])
const recentOrders = ref([])
const showForm = ref(false)
const selectedMessage = ref(null)
const sending = ref(false)
const loading = ref(true)
const formError = ref('')
const formSuccess = ref('')
const newMessage = ref({ category: 'payment_issue', subject: '', message: '', order_id: null })

async function loadMessages() {
  try {
    const res = await supportApi.getAll({ per_page: 50 })
    messages.value = res.data.data || []
  } catch { /* empty */ }
}

async function loadOrders() {
  try {
    const res = await orderApi.getAll({ per_page: 20 })
    recentOrders.value = res.data.data || []
  } catch { /* empty */ }
}

async function sendMessage() {
  sending.value = true
  formError.value = ''
  formSuccess.value = ''
  try {
    await supportApi.create(newMessage.value)
    formSuccess.value = t('support.messageSent')
    newMessage.value = { category: 'payment_issue', subject: '', message: '', order_id: null }
    await loadMessages()
    setTimeout(() => { showForm.value = false; formSuccess.value = '' }, 1500)
  } catch (err) {
    formError.value = err.response?.data?.message || t('support.failedToSend')
  } finally { sending.value = false }
}

function viewMessage(msg) { selectedMessage.value = msg }

function quickMessage(category) {
  newMessage.value.category = category
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  newMessage.value = { category: 'payment_issue', subject: '', message: '', order_id: null }
  formError.value = ''
  formSuccess.value = ''
}

onMounted(async () => { await Promise.all([loadMessages(), loadOrders()]); loading.value = false })
</script>

<style scoped>
.support-page { padding: 32px 0; }
.page-title { font-size: 28px; margin-bottom: 24px; display: flex; align-items: center; gap: 10px; }
.page-title i { color: #e74c3c; }

.support-layout { display: grid; grid-template-columns: 1fr 320px; gap: 24px; align-items: start; }
.support-section, .support-sidebar, .support-form-card, .support-detail-card { padding: 24px; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.section-header h2 { font-size: 18px; display: flex; align-items: center; gap: 8px; }
.section-header h2 i { color: #e74c3c; }

.empty-state { text-align: center; padding: 40px 20px; color: #999; }
.empty-state i { font-size: 48px; margin-bottom: 12px; display: block; }
.empty-state p { margin: 4px 0; }
.muted { color: #999; font-size: 13px; }

.message-list-item { padding: 16px; border: 1px solid #f0f0f0; border-radius: 8px; margin-bottom: 12px; cursor: pointer; transition: all 0.2s; }
.message-list-item:hover { border-color: #e74c3c; background: #fef5f5; }
.msg-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; font-size: 12px; }
.msg-status { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; text-transform: capitalize; }
.msg-status.status-open { background: #fff3cd; color: #856404; }
.msg-status.status-in_progress { background: #cce5ff; color: #004085; }
.msg-status.status-resolved { background: #d4edda; color: #155724; }
.msg-status.status-closed { background: #e9ecef; color: #6c757d; }
.msg-category { color: #666; }
.msg-date { margin-left: auto; color: #999; }
.message-list-item h3 { font-size: 15px; margin-bottom: 4px; }
.msg-preview { font-size: 13px; color: #666; margin-bottom: 6px; }
.msg-order { font-size: 12px; color: #e74c3c; font-weight: 600; }
.msg-reply-badge { margin-top: 8px; font-size: 12px; color: #27ae60; font-weight: 600; }

.support-sidebar h3 { font-size: 16px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.support-sidebar h3 i { color: #e74c3c; }
.support-sidebar p { font-size: 13px; color: #666; margin-bottom: 16px; }
.help-topics { display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; }
.help-topic { display: flex; align-items: center; gap: 10px; padding: 12px; border: 1px solid #f0f0f0; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500; transition: all 0.2s; }
.help-topic i { color: #e74c3c; width: 20px; text-align: center; }
.help-topic:hover { border-color: #e74c3c; background: #fef5f5; }
.account-reminder { padding: 14px; background: #fff3cd; border-radius: 8px; font-size: 13px; display: flex; gap: 10px; align-items: flex-start; }
.account-reminder i { color: #856404; margin-top: 2px; }
.account-reminder p { margin: 0; color: #856404; }

.support-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 13px; font-weight: 600; color: #555; }
.form-group input, .form-group select, .form-group textarea { padding: 10px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; font-family: inherit; }
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: #e74c3c; }
.form-error { color: #e74c3c; font-size: 13px; margin-top: 8px; }
.form-success { color: #27ae60; font-size: 13px; margin-top: 8px; }

.support-detail-card h2 { font-size: 20px; margin-bottom: 12px; }
.detail-meta { display: flex; gap: 16px; font-size: 13px; color: #666; margin-bottom: 20px; flex-wrap: wrap; }
.detail-meta i { margin-right: 4px; }
.message-bubble { padding: 16px; border-radius: 10px; margin-bottom: 12px; font-size: 14px; line-height: 1.6; }
.message-bubble.customer { background: #f0f7ff; border: 1px solid #d0e3f7; }
.message-bubble.admin { background: #eafaf1; border: 1px solid #c3e6cb; }
.bubble-header { font-size: 12px; font-weight: 600; color: #27ae60; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
.reply-time { color: #999; font-weight: 400; }
.waiting-reply { color: #999; font-size: 13px; font-style: italic; text-align: center; padding: 20px; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 13px; border: none; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: #e74c3c; color: #fff; }
.btn-primary:hover { background: #c0392b; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-outline { background: transparent; border: 1px solid #ddd; color: #555; }
.btn-outline:hover { border-color: #e74c3c; color: #e74c3c; }
.btn-sm { padding: 6px 14px; font-size: 12px; }

@media (max-width: 768px) {
  .support-layout { grid-template-columns: 1fr; }
}
</style>
