import os
import threading
import time

import requests
from dotenv import load_dotenv


load_dotenv()


class AuthManager:
    """Thread-safe token manager for the Restful Booker API."""

    def __init__(self):
        self.base_url = os.getenv(
            "BASE_URL",
            "https://restful-booker.herokuapp.com",
        ).rstrip("/")

        self.username = os.getenv("API_USERNAME", "admin")
        self.password = os.getenv("API_PASSWORD", "password123")

        self.timeout = float(os.getenv("REQUEST_TIMEOUT", "10"))
        self.token_ttl = int(os.getenv("TOKEN_TTL_SECONDS", "600"))

        self._token = None
        self._expires_at = 0.0
        self._lock = threading.Lock()

    def _request_new_token(self):
        """Call the authentication endpoint and validate its response."""
        response = requests.post(
            f"{self.base_url}/auth",
            json={
                "username": self.username,
                "password": self.password,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        token = data.get("token")

        if not token:
            raise RuntimeError(
                f"Authentication failed: {data.get('reason', data)}"
            )

        self._token = token

        # Use a monotonic clock for elapsed-time calculations.
        # Refresh a little before the configured TTL expires.
        safe_ttl = max(0, self.token_ttl - 30)
        self._expires_at = time.monotonic() + safe_ttl

        return self._token

    def get_token(self):
        """Return a cached token or generate one safely."""
        if (
            self._token is not None
            and time.monotonic() < self._expires_at
        ):
            return self._token

        with self._lock:
            # Another thread may have refreshed the token while
            # this thread was waiting for the lock.
            if (
                self._token is not None
                and time.monotonic() < self._expires_at
            ):
                return self._token

            return self._request_new_token()

    def refresh_if_rejected(self, rejected_token):
        """Refresh a rejected token without redundant concurrent logins."""
        with self._lock:
            # Another thread may already have refreshed the token.
            if self._token != rejected_token:
                if (
                    self._token is not None
                    and time.monotonic() < self._expires_at
                ):
                    return self._token

            # Clear the cached token if it was rejected or expired.
            self._token = None
            self._expires_at = 0.0

            return self._request_new_token()
            
    def invalidate(self):
        """Mark the cached token as unusable."""
        with self._lock:
            self._token = None
            self._expires_at = 0.0