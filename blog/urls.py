from django.urls import path

from . import views

urlpatterns = [
    path("", views.BlogPostListView.as_view(), name="blog_post_list"),
    path("post/<int:pk>/", views.BlogPostDetailView.as_view(), name="blog_post_detail"),
    path("post/create/", views.BlogPostCreateView.as_view(), name="blog_post_create"),
    path(
        "post/<int:pk>/update/",
        views.BlogPostUpdateView.as_view(),
        name="blog_post_update",
    ),
    path(
        "post/<int:pk>/delete/",
        views.BlogPostDeleteView.as_view(),
        name="blog_post_delete",
    ),
    path(
        "post/<int:pk>/publish/",
        views.BlogPostPublishView.as_view(),
        name="blog_post_publish",
    ),
    path(
        "post/<int:pk>/unpublish/",
        views.BlogPostUnpublishView.as_view(),
        name="blog_post_unpublish",
    ),
]
