"""
Django settings for config project.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


# Load environment variables
load_dotenv(BASE_DIR / ".env")


# Security
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = os.getenv(
    "DEBUG",
    "False",
).lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1",
    ).split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "",
    ).split(",")
    if origin.strip()
]


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "rest_framework",

    # Local apps
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
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

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


WSGI_APPLICATION = "config.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
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


# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


# Email
MAILERS = {
    "default": {
        "BACKEND": os.getenv(
            "EMAIL_BACKEND",
            "django.core.mail.backends.smtp.EmailBackend",
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
            "use_tls": (
                os.getenv(
                    "EMAIL_USE_TLS",
                    "True",
                ).lower()
                == "true"
            ),
        },
    },
}
MEDIA_URL = "/media/"

MEDIA_ROOT = (
    BASE_DIR / "media"
)



# Custom user model
AUTH_USER_MODEL = "accounts.User"


# AI / Groq settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

AI_MODEL = os.getenv(
    "AI_MODEL",
    "openai/gpt-oss-120b",
)

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"

SECURE_REFERRER_POLICY = "same-origin"

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = False
