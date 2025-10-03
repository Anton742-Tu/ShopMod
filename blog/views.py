from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import BlogPostForm
from .models import BlogPost


class BlogPostListView(ListView):
    """Список опубликованных статей - доступен всем"""

    model = BlogPost
    template_name = "blog/blogpost_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        """Показываем только опубликованные статьи для всех пользователей"""
        return BlogPost.objects.filter(status="published")


class BlogPostDetailView(DetailView):
    """Детальная страница статьи - доступна всем"""

    model = BlogPost
    template_name = "blog/blogpost_detail.html"
    context_object_name = "post"


class BlogPostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание статьи - только для контент-менеджеров"""

    model = BlogPost
    form_class = BlogPostForm
    template_name = "blog/blogpost_form.html"
    permission_required = "blog.can_manage_blog"

    def form_valid(self, form):
        """Автоматически привязываем статью к текущему пользователю"""
        form.instance.author = self.request.user
        messages.success(self.request, "✅ Статья успешно создана!")
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

    def get_success_url(self):
        return reverse_lazy("blog_post_detail", kwargs={"pk": self.object.pk})


class BlogPostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаление статьи - только контент-менеджеры"""

    model = BlogPost
    template_name = "blog/blogpost_confirm_delete.html"
    success_url = reverse_lazy("blog_post_list")
    permission_required = "blog.can_manage_blog"

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
        return redirect("blog_post_list")

    def handle_no_permission(self):
        messages.error(
            self.request,
            "❌ Только контент-менеджеры могут снимать статьи с публикации.",
        )
        return redirect("blog_post_list")
