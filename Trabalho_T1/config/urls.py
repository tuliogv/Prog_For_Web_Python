from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from posts.views import PublicLoginView, SignUpView

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),

    # Autenticação
    path("accounts/login/", PublicLoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/signup/", SignUpView.as_view(), name="signup"),

    # Recuperação de senha
    path("password_reset/", auth_views.PasswordResetView.as_view(
        template_name="registration/password_reset.html"
    ), name="password_reset"),

    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="registration/password_reset_done.html"
    ), name="password_reset_done"),

    # Link enviado no e-mail leva para cá
    path('reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name="registration/password_reset_confirm.html"
    ), name='password_reset_confirm'
),

    # Mensagem final após redefinir a senha
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="registration/password_reset_complete.html"
    ), name="password_reset_complete"),

    # App de posts
    path("", include("posts.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
