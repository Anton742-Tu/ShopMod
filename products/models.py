from django.db import models


class Product(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название продукта'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание продукта'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
