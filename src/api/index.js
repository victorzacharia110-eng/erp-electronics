import api from './axios'

export const authApi = {
  register(data) {
    return api.post('/auth/register', data)
  },
  login(data) {
    return api.post('/auth/login', data)
  },
  logout() {
    return api.post('/auth/logout')
  },
  getProfile() {
    return api.get('/auth/profile')
  },
  updateProfile(data) {
    return api.put('/auth/profile', data)
  },
  changePassword(data) {
    return api.post('/auth/change-password', data)
  },
}

export const employeeApi = {
  getAll() {
    return api.get('/employees')
  },
  create(data) {
    return api.post('/employees', data)
  },
  toggleStatus(id) {
    return api.patch(`/employees/${id}/toggle-status`)
  },
  assignBranch(id, branchId) {
    return api.patch(`/employees/${id}/assign-branch`, { branch_id: branchId })
  },
  delete(id) {
    return api.delete(`/employees/${id}`)
  },
}

export const branchApi = {
  getAll() {
    return api.get('/branches')
  },
  create(data) {
    return api.post('/branches', data)
  },
  getOne(id) {
    return api.get(`/branches/${id}`)
  },
  update(id, data) {
    return api.put(`/branches/${id}`, data)
  },
  setDefault(id) {
    return api.patch(`/branches/${id}/set-default`)
  },
  delete(id) {
    return api.delete(`/branches/${id}`)
  },
}

export const conversationApi = {
  getAll(params) {
    return api.get('/conversations', { params })
  },
  create(data) {
    return api.post('/conversations', data)
  },
  getOne(id) {
    return api.get(`/conversations/${id}`)
  },
  sendMessage(id, data) {
    return api.post(`/conversations/${id}/messages`, data)
  },
  updateStatus(id, data) {
    return api.patch(`/conversations/${id}/status`, data)
  },
  getOwnerDetails(id) {
    return api.get(`/conversations/${id}/owner-details`)
  },
  getCustomerDetails(id) {
    return api.get(`/conversations/${id}/customer-details`)
  },
  getUnreadCount() {
    return api.get('/conversations/unread-count')
  },
}

export const customerApi = {
  getAll() {
    return api.get('/customers')
  },
  toggleStatus(id) {
    return api.patch(`/customers/${id}/toggle-status`)
  },
  delete(id) {
    return api.delete(`/customers/${id}`)
  },
}

export const productApi = {
  getAll(params) {
    return api.get('/products', { params })
  },
  getFeatured() {
    return api.get('/products/featured')
  },
  getBySlug(slug) {
    return api.get(`/products/${slug}`)
  },
}

export const productManageApi = {
  getAll(params) {
    return api.get('/products-manage', { params })
  },
  getById(id) {
    return api.get(`/products/${id}`)
  },
  create(data) {
    return api.post('/products', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  update(id, data) {
    return api.post(`/products/${id}`, data, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: { _method: 'PUT' },
    })
  },
  delete(id) {
    return api.delete(`/products/${id}`)
  },
}

export const categoryApi = {
  getAll() {
    return api.get('/categories')
  },
  getBySlug(slug) {
    return api.get(`/categories/${slug}`)
  },
}

export const cartApi = {
  get() {
    return api.get('/cart')
  },
  add(data) {
    return api.post('/cart', data)
  },
  update(itemId, data) {
    return api.put(`/cart/${itemId}`, data)
  },
  remove(itemId) {
    return api.delete(`/cart/${itemId}`)
  },
  clear() {
    return api.delete('/cart')
  },
}

export const orderApi = {
  getAll(params) {
    return api.get('/orders', { params })
  },
  create(data) {
    return api.post('/orders', data)
  },
  getById(id) {
    return api.get(`/orders/${id}`)
  },
}

export const orderManageApi = {
  getAll(params) {
    return api.get('/orders-manage', { params })
  },
  updateStatus(orderId, status) {
    return api.patch(`/orders/${orderId}/status`, { status })
  },
  updateDelivery(orderId, data) {
    return api.patch(`/orders/${orderId}/delivery`, data)
  },
}

export const reportApi = {
  getDaily(date) {
    return api.get('/reports/daily', { params: { date } })
  },
  getSummary(params) {
    return api.get('/reports/summary', { params })
  },
}

export const paymentApi = {
  initiate(data) {
    return api.post('/payments/initiate', data)
  },
  getStatus(orderId) {
    return api.get(`/orders/${orderId}/payment-status`)
  },
}

export const addressApi = {
  getAll() {
    return api.get('/addresses')
  },
  create(data) {
    return api.post('/addresses', data)
  },
  update(id, data) {
    return api.put(`/addresses/${id}`, data)
  },
  delete(id) {
    return api.delete(`/addresses/${id}`)
  },
}

export const settingsApi = {
  getPayment() {
    return api.get('/settings/payment')
  },
  updatePayment(data) {
    return api.put('/settings/payment', data)
  },
  getBranding() {
    return api.get('/settings/branding')
  },
}

export const supportApi = {
  getAll(params) {
    return api.get('/support-messages', { params })
  },
  create(data) {
    return api.post('/support-messages', data)
  },
  getById(id) {
    return api.get(`/support-messages/${id}`)
  },
  reply(id, data) {
    return api.patch(`/support-messages/${id}/reply`, data)
  },
  updateStatus(id, data) {
    return api.patch(`/support-messages/${id}/status`, data)
  },
  getUnreadCount() {
    return api.get('/support/unread-count')
  },
}

export const paymentProviderApi = {
  getAll() {
    return api.get('/payment-providers')
  },
  getEnabled() {
    return api.get('/payment-providers')
  },
  manage() {
    return api.get('/payment-providers-manage')
  },
  create(data) {
    return api.post('/payment-providers', data)
  },
  update(id, data) {
    return api.put(`/payment-providers/${id}`, data)
  },
  delete(id) {
    return api.delete(`/payment-providers/${id}`)
  },
}

export const shippingRuleApi = {
  getAll() {
    return api.get('/shipping-rules')
  },
  calculate(data) {
    return api.post('/shipping/calculate', data)
  },
  create(data) {
    return api.post('/shipping-rules', data)
  },
  update(id, data) {
    return api.put(`/shipping-rules/${id}`, data)
  },
  delete(id) {
    return api.delete(`/shipping-rules/${id}`)
  },
}

export const analyticsApi = {
  getSales(months = 12) {
    return api.get('/analytics/sales', { params: { months } })
  },
  getAiSuggestions(analytics) {
    return api.post('/analytics/ai-suggestions', { analytics })
  },
}

export const superadminApi = {
  getStats() {
    return api.get('/superadmin/stats')
  },
  getOwners() {
    return api.get('/superadmin/owners')
  },
  getOwner(id) {
    return api.get(`/superadmin/owners/${id}`)
  },
  createOwner(data) {
    return api.post('/superadmin/owners', data)
  },
  toggleActive(id) {
    return api.patch(`/superadmin/owners/${id}/toggle-active`)
  },
  updateSubscription(id, data) {
    return api.put(`/superadmin/owners/${id}/subscription`, data)
  },
  updateLimits(id, data) {
    return api.put(`/superadmin/owners/${id}/limits`, data)
  },
  updateBranding(id, data) {
    return api.put(`/superadmin/owners/${id}/branding`, data)
  },
  uploadBrandingLogo(id, formData) {
    return api.post(`/superadmin/owners/${id}/branding-logo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  deleteOwner(id) {
    return api.delete(`/superadmin/owners/${id}`)
  },
  getPasswordStatus(id) {
    return api.get(`/superadmin/owners/${id}/password-status`)
  },
  getAllPasswordsStatus() {
    return api.get('/superadmin/passwords/status')
  },
  resetOwnerPassword(id) {
    return api.post(`/superadmin/owners/${id}/reset-password`)
  },
  setOwnerPassword(id, data) {
    return api.post(`/superadmin/owners/${id}/set-password`, data)
  },
  forcePasswordChange(id) {
    return api.post(`/superadmin/owners/${id}/force-password-change`)
  },
  unlockOwnerAccount(id) {
    return api.post(`/superadmin/owners/${id}/unlock-account`)
  },
}

export const accountApi = {
  getAll(params) {
    return api.get('/accounts', { params })
  },
  getTree() {
    return api.get('/accounts/tree')
  },
  create(data) {
    return api.post('/accounts', data)
  },
  update(id, data) {
    return api.put(`/accounts/${id}`, data)
  },
  delete(id) {
    return api.delete(`/accounts/${id}`)
  },
}

export const journalApi = {
  getAll(params) {
    return api.get('/journal-entries', { params })
  },
  create(data) {
    return api.post('/journal-entries', data)
  },
  getOne(id) {
    return api.get(`/journal-entries/${id}`)
  },
  update(id, data) {
    return api.put(`/journal-entries/${id}`, data)
  },
  delete(id) {
    return api.delete(`/journal-entries/${id}`)
  },
  post(id) {
    return api.post(`/journal-entries/${id}/post`)
  },
  void(id, data) {
    return api.post(`/journal-entries/${id}/void`, data)
  },
}

export const accountingReportApi = {
  getTrialBalance(params) {
    return api.get('/reports/trial-balance', { params })
  },
  getProfitLoss(params) {
    return api.get('/reports/profit-loss', { params })
  },
  getBalanceSheet(params) {
    return api.get('/reports/balance-sheet', { params })
  },
  getGeneralLedger(params) {
    return api.get('/reports/general-ledger', { params })
  },
}

export const commissionApi = {
  getAll(params) {
    return api.get('/commissions', { params })
  },
  getSummary() {
    return api.get('/commissions/summary')
  },
  pay(id) {
    return api.post(`/commissions/${id}/pay`)
  },
  payAll() {
    return api.post('/commissions/pay-all')
  },
  getMyEarnings() {
    return api.get('/commissions/my-earnings')
  },
}

export const inventoryApi = {
  getAll(params) {
    return api.get('/inventory', { params })
  },
  adjust(data) {
    return api.post('/inventory/adjust', data)
  },
  getTransactions(params) {
    return api.get('/inventory/transactions', { params })
  },
  getLowStock() {
    return api.get('/inventory/low-stock')
  },
  getDashboard() {
    return api.get('/inventory/dashboard')
  },
}

export const purchaseOrderApi = {
  getAll(params) {
    return api.get('/purchase-orders', { params })
  },
  create(data) {
    return api.post('/purchase-orders', data)
  },
  getOne(id) {
    return api.get(`/purchase-orders/${id}`)
  },
  receive(id) {
    return api.post(`/purchase-orders/${id}/receive`)
  },
  delete(id) {
    return api.delete(`/purchase-orders/${id}`)
  },
}

export const employeeProfileApi = {
  updateProfile(userId, data) {
    return api.put(`/employees/${userId}/profile`, data)
  },
}

export const supplierApi = {
  getAll(params) {
    return api.get('/suppliers', { params })
  },
  getActive() {
    return api.get('/suppliers/all')
  },
  create(data) {
    return api.post('/suppliers', data)
  },
  getOne(id) {
    return api.get(`/suppliers/${id}`)
  },
  update(id, data) {
    return api.put(`/suppliers/${id}`, data)
  },
  delete(id) {
    return api.delete(`/suppliers/${id}`)
  },
}

export const stockAlertApi = {
  getAll(params) {
    return api.get('/stock-alerts', { params })
  },
  getCount() {
    return api.get('/stock-alerts/count')
  },
  acknowledge(id) {
    return api.post(`/stock-alerts/${id}/acknowledge`)
  },
  resolve(id) {
    return api.post(`/stock-alerts/${id}/resolve`)
  },
}

export const notificationApi = {
  getAll() {
    return api.get('/notifications')
  },
  getCount() {
    return api.get('/notifications/count')
  },
  markRead(id) {
    return api.post(`/notifications/${id}/read`)
  },
  markAllRead() {
    return api.post('/notifications/read-all')
  },
}

export const supplierPortalApi = {
  getProfile() {
    return api.get('/supplier-portal/profile')
  },
  getOrders(params) {
    return api.get('/supplier-portal/purchase-orders', { params })
  },
  getOrder(id) {
    return api.get(`/supplier-portal/purchase-orders/${id}`)
  },
  updateOrderStatus(id, data) {
    return api.post(`/supplier-portal/purchase-orders/${id}/update-status`, data)
  },
}
