from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, PaymentInitiationView, PaymentVerificationView

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('payment-initiate/', PaymentInitiationView.as_view(), name='payment-initiate'),
    path('payment-verify/', PaymentVerificationView.as_view(), name='payment-verify'),
]

