<template>
  <div class="session-overlay">
    <div class="session-card card">
      <div class="session-icon"><i class="fas fa-hourglass-half"></i></div>
      <h2>{{ $t('session.title') }}</h2>
      <p class="session-message">{{ $t('session.message') }}</p>
      <div class="session-count">{{ session.warningSeconds }}</div>
      <p class="session-hint">{{ $t('session.hint') }}</p>
      <button class="btn btn-primary session-btn" @click="staySignedIn">
        <i class="fas fa-hand-pointer"></i> {{ $t('session.staySignedIn') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { useSessionStore } from '@/stores/session'

const session = useSessionStore()

function staySignedIn() {
  session.activity()
}
</script>

<style scoped>
.session-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 24px;
}

.session-card {
  width: 100%;
  max-width: 400px;
  padding: 36px 32px;
  text-align: center;
}

.session-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  border-radius: 50%;
  background: #fdecea;
  color: #e74c3c;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
}

.session-card h2 {
  font-size: 20px;
  margin-bottom: 8px;
}

.session-message {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
}

.session-count {
  font-size: 44px;
  font-weight: 700;
  color: #e74c3c;
  line-height: 1.1;
}

.session-hint {
  color: #888;
  font-size: 13px;
  margin-top: 8px;
  margin-bottom: 20px;
}

.session-btn {
  width: 100%;
  justify-content: center;
}
</style>
