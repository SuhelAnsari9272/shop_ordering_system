"""
Thin HTTP client wrapping calls to the FastAPI backend.
Keeps requests/error-handling logic out of the Streamlit page code.
"""
import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 10  # seconds


class ApiError(Exception):
    """Raised when the backend returns a non-2xx response."""

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


def list_products() -> list:
    resp = requests.get(f"{API_BASE_URL}/products", headers=_auth_headers(), timeout=REQUEST_TIMEOUT)
    return _handle_response(resp)


def place_order(items: list[dict]) -> dict:
    resp = requests.post(
        f"{API_BASE_URL}/orders",
        json={"items": items},
        headers=_auth_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    return _handle_response(resp)


def list_my_orders() -> list:
    resp = requests.get(f"{API_BASE_URL}/orders", headers=_auth_headers(), timeout=REQUEST_TIMEOUT)
    return _handle_response(resp)


def get_order(order_id: int) -> dict:
    resp = requests.get(f"{API_BASE_URL}/orders/{order_id}", headers=_auth_headers(), timeout=REQUEST_TIMEOUT)
    return _handle_response(resp)
