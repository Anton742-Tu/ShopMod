import os

from django.db import models


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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
