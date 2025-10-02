from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from products.models import Product


class Command(BaseCommand):
    help = "Создает группу модераторов продуктов и назначает права"

    def handle(self, *args, **options):
        # Создаем или получаем группу
        moderator_group, created = Group.objects.get_or_create(
            name="Модератор продуктов"
        )

        # Получаем права
        content_type = ContentType.objects.get_for_model(Product)

        # Право на отмену публикации (кастомное)
        unpublish_permission = Permission.objects.get(
            codename="can_unpublish_product", content_type=content_type
        )

        # Право на удаление любого продукта (стандартное)
        delete_permission = Permission.objects.get(
            codename="delete_product", content_type=content_type
        )

        # Добавляем права в группу
        moderator_group.permissions.add(unpublish_permission, delete_permission)

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Группа "Модератор продуктов" создана и права назначены!'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Права для группы "Модератор продуктов" обновлены!'
                )
            )
