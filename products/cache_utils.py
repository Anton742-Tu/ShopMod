import logging

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def cache_product_list(products, timeout=60 * 15):  # 15 минут
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


def invalidate_product_cache():
    """
    Инвалидирует кеш товаров
    """
    cache_key = "product_list"
    try:
        cache.delete(cache_key)
        logger.info("Product cache invalidated")
        return True
    except Exception as e:
        logger.error(f"Error invalidating product cache: {e}")
        return False


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
