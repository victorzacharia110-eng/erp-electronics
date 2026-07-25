import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cartApi } from '@/api'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  const loading = ref(false)

  const itemCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )

  const subtotal = computed(() =>
    items.value.reduce((sum, item) => sum + parseFloat(item.total), 0)
  )

  const total = computed(() => subtotal.value + 5000)

  async function fetchCart() {
    loading.value = true
    try {
      const response = await cartApi.get()
      items.value = response.data.items || []
    } finally {
      loading.value = false
    }
  }

  async function addItem(productVariantId, quantity = 1) {
    loading.value = true
    try {
      const response = await cartApi.add({ product_variant_id: productVariantId, quantity })
      items.value = response.data.items || []
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function updateItem(itemId, quantity) {
    loading.value = true
    try {
      const response = await cartApi.update(itemId, { quantity })
      items.value = response.data.items || []
    } finally {
      loading.value = false
    }
  }

  async function removeItem(itemId) {
    loading.value = true
    try {
      const response = await cartApi.remove(itemId)
      items.value = response.data.items || []
    } finally {
      loading.value = false
    }
  }

  async function clearCart() {
    loading.value = true
    try {
      await cartApi.clear()
      items.value = []
    } finally {
      loading.value = false
    }
  }

  function $reset() {
    items.value = []
  }

  return {
    items,
    loading,
    itemCount,
    subtotal,
    total,
    fetchCart,
    addItem,
    updateItem,
    removeItem,
    clearCart,
    $reset,
  }
})
