import { useState } from 'react'
import { customersApi, getDetail } from '../../api/client'
import { useFetch } from '../../hooks/useFetch'
import './AdminCustomers.css'

function RegisterForm({ onCreated }) {
  const [form, setForm]     = useState({ name: '', mobile: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)
  const [success, setSuccess] = useState(null)

  const set = (field) => (e) => setForm((p) => ({ ...p, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.name || !form.mobile || !form.password) {
      setError('All fields are required.'); return
    }
    setLoading(true); setError(null); setSuccess(null)
    try {
      const customer = await customersApi.create(form)
      setSuccess(`${customer.name} registered successfully.`)
      setForm({ name: '', mobile: '', password: '' })
      onCreated()
    } catch (err) {
      setError(getDetail(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="register-form card">
      <h3>Register New Customer</h3>
      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}
      <form onSubmit={handleSubmit} noValidate>
        <div className="form-row">
          <div className="form-group">
            <label>Full Name</label>
            <input value={form.name} onChange={set('name')} placeholder="Suhel Ahmed" />
          </div>
          <div className="form-group">
            <label>Mobile Number</label>
            <input value={form.mobile} onChange={set('mobile')} placeholder="9876543210" type="tel" />
          </div>
          <div className="form-group">
            <label>Temporary Password</label>
            <input value={form.password} onChange={set('password')} type="password" placeholder="••••••••" />
          </div>
          <div className="form-submit">
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? <span className="spinner" /> : '+ Register'}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}

export default function AdminCustomers() {
  const { data: customers, loading, error, refetch } = useFetch(customersApi.list)

  return (
    <div>
      <div className="page-header">
        <h1>Customers</h1>
        <p>Register new customers and view all registered accounts.</p>
      </div>

      <RegisterForm onCreated={refetch} />

      <div className="section-header">
        <h2>All Customers</h2>
        <button className="btn btn-secondary btn-sm" onClick={refetch}>↻ Refresh</button>
      </div>

      {loading && <div className="loading-screen"><span className="spinner" /><span>Loading…</span></div>}
      {error   && <div className="alert alert-error">{error}</div>}

      {!loading && customers?.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">👥</div>
          <h3>No customers yet</h3>
          <p>Register the first customer using the form above.</p>
        </div>
      )}

      {customers && customers.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Mobile</th>
                <th>Status</th>
                <th>Role</th>
                <th>Registered</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((c) => (
                <tr key={c.id}>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>#{c.id}</td>
                  <td style={{ fontWeight: 600 }}>{c.name}</td>
                  <td>{c.mobile}</td>
                  <td>
                    {c.is_active
                      ? <span className="badge" style={{ background: 'var(--green-soft)', color: 'var(--green)' }}>Active</span>
                      : <span className="badge" style={{ background: 'var(--red-soft)', color: 'var(--red)' }}>Inactive</span>
                    }
                  </td>
                  <td>
                    {c.is_admin
                      ? <span className="badge" style={{ background: 'var(--accent-soft)', color: 'var(--accent)' }}>Admin</span>
                      : <span className="badge" style={{ background: 'var(--bg-muted)', color: 'var(--text-muted)' }}>Customer</span>
                    }
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                    {new Date(c.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
