const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const API_ORIGIN = API_BASE.replace(/\/api\/?$/, '')

export function imageUrl(path) {
  if (!path) return null
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  const clean = path.startsWith('/') ? path : `/${path}`
  if (!clean.startsWith('/products/')) {
    return API_ORIGIN + '/products' + clean
  }
  return API_ORIGIN + clean
}
