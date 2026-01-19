from django.urls import path
from .views import OrderCreateView, OrderListView, OrderCancelView, OrderStatusUpdateView

urlpatterns = [
    path("", OrderCreateView.as_view(), name="order-create"),
    path("list/", OrderListView.as_view(), name="order-list"),
    path("<int:order_id>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path("<int:order_id>/status/", OrderStatusUpdateView.as_view(), name="order-status-update"),
]
