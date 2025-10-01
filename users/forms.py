from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания пользователя"""

    class Meta:
        model = User
        fields = ("email", "username", "phone", "country", "avatar")


class CustomUserChangeForm(UserChangeForm):
    """Форма для редактирования пользователя"""

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "phone",
            "country",
            "avatar",
        )
