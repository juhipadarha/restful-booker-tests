from framework.data import booking_payload


def test_repeated_put_is_idempotent(client, booking):
    booking_id = booking["id"]

    payload = booking_payload(
        firstname="Idempotent",
        lastname="Customer",
        totalprice=450,
        depositpaid=True,
    )

    observed_states = []

    for _ in range(3):
        response = client.put(
            f"/booking/{booking_id}",
            json=payload,
        )

        assert response.status_code == 200

        read_response = client.get(f"/booking/{booking_id}")
        assert read_response.status_code == 200

        observed_states.append(read_response.json())

    assert observed_states[0] == payload
    assert observed_states[1] == payload
    assert observed_states[2] == payload

    assert observed_states[0] == observed_states[1]
    assert observed_states[1] == observed_states[2]


def test_patch_preserves_unmodified_fields(client, booking):
    booking_id = booking["id"]

    before_response = client.get(f"/booking/{booking_id}")
    assert before_response.status_code == 200
    before = before_response.json()

    new_price = before["totalprice"] + 100

    patch_response = client.patch(
        f"/booking/{booking_id}",
        json={"totalprice": new_price},
    )

    assert patch_response.status_code == 200

    after_response = client.get(f"/booking/{booking_id}")
    assert after_response.status_code == 200
    after = after_response.json()

    assert after["totalprice"] == new_price

    assert after["firstname"] == before["firstname"]
    assert after["lastname"] == before["lastname"]
    assert after["bookingdates"] == before["bookingdates"]
    assert after["depositpaid"] == before["depositpaid"]
    assert after["additionalneeds"] == before["additionalneeds"]