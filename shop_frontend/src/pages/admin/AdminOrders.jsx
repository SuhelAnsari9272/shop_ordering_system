import { useState, useEffect, useCallback } from 'react'
import { ordersApi, dashboardApi, getDetail } from '../../api/client'
import StatusBadge from '../../components/StatusBadge'
import './AdminOrders.css'

const NEXT_STATUS = { RECEIVED: 'PREPARING', PREPARING: 'READY', READY: 'COMPLETED' }
const NEXT_LABEL  = { RECEIVED: 'Mark Preparing', PREPARING: 'Mark Ready', READY: 'Mark Completed' }

function MetricsBar({ metrics }) {
  if (!metrics) return null
  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <div className="metric-label">Total Today</div>
        <div className="metric-value">{metrics.total_orders_today}</div>
      </div>
      <div className="metric-card">
        <div className="metric-label">⏳ Pending</div>
        <div className="metric-value" style={{ color: 'var(--orange)' }}>{metrics.pending_orders}</div>
      </div>
      <div className="metric-card">
        <div className="metric-label">✅ Completed</div>
        <div className="metric-value" style={{ color: 'var(--green)' }}>{metrics.completed_orders}</div>
      </div>
    </div>
  )
}

function OrderRow({ order, onStatusChange }) {
  const [updating, setUpdating] = useState(false)
  const [cancelling, setCancelling] = useState(false)

  const advance = async () => {
    const next = NEXT_STATUS[order.status]
    if (!next) return
    setUpdating(true)
    try { await onStatusChange(order.id, next) }
    finally { setUpdating(false) }
  }

  const cancel = async () => {
    setCancelling(true)
    try { await onStatusChange(order.id, 'CANCELLED') }
    finally { setCancelling(false) }
  }

  const date = new Date(order.created_at).toLocaleString('en-IN', {
    day: 'numeric', month: 'short',
    hour: '2-digit', minute: '2-digit',
  })

  const itemsSummary = order.items
    .map((i) => `${i.product_name} ×${i.quantity}`)
    .join(', ')

  return (
    <div className="order-row fade-in">
      <div className="order-row-main">
        <div className="order-row-top">
          <span className="order-row-id">#{order.id}</span>
          <StatusBadge status={order.status} />
          <span className="order-row-time">{date}</span>
        </div>
        <div className="order-row-customer">
          👤 {order.customer_name} · {order.customer_mobile}
        </div>
        <div className="order-row-items">{itemsSummary}</div>
      </div>
      <div className="order-row-right">
        <span className="order-row-total">₹{parseFloat(order.total_amount).toFixed(2)}</span>
        <div className="order-row-actions">
          {NEXT_STATUS[order.status] && (
            <button
              className="btn btn-primary btn-sm"
              onClick={advance}
              disabled={updating}
            >
              {updating ? <span className="spinner" style={{ width: 14, height: 14 }} /> : NEXT_LABEL[order.status]}
            </button>
          )}
          {!['COMPLETED', 'CANCELLED'].includes(order.status) && (
            <button
              className="btn btn-danger btn-sm"
              onClick={cancel}
              disabled={cancelling}
            >
              {cancelling ? <span className="spinner" style={{ width: 14, height: 14 }} /> : 'Cancel'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default function AdminOrders() {
  const [orders,     setOrders]     = useState([])
  const [metrics,    setMetrics]    = useState(null)
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState(null)
  const [statusFilter, setFilter]   = useState('ALL')
  const [todayOnly,  setTodayOnly]  = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(null)

  const load = useCallback(async () => {
    setError(null)
    try {
      const params = {}
      if (statusFilter !== 'ALL') params.status = statusFilter
      if (todayOnly) params.today_only = true
      const [ordersData, metricsData] = await Promise.all([
        ordersApi.listAll(params),
        dashboardApi.metrics(),
      ])
      setOrders(ordersData)
      setMetrics(metricsData)
      setLastRefresh(new Date())
    } catch (err) {
      setError(getDetail(err))
    } finally {
      setLoading(false)
    }
  }, [statusFilter, todayOnly])

  useEffect(() => { load() }, [load])

  // Auto-refresh every 5s
  useEffect(() => {
    if (!autoRefresh) return
    const id = setInterval(load, 5000)
    return () => clearInterval(id)
  }, [autoRefresh, load])

  const handleStatusChange = async (orderId, newStatus) => {
    await ordersApi.updateStatus(orderId, newStatus)
    await load()
  }

  const STATUS_OPTS = ['ALL', 'RECEIVED', 'PREPARING', 'READY', 'COMPLETED', 'CANCELLED']

  return (
    <div>
      <div className="page-header">
        <h1>Incoming Orders</h1>
        <p>Manage and advance orders as you prepare them.</p>
      </div>

      <MetricsBar metrics={metrics} />

      <div className="orders-toolbar">
        <div className="orders-filters">
          <select
            className="filter-select"
            value={statusFilter}
            onChange={(e) => setFilter(e.target.value)}
          >
            {STATUS_OPTS.map((s) => (
              <option key={s} value={s}>{s === 'ALL' ? 'All statuses' : s}</option>
            ))}
          </select>
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={todayOnly}
              onChange={(e) => setTodayOnly(e.target.checked)}
            />
            Today only
          </label>
        </div>
        <div className="orders-toolbar-right">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh (5s)
          </label>
          <button className="btn btn-secondary btn-sm" onClick={load}>↻ Refresh</button>
          {lastRefresh && (
            <span className="refresh-time">
              Updated {lastRefresh.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </span>
          )}
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading && (
        <div className="loading-screen"><span className="spinner" /><span>Loading orders…</span></div>
      )}

      {!loading && orders.length === 0 && !error && (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h3>No orders found</h3>
          <p>No orders match the current filter.</p>
        </div>
      )}

      <div className="admin-orders-list">
        {orders.map((o) => (
          <OrderRow key={o.id} order={o} onStatusChange={handleStatusChange} />
        ))}
      </div>
    </div>
  )
}
