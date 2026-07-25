<template>
  <div class="table-pagination" v-if="total > 0">
    <div class="pagination-info">
      <span class="page-summary">{{ from }}–{{ to }} {{ $t('common.of') }} {{ total }}</span>
    </div>
    <div class="pagination-controls" v-if="!showAll">
      <button class="page-btn" :disabled="currentPage <= 1" @click="$emit('page', currentPage - 1)">
        <i class="fas fa-chevron-left"></i>
      </button>
      <template v-for="p in visiblePages" :key="p">
        <span v-if="p === '...'" class="page-dots">...</span>
        <button v-else :class="['page-btn', { active: p === currentPage }]" @click="$emit('page', p)">{{ p }}</button>
      </template>
      <button class="page-btn" :disabled="currentPage >= totalPages" @click="$emit('page', currentPage + 1)">
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>
    <button class="view-all-btn" @click="$emit('toggleAll')">
      <i :class="showAll ? 'fas fa-list-ol' : 'fas fa-list'"></i>
      {{ showAll ? $t('common.showPaginated') : $t('common.viewAll') }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: { type: Number, required: true },
  totalPages: { type: Number, required: true },
  from: { type: Number, required: true },
  to: { type: Number, required: true },
  total: { type: Number, required: true },
  showAll: { type: Boolean, default: false },
})

defineEmits(['page', 'toggleAll'])

const visiblePages = computed(() => {
  const pages = []
  const tp = props.totalPages
  const cp = props.currentPage
  if (tp <= 7) {
    for (let i = 1; i <= tp; i++) pages.push(i)
  } else {
    pages.push(1)
    if (cp > 3) pages.push('...')
    const start = Math.max(2, cp - 1)
    const end = Math.min(tp - 1, cp + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    if (cp < tp - 2) pages.push('...')
    pages.push(tp)
  }
  return pages
})
</script>

<style scoped>
.table-pagination { display: flex; align-items: center; gap: 16px; padding: 14px 0; flex-wrap: wrap; }
.pagination-info { font-size: 13px; color: #888; }
.pagination-controls { display: flex; align-items: center; gap: 4px; }
.page-btn { min-width: 32px; height: 32px; border: 1px solid #e0e0e0; border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px; font-weight: 500; color: #555; display: flex; align-items: center; justify-content: center; transition: all 0.15s; padding: 0 6px; }
.page-btn:hover:not(:disabled):not(.active) { border-color: #e74c3c; color: #e74c3c; }
.page-btn.active { background: #e74c3c; color: #fff; border-color: #e74c3c; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-dots { padding: 0 4px; color: #999; font-size: 13px; }
.view-all-btn { margin-left: auto; padding: 6px 14px; border: 1px dashed #ddd; border-radius: 6px; background: #fff; cursor: pointer; font-size: 12px; font-weight: 500; color: #666; display: inline-flex; align-items: center; gap: 6px; transition: all 0.15s; }
.view-all-btn:hover { border-color: #e74c3c; color: #e74c3c; }
</style>
