from framework.data import booking_payload
from framework.schemas import validate_booking


def test_create_and_read_booking(client):
    payload = booking_payload(
        firstname="Alice",
        lastname="Johnson",
    )

    create_response = client.post(
        "/booking",
        json=payload,
    )

    assert create_response.status_code == 200

    booking_id = create_response.json()["bookingid"]
    assert isinstance(booking_id, int)

    read_response = client.get(f"/booking/{booking_id}")

    assert read_response.status_code == 200

    actual_booking = read_response.json()

    validate_booking(actual_booking)
    assert actual_booking == payload


def test_update_booking(client, booking):
    booking_id = booking["id"]

    updated_payload = booking_payload(
        firstname="Updated",
        lastname="Customer",
        totalprice=450,
    )

    update_response = client.put(
        f"/booking/{booking_id}",
        json=updated_payload,
    )

    assert update_response.status_code == 200

    read_response = client.get(f"/booking/{booking_id}")

    assert read_response.status_code == 200
    assert read_response.json() == updated_payload


def test_delete_booking(client):
    payload = booking_payload()

    create_response = client.post("/booking", json=payload)

    assert create_response.status_code == 200
    booking_id = create_response.json()["bookingid"]

    delete_response = client.delete(f"/booking/{booking_id}")

    assert delete_response.status_code in (200, 201, 204)

    read_response = client.get(f"/booking/{booking_id}")

    assert read_response.status_code == 404