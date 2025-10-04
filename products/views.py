from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
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

from .forms import ProductForm
from .models import Product


class HomeView(TemplateView):
    """Главная страница ShopMod"""

    template_name = "products/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from blog.models import BlogPost
        from products.models import Product
        from users.models import User

        # Добавляем статистику для главной страницы
        context["products_count"] = Product.objects.count()
        context["users_count"] = User.objects.count()
        context["blog_posts_count"] = BlogPost.objects.filter(
            status="published"
        ).count()

        return context


class ProductListView(ListView):
    """Список товаров с кешированием"""

    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    @method_decorator(cache_page(30))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """Убираем кастомное кеширование - используем cache_page"""
        queryset = super().get_queryset()

        if self.request.user.is_authenticated and (
            self.request.user.has_perm("products.can_unpublish_product")
            or self.request.user.is_superuser
        ):
            return queryset
        else:
            return queryset.filter(is_published=True)


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание товара - только для авторизованных"""

    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        return response


class ProductDetailView(DetailView):
    """Детальная страница товара с кешированием"""

    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    @method_decorator(cache_page(30))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated and (
            self.request.user.has_perm("products.can_unpublish_product")
            or self.request.user.is_superuser
        ):
            return queryset
        else:
            return queryset.filter(is_published=True)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование товара - только для владельца"""

    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("product_list")

    def test_func(self):
        """Проверка что пользователь - владелец товара"""
        product = self.get_object()
        user = self.request.user
        return product.owner == user  # ТОЛЬКО ВЛАДЕЛЕЦ

    def handle_no_permission(self):
        """Обработка отсутствия прав"""
        messages.error(self.request, "❌ Вы можете редактировать только свои товары.")
        return redirect("product_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        invalidate_product_detail_cache(
            self.object.id
        )  # ИНВАЛИДИРУЕМ КЕШ ДЕТАЛЬНОЙ СТРАНИЦЫ
        return response


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy("product_list")

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return (
            product.owner == user
            or user.has_perm("products.delete_product")
            or user.is_superuser
        )

    def form_valid(self, form):
        """Должен быть ПУСТОЙ или только super()"""
        response = super().form_valid(form)

        return response


class ProductUnpublishView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        user = self.request.user
        return user.has_perm("products.can_unpublish_product") or user.is_superuser

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.unpublish()

        messages.success(request, f'✅ Товар "{product.name}" снят с публикации.')
        return redirect("product_list")


class ProductPublishView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        user = self.request.user
        return user.has_perm("products.can_unpublish_product") or user.is_superuser

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.publish()

        messages.success(request, f'✅ Товар "{product.name}" опубликован.')
        return redirect("product_list")
