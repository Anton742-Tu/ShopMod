from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
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

    # Отображение аватара в админке (опционально)
    readonly_fields = ("avatar_preview",)

    def avatar_preview(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" style="max-height: 100px;" />'
        return "Нет аватара"

    avatar_preview.allow_tags = True
    avatar_preview.short_description = "Превью аватара"
