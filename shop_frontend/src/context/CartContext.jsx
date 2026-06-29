import { createContext, useContext, useState, useCallback } from 'react'

const CartContext = createContext(null)

export function CartProvider({ children }) {
  // cart: { [product_id]: { product, quantity } }
  const [cart, setCart] = useState({})

  const setQuantity = useCallback((product, quantity) => {
    setCart((prev) => {
      if (quantity <= 0) {
        const next = { ...prev }
        delete next[product.id]
        return next
      }
      return { ...prev, [product.id]: { product, quantity } }
    })
  }, [])

  const clearCart = useCallback(() => setCart({}), [])

  const items = Object.values(cart)
  const totalItems = items.reduce((sum, i) => sum + i.quantity, 0)
  const totalAmount = items.reduce(
    (sum, i) => sum + parseFloat(i.product.price) * i.quantity,
    0
  )

  const toOrderPayload = () =>
    items.map((i) => ({ product_id: i.product.id, quantity: i.quantity }))

  return (
    <CartContext.Provider
      value={{ cart, items, totalItems, totalAmount, setQuantity, clearCart, toOrderPayload }}
    >
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used inside CartProvider')
  return ctx
}
