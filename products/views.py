from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ProductForm
from .models import Product


class ProductListView(ListView):
    """Список товаров - доступен всем"""

    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12  # Опционально: пагинация


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание товара - только для авторизованных"""

    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        """Автоматически привязываем товар к текущему пользователю"""
        form.instance.user = (
            self.request.user
        )  # Если нужно связать товар с пользователем
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование товара - только для авторизованных"""

    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("product_list")


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление товара - только для авторизованных"""

    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy("product_list")


# Альтернативный вариант для function-based views (если будут нужны)
@login_required
def protected_view(request):
    """Пример защищенного представления"""
    return render(request, "products/protected.html")
