from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Очищает кеш продуктов"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Очистить весь кеш продуктов",
        )

    def handle(self, *args, **options):
        from products.services import invalidate_product_list_cache

        if options["all"]:
            invalidate_product_list_cache()
            self.stdout.write(self.style.SUCCESS("✅ Весь кеш продуктов очищен"))
        else:
            # Можно добавить более специфичную очистку
            cache.delete_pattern("*product_list*")
            self.stdout.write(self.style.SUCCESS("✅ Кеш списков продуктов очищен"))
