from django.urls import path
from .views import (
    PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView
)

app_name = "posts"

urlpatterns = [
    path("", PostListView.as_view(), name="list"),                # público
    path("<int:pk>/", PostDetailView.as_view(), name="detail"),   # público
    path("novo/", PostCreateView.as_view(), name="create"),       # autenticado
    path("<int:pk>/editar/", PostUpdateView.as_view(), name="update"),  # autor/staff
    path("<int:pk>/excluir/", PostDeleteView.as_view(), name="delete"), # autor/staff
]
