"""
Thin HTTP client wrapping calls to the FastAPI backend, for the admin dashboard.
"""
import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 10  # seconds


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"[{status_code}] {detail}")


def _handle_response(resp: requests.Response):
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise ApiError(resp.status_code, detail)
    if resp.status_code == 204 or not resp.content:
        return None
    return resp.json()


def _auth_headers() -> dict:
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def login(mobile: str, password: str) -> dict:
    resp = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={"mobile": mobile, "password": password},
        timeout=REQUEST_TIMEOUT,
    )
    return _handle_response(resp)


def get_my_profile() -> dict:
    resp = requests.get(f"{API_BASE_URL}/customers/me", headers=_auth_headers(), timeout=REQUEST_TIMEOUT)
    return _handle_response(resp)


def list_all_orders(status: str | None = None, today_only: bool = False) -> list:
    params = {}
    if status:
        params["status"] = status
    if today_only:
        params["today_only"] = "true"
    resp = requests.get(
        f"{API_BASE_URL}/orders", headers=_auth_headers(), params=params, timeout=REQUEST_TIMEOUT
    )
    return _handle_response(resp)


def update_order_status(order_id: int, new_status: str) -> dict:
    resp = requests.put(
        f"{API_BASE_URL}/orders/{order_id}/status",
        json={"status": new_status},
        headers=_auth_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    return _handle_response(resp)


def get_dashboard_metrics() -> dict:
    resp = requests.get(f"{API_BASE_URL}/dashboard/metrics", headers=_auth_headers(), timeout=REQUEST_TIMEOUT)
    return _handle_response(resp)


def list_customers() -> list:
    resp = requests.get(f"{API_BASE_URL}/customers", headers=_auth_headers(), timeout=REQUEST_TIMEOUT)
    return _handle_response(resp)


def list_all_products() -> list:
    resp = requests.get(f"{API_BASE_URL}/products/all", headers=_auth_headers(), timeout=REQUEST_TIMEOUT)
    return _handle_response(resp)


def create_product(name: str, description: str, price: float) -> dict:
    resp = requests.post(
        f"{API_BASE_URL}/products",
        json={"name": name, "description": description, "price": price, "is_active": True},
        headers=_auth_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    return _handle_response(resp)


def update_product(product_id: int, **fields) -> dict:
    resp = requests.put(
        f"{API_BASE_URL}/products/{product_id}",
        json=fields,
        headers=_auth_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    return _handle_response(resp)


def create_customer(name: str, mobile: str, password: str) -> dict:
    resp = requests.post(
        f"{API_BASE_URL}/customers",
        json={"name": name, "mobile": mobile, "password": password},
        headers=_auth_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    return _handle_response(resp)
