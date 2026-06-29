import { useState } from 'react'
import { useCart } from '../../context/CartContext'
import { ordersApi } from '../../api/client'
import { getDetail } from '../../api/client'
import './CartSidebar.css'

export default function CartSidebar({ open, onClose }) {
  const { items, totalAmount, clearCart, toOrderPayload, setQuantity } = useCart()
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(null)
  const [error, setError]     = useState(null)

  const handlePlaceOrder = async () => {
    if (items.length === 0) return
    setLoading(true)
    setError(null)
    try {
      const order = await ordersApi.place(toOrderPayload())
      setSuccess(order)
      clearCart()
    } catch (err) {
      setError(getDetail(err))
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setSuccess(null)
    setError(null)
    onClose()
  }

  return (
    <aside className={`cart-sidebar ${open ? 'cart-sidebar--open' : ''}`}>
      <div className="cart-sidebar-header">
        <h2>Your Cart</h2>
        <button className="btn btn-ghost" onClick={handleClose} aria-label="Close cart">✕</button>
      </div>

      {success ? (
        <div className="cart-success fade-in">
          <div className="cart-success-icon">✅</div>
          <h3>Order placed!</h3>
          <p>Order <strong>#{success.id}</strong> received.</p>
          <p className="cart-success-total">Total: ₹{parseFloat(success.total_amount).toFixed(2)}</p>
          <p className="cart-success-sub">We'll start preparing it shortly. Check My Orders for updates.</p>
          <button className="btn btn-primary btn-full" style={{ marginTop: 20 }} onClick={handleClose}>
            Done
          </button>
        </div>
      ) : (
        <>
          {items.length === 0 ? (
            <div className="cart-empty">
              <span>🛒</span>
              <p>Your cart is empty.<br />Add items from the menu.</p>
            </div>
          ) : (
            <div className="cart-items">
              {items.map(({ product, quantity }) => (
                <div key={product.id} className="cart-item">
                  <div className="cart-item-info">
                    <span className="cart-item-name">{product.name}</span>
                    <span className="cart-item-price">
                      ₹{(parseFloat(product.price) * quantity).toFixed(2)}
                    </span>
                  </div>
                  <div className="cart-item-controls">
                    <button
                      className="qty-btn"
                      onClick={() => setQuantity(product, quantity - 1)}
                    >−</button>
                    <span className="qty-value">{quantity}</span>
                    <button
                      className="qty-btn"
                      onClick={() => setQuantity(product, quantity + 1)}
                    >+</button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {items.length > 0 && (
            <div className="cart-footer">
              {error && <div className="alert alert-error" style={{ fontSize: '0.83rem' }}>{error}</div>}
              <div className="cart-total">
                <span>Total</span>
                <span className="cart-total-amount">₹{totalAmount.toFixed(2)}</span>
              </div>
              <button
                className="btn btn-primary btn-full btn-lg"
                onClick={handlePlaceOrder}
                disabled={loading}
              >
                {loading ? <span className="spinner" /> : 'Place Order'}
              </button>
              <button
                className="btn btn-ghost btn-full btn-sm"
                onClick={clearCart}
                style={{ marginTop: 8 }}
              >
                Clear cart
              </button>
            </div>
          )}
        </>
      )}
    </aside>
  )
}
