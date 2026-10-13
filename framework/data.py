from datetime import date, timedelta


def booking_payload(
    firstname="John",
    lastname="Smith",
    totalprice=250,
    depositpaid=True,
    additionalneeds="Breakfast",
    checkin=None,
    checkout=None,
):
    """Build a valid booking payload with future dates."""

    today = date.today()

    if checkin is None:
        checkin = today + timedelta(days=30)

    if checkout is None:
        checkout = checkin + timedelta(days=5)

    return {
        "firstname": firstname,
        "lastname": lastname,
        "totalprice": totalprice,
        "depositpaid": depositpaid,
        "bookingdates": {
            "checkin": checkin.isoformat(),
            "checkout": checkout.isoformat(),
        },
        "additionalneeds": additionalneeds,
    }
