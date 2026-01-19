from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from products.models import Product
from .serializers import ProductSerializer
from django.core.cache import cache


class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cache_key = "product_list"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        products = Product.objects.filter(is_active=True, stock__gt=0)
        serializer = ProductSerializer(products, many=True)

        cache.set(cache_key, serializer.data, timeout=60 * 5)  # 5 minutes
        return Response(serializer.data)

