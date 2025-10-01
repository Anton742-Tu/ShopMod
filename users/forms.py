import os

from django import forms
from django.conf import settings
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)
from django.core.exceptions import ValidationError

from .models import User


class UserRegisterForm(UserCreationForm):
    """Форма для регистрации пользователя"""

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Введите ваш email"}
        ),
    )

    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        ),
    )

    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Повторите пароль"}
        ),
    )

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""


class UserLoginForm(AuthenticationForm):
    """Форма для авторизации пользователя по email"""

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Введите ваш email"}
        ),
    )

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""

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

        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Введите ваш email"}
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите имя пользователя",
                }
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите ваше имя"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите вашу фамилию"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+7 XXX XXX-XX-XX"}
            ),
            "country": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Введите вашу страну"}
            ),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Кастомные лейблы с иконками
        self.fields["email"].label = "📧 Email"
        self.fields["username"].label = "👤 Имя пользователя"
        self.fields["first_name"].label = "👨‍💼 Имя"
        self.fields["last_name"].label = "👨‍💼 Фамилия"
        self.fields["phone"].label = "📞 Телефон"
        self.fields["country"].label = "🌍 Страна"
        self.fields["avatar"].label = "🖼️ Аватар"

        # Подсказки для полей
        self.fields["username"].help_text = "Отображаемое имя в системе"
        self.fields["avatar"].help_text = (
            "Загрузите ваше фото. Максимальный размер: 2 МБ"
        )

    def clean_avatar(self):
        """Валидация загружаемого аватара"""
        avatar = self.cleaned_data.get("avatar")

        if not avatar:
            return avatar

        # Проверка формата
        valid_extensions = [".jpg", ".jpeg", ".png", ".gif"]
        ext = os.path.splitext(avatar.name)[1].lower()

        if ext not in valid_extensions:
            raise ValidationError("❌ Поддерживаются только форматы JPEG, PNG и GIF.")

        # Проверка размера (2 МБ)
        max_size = 2 * 1024 * 1024
        if avatar.size > max_size:
            raise ValidationError(
                f"❌ Размер файла не должен превышать 2 МБ. Ваш файл: {avatar.size // 1024} КБ"
            )

        return avatar

    def clean_username(self):
        """Валидация имени пользователя на запрещенные слова"""
        username = self.cleaned_data.get("username", "").lower()

        for word in settings.FORBIDDEN_WORDS:
            if word in username:
                raise forms.ValidationError(
                    f"❌ Использование слова '{word}' в имени пользователя запрещено."
                )

        return self.cleaned_data["username"]
