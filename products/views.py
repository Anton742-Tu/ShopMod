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
from .models import Category, Product
from .services import (
    get_all_categories,
    get_cached_product_list,
    get_products_by_category,
    get_products_count,
    invalidate_product_list_cache,
)


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
    """Список товаров с низкоуровневым кешированием"""

    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    @method_decorator(cache_page(30))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """Используем низкоуровневое кеширование"""
        return get_cached_product_list(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products_count"] = get_products_count()
        context["cache_type"] = "low_level"
        context["cache_time"] = "2 минуты"
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание товара - только для авторизованных"""

    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        invalidate_product_list_cache()
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
        invalidate_product_list_cache()
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
        response = super().form_valid(form)
        invalidate_product_list_cache()
        return response


class ProductUnpublishView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        user = self.request.user
        return user.has_perm("products.can_unpublish_product") or user.is_superuser

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.unpublish()
        invalidate_product_list_cache()
        messages.success(request, f'✅ Товар "{product.name}" снят с публикации.')
        return redirect("product_list")


class ProductPublishView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        user = self.request.user
        return user.has_perm("products.can_unpublish_product") or user.is_superuser

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.publish()
        invalidate_product_list_cache()
        messages.success(request, f'✅ Товар "{product.name}" опубликован.')
        return redirect("product_list")


class ProductsByCategoryView(ListView):
    """Список товаров по категории"""

    template_name = "products/products_by_category.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        category_slug = self.kwargs["category_slug"]
        return get_products_by_category(category_slug, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs["category_slug"]
        context["category"] = get_object_or_404(Category, slug=category_slug)
        context["all_categories"] = get_all_categories()
        return context


class CategoryListView(ListView):
    """Список всех категорий"""

    model = Category
    template_name = "products/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return get_all_categories()


# products/views.py
from django.http import JsonResponse


def cache_debug_view(request):
    """Отладочная страница для проверки кеша"""
    cache_key = (
        f'product_list_{request.user.pk if request.user.is_authenticated else "anon"}'
    )

    data = {
        "cache_key": cache_key,
        "cache_exists": cache.get(cache_key) is not None,
        "user": request.user.email if request.user.is_authenticated else "Anonymous",
        "redis_keys": [],
    }

    # Проверяем Redis ключи
    try:
        import redis

        r = redis.Redis(host="localhost", port=6379, db=0)
        keys = [key.decode("utf-8") for key in r.keys("*")]
        data["redis_keys"] = keys
    except Exception as e:
        data["redis_error"] = str(e)

    return JsonResponse(data)


from django.http import JsonResponse

from .services import debug_cache_keys


def cache_info_view(request):
    """Страница информации о кеше"""
    cache_keys = debug_cache_keys()

    # Проверяем наш кеш
    cache_key = (
        f'product_list_{request.user.pk if request.user.is_authenticated else "anon"}'
    )
    cache_exists = cache.get(cache_key) is not None

    return JsonResponse(
        {
            "user": (
                request.user.email if request.user.is_authenticated else "Anonymous"
            ),
            "cache_key": cache_key,
            "cache_exists": cache_exists,
            "all_cache_keys": cache_keys,
            "total_keys": len(cache_keys),
        }
    )
