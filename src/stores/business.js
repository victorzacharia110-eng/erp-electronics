import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { businessApi } from '@/api'

export const useBusinessStore = defineStore('business', () => {
  const directory = ref([])
  const mine = ref([])
  const current = ref(null)
  const slugMode = ref(false)
  const loading = ref(false)

  const activeSlug = computed(() => current.value?.slug || null)

  function persist() {
    if (current.value) {
      localStorage.setItem('active_business_id', String(current.value.id))
    } else {
      localStorage.removeItem('active_business_id')
    }
  }

  function setSlugMode(mode) {
    slugMode.value = !!mode
  }

  async function fetchDirectory() {
    try {
      const res = await businessApi.list()
      directory.value = res.data.data || []
    } catch {
      directory.value = []
    }
  }

  async function fetchMine() {
    try {
      const res = await businessApi.mine()
      mine.value = res.data.data || []
    } catch {
      mine.value = []
    }
  }

  async function setCurrent(business) {
    current.value = business
    persist()
  }

  function syncBusiness(business) {
    if (!business?.id) return
    const replace = (list) => list.map((b) => (String(b.id) === String(business.id) ? business : b))
    directory.value = replace(directory.value)
    mine.value = replace(mine.value)
    if (current.value && String(current.value.id) === String(business.id)) {
      current.value = business
      persist()
    }
  }

  async function loadBySlug(slug) {
    if (!slug) {
      current.value = null
      return null
    }
    const cached =
      directory.value.find((b) => b.slug === slug) ||
      mine.value.find((b) => b.slug === slug)
    if (cached) {
      current.value = cached
      persist()
    }
    try {
      const res = await businessApi.bySlug(slug)
      current.value = res.data
      persist()
      return res.data
    } catch {
      if (cached) return cached
      current.value = null
      return null
    }
  }

  function restoreFromStorage() {
    const id = localStorage.getItem('active_business_id')
    if (!id) return null
    const found =
      mine.value.find((b) => String(b.id) === String(id)) ||
      directory.value.find((b) => String(b.id) === String(id))
    if (found) {
      current.value = found
      return found
    }
    return null
  }

  function pickFallback() {
    if (current.value) return current.value
    const list = mine.value.length ? mine.value : directory.value
    if (list.length === 1) {
      current.value = list[0]
      persist()
      return list[0]
    }
    return null
  }

  function link(path) {
    if (slugMode.value && activeSlug.value) {
      return `/${activeSlug.value}${path}`
    }
    return path
  }

  return {
    directory,
    mine,
    current,
    slugMode,
    loading,
    activeSlug,
    setSlugMode,
    fetchDirectory,
    fetchMine,
    setCurrent,
    syncBusiness,
    loadBySlug,
    restoreFromStorage,
    pickFallback,
    link,
  }
})
