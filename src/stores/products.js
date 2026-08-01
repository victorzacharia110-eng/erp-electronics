import { defineStore } from 'pinia'
import { ref } from 'vue'
import { productApi, categoryApi } from '@/api'
import { useBusinessStore } from '@/stores/business'

export const useProductStore = defineStore('products', () => {
  const products = ref([])
  const featuredProducts = ref([])
  const categories = ref([])
  const currentProduct = ref(null)
  const currentCategory = ref(null)
  const loading = ref(false)
  const pagination = ref({})

  function businessParams(params = {}) {
    const businessStore = useBusinessStore()
    if (businessStore.activeSlug) {
      return { ...params, business: businessStore.activeSlug }
    }
    return params
  }

  async function fetchProducts(params = {}) {
    loading.value = true
    try {
      const response = await productApi.getAll(businessParams(params))
      products.value = response.data.data
      pagination.value = {
        currentPage: response.data.current_page,
        lastPage: response.data.last_page,
        perPage: response.data.per_page,
        total: response.data.total,
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchFeatured() {
    loading.value = true
    try {
      const response = await productApi.getFeatured(businessParams())
      featuredProducts.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function fetchProduct(slug) {
    loading.value = true
    try {
      const response = await productApi.getBySlug(slug, businessParams())
      currentProduct.value = response.data
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    loading.value = true
    try {
      const response = await categoryApi.getAll(businessParams())
      categories.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function fetchCategory(slug) {
    loading.value = true
    try {
      const response = await categoryApi.getBySlug(slug, businessParams())
      currentCategory.value = response.data
      products.value = response.data.products || []
      return response.data
    } finally {
      loading.value = false
    }
  }

  return {
    products,
    featuredProducts,
    categories,
    currentProduct,
    currentCategory,
    loading,
    pagination,
    fetchProducts,
    fetchFeatured,
    fetchProduct,
    fetchCategories,
    fetchCategory,
  }
})
