import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import './AdminLayout.css'

const NAV_ITEMS = [
  { to: '/admin',          label: 'Orders',    icon: '📦', end: true },
  { to: '/admin/customers', label: 'Customers', icon: '👥' },
  { to: '/admin/menu',      label: 'Menu',      icon: '🍽️' },
]

export default function AdminLayout() {
  const { user, logout } = useAuth()
  const navigate          = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="admin-root">
      <aside className="admin-sidebar">
        <div className="sidebar-brand">
          <span>🧑‍🍳</span>
          <span>Admin</span>
        </div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map(({ to, label, icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <span className="sidebar-icon">{icon}</span>
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span className="sidebar-user">{user?.name}</span>
          <button className="btn btn-ghost btn-sm" onClick={handleLogout}>Logout</button>
        </div>
      </aside>

      {/* Mobile top bar */}
      <header className="admin-topbar">
        <span className="admin-topbar-title">🧑‍🍳 Admin</span>
        <div className="topbar-nav">
          {NAV_ITEMS.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `topbar-link ${isActive ? 'active' : ''}`}
            >
              {label}
            </NavLink>
          ))}
        </div>
        <button className="btn btn-ghost btn-sm" onClick={handleLogout}>Logout</button>
      </header>

      <main className="admin-main">
        <Outlet />
      </main>
    </div>
  )
}
