<template>
  <div class="inbox-page container">
    <h1 class="page-title"><i class="fas fa-inbox"></i> {{ $t('support.inbox') }}</h1>

    <SkeletonLoader v-if="loading" type="list" :count="4" />

    <div v-if="!loading && !selectedMessage" class="inbox-layout">
      <div class="inbox-filters">
        <button v-for="f in filters" :key="f.value" :class="['filter-btn', { active: activeFilter === f.value }]"
          @click="activeFilter = f.value">
          {{ f.label }} <span v-if="f.count" class="filter-count">{{ f.count }}</span>
        </button>
      </div>

      <div class="inbox-search" v-if="allMessages.length > 0">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input v-model="search" type="text" :placeholder="$t('common.searchPlaceholder')" @input="onSearch" />
        </div>
      </div>

      <div class="card inbox-list">
        <div v-if="filteredMessages.length === 0" class="empty-state">
          <i class="fas fa-envelope-open"></i>
          <p>{{ $t('support.noMessages') }}</p>
        </div>
        <div v-for="msg in paginatedMessages" :key="msg.id" class="inbox-item" @click="viewMessage(msg)">
          <div class="item-left">
            <span :class="['msg-status', `status-${msg.status}`]">{{ $t(`support.statuses.${msg.status}`) }}</span>
            <div>
              <h3>{{ msg.subject }}</h3>
              <p class="item-meta">
                <i class="fas fa-user"></i> {{ msg.user?.name }}
                <span v-if="msg.order_id"><i class="fas fa-receipt"></i> {{ msg.order?.order_number }}</span>
                <span><i class="fas fa-tag"></i> {{ $t(`support.categories.${msg.category}`) }}</span>
              </p>
            </div>
          </div>
          <span class="item-date">{{ new Date(msg.created_at).toLocaleDateString() }}</span>
        </div>
      </div>

      <TablePagination v-if="allMessages.length > 15" :current-page="currentPage" :total-pages="totalPages"
        :from="pageInfo.from" :to="pageInfo.to" :total="pageInfo.total" :show-all="showAll" @page="goToPage"
        @toggle-all="toggleShowAll" />
    </div>

    <div v-if="!loading && selectedMessage" class="card inbox-detail">
      <div class="section-header">
        <button class="btn btn-outline btn-sm" @click="selectedMessage = null"><i class="fas fa-arrow-left"></i> {{
          $t('common.back') }}</button>
        <div class="header-actions">
          <select v-model="selectedMessage.status" @change="changeStatus" class="status-select">
            <option value="open">{{ $t('support.statuses.open') }}</option>
            <option value="in_progress">{{ $t('support.statuses.in_progress') }}</option>
            <option value="resolved">{{ $t('support.statuses.resolved') }}</option>
            <option value="closed">{{ $t('support.statuses.closed') }}</option>
          </select>
        </div>
      </div>

      <div class="detail-top">
        <h2>{{ selectedMessage.subject }}</h2>
        <div class="detail-meta">
          <span><i class="fas fa-user"></i> {{ selectedMessage.user?.name }} ({{ selectedMessage.user?.email }})</span>
          <span><i class="fas fa-tag"></i> {{ $t(`support.categories.${selectedMessage.category}`) }}</span>
          <span><i class="fas fa-calendar"></i> {{ new Date(selectedMessage.created_at).toLocaleString() }}</span>
          <span v-if="selectedMessage.order_id"><i class="fas fa-receipt"></i> {{ selectedMessage.order?.order_number
            }}</span>
        </div>
      </div>

      <div class="message-bubble customer">
        <p>{{ selectedMessage.message }}</p>
      </div>

      <div v-if="selectedMessage.admin_reply" class="message-bubble admin">
        <div class="bubble-header"><i class="fas fa-headset"></i> {{ $t('support.yourReply') }}</div>
        <p>{{ selectedMessage.admin_reply }}</p>
      </div>

      <form v-if="selectedMessage.status !== 'closed'" @submit.prevent="sendReply" class="reply-form">
        <h3><i class="fas fa-reply"></i> {{ $t('support.reply') }}</h3>
        <textarea v-model="replyText" rows="4" :placeholder="$t('support.replyPlaceholder')" required></textarea>
        <div class="reply-actions">
          <select v-model="replyStatus" class="status-select">
            <option value="in_progress">{{ $t('support.statuses.in_progress') }}</option>
            <option value="resolved">{{ $t('support.statuses.resolved') }}</option>
            <option value="closed">{{ $t('support.statuses.closed') }}</option>
          </select>
          <button type="submit" class="btn btn-primary" :disabled="!replyText || replying">
            <i class="fas" :class="replying ? 'fa-spinner fa-spin' : 'fa-paper-plane'"></i>
            {{ replying ? $t('common.saving') : $t('support.sendReply') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { supportApi } from '@/api'
import TablePagination from '@/components/TablePagination.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const { t, locale } = useI18n()

const selectedMessage = ref(null)
const allMessages = ref([])
const activeFilter = ref('open')
const replyText = ref('')
const replyStatus = ref('in_progress')
const replying = ref(false)
const loading = ref(true)
const search = ref('')
const currentPage = ref(1)
const showAll = ref(false)
const PER_PAGE = 15

const filters = computed(() => {
  void locale.value
  const counts = { open: 0, in_progress: 0, resolved: 0, closed: 0, all: allMessages.value.length }
  allMessages.value.forEach(m => { if (counts[m.status] !== undefined) counts[m.status]++ })
  return [
    { value: 'all', label: t('support.statuses.all'), count: counts.all },
    { value: 'open', label: t('support.statuses.open'), count: counts.open },
    { value: 'in_progress', label: t('support.statuses.in_progress'), count: counts.in_progress },
    { value: 'resolved', label: t('support.statuses.resolved'), count: counts.resolved },
    { value: 'closed', label: t('support.statuses.closed'), count: counts.closed },
  ]
})

const filteredMessages = computed(() => {
  const q = search.value.toLowerCase().trim()
  let list = allMessages.value
  if (activeFilter.value !== 'all') {
    list = list.filter(m => m.status === activeFilter.value)
  }
  if (q) {
    list = list.filter(m =>
      (m.subject && m.subject.toLowerCase().includes(q)) ||
      (m.message && m.message.toLowerCase().includes(q)) ||
      (m.user?.name && m.user.name.toLowerCase().includes(q))
    )
  }
  return list
})

const totalPages = computed(() => Math.ceil(filteredMessages.value.length / PER_PAGE))
const pageInfo = computed(() => {
  const total = filteredMessages.value.length
  if (showAll.value) return { from: 1, to: total, total }
  const from = total === 0 ? 0 : (currentPage.value - 1) * PER_PAGE + 1
  const to = Math.min(currentPage.value * PER_PAGE, total)
  return { from, to, total }
})
const paginatedMessages = computed(() => {
  if (showAll.value) return filteredMessages.value
  const start = (currentPage.value - 1) * PER_PAGE
  return filteredMessages.value.slice(start, start + PER_PAGE)
})
function onSearch() { currentPage.value = 1; showAll.value = false }
function goToPage(p) { currentPage.value = p; showAll.value = false }
function toggleShowAll() { showAll.value = !showAll.value }

async function loadMessages() {
  try {
    const res = await supportApi.getAll({ per_page: 50, status: activeFilter.value === 'all' ? undefined : activeFilter.value })
    allMessages.value = res.data.data || []
  } catch { /* empty */ }
}

async function viewMessage(msg) {
  try {
    const res = await supportApi.getById(msg.id)
    selectedMessage.value = res.data
  } catch { selectedMessage.value = msg }
}

async function sendReply() {
  if (!replyText.value || !selectedMessage.value) return
  replying.value = true
  try {
    await supportApi.reply(selectedMessage.value.id, { admin_reply: replyText.value, status: replyStatus.value })
    selectedMessage.value.admin_reply = replyText.value
    selectedMessage.value.status = replyStatus.value
    replyText.value = ''
    await loadMessages()
  } catch (err) {
    alert(err.response?.data?.message || t('support.failedReply'))
  } finally { replying.value = false }
}

async function changeStatus() {
  if (!selectedMessage.value) return
  try {
    await supportApi.updateStatus(selectedMessage.value.id, { status: selectedMessage.value.status })
    await loadMessages()
  } catch { /* empty */ }
}

watch(activeFilter, () => { currentPage.value = 1; loadMessages() })
onMounted(async () => { await loadMessages(); loading.value = false })
</script>

<style scoped>
.inbox-page {
  padding: 32px 0;
}

.page-title {
  font-size: 28px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title i {
  color: #e74c3c;
}

.inbox-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  background: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.filter-btn.active {
  background: #e74c3c;
  color: #fff;
  border-color: #e74c3c;
}

.filter-count {
  background: rgba(0, 0, 0, 0.1);
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 11px;
}

.inbox-search {
  margin-bottom: 16px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f8f9fa;
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 10px 14px;
  max-width: 400px;
}

.search-box i {
  color: #999;
}

.search-box input {
  flex: 1;
  border: none;
  background: none;
  font-size: 14px;
  outline: none;
  font-family: inherit;
}

.inbox-list {
  padding: 16px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 12px;
  display: block;
}

.inbox-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.inbox-item:hover {
  border-color: #e74c3c;
  background: #fef5f5;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-left h3 {
  font-size: 14px;
  margin-bottom: 2px;
}

.item-meta {
  font-size: 12px;
  color: #888;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.item-meta i {
  margin-right: 3px;
}

.item-date {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.msg-status {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  text-transform: capitalize;
  white-space: nowrap;
}

.msg-status.status-open {
  background: #fff3cd;
  color: #856404;
}

.msg-status.status-in_progress {
  background: #cce5ff;
  color: #004085;
}

.msg-status.status-resolved {
  background: #d4edda;
  color: #155724;
}

.msg-status.status-closed {
  background: #e9ecef;
  color: #6c757d;
}

.inbox-detail {
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-top h2 {
  font-size: 20px;
  margin-bottom: 8px;
}

.detail-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #666;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.detail-meta i {
  margin-right: 4px;
}

.message-bubble {
  padding: 16px;
  border-radius: 10px;
  margin-bottom: 12px;
  font-size: 14px;
  line-height: 1.6;
}

.message-bubble.customer {
  background: #f0f7ff;
  border: 1px solid #d0e3f7;
}

.message-bubble.admin {
  background: #eafaf1;
  border: 1px solid #c3e6cb;
}

.bubble-header {
  font-size: 12px;
  font-weight: 600;
  color: #27ae60;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.reply-form {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.reply-form h3 {
  font-size: 16px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.reply-form h3 i {
  color: #e74c3c;
}

.reply-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
}

.reply-form textarea:focus {
  outline: none;
  border-color: #e74c3c;
}

.reply-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.status-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  background: #fff;
  cursor: pointer;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #e74c3c;
  color: #fff;
}

.btn-primary:hover {
  background: #c0392b;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline {
  background: transparent;
  border: 1px solid #ddd;
  color: #555;
}

.btn-outline:hover {
  border-color: #e74c3c;
  color: #e74c3c;
}

.btn-sm {
  padding: 6px 14px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .inbox-filters {
    overflow-x: auto;
    flex-wrap: nowrap;
  }
}
</style>
