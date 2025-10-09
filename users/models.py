import os

from django.contrib.auth.models import AbstractUser
from django.db import models


def user_avatar_path(instance, filename):
    """Генерирует путь для сохранения аватаров пользователей"""
    ext = filename.split(".")[-1]
    filename = f"avatar_{instance.username}_{instance.id}.{ext}"
    return os.path.join("users/avatars", filename)


class User(AbstractUser):
    """Кастомная модель пользователя с email как полем для авторизации"""

    # Делаем email обязательным и уникальным
    email = models.EmailField("Email адрес", unique=True, blank=False, null=False)

    # Дополнительные поля
    avatar = models.ImageField(
        "Аватар",
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        help_text="Загрузите ваш аватар",
    )

    phone = models.CharField(
        "Номер телефона",
        max_length=20,
        blank=True,
        help_text="В формате +7 XXX XXX-XX-XX",
    )

    country = models.CharField(
        "Страна", max_length=100, blank=True, help_text="Ваша страна проживания"
    )

    # Указываем поле для аутентификации
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # username все еще нужен для админки

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.email} ({self.get_full_name() or self.username})"

    def save(self, *args, **kwargs):
        # При сохранении устанавливаем username как email, если username пустой
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
