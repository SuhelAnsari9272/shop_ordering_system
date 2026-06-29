import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useCart } from '../../context/CartContext'
import CartSidebar from './CartSidebar'
import './CustomerLayout.css'

export default function CustomerLayout() {
  const { user, logout } = useAuth()
  const { totalItems }   = useCart()
  const navigate         = useNavigate()
  const [cartOpen, setCartOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="customer-root">
      {/* ---- Top navbar ---- */}
      <header className="customer-nav">
        <div className="nav-brand">
          <span>🛍️</span>
          <span className="nav-title">Shop Pre-Order</span>
        </div>
        <nav className="nav-links">
          <NavLink to="/menu"   className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Menu</NavLink>
          <NavLink to="/orders" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>My Orders</NavLink>
        </nav>
        <div className="nav-right">
          <button
            className="cart-btn"
            onClick={() => setCartOpen(true)}
            aria-label="Open cart"
          >
            🛒
            {totalItems > 0 && <span className="cart-count">{totalItems}</span>}
          </button>
          <div className="nav-user">
            <span className="nav-user-name">{user?.name}</span>
            <button className="btn btn-ghost btn-sm" onClick={handleLogout}>Logout</button>
          </div>
        </div>
      </header>

      {/* ---- Mobile bottom tab bar ---- */}
      <nav className="bottom-nav">
        <NavLink to="/menu"   className={({ isActive }) => isActive ? 'bottom-tab active' : 'bottom-tab'}>
          <span>🍽️</span><span>Menu</span>
        </NavLink>
        <button className="bottom-tab cart-tab" onClick={() => setCartOpen(true)}>
          <span>🛒{totalItems > 0 && <sup className="cart-sup">{totalItems}</sup>}</span>
          <span>Cart</span>
        </button>
        <NavLink to="/orders" className={({ isActive }) => isActive ? 'bottom-tab active' : 'bottom-tab'}>
          <span>📦</span><span>Orders</span>
        </NavLink>
      </nav>

      {/* ---- Page content ---- */}
      <main className="customer-main">
        <Outlet />
      </main>

      {/* ---- Cart sidebar ---- */}
      <CartSidebar open={cartOpen} onClose={() => setCartOpen(false)} />
      {cartOpen && <div className="cart-overlay" onClick={() => setCartOpen(false)} />}
    </div>
  )
}
