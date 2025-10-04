import os

from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-имя")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products_by_category", kwargs={"category_slug": self.slug})


def product_image_path(instance, filename):
    """Генерирует путь для сохранения изображений товаров"""
    ext = filename.split(".")[-1]
    filename = f"{instance.name}_{instance.id}.{ext}"
    return os.path.join("products", filename)


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название продукта")
    description = models.TextField(blank=True, verbose_name="Описание продукта")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена", default=0.00
    )
    image = models.ImageField(
        upload_to=product_image_path,
        verbose_name="Изображение товара",
        blank=True,
        null=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="products",
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликован",
        help_text="Отображается ли товар в общем списке",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория",
        related_name="products",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        permissions = [
            ("can_unpublish_product", "Может отменять публикацию продукта"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def unpublish(self):
        """Метод для снятия с публикации"""
        self.is_published = False
        self.save()

    def publish(self):
        """Метод для публикации"""
        self.is_published = True
        self.save()

    def is_owner(self, user):
        """Проверяет, является ли пользователь владельцем"""
        return self.owner == user
