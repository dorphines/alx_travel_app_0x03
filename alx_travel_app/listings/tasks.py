from celery import shared_task
from django.core.mail import send_mail
from .models import Booking

@shared_task
def send_booking_confirmation_email(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        subject = f'Booking Confirmation: {booking.listing.title}'
        message = (
            f'Hi {booking.guest.first_name or booking.guest.username},\n\n'
            f'Your booking for {booking.listing.title} has been confirmed!\n'
            f'Check-in: {booking.check_in_date}\n'
            f'Check-out: {booking.check_out_date}\n'
            f'Total Price: ${booking.total_price}\n\n'
            f'Thank you for booking with us!'
        )
        recipient_list = [booking.guest.email]
        send_mail(subject, message, 'noreply@alxtravelapp.com', recipient_list)
        return f"Email sent successfully to {booking.guest.email}"
    except Booking.DoesNotExist:
        return f"Booking with ID {booking_id} does not exist"
