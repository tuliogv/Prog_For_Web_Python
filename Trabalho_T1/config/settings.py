# config/settings.py
from pathlib import Path
import os
import dj_database_url

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Segurança / Debug
# -----------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-unsafe")
DEBUG = os.getenv("DEBUG", "1") == "1"

# Em produção, sobrescreva por env: ALLOWED_HOSTS="meusite.com,www.meusite.com"
# Em dev, padrão cobre localhost/127.0.0.1 e (opcional) wildcard.
_default_allowed = ["localhost", "127.0.0.1"]
_env_allowed = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
ALLOWED_HOSTS = _env_allowed or (_default_allowed if DEBUG else _default_allowed)

# --- ADIÇÃO: Liberar TODOS os hosts via toggle (padrão: ligado) ----------------
# Use ALLOW_ALL_HOSTS=0 para desativar isso (recomendado em produção).
if os.getenv("ALLOW_ALL_HOSTS", "1") == "1":
    ALLOWED_HOSTS = ["*"]

# Se estiver atrás de proxy TLS (Codespaces/Render/Railway), mantenha:
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- ADIÇÃO (opcional): Confiar no X-Forwarded-Host quando atrás de proxy ------
# Útil para não tomar DisallowedHost dependendo do balanceador/proxy.
# USE_X_FORWARDED_HOST=1 para ativar (por padrão, desativado).
USE_X_FORWARDED_HOST = os.getenv("USE_X_FORWARDED_HOST", "0") == "1"

# -----------------------------------------------------------------------------
# Apps / Middleware
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "posts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",   # CSRF ativo por padrão
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --- (Opcional) Desligar CSRF por variável de ambiente, somente para DEV ---
# Ex.: DISABLE_CSRF=1
DISABLE_CSRF = os.getenv("DISABLE_CSRF", "0") == "1"
if DISABLE_CSRF:
    try:
        idx = MIDDLEWARE.index("django.middleware.csrf.CsrfViewMiddleware")
    except ValueError:
        idx = 0
    # Requer um middleware seu em config/middleware.py que ignore a checagem.
    MIDDLEWARE.insert(idx, "config.middleware.DisableCSRFMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# -----------------------------------------------------------------------------
# Banco de Dados
# -----------------------------------------------------------------------------
# Padrão: SQLite em dev. Se DATABASE_URL existir, usa (ex.: Postgres).
# Exemplos:
#   sqlite:///.../db.sqlite3
#   postgres://USER:PASS@HOST:5432/DBNAME
_db_default = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
DATABASES = {
    "default": dj_database_url.config(
        default=_db_default,
        conn_max_age=600,  # mantém conexões (bom para PaaS)
    )
}

# -----------------------------------------------------------------------------
# Autenticação / Senhas
# -----------------------------------------------------------------------------
# Para o seu trabalho, sem validadores "chatos".
AUTH_PASSWORD_VALIDATORS = []

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "posts:list"
LOGOUT_REDIRECT_URL = "login"

# -----------------------------------------------------------------------------
# i18n / fuso horário
# -----------------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Arquivos estáticos e mídia
# -----------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Django 5 recomenda STORAGES; mantém WhiteNoise comprimindo e com manifest.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Mídia (uploads de usuários)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Limites de upload (opcional)
FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024  # 25 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024  # 25 MB

# Tipos permitidos para anexos (usados na validação do form)
ALLOWED_MEDIA_CONTENT_TYPES = [
    # imagens
    "image/jpeg", "image/png", "image/gif", "image/webp",
    # áudio
    "audio/mpeg", "audio/mp3", "audio/ogg", "audio/wav",
    # vídeo
    "video/mp4", "video/webm", "video/ogg",
]
MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB

# -----------------------------------------------------------------------------
# E-mail (dev: console)
# -----------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# -----------------------------------------------------------------------------
# CSRF Trusted Origins
# -----------------------------------------------------------------------------
# Cobre localhost/127.0.0.1 e Codespaces por padrão.
CODESPACES_HOST_SUFFIX = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")

CSRF_TRUSTED_ORIGINS = [
    "http://localhost", "http://localhost:8000",
    "https://localhost", "https://localhost:8000",
    "http://127.0.0.1", "http://127.0.0.1:8000",
    "https://127.0.0.1", "https://127.0.0.1:8000",
    f"https://*.{CODESPACES_HOST_SUFFIX}",
    "https://*.githubpreview.dev",
]

# Permite acrescentar origens extras via env:
# Ex.: CSRF_EXTRA_ORIGINS="https://meuapp.onrender.com,https://www.meusite.com"
_extra_csrf = [o.strip() for o in os.getenv("CSRF_EXTRA_ORIGINS", "").split(",") if o.strip()]
if _extra_csrf:
    CSRF_TRUSTED_ORIGINS.extend(_extra_csrf)

# -----------------------------------------------------------------------------
# Misc
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"