import requests

from framework.auth import AuthManager


class APIClient:
    """Reusable HTTP client with bounded authentication recovery."""

    def __init__(self, auth_manager=None):
        self.auth = auth_manager or AuthManager()
        self.base_url = self.auth.base_url
        self.timeout = self.auth.timeout

    def request(
        self,
        method,
        path,
        *,
        json=None,
        authenticated=False,
        **kwargs,
    ):
        """Send a request and retry once after an auth rejection."""

        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = dict(kwargs.pop("headers", {}))

        token = None

        if authenticated:
            token = self.auth.get_token()
            headers["Cookie"] = f"token={token}"

        response = requests.request(
            method=method,
            url=url,
            json=json,
            headers=headers,
            timeout=self.timeout,
            **kwargs,
        )

        # Only authenticated requests need token recovery.
        if authenticated and response.status_code in (401, 403):
            token = self.auth.refresh_if_rejected(token)
            headers["Cookie"] = f"token={token}"

            # Exactly one retry; do not create an infinite loop.
            response = requests.request(
                method=method,
                url=url,
                json=json,
                headers=headers,
                timeout=self.timeout,
                **kwargs,
            )

        return response

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request(
            "PUT", path, authenticated=True, **kwargs
        )

    def patch(self, path, **kwargs):
        return self.request(
            "PATCH", path, authenticated=True, **kwargs
        )

    def delete(self, path, **kwargs):
        return self.request(
            "DELETE", path, authenticated=True, **kwargs
        )