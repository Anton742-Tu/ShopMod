import logging

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def clear_product_pages_cache():
    """Очищает только кеш страниц товаров, не трогая сессии"""
    try:
        # Если используем Redis
        from django_redis import get_redis_connection

        redis = get_redis_connection("default")

        # Получаем все ключи
        all_keys = redis.keys("*")

        # Фильтруем - оставляем только ключи страниц (исключаем сессии)
        keys_to_delete = []
        for key in all_keys:
            key_str = key.decode("utf-8") if isinstance(key, bytes) else str(key)

            # Удаляем только кеш страниц, но не сессии
            if (
                "product" in key_str or "views.decorators.cache" in key_str
            ) and "session" not in key_str:
                keys_to_delete.append(key)

        # Удаляем отфильтрованные ключи
        if keys_to_delete:
            redis.delete(*keys_to_delete)
            print(f"Удалено ключей кеша: {len(keys_to_delete)}")

    except Exception as e:
        print(f"Ошибка при очистке кеша: {e}")
        # fallback - не очищаем ничего, чтобы не потерять сессии


def cache_product_list(products, timeout=60 * 15):  # 15 Мин.
    """
    Кеширует список товаров
    """
    cache_key = "product_list"
    try:
        cache.set(cache_key, products, timeout)
        logger.info(f"Product list cached for {timeout} seconds")
        return True
    except Exception as e:
        logger.error(f"Error caching product list: {e}")
        return False


def get_cached_product_list():
    """
    Получает кешированный список товаров
    """
    cache_key = "product_list"
    try:
        return cache.get(cache_key)
    except Exception as e:
        logger.error(f"Error getting cached product list: {e}")
        return None


def cache_blog_posts(posts, timeout=60 * 30):  # 30 минут
    """
    Кеширует список статей блога
    """
    cache_key = "blog_posts"
    try:
        cache.set(cache_key, posts, timeout)
        logger.info(f"Blog posts cached for {timeout} seconds")
        return True
    except Exception as e:
        logger.error(f"Error caching blog posts: {e}")
        return False


def get_cached_blog_posts():
    """
    Получает кешированный список статей
    """
    cache_key = "blog_posts"
    try:
        return cache.get(cache_key)
    except Exception as e:
        logger.error(f"Error getting cached blog posts: {e}")
        return None


def clear_all_cache():
    """
    Очищает весь кеш
    """
    try:
        cache.clear()
        logger.info("All cache cleared")
        return True
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return False
