<template>
  <div class="dashboard-page container">
    <div class="dash-header">
      <div>
        <h1><i class="fas fa-box" style="color: #e74c3c; margin-right: 12px;"></i>{{ $t('productsManage.title') }}</h1>
        <p>{{ $t('productsManage.subtitle') }}</p>
      </div>
      <div class="header-actions">
        <router-link to="/owner/products/new" class="btn btn-primary"><i class="fas fa-plus"></i> {{ $t('productsManage.addProduct') }}</router-link>
        <router-link to="/owner" class="back-btn"><i class="fas fa-arrow-left"></i> Back</router-link>
      </div>
    </div>

    <div class="filters-bar card">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input v-model="search" type="text" :placeholder="$t('productsManage.searchPlaceholder')" @input="debouncedLoad" />
      </div>
      <div class="filter-right">
        <select v-model="categoryFilter" @change="loadProducts" class="category-select">
          <option value="">{{ $t('productsManage.allCategories') }}</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </div>
    </div>

    <div class="summary-row">
      <div class="summary-pill"><span class="pill-num">{{ products.length }}</span> {{ $t('productsManage.products') }}</div>
      <div class="summary-pill"><span class="pill-num active-num">{{ products.filter(p => p.is_active).length }}</span> {{ $t('productsManage.active') }}</div>
      <div class="summary-pill"><span class="pill-num inactive-num">{{ products.filter(p => !p.is_active).length }}</span> {{ $t('productsManage.inactive') }}</div>
    </div>

    <SkeletonLoader v-if="loading" type="card" :count="6" />

    <div v-else-if="products.length === 0" class="empty-state card">
      <i class="fas fa-box-open"></i>
      <h3>{{ $t('productsManage.noProducts') }}</h3>
      <p>{{ $t('productsManage.noProductsDesc') }}</p>
      <router-link to="/owner/products/new" class="btn btn-primary" style="margin-top: 16px;"><i class="fas fa-plus"></i> {{ $t('productsManage.addYourFirst') }}</router-link>
    </div>

    <div v-else class="products-grid">
      <div v-for="product in paginatedProducts" :key="product.id" class="product-card card">
        <div class="product-image">
          <img :src="imageUrl(product.image) || '/placeholder.svg'" :alt="product.name" />
          <span :class="['active-badge', product.is_active ? 'active' : 'inactive']">{{ product.is_active ? $t('common.active') : $t('common.inactive') }}</span>
        </div>
        <div class="product-body">
          <span class="product-category">{{ product.category?.name || 'Uncategorized' }}</span>
          <h3 class="product-name">{{ product.name }}</h3>
          <div class="product-meta">
            <span class="product-sku">SKU: {{ product.sku }}</span>
            <span class="product-brand" v-if="product.brand">{{ product.brand }}</span>
          </div>
          <div class="product-pricing">
            <span class="current-price">TSh {{ formatPrice(product.price) }}</span>
            <span class="cost-price" v-if="product.cost_price">Cost: TSh {{ formatPrice(product.cost_price) }}</span>
          </div>
          <div class="product-stock">
            <span v-if="totalStock(product) > 0" class="in-stock">
              <i class="fas fa-check-circle"></i> {{ $t('productsManage.inStock', { count: totalStock(product) }) }}
            </span>
            <span v-else class="out-of-stock">
              <i class="fas fa-times-circle"></i> {{ $t('productsManage.outOfStock') }}
            </span>
            <span class="variant-count">{{ product.variants?.length || 0 }} {{ $t('productsManage.variants') }}</span>
          </div>
          <div class="product-actions">
            <router-link :to="`/owner/products/${product.id}/edit`" class="btn btn-sm btn-outline">
              <i class="fas fa-pen"></i> {{ $t('productsManage.edit') }}
            </router-link>
            <button class="btn btn-sm btn-danger" @click="confirmDelete(product)">
              <i class="fas fa-trash"></i> {{ $t('productsManage.delete') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <TablePagination
      v-if="products.length > 15"
      :current-page="currentPage" :total-pages="totalPages"
      :from="pageInfo.from" :to="pageInfo.to" :total="pageInfo.total"
      :show-all="showAll"
      @page="goToPage" @toggle-all="toggleShowAll"
    />

    <div class="modal-overlay" v-if="deleteDialog.show" @click.self="deleteDialog.show = false">
      <div class="modal-content">
        <h3><i class="fas fa-exclamation-triangle"></i> {{ $t('productsManage.confirmDelete') }}</h3>
        <p>{{ $t('productsManage.confirmDeleteDesc') }}</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="deleteDialog.show = false">{{ $t('common.cancel') }}</button>
          <button class="btn btn-danger" @click="doDelete">{{ $t('common.delete') }}</button>
        </div>
      </div>
    </div>

    <div class="toast" v-if="toastMsg" @click="toastMsg = ''">
      <i class="fas fa-check-circle"></i> {{ toastMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import TablePagination from '@/components/TablePagination.vue'
import { productManageApi, categoryApi } from '@/api'
import { imageUrl } from '@/utils/image'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

const products = ref([])
const categories = ref([])
const loading = ref(true)
const search = ref('')
const categoryFilter = ref('')
const toastMsg = ref('')
const deleteDialog = reactive({ show: false, product: null })

const currentPage = ref(1)
const showAll = ref(false)
const PER_PAGE = 15
const paginatedProducts = computed(() => {
  if (showAll.value) return products.value
  const start = (currentPage.value - 1) * PER_PAGE
  return products.value.slice(start, start + PER_PAGE)
})
const totalPages = computed(() => Math.ceil(products.value.length / PER_PAGE))
const pageInfo = computed(() => {
  const total = products.value.length
  if (showAll.value) return { from: 1, to: total, total }
  const from = total === 0 ? 0 : (currentPage.value - 1) * PER_PAGE + 1
  const to = Math.min(currentPage.value * PER_PAGE, total)
  return { from, to, total }
})
function goToPage(p) { currentPage.value = p; showAll.value = false }
function toggleShowAll() { showAll.value = !showAll.value }

watch([search, categoryFilter], () => { currentPage.value = 1; showAll.value = false })

function formatPrice(v) { return Number(v).toLocaleString('en-TZ') }
function totalStock(p) { return (p.variants || []).reduce((sum, v) => sum + (v.inventory?.quantity_on_hand || 0), 0) }

let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadProducts(), 300)
}

async function loadProducts() {
  loading.value = true
  try {
    const params = { all: 1 }
    if (search.value) params.search = search.value
    if (categoryFilter.value) params.category_id = categoryFilter.value
    const res = await productManageApi.getAll(params)
    products.value = res.data.data || []
  } catch { /* empty */ }
  loading.value = false
}

function confirmDelete(product) {
  deleteDialog.product = product
  deleteDialog.show = true
}

async function doDelete() {
  try {
    await productManageApi.delete(deleteDialog.product.id)
    products.value = products.value.filter(p => p.id !== deleteDialog.product.id)
    toastMsg.value = `${deleteDialog.product.name} deleted`
    setTimeout(() => toastMsg.value = '', 3000)
  } catch { /* empty */ }
  deleteDialog.show = false
}

onMounted(async () => {
  const catRes = await categoryApi.getAll()
  categories.value = catRes.data
  await loadProducts()
})
</script>

<style scoped>
.dashboard-page { padding: 32px 0; }
.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.dash-header h1 { font-size: 26px; }
.dash-header p { color: #888; font-size: 14px; margin-top: 4px; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.back-btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 16px; border: 1px solid #ddd; border-radius: 6px; text-decoration: none; color: #333; font-size: 13px; font-weight: 500; transition: all 0.2s; }
.back-btn:hover { border-color: #e74c3c; color: #e74c3c; }
.btn-primary { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; background: #e74c3c; color: #fff; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; text-decoration: none; transition: background 0.2s; }
.btn-primary:hover { background: #c0392b; }

.filters-bar { padding: 16px 20px; margin-bottom: 16px; display: flex; gap: 12px; align-items: center; }
.search-box { display: flex; align-items: center; gap: 10px; background: #f8f9fa; border: 1px solid #eee; border-radius: 6px; padding: 10px 14px; flex: 1; }
.search-box i { color: #999; }
.search-box input { flex: 1; border: none; background: none; font-size: 14px; outline: none; }
.category-select { padding: 10px 14px; border: 1px solid #eee; border-radius: 6px; font-size: 14px; font-family: inherit; background: #fff; cursor: pointer; }
.category-select:focus { outline: none; border-color: #e74c3c; }

.summary-row { display: flex; gap: 12px; margin-bottom: 20px; }
.summary-pill { background: #fff; border: 1px solid #eee; border-radius: 20px; padding: 6px 16px; font-size: 13px; color: #666; }
.pill-num { font-weight: 700; color: #333; }
.active-num { color: #27ae60; }
.inactive-num { color: #e74c3c; }

.loading-state { text-align: center; padding: 60px 20px; color: #888; }
.loading-state i { color: #e74c3c; margin-right: 8px; }
.empty-state { text-align: center; padding: 60px 20px; }
.empty-state i { font-size: 48px; color: #ddd; margin-bottom: 16px; display: block; }
.empty-state h3 { font-size: 20px; margin-bottom: 8px; }
.empty-state p { color: #888; font-size: 14px; }

.products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
.product-card { overflow: hidden; padding: 0; }
.product-image { height: 180px; background: #f8f8f8; position: relative; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.product-image img { width: 100%; height: 100%; object-fit: cover; }
.active-badge { position: absolute; top: 10px; right: 10px; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.active-badge.active { background: #eafaf1; color: #27ae60; }
.active-badge.inactive { background: #fef5f5; color: #e74c3c; }

.product-body { padding: 16px; }
.product-category { font-size: 11px; color: #999; text-transform: uppercase; letter-spacing: 0.5px; }
.product-name { font-size: 15px; font-weight: 600; margin: 4px 0 8px; color: #333; }
.product-meta { display: flex; gap: 12px; font-size: 12px; color: #888; margin-bottom: 8px; }
.product-pricing { display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px; }
.current-price { font-size: 18px; font-weight: 700; color: #e74c3c; }
.cost-price { font-size: 12px; color: #999; }
.product-stock { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 12px; }
.in-stock { color: #27ae60; font-weight: 500; }
.out-of-stock { color: #e74c3c; font-weight: 500; }
.variant-count { color: #888; }
.product-actions { display: flex; gap: 8px; border-top: 1px solid #f0f0f0; padding-top: 12px; }
.btn-sm { padding: 7px 12px; font-size: 12px; font-weight: 500; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 5px; transition: all 0.2s; border: none; }
.btn-outline { border: 1px solid #ddd; background: #fff; color: #333; }
.btn-outline:hover { border-color: #e74c3c; color: #e74c3c; }
.btn-danger { background: #fff; color: #e74c3c; border: 1px solid #e74c3c; }
.btn-danger:hover { background: #fef5f5; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 2000; display: flex; align-items: center; justify-content: center; }
.modal-content { background: #fff; border-radius: 10px; padding: 28px; width: 90%; max-width: 400px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.modal-content h3 { font-size: 18px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.modal-content h3 i { color: #f39c12; }
.modal-content p { color: #666; font-size: 14px; line-height: 1.5; margin-bottom: 24px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; }
.btn-outline { padding: 10px 16px; border: 1px solid #ddd; border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px; font-weight: 500; }
.btn-danger { padding: 10px 20px; background: #e74c3c; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600; }

.toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: #2c3e50; color: #fff; padding: 14px 24px; border-radius: 8px; font-size: 14px; font-weight: 500; z-index: 2000; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); animation: slideUp 0.3s ease; }
.toast i { color: #27ae60; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(20px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

@media (max-width: 768px) {
  .dash-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .products-grid { grid-template-columns: 1fr; }
  .filters-bar { flex-direction: column; }
}
</style>
