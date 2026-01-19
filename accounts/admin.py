from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "id",
        "username",
        "email",
        "is_admin",
        "is_staff",
        "is_active",
    )

    list_filter = ("is_admin", "is_staff", "is_active")

    fieldsets = UserAdmin.fieldsets + (
        ("Role Information", {"fields": ("is_admin",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role Information", {"fields": ("is_admin",)}),
    )
