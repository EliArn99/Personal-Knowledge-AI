"""
Django settings for config project.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# =====================================================
# Base directory / environment
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    return (
        os.getenv(
            name,
            str(default),
        ).lower()
        == "true"
    )


def env_list(name, default=""):
    return [
        value.strip()
        for value in os.getenv(
            name,
            default,
        ).split(",")
        if value.strip()
    ]


# =====================================================
# Core security
# =====================================================

DEBUG = env_bool(
    "DEBUG",
    False,
)

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
)

if not SECRET_KEY:
    raise RuntimeError(
        "DJANGO_SECRET_KEY environment variable is required."
    )


ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1",
)


CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
)


# Enables HTTPS-only Django settings.
#
# Local Docker:
# DJANGO_HTTPS_ENABLED=False
#
# Production:
# DJANGO_HTTPS_ENABLED=True

DJANGO_HTTPS_ENABLED = env_bool(
    "DJANGO_HTTPS_ENABLED",
    False,
)


# =====================================================
# Application definition
# =====================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",

    "apps.accounts",
    "apps.chats",
    "apps.ai",
    "apps.frontend",
    "apps.documents",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django."
            "DjangoTemplates"
        ),
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors."
                    "request"
                ),
                (
                    "django.contrib.auth.context_processors."
                    "auth"
                ),
                (
                    "django.contrib.messages.context_processors."
                    "messages"
                ),
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# =====================================================
# Database
# =====================================================

DATABASES = {
    "default": {
        "ENGINE": (
            "django.db.backends.postgresql"
        ),

        "NAME": os.getenv(
            "POSTGRES_DB",
            "personal_knowledge_ai",
        ),

        "USER": os.getenv(
            "POSTGRES_USER",
            "personal_knowledge_ai_user",
        ),

        "PASSWORD": os.getenv(
            "POSTGRES_PASSWORD",
            "",
        ),

        "HOST": os.getenv(
            "POSTGRES_HOST",
            "db",
        ),

        "PORT": os.getenv(
            "POSTGRES_PORT",
            "5432",
        ),

        "CONN_MAX_AGE": int(
            os.getenv(
                "POSTGRES_CONN_MAX_AGE",
                "60",
            )
        ),

        "CONN_HEALTH_CHECKS": True,
    }
}


# =====================================================
# Password validation
# =====================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# =====================================================
# Internationalization
# =====================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# =====================================================
# Static files
# =====================================================

STATIC_URL = "/static/"

STATIC_ROOT = (
    BASE_DIR / "staticfiles"
)


# =====================================================
# Media / uploaded documents
# =====================================================

MEDIA_URL = "/media/"


MEDIA_ROOT = Path(
    os.getenv(
        "MEDIA_ROOT",
        str(BASE_DIR / "media"),
    )
)


# =====================================================
# Storage
# =====================================================

STORAGES = {
    "default": {
        "BACKEND": (
            "django.core.files.storage."
            "FileSystemStorage"
        ),
    },

    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


# =====================================================
# Email
# =====================================================

MAILERS = {
    "default": {
        "BACKEND": os.getenv(
            "EMAIL_BACKEND",
            (
                "django.core.mail.backends."
                "smtp.EmailBackend"
            ),
        ),

        "OPTIONS": {
            "host": os.getenv(
                "EMAIL_HOST",
                "localhost",
            ),

            "port": int(
                os.getenv(
                    "EMAIL_PORT",
                    "587",
                )
            ),

            "username": os.getenv(
                "EMAIL_HOST_USER",
                "",
            ),

            "password": os.getenv(
                "EMAIL_HOST_PASSWORD",
                "",
            ),

            "use_tls": env_bool(
                "EMAIL_USE_TLS",
                True,
            ),
        },
    },
}


# =====================================================
# Custom user model
# =====================================================

AUTH_USER_MODEL = "accounts.User"


# =====================================================
# AI / Groq
# =====================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
)


AI_MODEL = os.getenv(
    "AI_MODEL",
    "openai/gpt-oss-120b",
)


# =====================================================
# Shared security
# =====================================================

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"

SECURE_REFERRER_POLICY = "same-origin"

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = False

SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SAMESITE = "Lax"


# =====================================================
# Production HTTPS security
# =====================================================

if DJANGO_HTTPS_ENABLED:

    # Railway terminates HTTPS at its proxy and forwards
    # the original scheme through X-Forwarded-Proto.
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    # Start conservatively.
    #
    # After the production domain and HTTPS are proven
    # stable, this can later be increased.

    SECURE_HSTS_SECONDS = int(
        os.getenv(
            "SECURE_HSTS_SECONDS",
            "3600",
        )
    )

    SECURE_HSTS_INCLUDE_SUBDOMAINS = (
        env_bool(
            "SECURE_HSTS_INCLUDE_SUBDOMAINS",
            False,
        )
    )

    SECURE_HSTS_PRELOAD = (
        env_bool(
            "SECURE_HSTS_PRELOAD",
            False,
        )
    )

else:

    SECURE_SSL_REDIRECT = False

    SESSION_COOKIE_SECURE = False

    CSRF_COOKIE_SECURE = False

    SECURE_HSTS_SECONDS = 0

    SECURE_HSTS_INCLUDE_SUBDOMAINS = False

    SECURE_HSTS_PRELOAD = False
