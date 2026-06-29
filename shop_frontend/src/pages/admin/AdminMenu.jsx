import { useState } from 'react'
import { productsApi, getDetail } from '../../api/client'
import { useFetch } from '../../hooks/useFetch'
import './AdminMenu.css'

function AddProductForm({ onCreated }) {
  const [form, setForm]       = useState({ name: '', description: '', price: '' })
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)
  const [success, setSuccess] = useState(null)
  const [open,    setOpen]    = useState(false)

  const set = (field) => (e) => setForm((p) => ({ ...p, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.name || !form.price) { setError('Name and price are required.'); return }
    const price = parseFloat(form.price)
    if (isNaN(price) || price <= 0) { setError('Enter a valid price.'); return }
    setLoading(true); setError(null); setSuccess(null)
    try {
      const p = await productsApi.create({ ...form, price, is_active: true })
      setSuccess(`"${p.name}" added to the menu.`)
      setForm({ name: '', description: '', price: '' })
      onCreated()
    } catch (err) {
      setError(getDetail(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card add-product-card">
      <div className="add-product-header" onClick={() => setOpen((o) => !o)}>
        <h3>+ Add New Item</h3>
        <span className="toggle-chevron">{open ? '▲' : '▼'}</span>
      </div>
      {open && (
        <div className="fade-in">
          {error   && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}
          <form onSubmit={handleSubmit} noValidate>
            <div className="form-row-3">
              <div className="form-group">
                <label>Item Name</label>
                <input value={form.name} onChange={set('name')} placeholder="Chicken Roll" />
              </div>
              <div className="form-group">
                <label>Price (₹)</label>
                <input value={form.price} onChange={set('price')} placeholder="90" type="number" min="0" step="0.01" />
              </div>
              <div className="form-group" style={{ flex: 2 }}>
                <label>Description (optional)</label>
                <input value={form.description} onChange={set('description')} placeholder="Spiced chicken wrapped in a soft paratha" />
              </div>
            </div>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? <span className="spinner" /> : 'Add Item'}
            </button>
          </form>
        </div>
      )}
    </div>
  )
}

function ProductRow({ product, onToggle }) {
  const [loading, setLoading] = useState(false)

  const toggle = async () => {
    setLoading(true)
    try { await onToggle(product.id, !product.is_active) }
    finally { setLoading(false) }
  }

  return (
    <div className={`product-row ${!product.is_active ? 'product-row--inactive' : ''}`}>
      <div className="product-row-info">
        <span className="product-row-name">{product.name}</span>
        {product.description && (
          <span className="product-row-desc">{product.description}</span>
        )}
      </div>
      <div className="product-row-right">
        <span className="product-row-price">₹{parseFloat(product.price).toFixed(2)}</span>
        <span className={`badge ${product.is_active ? 'badge-ready' : 'badge-cancelled'}`}>
          {product.is_active ? 'Active' : 'Inactive'}
        </span>
        <button
          className={`btn btn-sm ${product.is_active ? 'btn-danger' : 'btn-secondary'}`}
          onClick={toggle}
          disabled={loading}
        >
          {loading
            ? <span className="spinner" style={{ width: 14, height: 14 }} />
            : product.is_active ? 'Deactivate' : 'Activate'
          }
        </button>
      </div>
    </div>
  )
}

export default function AdminMenu() {
  const { data: products, loading, error, refetch } = useFetch(productsApi.listAll)

  const handleToggle = async (id, is_active) => {
    await productsApi.update(id, { is_active })
    refetch()
  }

  const active   = products?.filter((p) => p.is_active)  || []
  const inactive = products?.filter((p) => !p.is_active) || []

  return (
    <div>
      <div className="page-header">
        <h1>Menu Management</h1>
        <p>Add items and toggle availability. Only active items appear on the customer menu.</p>
      </div>

      <AddProductForm onCreated={refetch} />

      <div className="section-header">
        <h2>Menu Items ({products?.length || 0})</h2>
        <button className="btn btn-secondary btn-sm" onClick={refetch}>↻ Refresh</button>
      </div>

      {loading && <div className="loading-screen"><span className="spinner" /><span>Loading…</span></div>}
      {error   && <div className="alert alert-error">{error}</div>}

      {!loading && products?.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">🍽️</div>
          <h3>No menu items yet</h3>
          <p>Add your first item using the form above.</p>
        </div>
      )}

      {active.length > 0 && (
        <div className="card product-list" style={{ marginBottom: 20 }}>
          <div className="product-list-label">Active ({active.length})</div>
          {active.map((p) => <ProductRow key={p.id} product={p} onToggle={handleToggle} />)}
        </div>
      )}

      {inactive.length > 0 && (
        <div className="card product-list">
          <div className="product-list-label inactive-label">Inactive ({inactive.length})</div>
          {inactive.map((p) => <ProductRow key={p.id} product={p} onToggle={handleToggle} />)}
        </div>
      )}
    </div>
  )
}
