from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from home.models import Booking, Property

User = get_user_model()


class BookingSignalEmailDisabledTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="testpass123",
            first_name="Olivia",
        )
        self.tenant = User.objects.create_user(
            username="tenant",
            email="tenant@example.com",
            password="testpass123",
            first_name="Taylor",
        )
        self.property = Property.objects.create(
            user=self.owner,
            title="Riverside Flat",
            description="Signal test property.",
            price="24000.00",
            location="Kathmandu",
            property_type="rent",
            image=SimpleUploadedFile(
                "property.jpg",
                b"fake-image-bytes",
                content_type="image/jpeg",
            ),
        )

    def create_booking(self, *, status=Booking.Status.PENDING):
        return Booking.objects.create(
            property=self.property,
            booked_by=self.tenant,
            owner=self.owner,
            status=status,
            is_accepted=status == Booking.Status.ACCEPTED,
        )

    def test_booking_create_does_not_send_email(self):
        with self.captureOnCommitCallbacks(execute=True):
            booking = self.create_booking()

        self.assertEqual(booking.status, Booking.Status.PENDING)
        self.assertEqual(len(mail.outbox), 0)

    def test_booking_accept_does_not_send_email(self):
        booking = self.create_booking()
        mail.outbox.clear()

        with self.captureOnCommitCallbacks(execute=True):
            booking.mark_accepted()
            booking.save(update_fields=["status", "is_accepted"])

        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.ACCEPTED)
        self.assertTrue(booking.is_accepted)
        self.assertEqual(len(mail.outbox), 0)

    def test_booking_reject_does_not_send_email(self):
        booking = self.create_booking()
        mail.outbox.clear()

        with self.captureOnCommitCallbacks(execute=True):
            booking.mark_rejected()
            booking.save(update_fields=["status", "is_accepted"])

        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.REJECTED)
        self.assertFalse(booking.is_accepted)
        self.assertEqual(len(mail.outbox), 0)

    def test_non_status_update_does_not_send_email(self):
        booking = self.create_booking()
        mail.outbox.clear()

        with self.captureOnCommitCallbacks(execute=True):
            booking.is_read = True
            booking.save(update_fields=["is_read"])

        self.assertEqual(len(mail.outbox), 0)
