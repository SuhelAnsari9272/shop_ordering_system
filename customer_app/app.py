"""
Customer-facing Streamlit app for the Shop Pre-Ordering System.

Run with: streamlit run app.py
"""
from datetime import datetime

import streamlit as st
from api_client import ApiError, get_my_profile, list_my_orders, list_products, login, place_order

st.set_page_config(page_title="Shop Pre-Order | Customer", page_icon="🛍️", layout="centered")

STATUS_COLORS = {
    "RECEIVED": "🟡",
    "PREPARING": "🟠",
    "READY": "🟢",
    "COMPLETED": "✅",
    "CANCELLED": "🔴",
}


# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
def init_session_state() -> None:
    defaults = {
        "access_token": None,
        "customer_name": None,
        "customer_id": None,
        "cart": {},  # {product_id: quantity}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def logout() -> None:
    st.session_state["access_token"] = None
    st.session_state["customer_name"] = None
    st.session_state["customer_id"] = None
    st.session_state["cart"] = {}


# ---------------------------------------------------------------------------
# Login page
# ---------------------------------------------------------------------------
def render_login_page() -> None:
    st.title("🛍️ Shop Pre-Order")
    st.caption("Order ahead, skip the wait. Pickup only — not a delivery service.")

    with st.form("login_form"):
        mobile = st.text_input("Mobile Number", max_chars=15, placeholder="9876543210")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In", use_container_width=True, type="primary")

    if submitted:
        if not mobile or not password:
            st.error("Please enter both mobile number and password.")
            return
        try:
            result = login(mobile.strip(), password)
            st.session_state["access_token"] = result["access_token"]
            st.session_state["customer_name"] = result["name"]
            st.session_state["customer_id"] = result["customer_id"]
            st.success(f"Welcome back, {result['name']}!")
            st.rerun()
        except ApiError as e:
            if e.status_code == 401:
                st.error("Invalid mobile number or password.")
            elif e.status_code == 403:
                st.error(e.detail)
            else:
                st.error(f"Login failed: {e.detail}")
        except Exception:
            st.error("Could not reach the server. Please check your connection and try again.")

    st.info("Don't have an account? Please contact the shop to get registered.")


# ---------------------------------------------------------------------------
# Product listing + cart
# ---------------------------------------------------------------------------
def render_menu_tab() -> None:
    try:
        products = list_products()
    except ApiError as e:
        st.error(f"Could not load menu: {e.detail}")
        return
    except Exception:
        st.error("Could not reach the server.")
        return

    if not products:
        st.info("No products are available right now. Please check back later.")
        return

    st.subheader("📋 Today's Menu")

    for product in products:
        pid = product["id"]
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{product['name']}** — ₹{float(product['price']):.2f}")
                if product.get("description"):
                    st.caption(product["description"])
            with col2:
                current_qty = st.session_state["cart"].get(pid, 0)
                qty = st.number_input(
                    "Qty",
                    min_value=0,
                    max_value=50,
                    value=current_qty,
                    step=1,
                    key=f"qty_{pid}",
                    label_visibility="collapsed",
                )
                if qty != current_qty:
                    if qty == 0:
                        st.session_state["cart"].pop(pid, None)
                    else:
                        st.session_state["cart"][pid] = qty
                    st.rerun()

    render_cart_summary(products)


def render_cart_summary(products: list) -> None:
    cart = st.session_state["cart"]
    if not cart:
        return

    product_lookup = {p["id"]: p for p in products}

    st.divider()
    st.subheader("🛒 Your Cart")

    total = 0.0
    for pid, qty in cart.items():
        product = product_lookup.get(pid)
        if product is None:
            continue
        line_total = float(product["price"]) * qty
        total += line_total
        st.write(f"{product['name']} × {qty} = ₹{line_total:.2f}")

    st.markdown(f"### Total: ₹{total:.2f}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Cart", use_container_width=True):
            st.session_state["cart"] = {}
            st.rerun()
    with col2:
        if st.button("Place Order ✅", type="primary", use_container_width=True):
            submit_order()


def submit_order() -> None:
    cart = st.session_state["cart"]
    if not cart:
        st.warning("Your cart is empty.")
        return

    items = [{"product_id": pid, "quantity": qty} for pid, qty in cart.items()]
    try:
        order = place_order(items)
        st.session_state["cart"] = {}
        st.success(f"Order #{order['id']} placed successfully! Total: ₹{float(order['total_amount']):.2f}")
        st.balloons()
        st.rerun()
    except ApiError as e:
        st.error(f"Could not place order: {e.detail}")
    except Exception:
        st.error("Could not reach the server. Please try again.")


# ---------------------------------------------------------------------------
# Order history / status tracking
# ---------------------------------------------------------------------------
def render_orders_tab() -> None:
    st.subheader("📦 Your Orders")

    if st.button("🔄 Refresh"):
        st.rerun()

    try:
        orders = list_my_orders()
    except ApiError as e:
        st.error(f"Could not load orders: {e.detail}")
        return
    except Exception:
        st.error("Could not reach the server.")
        return

    if not orders:
        st.info("You haven't placed any orders yet.")
        return

    for order in orders:
        status = order["status"]
        icon = STATUS_COLORS.get(status, "⚪")
        created = order["created_at"]
        try:
            created_display = datetime.fromisoformat(created.replace("Z", "+00:00")).strftime("%d %b %Y, %I:%M %p")
        except (ValueError, AttributeError):
            created_display = created

        with st.expander(f"{icon} Order #{order['id']} — {status} — ₹{float(order['total_amount']):.2f}"):
            st.caption(f"Placed on {created_display}")
            st.write("**Items:**")
            for item in order["items"]:
                st.write(f"- {item['product_name']} × {item['quantity']} = ₹{float(item['subtotal']):.2f}")
            st.markdown(f"**Status: {icon} {status}**")

            progress_map = {"RECEIVED": 25, "PREPARING": 50, "READY": 75, "COMPLETED": 100, "CANCELLED": 0}
            st.progress(progress_map.get(status, 0) / 100)


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------
def main() -> None:
    init_session_state()

    if not st.session_state["access_token"]:
        render_login_page()
        return

    # Verify the token is still valid by fetching the profile; logs out gracefully if not.
    try:
        get_my_profile()
    except ApiError as e:
        if e.status_code == 401:
            st.warning("Your session has expired. Please log in again.")
            logout()
            st.rerun()
            return
    except Exception:
        st.error("Could not reach the server.")
        return

    with st.sidebar:
        st.markdown(f"### 👋 Hi, {st.session_state['customer_name']}")
        if st.button("Log Out", use_container_width=True):
            logout()
            st.rerun()

    st.title("🛍️ Shop Pre-Order")

    tab1, tab2 = st.tabs(["📋 Menu & Order", "📦 My Orders"])
    with tab1:
        render_menu_tab()
    with tab2:
        render_orders_tab()


if __name__ == "__main__":
    main()
