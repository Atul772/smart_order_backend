from django.urls import path
from .views import PaymentInitiateView, PaymentCompleteView

urlpatterns = [
    path("initiate/", PaymentInitiateView.as_view(), name="payment-initiate"),
    path("complete/", PaymentCompleteView.as_view(), name="payment-complete"),
]
