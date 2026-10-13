from copy import deepcopy

import pytest

from framework.data import booking_payload
from framework.schemas import validate_booking


def test_valid_booking_passes_schema_validation():
    payload = booking_payload()

    assert validate_booking(payload) is True


def test_checkout_must_be_after_checkin():
    payload = booking_payload()

    payload["bookingdates"]["checkout"] = (
        payload["bookingdates"]["checkin"]
    )

    with pytest.raises(ValueError, match="Checkout must be later"):
        validate_booking(payload)


def test_depositpaid_must_be_boolean():
    payload = booking_payload()
    payload["depositpaid"] = "true"

    with pytest.raises(ValueError, match="Invalid booking schema"):
        validate_booking(payload)


def test_totalprice_cannot_be_negative():
    payload = booking_payload()
    payload["totalprice"] = -10

    with pytest.raises(ValueError, match="Invalid booking schema"):
        validate_booking(payload)


def test_nested_bookingdates_fields_are_required():
    payload = deepcopy(booking_payload())
    del payload["bookingdates"]["checkout"]

    with pytest.raises(ValueError, match="Invalid booking schema"):
        validate_booking(payload)

def test_checkout_before_checkin_is_rejected():
    payload = booking_payload()

    payload["bookingdates"]["checkout"] = (
        "2020-01-01"
    )
    payload["bookingdates"]["checkin"] = (
        "2020-01-02"
    )

    with pytest.raises(
        ValueError,
        match="Checkout must be later"
    ):
        validate_booking(payload)


def test_invalid_checkin_date_format_is_rejected():
    payload = booking_payload()
    payload["bookingdates"]["checkin"] = "not-a-date"

    with pytest.raises(ValueError):
        validate_booking(payload)


def test_missing_top_level_field_is_rejected():
    payload = deepcopy(booking_payload())
    del payload["firstname"]

    with pytest.raises(
        ValueError,
        match="Invalid booking schema"
    ):
        validate_booking(payload)


def test_totalprice_must_be_integer():
    payload = booking_payload()
    payload["totalprice"] = "175"

    with pytest.raises(
        ValueError,
        match="Invalid booking schema"
    ):
        validate_booking(payload)