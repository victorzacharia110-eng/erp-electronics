import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  const businessId = localStorage.getItem('active_business_id')
  if (businessId) {
    config.headers['X-Business-Id'] = businessId
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const token = localStorage.getItem('auth_token')
    if (error.response?.status === 401 && token) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
