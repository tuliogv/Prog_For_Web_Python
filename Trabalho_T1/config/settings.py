from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# Segurança / Debug
# -------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-unsafe")
DEBUG = os.getenv("DEBUG", "1") == "1"

# Libera qualquer host (DEV). Em produção, troque por lista explícita.
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# Se estiver atrás de proxy TLS (Codespaces, PaaS), mantenha:
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -------------------------
# Apps / Middleware
# -------------------------
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
    "django.middleware.csrf.CsrfViewMiddleware",   # continua na pilha
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# >>> ADIÇÃO: habilitar desligamento de CSRF via env var (apenas DEV).
DISABLE_CSRF = os.getenv("DISABLE_CSRF", "0") == "1"
if DISABLE_CSRF:
    # insere antes do CsrfViewMiddleware para marcar a flag de bypass
    try:
        idx = MIDDLEWARE.index("django.middleware.csrf.CsrfViewMiddleware")
    except ValueError:
        idx = 0
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

# -------------------------
# Banco de Dados
# -------------------------
# Padrão SQLite (dev). Se DATABASE_URL existir (ex.: Postgres), usa ele.
default_db = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "db.sqlite3",
}
DATABASES = {
    "default": dj_database_url.config(default=f"sqlite:///{default_db['NAME']}")
}

# -------------------------
# Passwords
# -------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------
# i18n / tz
# -------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# -------------------------
# Estáticos
# -------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------
# Auth / Login
# -------------------------
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "posts:list"
LOGOUT_REDIRECT_URL = "login"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------
# CSRF Trusted (mantém amplo p/ DEV; em prod, restrinja)
# -------------------------
CODESPACES_HOST_SUFFIX = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "https://localhost",
    "https://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "https://127.0.0.1",
    "https://127.0.0.1:8000",
    f"https://*.{CODESPACES_HOST_SUFFIX}",
    "https://*.githubpreview.dev",
]

