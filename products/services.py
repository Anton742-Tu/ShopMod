from django.core.cache import cache

from django.db import models
from .models import Category, Product


def get_products_by_category(category_slug, user):
    """
    Сервисная функция для получения товаров по категории
    с учетом прав доступа и кеширования
    """
    cache_key = f'products_category_{category_slug}_{user.pk if user.is_authenticated else "anon"}'
    cached_products = cache.get(cache_key)

    if cached_products:
        return cached_products

    try:
        category = Category.objects.get(slug=category_slug)

        # Базовый queryset
        queryset = Product.objects.filter(category=category).select_related(
            "owner", "category"
        )

        # Фильтрация по правам доступа
        if user.is_authenticated and (
            user.has_perm("products.can_unpublish_product") or user.is_superuser
        ):
            products = queryset
        else:
            products = queryset.filter(is_published=True)

        # Кешируем на 5 минут
        cache.set(cache_key, products, 60 * 5)
        return products

    except Category.DoesNotExist:
        return Product.objects.none()


def get_all_categories():
    """Получить все категории с количеством товаров"""
    cache_key = "all_categories"
    cached_categories = cache.get(cache_key)

    if cached_categories:
        return cached_categories

    categories = Category.objects.annotate(
        products_count=models.Count(
            "products", filter=models.Q(products__is_published=True)
        )
    ).filter(products_count__gt=0)

    cache.set(cache_key, categories, 60 * 30)  # 30 минут
    return categories
