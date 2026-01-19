from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import OrderCreateSerializer
from orders.services.order_service import OrderService
from orders.models import Order
from .serializers import OrderListSerializer, OrderStatusUpdateSerializer

from django.core.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from .serializers import OrderCreateSerializer


@extend_schema(
    request=OrderCreateSerializer,
)
class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = OrderService.create_order(
            user=request.user,
            items=serializer.validated_data["items"],
        )

        return Response(
            {
                "order_id": order.id,
                "total_amount": order.total_amount,
                "status": order.status,
            },
            status=status.HTTP_201_CREATED,
        )


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_admin:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=user)

        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)


class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = OrderService.cancel_order(
                user=request.user,
                order_id=order_id,
            )
            return Response(
                {
                    "order_id": order.id,
                    "status": order.status,
                }
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

class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = OrderService.admin_update_status(
                admin_user=request.user,
                order_id=order_id,
                new_status=serializer.validated_data["status"],
            )
            return Response(
                {
                    "order_id": order.id,
                    "new_status": order.status,
                }
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