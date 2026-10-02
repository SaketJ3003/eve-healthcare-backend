from django.db import transaction

from .models import Booking


@transaction.atomic
def create_booking(
    *,
    user,
    centre,
    test,
    appointment_datetime,
):
    booking = Booking.objects.create(
        user=user,
        centre=centre,
        test=test,
        appointment_datetime=appointment_datetime,
        amount=test.price,
    )

    return booking