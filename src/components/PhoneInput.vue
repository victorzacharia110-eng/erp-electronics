<template>
  <div class="phone-input" :class="{ 'phone-input--invalid': invalid, 'phone-input--disabled': disabled }">
    <button
      type="button"
      class="phone-input__dial"
      :disabled="disabled"
      @click="open = !open"
      @mousedown.prevent
    >
      <span class="phone-input__flag">{{ selected.flag }}</span>
      <span class="phone-input__code">+{{ selected.dial }}</span>
      <span class="phone-input__chevron">▾</span>
    </button>

    <input
      :id="id"
      :name="name"
      class="phone-input__number"
      type="tel"
      inputmode="tel"
      :value="display"
      :placeholder="placeholder"
      :disabled="disabled"
      :autocomplete="autocomplete"
      @input="onInput"
      @focus="onFocus"
      @blur="$emit('blur')"
      @keydown.down.prevent="open = true"
    />

    <div v-if="open" class="phone-input__menu">
      <button
        v-for="country in COUNTRIES"
        :key="country.code"
        type="button"
        class="phone-input__option"
        :class="{ 'phone-input__option--active': country.code === selected.code }"
        @click="select(country)"
      >
        <span class="phone-input__flag">{{ country.flag }}</span>
        <span class="phone-input__option-name">{{ country.name }}</span>
        <span class="phone-input__option-code">+{{ country.dial }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'

const COUNTRIES = [
  { code: 'TZ', name: 'Tanzania', dial: '255', flag: '🇹🇿', mask: '### ### ###' },
  { code: 'KE', name: 'Kenya', dial: '254', flag: '🇰🇪', mask: '### ### ###' },
  { code: 'UG', name: 'Uganda', dial: '256', flag: '🇺🇬', mask: '### ### ###' },
  { code: 'RW', name: 'Rwanda', dial: '250', flag: '🇷🇼', mask: '### ### ###' },
  { code: 'BI', name: 'Burundi', dial: '257', flag: '🇧🇮', mask: '### ### ##' },
  { code: 'ET', name: 'Ethiopia', dial: '251', flag: '🇪🇹', mask: '### ### ###' },
  { code: 'ZM', name: 'Zambia', dial: '260', flag: '🇿🇲', mask: '### ### ###' },
  { code: 'CD', name: 'DR Congo', dial: '243', flag: '🇨🇩', mask: '### ### ###' },
  { code: 'NG', name: 'Nigeria', dial: '234', flag: '🇳🇬', mask: '### ### ####' },
  { code: 'GH', name: 'Ghana', dial: '233', flag: '🇬🇭', mask: '### ### ####' },
  { code: 'ZA', name: 'South Africa', dial: '27', flag: '🇿🇦', mask: '### ### ###' },
  { code: 'EG', name: 'Egypt', dial: '20', flag: '🇪🇬', mask: '### ### ####' },
  { code: 'AE', name: 'UAE', dial: '971', flag: '🇦🇪', mask: '## ### ####' },
  { code: 'US', name: 'United States', dial: '1', flag: '🇺🇸', mask: '(###) ###-####' },
  { code: 'GB', name: 'United Kingdom', dial: '44', flag: '🇬🇧', mask: '#### ### ###' },
  { code: 'IN', name: 'India', dial: '91', flag: '🇮🇳', mask: '##### #####' },
  { code: 'CN', name: 'China', dial: '86', flag: '🇨🇳', mask: '### #### ####' },
  { code: 'DE', name: 'Germany', dial: '49', flag: '🇩🇪', mask: '### ### ####' },
  { code: 'FR', name: 'France', dial: '33', flag: '🇫🇷', mask: '### ### ###' },
]

const props = defineProps({
  modelValue: { type: String, default: '' },
  name: { type: String, default: 'phone' },
  id: { type: String, default: undefined },
  placeholder: { type: String, default: '700 000 000' },
  disabled: { type: Boolean, default: false },
  invalid: { type: Boolean, default: false },
  autocomplete: { type: String, default: 'tel' },
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const open = ref(false)
const selected = ref(COUNTRIES[0])
const national = ref('')

const display = computed(() => format(national.value, selected.value.mask))

const digitsOf = (value) => String(value).replace(/\D/g, '')

const matchesDial = (dial, digits) => digits.startsWith(dial)

function parseModel(value) {
  const raw = String(value || '').replace(/[\s\-()]/g, '')
  const digits = digitsOf(raw)
  if (!digits) {
    selected.value = COUNTRIES[0]
    national.value = ''
    return
  }
  const sorted = [...COUNTRIES].sort((a, b) => b.dial.length - a.dial.length)
  const found = sorted.find((c) => matchesDial(c.dial, digits))
  if (found) {
    selected.value = found
    national.value = digits.slice(found.dial.length)
  } else {
    selected.value = COUNTRIES[0]
    national.value = digits
  }
}

function format(digits, mask) {
  let out = ''
  let di = 0
  for (const ch of mask) {
    if (di >= digits.length) break
    if (ch === '#') {
      out += digits[di]
      di += 1
    } else {
      out += ch
    }
  }
  return out.replace(/[^0-9]+$/, '')
}

function onInput(e) {
  const digits = digitsOf(e.target.value)
  const max = (selected.value.mask.match(/#/g) || []).length
  national.value = digits.slice(0, max)
  emitUpdate()
}

function onFocus() {
  open.value = false
  emit('focus')
}

function select(country) {
  selected.value = country
  national.value = national.value.slice(0, (country.mask.match(/#/g) || []).length)
  emitUpdate()
  open.value = false
}

function emitUpdate() {
  emit('update:modelValue', national.value ? `+${selected.value.dial}${national.value}` : '')
}

function onDocClick(e) {
  if (!e.target.closest('.phone-input')) open.value = false
}

watch(
  () => props.modelValue,
  (value) => parseModel(value)
)

onMounted(() => {
  parseModel(props.modelValue)
  document.addEventListener('click', onDocClick)
})

onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
</script>

<style scoped>
.phone-input {
  position: relative;
  display: flex;
  width: 100%;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  background: #fff;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.phone-input:focus-within {
  border-color: #e74c3c;
  outline: none;
}

.phone-input--invalid {
  border-color: #e74c3c;
  background: #fef8f8;
}

.phone-input--disabled {
  opacity: 0.6;
  pointer-events: none;
}

.phone-input__dial {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 10px;
  border: none;
  border-right: 1px solid #e0e0e0;
  background: #fafafa;
  color: #333;
  font-size: 14px;
  font-family: inherit;
  cursor: pointer;
  white-space: nowrap;
  border-radius: 6px 0 0 6px;
}

.phone-input__flag {
  font-size: 16px;
  line-height: 1;
}

.phone-input__code {
  font-weight: 600;
}

.phone-input__chevron {
  font-size: 10px;
  color: #888;
}

.phone-input__number {
  flex: 1;
  min-width: 0;
  padding: 10px 14px;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  font-family: inherit;
  box-sizing: border-box;
}

.phone-input__number:focus {
  box-shadow: none;
}

.phone-input__menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 50;
  min-width: 240px;
  max-height: 260px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.phone-input__option {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 9px 12px;
  border: none;
  background: #fff;
  color: #333;
  font-size: 14px;
  font-family: inherit;
  text-align: left;
  cursor: pointer;
}

.phone-input__option:hover {
  background: #f5f5f5;
}

.phone-input__option--active {
  background: #fdecea;
  color: #e74c3c;
}

.phone-input__option-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.phone-input__option-code {
  color: #888;
  font-size: 13px;
}
</style>
