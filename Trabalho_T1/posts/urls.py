from django.urls import path
from .views import (
    PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView
)

app_name = "posts"

urlpatterns = [
    path("", PostListView.as_view(), name="list"),
    path("novo/", PostCreateView.as_view(), name="create"),
    path("<int:pk>/", PostDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", PostUpdateView.as_view(), name="update"),
    path("<int:pk>/excluir/", PostDeleteView.as_view(), name="delete"),
]
