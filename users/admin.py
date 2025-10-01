from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ("email", "username", "phone", "country", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "country")

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (
            "Персональная информация",
            {"fields": ("first_name", "last_name", "phone", "country", "avatar")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "phone",
                    "country",
                    "avatar",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    search_fields = ("email", "username", "phone")
    ordering = ("email",)
