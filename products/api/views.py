from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.cache import cache

from products.models import Product
from .serializers import ProductSerializer


class ProductListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(is_active=True, stock__gt=0)

    def list(self, request, *args, **kwargs):
        page = request.query_params.get("page", 1)

        cache_key = f"product_list_page_{page}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)

        # cache full paginated response
        cache.set(cache_key, response.data, timeout=60 * 5)  # 5 minutes
        return response
