<template>
  <div class="category-page container">
    <h1 class="page-title">{{ category?.translated_name || category?.name || $t('common.category') }}</h1>

    <SkeletonLoader v-if="loading" type="card" :count="4" />

    <div v-else>
      <div v-if="productStore.products.length > 0" class="products-grid">
        <ProductCard v-for="product in productStore.products" :key="product.id" :product="product" />
      </div>
      <div v-else class="empty-state">
        <i class="fas fa-box-open"></i>
        <h3>{{ $t('product.noProductsInCategory') }}</h3>
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
const category = ref(null)
const loading = ref(true)

async function loadCategory() {
  loading.value = true
  category.value = await productStore.fetchCategory(route.params.slug)
  loading.value = false
}

onMounted(loadCategory)
watch(() => route.params.slug, loadCategory)
watch(() => businessStore.activeSlug, loadCategory)
</script>

<style scoped>
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
}


</style>
