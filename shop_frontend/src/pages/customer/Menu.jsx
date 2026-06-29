import { productsApi } from '../../api/client'
import { useFetch } from '../../hooks/useFetch'
import { useCart } from '../../context/CartContext'
import './Menu.css'

function ProductCard({ product }) {
  const { cart, setQuantity } = useCart()
  const quantity = cart[product.id]?.quantity || 0

  return (
    <div className="product-card fade-in">
      <div className="product-card-body">
        <h3 className="product-name">{product.name}</h3>
        {product.description && (
          <p className="product-desc">{product.description}</p>
        )}
        <span className="product-price">₹{parseFloat(product.price).toFixed(2)}</span>
      </div>

      <div className="product-card-action">
        {quantity === 0 ? (
          <button
            className="btn btn-outline btn-sm add-btn"
            onClick={() => setQuantity(product, 1)}
          >
            + Add
          </button>
        ) : (
          <div className="qty-control">
            <button className="qty-btn" onClick={() => setQuantity(product, quantity - 1)}>−</button>
            <span className="qty-value">{quantity}</span>
            <button className="qty-btn" onClick={() => setQuantity(product, quantity + 1)}>+</button>
          </div>
        )}
      </div>
    </div>
  )
}

export default function Menu() {
  const { data: products, loading, error, refetch } = useFetch(productsApi.list)

  if (loading) {
    return (
      <div className="loading-screen">
        <span className="spinner" />
        <span>Loading menu…</span>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <div className="alert alert-error">{error}</div>
        <button className="btn btn-secondary" onClick={refetch}>Try again</button>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h1>Today's Menu</h1>
        <p>Select items and quantities, then open the cart to place your order.</p>
      </div>

      {products?.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🍽️</div>
          <h3>No items available</h3>
          <p>The menu is empty right now. Check back soon.</p>
        </div>
      ) : (
        <div className="product-grid">
          {products?.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </div>
  )
}
