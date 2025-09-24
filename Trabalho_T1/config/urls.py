from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from posts.views import PublicLoginView, SignUpView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Autenticação
    path("accounts/login/", PublicLoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/signup/", SignUpView.as_view(), name="signup"),

    # App de posts
    path("", include("posts.urls")),
]
