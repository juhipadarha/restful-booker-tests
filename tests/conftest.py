import pytest

from framework.client import APIClient
from framework.data import booking_payload


@pytest.fixture
def client():
    """Provide an API client for a test."""
    return APIClient()


@pytest.fixture
def booking(client):
    """Create a booking and clean it up after the test."""

    response = client.post(
        "/booking",
        json=booking_payload(),
    )
    response.raise_for_status()

    booking_id = response.json()["bookingid"]

    yield {
        "id": booking_id,
        "payload": booking_payload(),
    }

    # Cleanup: the booking may already have been deleted.
    delete_response = client.delete(f"/booking/{booking_id}")

    if delete_response.status_code not in (200, 201, 204, 404):
        delete_response.raise_for_status()