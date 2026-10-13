from unittest.mock import Mock, patch

from framework.client import APIClient


def test_client_refreshes_token_after_401():
    auth = Mock()
    auth.base_url = "https://restful-booker.herokuapp.com"
    auth.timeout = 10
    auth.get_token.return_value = "old-token"
    auth.refresh_if_rejected.return_value = "new-token"

    client = APIClient(auth_manager=auth)

    unauthorized = Mock()
    unauthorized.status_code = 401

    success = Mock()
    success.status_code = 200

    observed_headers = []

    def fake_request(*args, **kwargs):
        # Save a snapshot so later mutations don't change history.
        observed_headers.append(kwargs["headers"].copy())

        if len(observed_headers) == 1:
            return unauthorized

        return success

    with patch(
        "framework.client.requests.request",
        side_effect=fake_request,
    ) as mock_request:
        response = client.get(
            "/booking/123",
            authenticated=True,
        )

    assert response.status_code == 200
    assert mock_request.call_count == 2

    assert observed_headers[0]["Cookie"] == "token=old-token"
    assert observed_headers[1]["Cookie"] == "token=new-token"

    auth.refresh_if_rejected.assert_called_once_with("old-token")


def test_client_stops_after_one_failed_retry():
    auth = Mock()
    auth.base_url = "https://restful-booker.herokuapp.com"
    auth.timeout = 10
    auth.get_token.return_value = "old-token"
    auth.refresh_if_rejected.return_value = "new-token"

    client = APIClient(auth_manager=auth)

    unauthorized = Mock()
    unauthorized.status_code = 401

    with patch(
        "framework.client.requests.request",
        return_value=unauthorized,
    ) as mock_request:
        response = client.get(
            "/booking/123",
            authenticated=True,
        )

    assert response.status_code == 401
    assert mock_request.call_count == 2

    auth.refresh_if_rejected.assert_called_once_with("old-token")