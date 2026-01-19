from rest_framework import serializers
from products.models import Product
from orders.models import Order, OrderItem
from django.core.cache import cache


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Order must contain at least one item.")

        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]

            cache_key = f"product_availability_{product_id}"
            product_data = cache.get(cache_key)

            if not product_data:
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Product {product_id} does not exist."
                    )

                product_data = {
                    "is_active": product.is_active,
                    "stock": product.stock,
                    "price": str(product.price),
                }

                cache.set(cache_key, product_data, timeout=60 * 2)  # 2 minutes

            if not product_data["is_active"] or product_data["stock"] < quantity:
                raise serializers.ValidationError(
                    f"Product {product_id} is not available in required quantity."
                )

        return items



class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")

    class Meta:
        model = OrderItem
        fields = (
            "product_name",
            "quantity",
            "price_at_time",
        )


class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "total_amount",
            "created_at",
            "items",
        )


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
        ]
    )
