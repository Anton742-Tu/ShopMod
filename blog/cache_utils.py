import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)


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


def invalidate_blog_cache():
    """
    Инвалидирует кеш блога
    """
    cache_key = "blog_posts"
    try:
        cache.delete(cache_key)
        logger.info("Blog cache invalidated")
        return True
    except Exception as e:
        logger.error(f"Error invalidating blog cache: {e}")
        return False
