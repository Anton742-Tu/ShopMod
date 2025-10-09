from django.core.management.base import BaseCommand

from blog.cache_utils import invalidate_blog_cache  # 👈 ДОБАВЛЯЕМ ИМПОРТ
from products.cache_utils import clear_all_cache, invalidate_product_cache


class Command(BaseCommand):
    help = "Очистка кеша Redis"

    def add_arguments(self, parser):
        parser.add_argument(
            "--products-only",
            action="store_true",
            help="Очистить только кеш товаров",
        )
        parser.add_argument(
            "--blog-only",
            action="store_true",
            help="Очистить только кеш блога",
        )

    def handle(self, *args, **options):
        if options["products_only"]:
            if invalidate_product_cache():
                self.stdout.write(self.style.SUCCESS("✅ Кеш товаров очищен!"))
            else:
                self.stdout.write(self.style.ERROR("❌ Ошибка очистки кеша товаров"))
        elif options["blog_only"]:
            if invalidate_blog_cache():
                self.stdout.write(self.style.SUCCESS("✅ Кеш блога очищен!"))
            else:
                self.stdout.write(self.style.ERROR("❌ Ошибка очистки кеша блога"))
        else:
            if clear_all_cache():
                self.stdout.write(self.style.SUCCESS("✅ Весь кеш очищен!"))
            else:
                self.stdout.write(self.style.ERROR("❌ Ошибка очистки кеша"))
