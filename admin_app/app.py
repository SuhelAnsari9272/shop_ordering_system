"""
Admin dashboard Streamlit app for the Shop Pre-Ordering System.

Run with: streamlit run app.py
"""
from datetime import datetime

import streamlit as st
from api_client import (
    ApiError,
    create_customer,
    create_product,
    get_dashboard_metrics,
    get_my_profile,
    list_all_orders,
    list_all_products,
    list_customers,
    login,
    update_order_status,
    update_product,
)

st.set_page_config(page_title="Shop Pre-Order | Admin", page_icon="🧑‍🍳", layout="wide")

REFRESH_INTERVAL_SECONDS = 5

STATUS_FLOW = ["RECEIVED", "PREPARING", "READY", "COMPLETED"]
STATUS_COLORS = {
    "RECEIVED": "🟡",
    "PREPARING": "🟠",
    "READY": "🟢",
    "COMPLETED": "✅",
    "CANCELLED": "🔴",
}

NEXT_STATUS = {
    "RECEIVED": "PREPARING",
    "PREPARING": "READY",
    "READY": "COMPLETED",
}


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
def init_session_state() -> None:
    defaults = {"access_token": None, "admin_name": None}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def logout() -> None:
    st.session_state["access_token"] = None
    st.session_state["admin_name"] = None


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
def render_login_page() -> None:
    st.title("🧑‍🍳 Shop Admin Dashboard")
    st.caption("Operator login — manage incoming pre-orders.")

    with st.form("admin_login_form"):
        mobile = st.text_input("Admin Mobile Number")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In", type="primary", use_container_width=True)

    if submitted:
        if not mobile or not password:
            st.error("Please enter both mobile number and password.")
            return
        try:
            result = login(mobile.strip(), password)
            if result["role"] != "admin":
                st.error("This account does not have admin privileges.")
                return
            st.session_state["access_token"] = result["access_token"]
            st.session_state["admin_name"] = result["name"]
            st.rerun()
        except ApiError as e:
            st.error(f"Login failed: {e.detail}")
        except Exception:
            st.error("Could not reach the server. Please check your connection.")


# ---------------------------------------------------------------------------
# Dashboard metrics
# ---------------------------------------------------------------------------
def render_metrics() -> None:
    try:
        metrics = get_dashboard_metrics()
    except ApiError as e:
        st.error(f"Could not load metrics: {e.detail}")
        return
    except Exception:
        st.error("Could not reach the server.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Total Orders Today", metrics["total_orders_today"])
    col2.metric("⏳ Pending Orders", metrics["pending_orders"])
    col3.metric("✅ Completed Today", metrics["completed_orders"])


# ---------------------------------------------------------------------------
# Orders tab
# ---------------------------------------------------------------------------
def render_orders_tab() -> None:
    filter_col1, filter_col2 = st.columns([2, 1])
    with filter_col1:
        status_filter = st.selectbox(
            "Filter by status",
            options=["ALL"] + STATUS_FLOW + ["CANCELLED"],
            index=0,
        )
    with filter_col2:
        today_only = st.checkbox("Today only", value=False)

    try:
        status_param = None if status_filter == "ALL" else status_filter
        orders = list_all_orders(status=status_param, today_only=today_only)
    except ApiError as e:
        st.error(f"Could not load orders: {e.detail}")
        return
    except Exception:
        st.error("Could not reach the server.")
        return

    if not orders:
        st.info("No orders found for the selected filter.")
        return

    st.caption(f"Showing {len(orders)} order(s) — most recent first")

    for order in orders:
        status = order["status"]
        icon = STATUS_COLORS.get(status, "⚪")
        created = order["created_at"]
        try:
            created_display = datetime.fromisoformat(created.replace("Z", "+00:00")).strftime("%d %b %Y, %I:%M %p")
        except (ValueError, AttributeError):
            created_display = created

        with st.container(border=True):
            header_col, action_col = st.columns([3, 1])
            with header_col:
                st.markdown(
                    f"**Order #{order['id']}** — {icon} **{status}** — ₹{float(order['total_amount']):.2f}"
                )
                st.caption(
                    f"👤 {order['customer_name']} ({order['customer_mobile']})  •  🕒 {created_display}"
                )
                items_text = ", ".join(
                    f"{item['product_name']} ×{item['quantity']}" for item in order["items"]
                )
                st.write(items_text)

            with action_col:
                next_status = NEXT_STATUS.get(status)
                if next_status:
                    if st.button(
                        f"Mark {next_status}",
                        key=f"advance_{order['id']}",
                        use_container_width=True,
                        type="primary",
                    ):
                        advance_order_status(order["id"], next_status)
                if status not in ("COMPLETED", "CANCELLED"):
                    if st.button(
                        "Cancel Order",
                        key=f"cancel_{order['id']}",
                        use_container_width=True,
                    ):
                        advance_order_status(order["id"], "CANCELLED")


def advance_order_status(order_id: int, new_status: str) -> None:
    try:
        update_order_status(order_id, new_status)
        st.success(f"Order #{order_id} updated to {new_status}")
        st.rerun()
    except ApiError as e:
        st.error(f"Could not update order: {e.detail}")
    except Exception:
        st.error("Could not reach the server.")


# ---------------------------------------------------------------------------
# Customers tab
# ---------------------------------------------------------------------------
def render_customers_tab() -> None:
    st.subheader("👥 Registered Customers")

    with st.expander("➕ Register a new customer"):
        with st.form("new_customer_form"):
            name = st.text_input("Full Name")
            mobile = st.text_input("Mobile Number")
            password = st.text_input("Temporary Password", type="password")
            submitted = st.form_submit_button("Register Customer", type="primary")
        if submitted:
            if not (name and mobile and password):
                st.error("All fields are required.")
            else:
                try:
                    create_customer(name.strip(), mobile.strip(), password)
                    st.success(f"Customer '{name}' registered successfully.")
                    st.rerun()
                except ApiError as e:
                    st.error(f"Could not register customer: {e.detail}")
                except Exception:
                    st.error("Could not reach the server.")

    try:
        customers = list_customers()
    except ApiError as e:
        st.error(f"Could not load customers: {e.detail}")
        return
    except Exception:
        st.error("Could not reach the server.")
        return

    if not customers:
        st.info("No customers registered yet.")
        return

    table_data = [
        {
            "ID": c["id"],
            "Name": c["name"],
            "Mobile": c["mobile"],
            "Active": "✅" if c["is_active"] else "❌",
            "Admin": "✅" if c["is_admin"] else "",
            "Registered": c["created_at"][:10],
        }
        for c in customers
    ]
    st.dataframe(table_data, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Products tab
# ---------------------------------------------------------------------------
def render_products_tab() -> None:
    st.subheader("🍽️ Menu Management")

    with st.expander("➕ Add a new product"):
        with st.form("new_product_form"):
            name = st.text_input("Product Name")
            description = st.text_area("Description", height=80)
            price = st.number_input("Price (₹)", min_value=0.01, step=1.0, format="%.2f")
            submitted = st.form_submit_button("Add Product", type="primary")
        if submitted:
            if not name or price <= 0:
                st.error("Please provide a name and a valid price.")
            else:
                try:
                    create_product(name.strip(), description, price)
                    st.success(f"Product '{name}' added.")
                    st.rerun()
                except ApiError as e:
                    st.error(f"Could not add product: {e.detail}")
                except Exception:
                    st.error("Could not reach the server.")

    try:
        products = list_all_products()
    except ApiError as e:
        st.error(f"Could not load products: {e.detail}")
        return
    except Exception:
        st.error("Could not reach the server.")
        return

    for product in products:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{product['name']}** — ₹{float(product['price']):.2f}")
                st.caption(product.get("description", ""))
            with col2:
                st.write("Active" if product["is_active"] else "Inactive")
            with col3:
                label = "Deactivate" if product["is_active"] else "Activate"
                if st.button(label, key=f"toggle_{product['id']}", use_container_width=True):
                    try:
                        update_product(product["id"], is_active=not product["is_active"])
                        st.rerun()
                    except ApiError as e:
                        st.error(f"Could not update product: {e.detail}")


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------
def main() -> None:
    init_session_state()

    if not st.session_state["access_token"]:
        render_login_page()
        return

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
        st.markdown(f"### 🧑‍🍳 {st.session_state['admin_name']}")
        st.caption("Admin / Operator")
        auto_refresh = st.toggle("Auto-refresh (5s)", value=True)
        if st.button("Log Out", use_container_width=True):
            logout()
            st.rerun()

    st.title("🧑‍🍳 Shop Admin Dashboard")
    render_metrics()
    st.divider()

    tab1, tab2, tab3 = st.tabs(["📦 Orders", "👥 Customers", "🍽️ Menu"])
    with tab1:
        render_orders_tab()
    with tab2:
        render_customers_tab()
    with tab3:
        render_products_tab()

    if auto_refresh:
        import time

        time.sleep(REFRESH_INTERVAL_SECONDS)
        st.rerun()


if __name__ == "__main__":
    main()
