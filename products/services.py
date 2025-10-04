from django.core.cache import cache
from django.db import models

from .models import Category, Product


def get_cached_product_list(user):
    """
    Низкоуровневое кеширование списка продуктов
    """
    cache_key = f'product_list_{user.pk if user.is_authenticated else "anon"}'
    cached_products = cache.get(cache_key)

    if cached_products is not None:
        print(f"⚡ Кеш найден: {cache_key}")
        return cached_products

    print(f"🔄 Генерация кеша: {cache_key}")

    # Получаем продукты
    if user.is_authenticated and (
        user.has_perm("products.can_unpublish_product") or user.is_superuser
    ):
        products = list(Product.objects.all().select_related("owner"))
    else:
        products = list(
            Product.objects.filter(is_published=True).select_related("owner")
        )

    # Кешируем на 2 минуты
    cache.set(cache_key, products, 120)
    print(f"✅ Кеш сохранен: {cache_key}, товаров: {len(products)}")

    return products


def get_products_count():
    """Кешированное количество продуктов"""
    cache_key = "products_count"
    count = cache.get(cache_key)

    if count is None:
        count = Product.objects.filter(is_published=True).count()
        cache.set(cache_key, count, 60 * 5)
        print(f"📊 Кешировано количество товаров: {count}")

    return count


def invalidate_product_list_cache(user=None):
    """
    Инвалидация кеша списка продуктов
    """
    if user:
        cache_key = f'product_list_{user.pk if user.is_authenticated else "anon"}'
        deleted = cache.delete(cache_key)
        print(f"🗑️ Удален кеш {cache_key}: {deleted}")
    else:
        # Удаляем все кеши списков продуктов
        try:
            import redis

            r = redis.Redis(host="localhost", port=6379, db=0)

            # Ищем ключи с префиксом shopmod:1:product_list*
            pattern = "*product_list*"
            keys = r.keys(pattern)

            if keys:
                r.delete(*keys)
                print(f"🗑️ Удалены ключи: {[k.decode('utf-8') for k in keys]}")
            else:
                print("🔍 Ключи product_list* не найдены в Redis")

        except Exception as e:
            print(f"❌ Ошибка Redis: {e}")


def debug_cache_keys():
    """Отладочная функция для просмотра всех ключей"""
    try:
        import redis

        r = redis.Redis(host="localhost", port=6379, db=0)
        all_keys = r.keys("*")
        print("🔑 Все ключи в Redis:")
        for key in all_keys:
            print(f"   - {key.decode('utf-8')}")
        return [k.decode("utf-8") for k in all_keys]
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []


def get_products_by_category(category_slug, user):
    """
    Сервисная функция для получения товаров по категории
    """
    cache_key = f'products_category_{category_slug}_{user.pk if user.is_authenticated else "anon"}'
    cached_products = cache.get(cache_key)

    if cached_products:
        return cached_products

    try:
        category = Category.objects.get(slug=category_slug)
        queryset = Product.objects.filter(category=category).select_related(
            "owner", "category"
        )

        if user.is_authenticated and (
            user.has_perm("products.can_unpublish_product") or user.is_superuser
        ):
            products = queryset
        else:
            products = queryset.filter(is_published=True)

        cache.set(cache_key, list(products), 60 * 5)
        return products

    except Category.DoesNotExist:
        return Product.objects.none()


def get_all_categories():
    """Получить все категории"""
    cache_key = "all_categories"
    cached_categories = cache.get(cache_key)

    if cached_categories:
        return cached_categories

    categories = Category.objects.all()
    cache.set(cache_key, list(categories), 60 * 30)
    return categories
