import os
import requests
from dotenv import load_dotenv

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from .tasks import send_booking_confirmation_email

load_dotenv()

CHAPA_SECRET_KEY = os.getenv('CHAPA_SECRET_KEY')
CHAPA_BASE_URL = "https://api.chapa.co/v1" # Or sandbox URL

def _initiate_chapa_payment(booking, user, request):
    if CHAPA_SECRET_KEY is None:
        return {"error": "Chapa secret key not configured"}, status.HTTP_500_INTERNAL_SERVER_ERROR

    tx_ref = f"booking-payment-{booking.id}-{os.urandom(4).hex()}"

    data = {
        "amount": str(booking.total_price),
        "currency": "ETB",
        "email": user.email if user.email else "test@example.com",
        "first_name": user.first_name if user.first_name else "Test",
        "last_name": user.last_name if user.last_name else "User",
        "tx_ref": tx_ref,
        "callback_url": request.build_absolute_uri('/api/listings/payment-verify/'),
        "return_url": "http://localhost:8000/payment-success",
        "customization[title]": "Travel Booking Payment",
        "customization[description]": f"Payment for booking {booking.id}",
    }

    headers = {
        "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{CHAPA_BASE_URL}/initialize", json=data, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        if response_data.get('status') == 'success':
            checkout_url = response_data['data']['checkout_url']
            payment = Payment.objects.create(
                booking=booking,
                chapa_transaction_id=tx_ref,
                amount=booking.total_price,
                status='pending'
            )
            return {"message": "Payment initiated", "checkout_url": checkout_url, "payment_id": payment.id}, status.HTTP_200_OK
        else:
            return {"error": response_data.get('message', 'Chapa initiation failed')}, status.HTTP_400_BAD_REQUEST

    except requests.exceptions.RequestException as e:
        return {"error": f"Chapa API request failed: {e}"}, status.HTTP_500_INTERNAL_SERVER_ERROR
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}, status.HTTP_500_INTERNAL_SERVER_ERROR

class ListingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows listings to be viewed or edited.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed or edited.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        booking = serializer.instance

        # Trigger Celery task to send booking confirmation email
        send_booking_confirmation_email.delay(booking.id)

        # Initiate payment after booking creation
        payment_response_data, payment_status_code = _initiate_chapa_payment(booking, request.user, request)

        headers = self.get_success_headers(serializer.data)
        
        response_data = {
            "booking": serializer.data,
            "payment": payment_response_data
        }
        return Response(response_data, status=payment_status_code, headers=headers)

class PaymentInitiationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response({"error": "Booking ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id, guest=request.user)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found or does not belong to user"}, status=status.HTTP_404_NOT_FOUND)

        response_data, status_code = _initiate_chapa_payment(booking, request.user, request)
        return Response(response_data, status=status_code)

class PaymentVerificationView(APIView):
    # This endpoint will be called by Chapa as a webhook or user redirected to it
    # No permission_classes for webhook, but you might want to secure it with a shared secret
    # For user redirection, you might check if the user is logged in if needed
    def get(self, request, *args, **kwargs):
        transaction_id = request.query_params.get('trx_ref') # Chapa typically sends trx_ref in query params
        if not transaction_id:
            return Response({"error": "Transaction reference is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(chapa_transaction_id=transaction_id, status='pending')
        except Payment.DoesNotExist:
            return Response({"error": "Pending payment not found for this transaction reference"}, status=status.HTTP_404_NOT_FOUND)

        if CHAPA_SECRET_KEY is None:
            return Response({"error": "Chapa secret key not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        headers = {
            "Authorization": f"Bearer {CHAPA_SECRET_KEY}"
        }

        try:
            response = requests.get(f"{CHAPA_BASE_URL}/verify/{transaction_id}", headers=headers)
            response.raise_for_status()
            response_data = response.json()

            if response_data.get('status') == 'success' and response_data['data']['status'] == 'success':
                payment.status = 'completed'
                payment.save()
                # Trigger Celery task to send confirmation email
                # send_confirmation_email.delay(payment.booking.guest.email, payment.booking.id)
                return Response({"message": "Payment verified and completed", "payment_id": payment.id}, status=status.HTTP_200_OK)
            else:
                payment.status = 'failed'
                payment.save()
                return Response({"error": response_data.get('message', 'Chapa verification failed')}, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            payment.status = 'failed'
            payment.save()
            return Response({"error": f"Chapa API verification failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

