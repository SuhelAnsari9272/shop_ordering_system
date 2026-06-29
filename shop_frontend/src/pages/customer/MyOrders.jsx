import { ordersApi } from '../../api/client'
import { useFetch } from '../../hooks/useFetch'
import StatusBadge from '../../components/StatusBadge'
import './MyOrders.css'

const STATUS_PROGRESS = {
  RECEIVED: 1, PREPARING: 2, READY: 3, COMPLETED: 4, CANCELLED: 0,
}

function ProgressBar({ status }) {
  const step = STATUS_PROGRESS[status] || 0
  if (status === 'CANCELLED') {
    return <div className="order-progress cancelled">Order cancelled</div>
  }
  const steps = ['Received', 'Preparing', 'Ready', 'Completed']
  return (
    <div className="order-progress">
      {steps.map((label, i) => (
        <div key={label} className={`progress-step ${i < step ? 'done' : ''} ${i + 1 === step ? 'current' : ''}`}>
          <div className="progress-dot" />
          <span>{label}</span>
          {i < steps.length - 1 && <div className="progress-line" />}
        </div>
      ))}
    </div>
  )
}

function OrderCard({ order }) {
  const date = new Date(order.created_at).toLocaleString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })

  return (
    <div className="order-card fade-in">
      <div className="order-card-header">
        <div>
          <span className="order-id">Order #{order.id}</span>
          <span className="order-date">{date}</span>
        </div>
        <div className="order-header-right">
          <StatusBadge status={order.status} />
          <span className="order-total">₹{parseFloat(order.total_amount).toFixed(2)}</span>
        </div>
      </div>

      <ProgressBar status={order.status} />

      <div className="order-items-list">
        {order.items.map((item) => (
          <div key={item.id} className="order-line">
            <span>{item.product_name} × {item.quantity}</span>
            <span>₹{parseFloat(item.subtotal).toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function MyOrders() {
  const { data: orders, loading, error, refetch } = useFetch(ordersApi.listMine)

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1>My Orders</h1>
          <p>Track the status of your pre-orders.</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={refetch}>↻ Refresh</button>
      </div>

      {loading && (
        <div className="loading-screen"><span className="spinner" /><span>Loading orders…</span></div>
      )}
      {error && <div className="alert alert-error">{error}</div>}

      {!loading && !error && orders?.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📦</div>
          <h3>No orders yet</h3>
          <p>Head to the menu and place your first order.</p>
        </div>
      )}

      <div className="orders-list">
        {orders?.map((o) => <OrderCard key={o.id} order={o} />)}
      </div>
    </div>
  )
}
