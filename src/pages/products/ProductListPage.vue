<template>
  <div class="product-list-page container">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ productStore.currentCategory?.name || $t('product.allProducts') }}</h1>
      </div>
      <div class="filters">
        <select v-model="sortBy" @change="loadProducts" class="sort-select">
          <option value="created_at">{{ $t('product.newest') }}</option>
          <option value="price">{{ $t('product.price') }}</option>
          <option value="name">{{ $t('product.name') }}</option>
        </select>
      </div>
    </div>

    <SkeletonLoader v-if="productStore.loading" type="card" :count="8" />

    <div v-else-if="productStore.products.length === 0" class="empty-state">
      <i class="fas fa-box-open"></i>
      <h3>{{ $t('search.noProducts') }}</h3>
      <p>{{ $t('search.tryAdjust') }}</p>
    </div>

    <div v-else>
      <div class="products-grid">
        <ProductCard
          v-for="product in productStore.products"
          :key="product.id"
          :product="product"
        />
      </div>

      <div v-if="productStore.pagination.lastPage > 1" class="pagination">
        <button
          class="btn btn-outline btn-sm"
          :disabled="productStore.pagination.currentPage === 1"
          @click="changePage(productStore.pagination.currentPage - 1)"
        >
          <i class="fas fa-chevron-left"></i> {{ $t('common.previous') }}
        </button>
        <span class="page-info">
          {{ $t('common.pageOf', { current: productStore.pagination.currentPage, total: productStore.pagination.lastPage }) }}
        </span>
        <button
          class="btn btn-outline btn-sm"
          :disabled="productStore.pagination.currentPage === productStore.pagination.lastPage"
          @click="changePage(productStore.pagination.currentPage + 1)"
        >
          {{ $t('common.next') }} <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProductStore } from '@/stores/products'
import { useBusinessStore } from '@/stores/business'
import ProductCard from '@/components/product/ProductCard.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const route = useRoute()
const productStore = useProductStore()
const businessStore = useBusinessStore()
const sortBy = ref('created_at')

function loadProducts(overrides = {}) {
  productStore.fetchProducts({
    page: overrides.page,
    sort: sortBy.value,
    search: route.query.search || undefined,
    category_id: route.query.category_id || undefined,
  })
}

function changePage(page) {
  loadProducts({ page })
}

onMounted(() => loadProducts())
watch(() => route.query, () => loadProducts())
watch(() => businessStore.activeSlug, () => loadProducts())
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 32px;
  padding-top: 40px;
}

.sort-select {
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
}

.empty-state {
  text-align: center;
  padding: 80px 0;
  color: #999;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.3;
}

.empty-state h3 {
  color: #333;
  margin-bottom: 8px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 40px;
  padding-bottom: 40px;
}

.page-info {
  font-size: 14px;
  color: #777;
}


</style>
