from django.urls import path
from .views import AsyncHealthCheckView

urlpatterns = [
    path("system/health/", AsyncHealthCheckView.as_view()),
]
