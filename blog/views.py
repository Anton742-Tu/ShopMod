from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .cache_utils import cache_blog_posts, get_cached_blog_posts, invalidate_blog_cache
from .forms import BlogPostForm
from .models import BlogPost


class BlogPostListView(ListView):
    """Список статей с кешированием"""

    model = BlogPost
    template_name = "blog/blogpost_list.html"
    context_object_name = "posts"
    paginate_by = 6

    # @method_decorator(cache_page(60 * 30))  # Кешируем на 30 минут
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """Показываем только опубликованные статьи для всех пользователей"""
        # Пробуем получить из кеша
        cached_posts = get_cached_blog_posts()
        if cached_posts:
            return cached_posts

        result = BlogPost.objects.filter(status="published")

        # Кешируем результат
        cache_blog_posts(result)

        return result


class BlogPostDetailView(DetailView):
    """Детальная страница статьи - доступна всем"""

    model = BlogPost
    template_name = "blog/blogpost_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        """Для неавторизованных пользователей показываем только опубликованные статьи"""
        queryset = super().get_queryset()

        if self.request.user.is_authenticated and (
            self.request.user.has_perm("blog.can_manage_blog")
            or self.request.user.is_superuser
        ):
            # Контент-менеджеры и админы видят все статьи
            return queryset
        else:
            # Обычные пользователи видят только опубликованные
            return queryset.filter(status="published")


class BlogPostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание статьи - только для контент-менеджеров"""

    model = BlogPost
    form_class = BlogPostForm
    template_name = "blog/blogpost_form.html"
    permission_required = "blog.can_manage_blog"

    def form_valid(self, form):
        """После создания статьи инвалидируем кеш"""
        form.instance.author = self.request.user
        messages.success(self.request, "✅ Статья успешно создана!")
        invalidate_blog_cache()  # 👈 ИНВАЛИДИРУЕМ КЕШ
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("blog_post_detail", kwargs={"pk": self.object.pk})


class BlogPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование статьи - автор ИЛИ контент-менеджер"""

    model = BlogPost
    form_class = BlogPostForm
    template_name = "blog/blogpost_form.html"

    def test_func(self):
        """Проверка прав: автор ИЛИ контент-менеджер"""
        post = self.get_object()
        user = self.request.user

        # Автор ИЛИ контент-менеджер ИЛИ суперпользователь
        return (
            post.author == user
            or user.has_perm("blog.can_manage_blog")
            or user.is_superuser
        )

    def handle_no_permission(self):
        messages.error(
            self.request, "❌ У вас нет прав для редактирования этой статьи."
        )
        return redirect("blog_post_list")

    def form_valid(self, form):
        """После обновления статьи инвалидируем кеш"""
        response = super().form_valid(form)
        invalidate_blog_cache()  # 👈 ИНВАЛИДИРУЕМ КЕШ
        return response

    def get_success_url(self):
        return reverse_lazy("blog_post_detail", kwargs={"pk": self.object.pk})


class BlogPostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление статьи - только контент-менеджеры"""

    model = BlogPost
    template_name = "blog/blogpost_confirm_delete.html"
    success_url = reverse_lazy("blog_post_list")
    permission_required = "blog.can_manage_blog"

    def form_valid(self, form):
        """После удаления статьи инвалидируем кеш"""
        response = super().form_valid(form)
        invalidate_blog_cache()  # 👈 ИНВАЛИДИРУЕМ КЕШ
        return response

    def handle_no_permission(self):
        messages.error(
            self.request, "❌ Только контент-менеджеры могут удалять статьи."
        )
        return redirect("blog_post_list")


class BlogPostPublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Публикация статьи - только контент-менеджеры"""

    permission_required = "blog.can_publish_blog"

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)
        post.publish()

        messages.success(request, f'✅ Статья "{post.title}" опубликована!')
        invalidate_blog_cache()  # 👈 ИНВАЛИДИРУЕМ КЕШ
        return redirect("blog_post_list")

    def handle_no_permission(self):
        messages.error(
            self.request, "❌ Только контент-менеджеры могут публиковать статьи."
        )
        return redirect("blog_post_list")


class BlogPostUnpublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Снятие статьи с публикации - только контент-менеджеры"""

    permission_required = "blog.can_publish_blog"

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)
        post.unpublish()

        messages.success(request, f'✅ Статья "{post.title}" снята с публикации.')
        invalidate_blog_cache()  # 👈 ИНВАЛИДИРУЕМ КЕШ
        return redirect("blog_post_list")

    def handle_no_permission(self):
        messages.error(
            self.request,
            "❌ Только контент-менеджеры могут снимать статьи с публикации.",
        )
        return redirect("blog_post_list")
