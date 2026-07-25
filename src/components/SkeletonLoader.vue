<template>
  <div :class="['skeleton-wrap', `skeleton-${type}`]">
    <template v-for="n in count" :key="n">
      <!-- Card skeleton (product cards, etc.) -->
      <div v-if="type === 'card'" class="skel-card">
        <div class="skel-img pulse"></div>
        <div class="skel-body">
          <div class="skel-line w60 pulse"></div>
          <div class="skel-line w40 pulse"></div>
          <div class="skel-line w80 pulse"></div>
          <div class="skel-line w30 pulse"></div>
        </div>
      </div>

      <!-- Stats skeleton (dashboard stat cards) -->
      <div v-else-if="type === 'stats'" class="skel-stats-card">
        <div class="skel-icon pulse"></div>
        <div class="skel-stats-body">
          <div class="skel-line w70 pulse"></div>
          <div class="skel-line w50 pulse"></div>
        </div>
      </div>

      <!-- List item skeleton (orders, employees, customers, etc.) -->
      <div v-else-if="type === 'list'" class="skel-list-item">
        <div class="skel-avatar pulse"></div>
        <div class="skel-list-body">
          <div class="skel-line w60 pulse"></div>
          <div class="skel-line w40 pulse"></div>
        </div>
        <div class="skel-list-right">
          <div class="skel-line w30 pulse"></div>
        </div>
      </div>

      <!-- Table skeleton (management tables) -->
      <div v-else-if="type === 'table'" class="skel-table-row">
        <div class="skel-table-cell w15 pulse"></div>
        <div class="skel-table-cell w25 pulse"></div>
        <div class="skel-table-cell w20 pulse"></div>
        <div class="skel-table-cell w15 pulse"></div>
        <div class="skel-table-cell w10 pulse"></div>
      </div>

      <!-- Detail skeleton (product detail page) -->
      <div v-else-if="type === 'detail'" class="skel-detail">
        <div class="skel-detail-img pulse"></div>
        <div class="skel-detail-info">
          <div class="skel-line-lg w80 pulse"></div>
          <div class="skel-line w50 pulse"></div>
          <div class="skel-line-lg w60 pulse"></div>
          <div class="skel-line w40 pulse"></div>
          <div class="skel-line w70 pulse"></div>
          <div class="skel-line w50 pulse"></div>
          <div class="skel-btn pulse"></div>
        </div>
      </div>

      <!-- Text skeleton (generic content) -->
      <div v-else-if="type === 'text'" class="skel-text">
        <div class="skel-line w100 pulse"></div>
        <div class="skel-line w90 pulse"></div>
        <div class="skel-line w75 pulse"></div>
        <div class="skel-line w85 pulse"></div>
        <div class="skel-line w60 pulse"></div>
      </div>

      <!-- Alert skeleton (dashboard alert banners) -->
      <div v-else-if="type === 'alert'" class="skel-alert pulse"></div>

      <!-- Tiles skeleton (quick actions grid) -->
      <div v-else-if="type === 'tiles'" class="skel-tiles-grid">
        <div v-for="t in 6" :key="t" class="skel-tile pulse"></div>
      </div>

      <!-- Chart skeleton -->
      <div v-else-if="type === 'chart'" class="skel-chart pulse"></div>
    </template>
  </div>
</template>

<script setup>
defineProps({
  type: { type: String, default: 'card' },
  count: { type: Number, default: 4 },
})
</script>

<style scoped>
@keyframes shimmer {
  0% { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}

.pulse {
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 37%, #f0f0f0 63%);
  background-size: 800px 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 6px;
}

.skeleton-wrap { width: 100%; }

/* Card */
.skel-card { border: 1px solid #eee; border-radius: 8px; overflow: hidden; background: #fff; }
.skel-img { width: 100%; height: 180px; }
.skel-body { padding: 16px; display: flex; flex-direction: column; gap: 10px; }

/* Stats */
.skeleton-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 32px; }
.skel-stats-card { background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 24px; display: flex; align-items: center; gap: 16px; }
.skel-icon { width: 48px; height: 48px; border-radius: 10px; flex-shrink: 0; }
.skel-stats-body { display: flex; flex-direction: column; gap: 8px; flex: 1; }

/* List */
.skel-list-item { display: flex; align-items: center; gap: 14px; padding: 16px 20px; border: 1px solid #eee; border-radius: 8px; background: #fff; margin-bottom: 10px; }
.skel-avatar { width: 44px; height: 44px; border-radius: 50%; flex-shrink: 0; }
.skel-list-body { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.skel-list-right { flex-shrink: 0; width: 80px; display: flex; flex-direction: column; gap: 8px; align-items: flex-end; }

/* Table */
.skeleton-table { display: flex; flex-direction: column; gap: 0; border: 1px solid #eee; border-radius: 8px; overflow: hidden; background: #fff; }
.skel-table-row { display: grid; grid-template-columns: 1fr 2fr 1fr 1fr 0.5fr; gap: 16px; padding: 14px 20px; border-bottom: 1px solid #f5f5f5; }
.skel-table-row:last-child { border-bottom: none; }
.skel-table-cell { height: 16px; border-radius: 4px; }

/* Detail */
.skel-detail { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
.skel-detail-img { width: 100%; height: 400px; border-radius: 8px; }
.skel-detail-info { display: flex; flex-direction: column; gap: 14px; padding-top: 10px; }
.skel-line-lg { height: 24px; border-radius: 4px; }
.skel-btn { width: 160px; height: 48px; border-radius: 8px; margin-top: 10px; }

/* Text */
.skel-text { display: flex; flex-direction: column; gap: 12px; padding: 20px; }

/* Alert */
.skel-alert { width: 100%; height: 60px; border-radius: 8px; margin-bottom: 16px; }

/* Tiles grid */
.skel-tiles-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.skel-tile { height: 100px; border-radius: 8px; }

/* Chart */
.skel-chart { width: 100%; height: 300px; border-radius: 8px; }

/* Lines */
.skel-line { height: 12px; border-radius: 4px; }
.skel-line-lg { height: 20px; border-radius: 4px; }

/* Widths */
.w10 { width: 10%; }
.w15 { width: 15%; }
.w20 { width: 20%; }
.w25 { width: 25%; }
.w30 { width: 30%; }
.w40 { width: 40%; }
.w50 { width: 50%; }
.w60 { width: 60%; }
.w70 { width: 70%; }
.w75 { width: 75%; }
.w80 { width: 80%; }
.w85 { width: 85%; }
.w90 { width: 90%; }
.w100 { width: 100%; }

@media (max-width: 768px) {
  .skeleton-stats { grid-template-columns: repeat(2, 1fr); }
  .skel-detail { grid-template-columns: 1fr; }
  .skel-tiles-grid { grid-template-columns: repeat(2, 1fr); }
  .skel-table-row { grid-template-columns: 1fr 1.5fr 1fr; }
  .skel-table-cell:nth-child(4), .skel-table-cell:nth-child(5) { display: none; }
}
</style>
