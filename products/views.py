from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
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
        return context


class ProductListView(ListView):
    """Список товаров - доступен всем"""

    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        """Для обычных пользователей показываем только опубликованные товары"""
        queryset = super().get_queryset()

        if self.request.user.is_authenticated and (
            self.request.user.has_perm("products.can_unpublish_product")
            or self.request.user.is_superuser
        ):
            # Модераторы и админы видят все товары
            return queryset
        else:
            # Обычные пользователи видят только опубликованные
            return queryset.filter(is_published=True)


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание товара - только для авторизованных"""

    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        """Автоматически привязываем товар к текущему пользователю"""
        form.instance.owner = self.request.user  # 👈 АВТОМАТИЧЕСКАЯ ПРИВЯЗКА
        messages.success(self.request, "✅ Товар успешно создан!")
        return super().form_valid(form)


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
        return product.owner == user  # 👈 ТОЛЬКО ВЛАДЕЛЕЦ

    def handle_no_permission(self):
        """Обработка отсутствия прав"""
        messages.error(self.request, "❌ Вы можете редактировать только свои товары.")
        return redirect("product_list")


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление товара - только для владельца или модератора"""

    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy("product_list")

    def test_func(self):
        """Проверка прав на удаление - владелец ИЛИ модератор"""
        product = self.get_object()
        user = self.request.user

        # 👇 ВЛАДЕЛЕЦ ИЛИ МОДЕРАТОР ИЛИ СУПЕРПОЛЬЗОВАТЕЛЬ
        return (
            product.owner == user
            or user.has_perm("products.delete_product")
            or user.is_superuser
        )

    def handle_no_permission(self):
        """Обработка отсутствия прав"""
        messages.error(self.request, "❌ У вас нет прав для удаления этого товара.")
        return redirect("product_list")


class ProductUnpublishView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Снятие товара с публикации - для модераторов"""

    def test_func(self):
        """Проверка прав на снятие с публикации"""
        user = self.request.user
        return user.has_perm("products.can_unpublish_product") or user.is_superuser

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.unpublish()

        messages.success(request, f'✅ Товар "{product.name}" снят с публикации.')
        return redirect("product_list")


class ProductPublishView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Публикация товара - для модераторов"""

    def test_func(self):
        """Проверка прав на публикацию"""
        user = self.request.user
        return user.has_perm("products.can_unpublish_product") or user.is_superuser

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.publish()

        messages.success(request, f'✅ Товар "{product.name}" опубликован.')
        return redirect("product_list")
