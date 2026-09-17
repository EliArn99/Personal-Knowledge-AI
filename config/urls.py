from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "api/auth/",
        include("apps.accounts.urls"),
    ),

    path(
        "api/chats/",
        include("apps.chats.urls"),
    ),

    path(
        "api-auth/",
        include(
            "rest_framework.urls",
            namespace="rest_framework",
        ),
    ),

    path(
        "",
        include("apps.frontend.urls"),
    ),

    path(
        "api/documents/",
        include(
            "apps.documents.urls"
        ),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
