<template>
  <router-view />
  <SessionWarningModal v-if="session.showWarning" />
</template>

<script setup>
import { watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSessionStore } from '@/stores/session'
import SessionWarningModal from '@/components/SessionWarningModal.vue'

const authStore = useAuthStore()
const session = useSessionStore()

watch(
  () => authStore.token,
  (token) => {
    if (token) session.start()
    else session.stop()
  },
  { immediate: true }
)
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #333;
  background: #fff;
  min-height: 100vh;
  overflow-x: hidden;
}

.store-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
}

a {
  text-decoration: none;
  color: inherit;
  transition: color 0.2s;
}

button {
  cursor: pointer;
  border: none;
  background: none;
  font-family: 'Inter', sans-serif;
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::selection {
  background: #e74c3c;
  color: #fff;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 28px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-primary {
  background: #e74c3c;
  color: #fff;
  border: none;
}

.btn-primary:hover {
  background: #c0392b;
  transform: translateY(-1px);
}

.btn-outline {
  color: #333;
  background: transparent;
  border: 2px solid #333;
}

.btn-outline:hover {
  background: #333;
  color: #fff;
}

.btn-white {
  background: #fff;
  color: #e74c3c;
  border: none;
}

.btn-white:hover {
  background: #f8f8f8;
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-sm {
  padding: 8px 18px;
  font-size: 13px;
}

.card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 6px;
  font-size: 14px;
  color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #e74c3c;
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
}

.price {
  font-weight: 700;
  color: #e74c3c;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #eee;
  border-top-color: #e74c3c;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 8px;
}

.section-subtitle {
  text-align: center;
  color: #777;
  margin-bottom: 32px;
  font-size: 15px;
}

@media (max-width: 768px) {
  .container {
    padding: 0 16px;
  }
}
</style>
