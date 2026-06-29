import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
})

// Attach JWT to every request if present in localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// On 401, clear stored credentials so the app redirects to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ---------- helpers ----------
const getDetail = (err) =>
  err.response?.data?.detail || err.message || 'Something went wrong'

// ---------- Auth ----------
export const authApi = {
  login: async (mobile, password) => {
    const { data } = await api.post('/auth/login', { mobile, password })
    return data
  },
}

// ---------- Products ----------
export const productsApi = {
  list: async () => {
    const { data } = await api.get('/products')
    return data
  },
  listAll: async () => {
    const { data } = await api.get('/products/all')
    return data
  },
  create: async (payload) => {
    const { data } = await api.post('/products', payload)
    return data
  },
  update: async (id, payload) => {
    const { data } = await api.put(`/products/${id}`, payload)
    return data
  },
}

// ---------- Orders ----------
export const ordersApi = {
  place: async (items) => {
    const { data } = await api.post('/orders', { items })
    return data
  },
  listMine: async () => {
    const { data } = await api.get('/orders')
    return data
  },
  listAll: async (params = {}) => {
    const { data } = await api.get('/orders', { params })
    return data
  },
  get: async (id) => {
    const { data } = await api.get(`/orders/${id}`)
    return data
  },
  updateStatus: async (id, status) => {
    const { data } = await api.put(`/orders/${id}/status`, { status })
    return data
  },
}

// ---------- Customers ----------
export const customersApi = {
  me: async () => {
    const { data } = await api.get('/customers/me')
    return data
  },
  list: async () => {
    const { data } = await api.get('/customers')
    return data
  },
  create: async (payload) => {
    const { data } = await api.post('/customers', payload)
    return data
  },
}

// ---------- Dashboard ----------
export const dashboardApi = {
  metrics: async () => {
    const { data } = await api.get('/dashboard/metrics')
    return data
  },
}

export { getDetail }
export default api
