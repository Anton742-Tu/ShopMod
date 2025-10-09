import os

from django.conf import settings
from django.db import models
from django.urls import reverse


def blog_image_path(instance, filename):
    """Генерирует путь для сохранения изображений статей"""
    ext = filename.split(".")[-1]
    filename = f"{instance.title}_{instance.id}.{ext}"
    return os.path.join("blog", filename)


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("published", "Опубликовано"),
    ]

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    image = models.ImageField(
        upload_to=blog_image_path, verbose_name="Изображение", blank=True, null=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="blog_posts",
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="draft", verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    published_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата публикации"
    )

    class Meta:
        verbose_name = "Статья блога"
        verbose_name_plural = "Статьи блога"
        permissions = [
            ("can_publish_blog", "Может публиковать статьи блога"),
            ("can_manage_blog", "Может управлять всеми статьями блога"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog_post_detail", kwargs={"pk": self.pk})

    def publish(self):
        """Публикация статьи"""
        from django.utils import timezone

        self.status = "published"
        self.published_at = timezone.now()
        self.save()

    def unpublish(self):
        """Снятие статьи с публикации"""
        self.status = "draft"
        self.published_at = None
        self.save()

    def is_published(self):
        return self.status == "published"
