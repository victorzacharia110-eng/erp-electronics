<template>
  <div class="ai-suggestions">
    <div class="suggestions-header">
      <h2><i class="fas fa-brain"></i> {{ $t('analytics.aiInsights') }}</h2>
      <button class="refresh-btn" @click="loadSuggestions" :disabled="loading">
        <i :class="loading ? 'fas fa-spinner fa-spin' : 'fas fa-rotate'"></i>
        {{ loading ? $t('common.loading') : $t('analytics.refresh') }}
      </button>
    </div>

    <div v-if="loading && suggestions.length === 0" class="ai-loading">
      <div class="ai-brain"><i class="fas fa-robot"></i></div>
      <p>{{ $t('analytics.analyzingData') }}</p>
    </div>

    <div v-else-if="error" class="ai-error">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button class="btn btn-outline btn-sm" @click="loadSuggestions">{{ $t('common.tryAgain') }}</button>
    </div>

    <div v-else class="suggestions-grid">
      <div v-for="(s, i) in suggestions" :key="i" :class="['suggestion-card', `priority-${s.priority}`]">
        <div class="suggestion-top">
          <span :class="['priority-badge', s.priority]">{{ s.priority }}</span>
          <span class="category-badge"><i :class="categoryIcon(s.category)"></i> {{ s.category }}</span>
        </div>
        <h3>{{ s.title }}</h3>
        <p>{{ s.description }}</p>
      </div>
    </div>

    <div v-if="source === 'fallback' && suggestions.length > 0" class="ai-note">
      <i class="fas fa-info-circle"></i> {{ $t('analytics.basedOnYourData') }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { analyticsApi } from '@/api'

const props = defineProps({
  analyticsData: { type: Object, default: null },
})

const loading = ref(false)
const error = ref('')
const suggestions = ref([])
const source = ref('')

function categoryIcon(cat) {
  const icons = { inventory: 'fas fa-boxes-stacked', pricing: 'fas fa-tags', marketing: 'fas fa-bullhorn', operations: 'fas fa-cog', growth: 'fas fa-rocket' }
  return icons[cat] || 'fas fa-lightbulb'
}

async function loadSuggestions() {
  if (!props.analyticsData) return
  loading.value = true
  error.value = ''
  try {
    const res = await analyticsApi.getAiSuggestions(props.analyticsData)
    suggestions.value = res.data.suggestions || []
    source.value = res.data.source || 'ai'
  } catch {
    error.value = 'Failed to load AI suggestions'
  }
  loading.value = false
}

watch(() => props.analyticsData, (val) => { if (val) loadSuggestions() })
onMounted(() => { if (props.analyticsData) loadSuggestions() })
</script>

<style scoped>
.ai-suggestions {
  margin-bottom: 32px;
}

.suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.suggestions-header h2 {
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.suggestions-header h2 i {
  color: #9b59b6;
}

.refresh-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  font-family: inherit;
}

.refresh-btn:hover {
  border-color: #9b59b6;
  color: #9b59b6;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ai-loading {
  text-align: center;
  padding: 48px 20px;
}

.ai-brain {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #9b59b6, #3498db);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.ai-brain i {
  font-size: 28px;
  color: #fff;
}

.ai-loading p {
  color: #888;
  font-size: 14px;
}

.ai-error {
  text-align: center;
  padding: 32px 20px;
  color: #e74c3c;
}

.ai-error i {
  font-size: 28px;
  margin-bottom: 12px;
  display: block;
}

.ai-error p {
  margin-bottom: 12px;
  color: #666;
}

.btn-outline {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
}

.btn-outline:hover {
  border-color: #e74c3c;
  color: #e74c3c;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.suggestion-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 10px;
  padding: 20px;
  border-left: 4px solid #ddd;
  transition: box-shadow 0.2s;
}

.suggestion-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.suggestion-card.priority-high {
  border-left-color: #e74c3c;
}

.suggestion-card.priority-medium {
  border-left-color: #f39c12;
}

.suggestion-card.priority-low {
  border-left-color: #3498db;
}

.suggestion-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.priority-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.priority-badge.high {
  background: #fef5f5;
  color: #e74c3c;
}

.priority-badge.medium {
  background: #fef9e7;
  color: #f39c12;
}

.priority-badge.low {
  background: #eaf4ff;
  color: #3498db;
}

.category-badge {
  font-size: 11px;
  color: #888;
  display: flex;
  align-items: center;
  gap: 4px;
  text-transform: capitalize;
}

.suggestion-card h3 {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.suggestion-card p {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.ai-note {
  margin-top: 16px;
  padding: 12px 16px;
  background: #fef9e7;
  border: 1px solid #fdebd0;
  border-radius: 8px;
  font-size: 13px;
  color: #7d6608;
  display: flex;
  align-items: center;
  gap: 8px;
}

@media (max-width: 768px) {
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
