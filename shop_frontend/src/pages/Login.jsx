import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getDetail } from '../api/client'
import './Login.css'

export default function Login() {
  const { login } = useAuth()
  const navigate   = useNavigate()

  const [mobile,   setMobile]   = useState('')
  const [password, setPassword] = useState('')
  const [error,    setError]    = useState('')
  const [loading,  setLoading]  = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!mobile.trim() || !password) { setError('Enter your mobile number and password.'); return }
    setError('')
    setLoading(true)
    try {
      const user = await login(mobile.trim(), password)
      navigate(user.role === 'admin' ? '/admin' : '/menu', { replace: true })
    } catch (err) {
      const detail = getDetail(err)
      setError(
        err.response?.status === 401
          ? 'Wrong mobile number or password.'
          : detail
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-root">
      <div className="login-card fade-in">
        <div className="login-brand">
          <span className="login-logo">🛍️</span>
          <h1>Shop Pre-Order</h1>
          <p>Order ahead · Skip the wait · Pickup only</p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="mobile">Mobile number</label>
            <input
              id="mobile"
              type="tel"
              placeholder="9876543210"
              value={mobile}
              onChange={(e) => setMobile(e.target.value)}
              autoComplete="username"
              autoFocus
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>
          <button
            type="submit"
            className="btn btn-primary btn-full btn-lg"
            disabled={loading}
          >
            {loading ? <span className="spinner" /> : 'Log in'}
          </button>
        </form>

        <p className="login-footer">
          Don't have an account? Ask the shop to register you.
        </p>
      </div>
    </div>
  )
}
