import random

from django.db import transaction
from django.db import IntegrityError

from bookings.models import Booking, BookingStatus

from .models import Payment, PaymentStatus, PaymentWebhookEvent


@transaction.atomic
def process_payment(
    *,
    user,
    booking_id,
    force_status=None,
):
    booking = (
        Booking.objects
        .select_for_update()
        .select_related("test")
        .get(
            id=booking_id,
            user=user,
        )
    )

    if booking.status != BookingStatus.PENDING:
        raise ValueError(
            "Payment can only be processed "
            "for a pending booking."
        )

    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            "amount": booking.amount,
        },
    )

    if not created and payment.status != PaymentStatus.PENDING:
        return payment

    # Simulated payment provider.
    if force_status == PaymentStatus.SUCCESS:
        success = True
    elif force_status == PaymentStatus.FAILED:
        success = False
    else:
        success = random.choice([True, False])

    if success:
        payment.status = PaymentStatus.SUCCESS
        booking.status = BookingStatus.CONFIRMED
    else:
        payment.status = PaymentStatus.FAILED
        booking.status = BookingStatus.FAILED

    payment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    booking.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return payment


@transaction.atomic
def process_payment_webhook(
    *,
    event_id,
    event_type,
    payment_id,
    status,
    payload,
):
    try:
        payment = (
            Payment.objects
            .select_for_update()
            .select_related("booking")
            .get(
                provider_payment_id=payment_id
            )
        )
    except Payment.DoesNotExist:
        raise Payment.DoesNotExist

    # Check whether this exact webhook event
    # has already been processed.
    existing_event = (
        PaymentWebhookEvent.objects
        .filter(event_id=event_id)
        .first()
    )

    if existing_event:
        return {
            "duplicate": True,
            "event_id": event_id,
            "payment": payment,
        }

    # Create the webhook event using the actual
    # Payment object, not the provider UUID.
    try:
        PaymentWebhookEvent.objects.create(
            event_id=event_id,
            payment=payment,
            event_type=event_type,
            status=status,
            payload=payload,
        )
    except IntegrityError:
        # Protect against a race where the same
        # event is inserted concurrently.
        existing_event = (
            PaymentWebhookEvent.objects
            .filter(event_id=event_id)
            .first()
        )

        if existing_event:
            return {
                "duplicate": True,
                "event_id": event_id,
                "payment": payment,
            }

        raise

    # If the payment has already reached a final state,
    # don't change it again.
    if payment.status != PaymentStatus.PENDING:
        return {
            "duplicate": False,
            "already_processed": True,
            "event_id": event_id,
            "payment": payment,
        }

    # Apply the provider's payment status.
    payment.status = status
    payment.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    # Update booking according to payment result.
    if status == PaymentStatus.SUCCESS:
        payment.booking.status = BookingStatus.CONFIRMED
    else:
        payment.booking.status = BookingStatus.FAILED

    payment.booking.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return {
        "duplicate": False,
        "already_processed": False,
        "event_id": event_id,
        "payment": payment,
    }