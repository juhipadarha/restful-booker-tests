from datetime import date

from jsonschema import Draft202012Validator


BOOKING_SCHEMA = {
    "type": "object",
    "required": [
        "firstname",
        "lastname",
        "totalprice",
        "depositpaid",
        "bookingdates",
        "additionalneeds",
    ],
    "properties": {
        "firstname": {"type": "string", "minLength": 1},
        "lastname": {"type": "string", "minLength": 1},
        "totalprice": {
            "type": "integer",
            "minimum": 0,
        },
        "depositpaid": {"type": "boolean"},
        "bookingdates": {
            "type": "object",
            "required": ["checkin", "checkout"],
            "properties": {
                "checkin": {
                    "type": "string",
                    "format": "date",
                },
                "checkout": {
                    "type": "string",
                    "format": "date",
                },
            },
            "additionalProperties": False,
        },
        "additionalneeds": {"type": "string"},
    },
    "additionalProperties": False,
}


def validate_booking(booking):
    """Validate booking structure, formats, and business rules."""

    validator = Draft202012Validator(
        BOOKING_SCHEMA,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )

    errors = sorted(
        validator.iter_errors(booking),
        key=lambda error: list(map(str, error.path)),
    )

    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(f"Invalid booking schema: {details}")

    checkin = date.fromisoformat(
        booking["bookingdates"]["checkin"]
    )
    checkout = date.fromisoformat(
        booking["bookingdates"]["checkout"]
    )

    if checkout <= checkin:
        raise ValueError(
            "Checkout must be later than check-in"
        )

    return True