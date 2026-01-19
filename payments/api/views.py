from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import PaymentInitiateSerializer, PaymentCompleteSerializer
from payments.services.payment_service import PaymentService
from django.core.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from .serializers import PaymentInitiateSerializer, PaymentCompleteSerializer


@extend_schema(
    request=PaymentInitiateSerializer,
)
class PaymentInitiateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment = PaymentService.initiate_payment(
                user=request.user,
                order_id=serializer.validated_data["order_id"],
            )
            return Response(
                {
                    "payment_id": payment.id,
                    "order_id": payment.order.id,
                    "amount": payment.amount,
                    "status": payment.status,
                },
                status=status.HTTP_200_OK,
            )
        except PermissionDenied as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

@extend_schema(
    request=PaymentCompleteSerializer,
)
class PaymentCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment = PaymentService.complete_payment(
                payment_id=serializer.validated_data["payment_id"],
                status=serializer.validated_data["status"],
                transaction_id=serializer.validated_data.get("transaction_id"),
            )
            return Response(
                {
                    "payment_id": payment.id,
                    "payment_status": payment.status,
                    "order_id": payment.order.id,
                    "order_status": payment.order.status,
                }
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )