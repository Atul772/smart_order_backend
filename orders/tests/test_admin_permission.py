import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from orders.services.order_service import OrderService

User = get_user_model()


@pytest.mark.django_db
def test_only_admin_can_update_order_status():
    user = User.objects.create_user(
        "user", "u@test.com", "pass", is_admin=False
    )

    with pytest.raises(PermissionDenied):
        OrderService.admin_update_status(
            admin_user=user,
            order_id=1,
            new_status="SHIPPED"
        )
