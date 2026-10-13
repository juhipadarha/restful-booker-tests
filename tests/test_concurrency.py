from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest


def test_concurrent_put_updates(client, booking):
    booking_id = booking["id"]

    # Prepare two independent, complete payloads.
    payload_a = dict(booking["payload"])
    payload_a["bookingdates"] = dict(
        booking["payload"]["bookingdates"]
    )
    payload_a["firstname"] = "Alice"
    payload_a["lastname"] = "ThreadA"
    payload_a["totalprice"] = 400

    payload_b = dict(booking["payload"])
    payload_b["bookingdates"] = dict(
        booking["payload"]["bookingdates"]
    )
    payload_b["firstname"] = "Bob"
    payload_b["lastname"] = "ThreadB"
    payload_b["totalprice"] = 600

    # Release both workers when they are ready.
    barrier = Barrier(2)

    def update_booking(payload):
        barrier.wait(timeout=10)

        return client.put(
            f"/booking/{booking_id}",
            json=payload,
        )

    # Submit both updates concurrently.
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(update_booking, payload_a)
        future_b = executor.submit(update_booking, payload_b)

        response_a = future_a.result(timeout=30)
        response_b = future_b.result(timeout=30)

    # Both updates should succeed under the expected
    # behavior of this sandbox.
    assert response_a.status_code == 200
    assert response_b.status_code == 200

    # Read the final persisted state.
    final_response = client.get(f"/booking/{booking_id}")
    assert final_response.status_code == 200

    final_booking = final_response.json()

    # The result should match one complete submitted payload.
    assert final_booking in (payload_a, payload_b)

    # Verify that the final booking remains structurally valid.
    from framework.schemas import validate_booking

    validate_booking(final_booking)