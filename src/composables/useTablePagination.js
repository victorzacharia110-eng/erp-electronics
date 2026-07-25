import { ref, computed } from 'vue'

const PER_PAGE = 15

export function useTablePagination(items, searchFields, perPage = PER_PAGE) {
  const search = ref('')
  const currentPage = ref(1)
  const showAll = ref(false)

  const filteredItems = computed(() => {
    const q = search.value.toLowerCase().trim()
    if (!q) return items.value
    return items.value.filter(item =>
      searchFields.some(field => {
        const val = field.split('.').reduce((obj, k) => obj?.[k], item)
        return val != null && String(val).toLowerCase().includes(q)
      })
    )
  })

  const totalPages = computed(() => Math.ceil(filteredItems.value.length / perPage))

  const paginatedItems = computed(() => {
    if (showAll.value) return filteredItems.value
    const start = (currentPage.value - 1) * perPage
    return filteredItems.value.slice(start, start + perPage)
  })

  const displayItems = computed(() => paginatedItems.value)

  const pageInfo = computed(() => {
    const total = filteredItems.value.length
    if (showAll.value) return { from: 1, to: total, total }
    const from = total === 0 ? 0 : (currentPage.value - 1) * perPage + 1
    const to = Math.min(currentPage.value * perPage, total)
    return { from, to, total }
  })

  function onSearch() {
    currentPage.value = 1
    showAll.value = false
  }

  function goToPage(page) {
    currentPage.value = page
    showAll.value = false
  }

  function toggleShowAll() {
    showAll.value = !showAll.value
  }

  return {
    search,
    currentPage,
    showAll,
    filteredItems,
    displayItems,
    totalPages,
    pageInfo,
    onSearch,
    goToPage,
    toggleShowAll,
  }
}
