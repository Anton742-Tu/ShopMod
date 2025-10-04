from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"),
    path("products/create/", views.ProductCreateView.as_view(), name="product_create"),
    path(
        "products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"
    ),
    path(
        "products/<int:pk>/update/",
        views.ProductUpdateView.as_view(),
        name="product_update",
    ),
    path(
        "products/<int:pk>/delete/",
        views.ProductDeleteView.as_view(),
        name="product_delete",
    ),
    path(
        "products/<int:pk>/unpublish/",
        views.ProductUnpublishView.as_view(),
        name="product_unpublish",
    ),
    path(
        "products/<int:pk>/publish/",
        views.ProductPublishView.as_view(),
        name="product_publish",
    ),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path(
        "category/<slug:category_slug>/",
        views.ProductsByCategoryView.as_view(),
        name="products_by_category",
    ),
]
