from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from blog.models import BlogPost


class Command(BaseCommand):
    help = "Создает группу контент-менеджеров и назначает права для блога"

    def handle(self, *args, **options):
        # Создаем или получаем группу
        content_manager_group, created = Group.objects.get_or_create(
            name="Контент-менеджер"
        )

        # Получаем права для модели BlogPost
        content_type = ContentType.objects.get_for_model(BlogPost)

        # Получаем все кастомные права для блога
        can_publish_permission = Permission.objects.get(
            codename="can_publish_blog", content_type=content_type
        )

        can_manage_permission = Permission.objects.get(
            codename="can_manage_blog", content_type=content_type
        )

        # Стандартные права Django
        add_permission = Permission.objects.get(
            codename="add_blogpost", content_type=content_type
        )

        change_permission = Permission.objects.get(
            codename="change_blogpost", content_type=content_type
        )

        delete_permission = Permission.objects.get(
            codename="delete_blogpost", content_type=content_type
        )

        # Добавляем все права в группу
        permissions = [
            can_publish_permission,
            can_manage_permission,
            add_permission,
            change_permission,
            delete_permission,
        ]

        content_manager_group.permissions.set(permissions)

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Группа "Контент-менеджер" создана и права назначены!'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Права для группы "Контент-менеджер" обновлены!')
            )
