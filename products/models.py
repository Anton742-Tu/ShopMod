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
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        default=0.00
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
