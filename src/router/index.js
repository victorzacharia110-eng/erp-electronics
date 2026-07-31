import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/StoreLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/pages/home/HomePage.vue'),
      },
      {
        path: 'products',
        name: 'products',
        component: () => import('@/pages/products/ProductListPage.vue'),
      },
      {
        path: 'products/:slug',
        name: 'product-detail',
        component: () => import('@/pages/products/ProductDetailPage.vue'),
      },
      {
        path: 'category/:slug',
        name: 'category',
        component: () => import('@/pages/products/CategoryPage.vue'),
      },
      {
        path: 'cart',
        name: 'cart',
        component: () => import('@/pages/cart/CartPage.vue'),
      },
      {
        path: 'checkout',
        name: 'checkout',
        component: () => import('@/pages/checkout/CheckoutPage.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'orders',
        name: 'orders',
        component: () => import('@/pages/account/OrdersPage.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'account',
        name: 'account',
        component: () => import('@/pages/account/AccountPage.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'support',
        name: 'support',
        component: () => import('@/pages/account/SupportPage.vue'),
        meta: { requiresAuth: true, role: 'customer' },
      },
      {
        path: 'employee/support',
        name: 'employee-support',
        component: () => import('@/pages/employee/SupportInboxPage.vue'),
        meta: { requiresAuth: true, role: 'employee' },
      },
      {
        path: 'owner',
        name: 'owner-dashboard',
        component: () => import('@/pages/dashboards/OwnerDashboard.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/employees',
        name: 'owner-employees',
        component: () => import('@/pages/owner/EmployeeManagementPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'employee/clients',
        name: 'employee-clients',
        component: () => import('@/pages/employee/CustomerManagementPage.vue'),
        meta: { requiresAuth: true, role: 'employee' },
      },
      {
        path: 'owner/payment-settings',
        name: 'owner-payment-settings',
        component: () => import('@/pages/owner/PaymentSettingsPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/reports',
        name: 'owner-reports',
        component: () => import('@/pages/owner/ReportsPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/shipping',
        name: 'owner-shipping',
        component: () => import('@/pages/owner/ShippingSettingsPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/products',
        name: 'owner-products',
        component: () => import('@/pages/owner/ProductManagementPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/branches',
        name: 'owner-branches',
        component: () => import('@/pages/owner/BranchManagementPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/inbox',
        name: 'owner-inbox',
        component: () => import('@/pages/owner/OwnerInboxPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/products/new',
        name: 'owner-product-new',
        component: () => import('@/pages/owner/ProductFormPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/products/:id/edit',
        name: 'owner-product-edit',
        component: () => import('@/pages/owner/ProductFormPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/accounting',
        name: 'owner-accounting',
        component: () => import('@/pages/owner/AccountingDashboardPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/accounting/chart-of-accounts',
        name: 'owner-chart-of-accounts',
        component: () => import('@/pages/owner/ChartOfAccountsPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/accounting/journal',
        name: 'owner-journal',
        component: () => import('@/pages/owner/JournalEntryListPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/accounting/journal/new',
        name: 'owner-journal-new',
        component: () => import('@/pages/owner/JournalEntryCreatePage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/accounting/journal/:id',
        name: 'owner-journal-detail',
        component: () => import('@/pages/owner/JournalEntryDetailPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/accounting/trial-balance',
        name: 'owner-trial-balance',
        component: () => import('@/pages/owner/TrialBalancePage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/accounting/profit-loss',
        name: 'owner-profit-loss',
        component: () => import('@/pages/owner/ProfitLossPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/accounting/balance-sheet',
        name: 'owner-balance-sheet',
        component: () => import('@/pages/owner/BalanceSheetPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/accounting/general-ledger',
        name: 'owner-general-ledger',
        component: () => import('@/pages/owner/GeneralLedgerPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/commissions',
        name: 'owner-commissions',
        component: () => import('@/pages/owner/CommissionManagementPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/inventory',
        name: 'owner-inventory',
        component: () => import('@/pages/owner/InventoryManagementPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/purchase-orders',
        name: 'owner-purchase-orders',
        component: () => import('@/pages/owner/PurchaseOrderPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'employee/earnings',
        name: 'employee-earnings',
        component: () => import('@/pages/employee/EmployeeEarningsPage.vue'),
        meta: { requiresAuth: true, role: 'employee' },
      },
      {
        path: 'owner/suppliers',
        name: 'owner-suppliers',
        component: () => import('@/pages/owner/SupplierManagementPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'owner/stock-alerts',
        name: 'owner-stock-alerts',
        component: () => import('@/pages/owner/StockAlertsPage.vue'),
        meta: { requiresAuth: true, role: 'owner' },
      },
      {
        path: 'supplier',
        name: 'supplier-dashboard',
        component: () => import('@/pages/supplier/SupplierPortalPage.vue'),
        meta: { requiresAuth: true, role: 'supplier' },
      },
      {
        path: 'employee/orders',
        name: 'employee-orders',
        component: () => import('@/pages/employee/OrderManagementPage.vue'),
        meta: { requiresAuth: true, role: 'employee' },
      },
      {
        path: 'owner/orders',
        name: 'owner-orders',
        component: () => import('@/pages/employee/OrderManagementPage.vue'),
        meta: { requiresAuth: true, role: ['owner', 'employee'] },
      },
      {
        path: 'owner/customers',
        name: 'owner-customers',
        component: () => import('@/pages/employee/CustomerManagementPage.vue'),
        meta: { requiresAuth: true, role: ['owner', 'employee'] },
      },
      {
        path: 'employee',
        name: 'employee-dashboard',
        component: () => import('@/pages/dashboards/EmployeeDashboard.vue'),
        meta: { requiresAuth: true, role: 'employee' },
      },
      {
        path: 'customer',
        name: 'customer-dashboard',
        component: () => import('@/pages/dashboards/CustomerDashboard.vue'),
        meta: { requiresAuth: true, role: 'customer' },
      },
      {
        path: 'customer/inbox',
        name: 'customer-inbox',
        component: () => import('@/pages/customer/CustomerInboxPage.vue'),
        meta: { requiresAuth: true, role: 'customer' },
      },
    ],
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/auth/LoginPage.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/pages/auth/RegisterPage.vue'),
    meta: { guest: true },
  },
  {
    path: '/superadmin',
    component: () => import('@/layouts/SuperadminLayout.vue'),
    meta: { requiresAuth: true, role: 'superadmin' },
    children: [
      {
        path: '',
        name: 'superadmin-dashboard',
        component: () => import('@/pages/superadmin/SuperadminDashboard.vue'),
      },
      {
        path: 'owners',
        name: 'superadmin-owners',
        component: () => import('@/pages/superadmin/OwnerManagementPage.vue'),
      },
      {
        path: 'owners/:id',
        name: 'superadmin-owner-detail',
        component: () => import('@/pages/superadmin/OwnerDetailPage.vue'),
      },
      {
        path: 'branding/:id',
        name: 'superadmin-branding',
        component: () => import('@/pages/superadmin/BrandingPage.vue'),
      },
      {
        path: 'inbox',
        name: 'superadmin-inbox',
        component: () => import('@/pages/superadmin/SuperadminInboxPage.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const token = localStorage.getItem('auth_token')

  if (to.meta.requiresAuth && !token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  } else if (to.meta.guest && token) {
    return { name: 'home' }
  } else if (to.meta.role && token) {
    const authStore = useAuthStore()
    if (!authStore.user) {
      try {
        await authStore.fetchProfile()
      } catch {
        return { name: 'login' }
      }
    }
    const allowedRoles = Array.isArray(to.meta.role) ? to.meta.role : [to.meta.role]
    if (!allowedRoles.includes(authStore.user?.role)) {
      const dashboardMap = {
        superadmin: '/superadmin',
        owner: '/owner',
        employee: '/employee',
        customer: '/customer',
      }
      return dashboardMap[authStore.user?.role] || '/'
    }
  }
})

export default router
