import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { CartProvider } from './context/CartContext'
import Login from './pages/Login'
import CustomerLayout from './pages/customer/CustomerLayout'
import Menu from './pages/customer/Menu'
import MyOrders from './pages/customer/MyOrders'
import AdminLayout from './pages/admin/AdminLayout'
import AdminOrders from './pages/admin/AdminOrders'
import AdminCustomers from './pages/admin/AdminCustomers'
import AdminMenu from './pages/admin/AdminMenu'

// Route guard: redirect to /login if not authenticated
function RequireAuth({ children, adminOnly = false }) {
  const { user, isAdmin } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (adminOnly && !isAdmin) return <Navigate to="/menu" replace />
  return children
}

// Redirect logged-in users away from /login
function RedirectIfLoggedIn() {
  const { user, isAdmin } = useAuth()
  if (user) return <Navigate to={isAdmin ? '/admin' : '/menu'} replace />
  return <Login />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<RedirectIfLoggedIn />} />

      {/* Customer routes */}
      <Route
        element={
          <RequireAuth>
            <CartProvider>
              <CustomerLayout />
            </CartProvider>
          </RequireAuth>
        }
      >
        <Route path="/menu"   element={<Menu />} />
        <Route path="/orders" element={<MyOrders />} />
      </Route>

      {/* Admin routes */}
      <Route
        element={
          <RequireAuth adminOnly>
            <AdminLayout />
          </RequireAuth>
        }
      >
        <Route path="/admin"            element={<AdminOrders />} />
        <Route path="/admin/customers"  element={<AdminCustomers />} />
        <Route path="/admin/menu"       element={<AdminMenu />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
