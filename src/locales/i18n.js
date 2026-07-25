import { createI18n } from 'vue-i18n'
import sw from './sw.json'
import en from './en.json'

const saved = localStorage.getItem('locale')
const defaultLocale = saved || 'sw'

const i18n = createI18n({
  legacy: false,
  locale: defaultLocale,
  fallbackLocale: 'en',
  messages: { sw, en },
})

export default i18n
