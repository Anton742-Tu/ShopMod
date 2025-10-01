from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название продукта')
    description = models.TextField(blank=True, verbose_name='Описание продукта')
    # Добавь другие поля при необходимости, например:
    # price = models.DecimalField(max_digits=10, decimal_places=2)
    # created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
