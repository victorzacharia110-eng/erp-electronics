<template>
  <div class="checkout-page container">
    <SkeletonLoader v-if="loading" type="text" :count="1" />

    <div v-else-if="orderSuccess" class="order-success">
      <div class="success-icon"><i class="fas"
          :class="orderSuccess.paymentType === 'paid' ? 'fa-check-circle' : 'fa-receipt'"></i></div>
      <h1>{{ orderSuccess.paymentType === 'paid' ? $t('checkout.orderConfirmed') : $t('checkout.orderPlaced') }}</h1>
      <p class="success-msg">{{ orderSuccess.message }}</p>
      <div class="success-details card">
        <div class="detail-row"><span>{{ $t('checkout.orderNumber') }}</span><strong>{{ orderSuccess.orderNumber
            }}</strong></div>
        <div class="detail-row"><span>{{ $t('checkout.total') }}</span><strong>TSh {{ formatPrice(orderSuccess.total)
            }}</strong></div>
        <div class="detail-row"><span>{{ $t('checkout.payment') }}</span><strong>{{ orderSuccess.paymentType === 'paid'
          ? $t('checkout.paid') : orderSuccess.paymentType }}</strong></div>
      </div>
      <div class="success-actions">
        <button v-if="orderSuccess.paymentType === 'pending'" class="btn btn-primary" @click="confirmPendingOrder">
          <i class="fas fa-check"></i> {{ $t('checkout.confirmPayment') }}
        </button>
        <button class="btn btn-outline" @click="goToOrders">
          <i class="fas fa-list"></i> {{ $t('checkout.viewOrders') }}
        </button>
      </div>
    </div>

    <template v-else>
      <h1 class="page-title">{{ $t('checkout.title') }}</h1>
      <div class="checkout-layout">
        <div class="checkout-form">
          <div class="card form-section">
            <h2><i class="fas fa-location-dot"></i> {{ $t('checkout.shippingAddress') }}</h2>
            <div v-if="addresses.length > 0" class="saved-addresses">
              <label v-for="addr in addresses" :key="addr.id"
                :class="['address-option', { active: selectedAddressId === addr.id }]">
                <input type="radio" :value="addr.id" v-model="selectedAddressId" name="address" />
                <div><strong>{{ addr.label || $t('checkout.defaultAddress') }}</strong>
                  <p>{{ addr.street }}, {{ addr.city }}, {{ addr.country }}</p>
                </div>
              </label>
              <button @click="showNewAddress = !showNewAddress" class="btn btn-outline btn-sm">
                <i class="fas" :class="showNewAddress ? 'fa-times' : 'fa-plus'"></i> {{ showNewAddress ?
                  $t('common.cancel') : $t('checkout.addNew') }}
              </button>
            </div>
            <div v-if="showNewAddress || addresses.length === 0" class="new-address-form">
              <div class="form-row">
                <div class="form-group"><label>{{ $t('checkout.label') }}</label><input v-model="newAddress.label"
                    type="text" :placeholder="$t('checkout.labelPlaceholder')" /></div>
                <div class="form-group"><label>{{ $t('checkout.street') }}</label><input v-model="newAddress.street"
                    type="text" required /></div>
              </div>
              <div class="form-row">
                <div class="form-group"><label>{{ $t('checkout.city') }}</label><input v-model="newAddress.city"
                    type="text" required /></div>
                <div class="form-group"><label>{{ $t('checkout.country') }}</label><input v-model="newAddress.country"
                    type="text" value="Tanzania" /></div>
              </div>
              <button @click="saveAddress" class="btn btn-outline btn-sm" :disabled="savingAddress"><i
                  class="fas fa-save"></i> {{ savingAddress ? $t('common.saving') : $t('common.save') }}</button>
              <p v-if="addressError" class="address-error"><i class="fas fa-exclamation-circle"></i> {{ addressError }}</p>
            </div>
          </div>

          <div class="card form-section">
            <h2><i class="fas fa-credit-card"></i> {{ $t('checkout.paymentMethod') }}</h2>

            <div v-if="clickpesaEnabled" class="clickpesa-section">
              <label :class="['payment-option clickpesa-option', { active: selectedPayment === 'clickpesa' }]">
                <input type="radio" value="clickpesa" v-model="selectedPayment" name="payment" />
                <i class="fas fa-globe"></i>
                <span>ClickPesa</span>
              </label>
              <div v-if="selectedPayment === 'clickpesa'" class="coming-soon-notice">
                <i class="fas fa-info-circle"></i>
                <div>
                  <strong>{{ $t('checkout.comingSoon') }}</strong>
                  <p>{{ $t('checkout.comingSoonDesc') }}</p>
                </div>
              </div>
            </div>

            <div class="mobile-money-section">
              <div class="payment-options">
                <label v-for="p in mobileMoneyProviders" :key="p.slug"
                  :class="['payment-option', { active: selectedPayment === p.slug }]">
                  <input type="radio" :value="p.slug" v-model="selectedPayment" name="payment" />
                  <i :class="p.icon"></i>
                  <span>{{ p.name }}</span>
                </label>
              </div>

              <div v-if="selectedPayment && selectedPayment !== 'cash'" class="payment-instructions">
                <div class="instruction-header">
                  <i class="fas fa-mobile-screen"></i>
                  <span>{{ $t('checkout.sendPaymentTo') }}</span>
                </div>
                <div class="payment-number">
                  <span class="number-label">{{ selectedProviderName }}</span>
                  <span class="number-value">{{ selectedProviderNumber }}</span>
                  <button class="copy-btn" @click="copyNumber"
                    :title="copied ? $t('checkout.copied') : $t('checkout.copyNumber')">
                    <i :class="copied ? 'fas fa-check' : 'fas fa-copy'"></i>
                  </button>
                </div>
                <p class="instruction-note">{{ $t('checkout.enterPhoneBelow') }}</p>
              </div>

              <div v-if="selectedPayment === 'cash'" class="cash-notice">
                <i class="fas fa-money-bill-wave"></i>
                <div>
                  <strong>{{ $t('checkout.payAtCounter') }}</strong>
                  <p>{{ $t('checkout.payAtCounterDesc') }}</p>
                </div>
              </div>

              <div class="form-group"
                v-if="selectedPayment && selectedPayment !== 'cash' && selectedPayment !== 'clickpesa'">
                <label>{{ $t('checkout.yourPhone') }}</label>
                <input v-model="phoneNumber" type="tel" :placeholder="$t('checkout.phonePlaceholder')" />
              </div>
            </div>
          </div>
        </div>

        <div class="card form-section delivery-section">
          <h2><i class="fas fa-truck"></i> {{ $t('checkout.deliveryOptions') }}</h2>
          <div class="delivery-options">
            <label :class="['delivery-option', { active: !deliveryRequired }]">
              <input type="radio" :value="false" v-model="deliveryRequired" />
              <i class="fas fa-store"></i>
              <div>
                <strong>{{ $t('checkout.pickup') }}</strong>
                <p>{{ $t('checkout.pickupDesc') }}</p>
              </div>
            </label>
            <label :class="['delivery-option', { active: deliveryRequired }]">
              <input type="radio" :value="true" v-model="deliveryRequired" />
              <i class="fas fa-truck"></i>
              <div>
                <strong>{{ $t('checkout.delivery') }}</strong>
                <p>{{ $t('checkout.deliveryDesc') }}</p>
              </div>
            </label>
          </div>
          <p v-if="deliveryRequired" class="delivery-note"><i class="fas fa-info-circle"></i> {{
            $t('checkout.deliveryNote') }}</p>
        </div>

        <div class="order-summary card">
          <h2>{{ $t('checkout.orderSummary') }}</h2>
          <div v-for="item in cartStore.items" :key="item.id" class="summary-item">
            <span>{{ item.product_variant?.product?.name }} x {{ item.quantity }}</span>
            <span>TSh {{ formatPrice(item.total) }}</span>
          </div>
          <div class="summary-row"><span>{{ $t('checkout.subtotal') }}</span><span>TSh {{
            formatPrice(cartStore.subtotal)
              }}</span></div>
          <div class="summary-row"><span>{{ $t('checkout.shipping') }}</span><span>{{ deliveryRequired ? shippingLabel :
            $t('checkout.free') }}</span></div>
          <div class="summary-row total"><span>{{ $t('checkout.total') }}</span><span>TSh {{
            formatPrice(cartStore.subtotal + (deliveryRequired ? shippingCost : 0))
              }}</span></div>
          <button class="btn btn-primary place-order-btn" @click="placeOrder" :disabled="!canPlaceOrder || placing">
            <i class="fas" :class="placing ? 'fa-spinner fa-spin' : 'fa-lock'"></i>
            {{ placing ? $t('checkout.placing') : $t('checkout.placeOrder') }}
          </button>
          <p v-if="selectedPayment === 'clickpesa'" class="disabled-reason">{{ $t('checkout.clickpesaUnavailable') }}
          </p>
          <p v-if="orderError" class="order-error"><i class="fas fa-exclamation-circle"></i> {{ orderError }}</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import { useCartStore } from '@/stores/cart'
import { addressApi, orderApi, paymentApi, settingsApi, cartApi, orderManageApi, shippingRuleApi } from '@/api'

const router = useRouter()
const cartStore = useCartStore()
const addresses = ref([])
const selectedAddressId = ref(null)
const showNewAddress = ref(false)
const savingAddress = ref(false)
const newAddress = ref({ label: '', street: '', city: '', country: 'Tanzania' })
const addressError = ref('')
const selectedPayment = ref('mpesa')
const phoneNumber = ref('')
const placing = ref(false)
const clickpesaEnabled = ref(false)
const copied = ref(false)
const orderError = ref('')
const orderSuccess = ref(null)
const loading = ref(true)
const deliveryRequired = ref(false)
const shippingCost = ref(0)
const shippingLabel = ref('')

watch(deliveryRequired, (val) => {
  if (val) calculateShipping()
  else { shippingCost.value = 0; shippingLabel.value = '' }
})

watch(() => newAddress.value.city, () => {
  if (deliveryRequired.value) calculateShipping()
})

const defaultProviders = [
  { slug: 'cash', name: 'Cash', icon: 'fas fa-money-bill-wave', number: null },
  { slug: 'mpesa', name: 'M-Pesa', icon: 'fas fa-mobile-screen', number: '0794770268' },
  { slug: 'airtel', name: 'Airtel Money', icon: 'fas fa-signal', number: '0683870268' },
  { slug: 'mixx_by_yas', name: 'Mixx by Yas', icon: 'fas fa-water', number: '0703870268' },
  { slug: 'halopesa', name: 'Halopesa', icon: 'fas fa-bolt', number: '0632870268' },
]

const extraProviders = ref([])
const mobileMoneyProviders = computed(() => {
  const extra = extraProviders.value.filter(p => !defaultProviders.find(d => d.slug === p.slug))
  return [...defaultProviders, ...extra]
})

const selectedProvider = computed(() => mobileMoneyProviders.value.find(p => p.slug === selectedPayment.value))
const selectedProviderName = computed(() => selectedProvider.value?.name || '')
const selectedProviderNumber = computed(() => selectedProvider.value?.number || '')

const canPlaceOrder = computed(() => {
  if (!selectedAddressId.value || !selectedPayment.value) return false
  if (selectedPayment.value === 'clickpesa') return false
  if (['cash'].includes(selectedPayment.value)) return true
  return !!phoneNumber.value
})

function formatPrice(v) { return Number(v).toLocaleString('en-TZ') }

async function copyNumber() {
  if (!selectedProvider.value) return
  await navigator.clipboard.writeText(selectedProvider.value.number)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

async function loadAddresses() {
  const r = await addressApi.getAll()
  addresses.value = r.data
  if (addresses.value.length) selectedAddressId.value = addresses.value.find(a => a.is_default)?.id || addresses.value[0].id
}

async function saveAddress() {
  addressError.value = ''
  if (!newAddress.value.street.trim()) { addressError.value = 'Street is required'; return }
  if (!newAddress.value.city.trim()) { addressError.value = 'City is required'; return }
  if (!newAddress.value.country.trim()) { addressError.value = 'Country is required'; return }
  savingAddress.value = true
  try {
    const r = await addressApi.create(newAddress.value)
    addresses.value.push(r.data)
    selectedAddressId.value = r.data.id
    showNewAddress.value = false
    newAddress.value = { label: '', street: '', city: '', country: 'Tanzania' }
  } catch (err) {
    const errors = err.response?.data?.errors
    if (errors) {
      const first = Object.values(errors)[0]
      addressError.value = Array.isArray(first) ? first[0] : String(first)
    } else {
      addressError.value = err.response?.data?.message || 'Failed to save address. Please try again.'
    }
  } finally { savingAddress.value = false }
}

async function placeOrder() {
  placing.value = true
  orderError.value = ''
  try {
    const o = await orderApi.create({ shipping_address_id: selectedAddressId.value, delivery_required: deliveryRequired.value, shipping_cost: deliveryRequired.value ? shippingCost.value : 0 })
    const res = await paymentApi.initiate({ order_id: o.data.id, provider: selectedPayment.value, phone_number: phoneNumber.value })
    await cartApi.clear()
    cartStore.$reset()
    orderSuccess.value = {
      orderId: o.data.id,
      orderNumber: o.data.order_number,
      total: o.data.total,
      paymentType: selectedPayment.value,
      message: res.data.message,
    }
  } catch (err) {
    orderError.value = err.response?.data?.message || err.message || 'Failed to place order. Please try again.'
  } finally {
    placing.value = false
  }
}

async function confirmPendingOrder() {
  if (!orderSuccess.value) return
  try {
    await orderManageApi.updateStatus(orderSuccess.value.orderId, 'paid')
    orderSuccess.value = { ...orderSuccess.value, paymentType: 'paid', message: 'Payment confirmed!' }
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to confirm payment')
  }
}

function goToOrders() { router.push('/orders') }

async function calculateShipping() {
  if (!deliveryRequired.value) {
    shippingCost.value = 0
    shippingLabel.value = ''
    return
  }
  const city = newAddress.value.city || 'Dar es Salaam'
  try {
    const res = await shippingRuleApi.calculate({ from_city: 'Dar es Salaam', to_city: city, subtotal: cartStore.subtotal })
    shippingCost.value = res.data.cost || 0
    shippingLabel.value = `TSh ${formatPrice(shippingCost.value)}`
  } catch {
    shippingCost.value = 0
    shippingLabel.value = ''
  }
}

async function initCheckout() {
  try {
    await cartStore.fetchCart()
    if (!cartStore.items.length) {
      router.push('/cart')
      return
    }
    try { await loadAddresses() } catch { /* user may have no addresses yet */ }
    try {
      const res = await settingsApi.getPayment()
      clickpesaEnabled.value = res.data.clickpesa_enabled
      if (clickpesaEnabled.value) selectedPayment.value = 'clickpesa'
      else selectedPayment.value = 'cash'
    } catch {
      selectedPayment.value = 'cash'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => initCheckout())
</script>

<style scoped>
.checkout-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 32px;
  align-items: start;
}

.form-section {
  padding: 24px;
  margin-bottom: 20px;
}

.form-section h2 {
  font-size: 18px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-section h2 i {
  color: #e74c3c;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #e74c3c;
}

.address-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border: 2px solid #eee;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.address-option.active {
  border-color: #e74c3c;
  background: #fef5f5;
}

.address-option p {
  font-size: 13px;
  color: #888;
  margin: 4px 0 0;
}

.payment-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 16px;
}

.payment-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  border: 2px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
}

.payment-option.active {
  border-color: #e74c3c;
  background: #fef5f5;
  color: #e74c3c;
}

.payment-option i {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.clickpesa-option {
  grid-column: 1 / -1;
  justify-content: center;
}

.clickpesa-section {}

.coming-soon-notice {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #fff8e1;
  border: 1px solid #ffe082;
  border-radius: 8px;
  margin-top: 12px;
}

.coming-soon-notice>i {
  color: #f39c12;
  font-size: 20px;
  margin-top: 2px;
  flex-shrink: 0;
}

.coming-soon-notice strong {
  display: block;
  font-size: 14px;
  margin-bottom: 4px;
  color: #e67e22;
}

.coming-soon-notice p {
  font-size: 13px;
  color: #888;
  margin: 0;
  line-height: 1.5;
}

.cash-notice {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #eafaf1;
  border: 1px solid #a3d9b1;
  border-radius: 8px;
  margin-bottom: 16px;
}

.cash-notice>i {
  color: #27ae60;
  font-size: 20px;
  margin-top: 2px;
  flex-shrink: 0;
}

.cash-notice strong {
  display: block;
  font-size: 14px;
  margin-bottom: 4px;
  color: #1a7a42;
}

.cash-notice p {
  font-size: 13px;
  color: #666;
  margin: 0;
  line-height: 1.5;
}

.payment-instructions {
  background: #f8f9fa;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.instruction-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #555;
  margin-bottom: 12px;
}

.instruction-header i {
  color: #e74c3c;
}

.payment-number {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 12px 16px;
}

.number-label {
  font-size: 12px;
  color: #888;
  min-width: 80px;
}

.number-value {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: 1px;
  flex: 1;
}

.copy-btn {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  border: 1px solid #eee;
  background: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  transition: all 0.2s;
  flex-shrink: 0;
}

.copy-btn:hover {
  background: #e74c3c;
  border-color: #e74c3c;
  color: #fff;
}

.instruction-note {
  font-size: 12px;
  color: #999;
  margin: 10px 0 0;
}

.order-summary {
  padding: 24px;
  position: sticky;
  top: 100px;
}

.order-summary h2 {
  font-size: 18px;
  margin-bottom: 20px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 8px 0;
  color: #777;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
  font-size: 14px;
}

.summary-row.total {
  font-size: 18px;
  font-weight: 700;
  border-bottom: none;
  color: #e74c3c;
}

.place-order-btn {
  width: 100%;
  margin-top: 20px;
  padding: 16px;
  font-size: 16px;
}

.place-order-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.disabled-reason {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.order-error, .address-error {
  text-align: center;
  font-size: 13px;
  color: #e74c3c;
  margin-top: 10px;
  padding: 10px;
  background: #fef5f5;
  border-radius: 6px;
}

.mobile-money-section {}

.delivery-section h2 {
  font-size: 18px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.delivery-section h2 i {
  color: #e74c3c;
}

.delivery-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

.delivery-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border: 2px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.delivery-option.active {
  border-color: #e74c3c;
  background: #fef5f5;
}

.delivery-option input {
  display: none;
}

.delivery-option i {
  font-size: 24px;
  color: #e74c3c;
  margin-top: 4px;
}

.delivery-option strong {
  display: block;
  font-size: 14px;
  margin-bottom: 2px;
}

.delivery-option p {
  margin: 0;
  font-size: 12px;
  color: #888;
}

.delivery-note {
  font-size: 13px;
  color: #2980b9;
  background: #eaf4ff;
  padding: 10px 14px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.order-success {
  text-align: center;
  max-width: 480px;
  margin: 40px auto;
}

.order-success .success-icon {
  font-size: 64px;
  color: #27ae60;
  margin-bottom: 16px;
}

.order-success h1 {
  font-size: 28px;
  margin-bottom: 8px;
}

.order-success .success-msg {
  color: #666;
  margin-bottom: 24px;
}

.success-details {
  padding: 20px;
  text-align: left;
  margin-bottom: 24px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row span {
  color: #888;
}

.detail-row strong {
  color: #333;
}

.success-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

@media (max-width: 768px) {
  .checkout-layout {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .payment-options {
    grid-template-columns: 1fr;
  }
}
</style>
