from django.urls import path

from .views import (
    DocumentListCreateAPIView,
    DocumentDetailAPIView,
    DocumentDownloadAPIView,
)


urlpatterns = [
    path(
        "",
        DocumentListCreateAPIView.as_view(),
        name="document-list-create",
    ),

    path(
        "<int:pk>/download/",
        DocumentDownloadAPIView.as_view(),
        name="document-download",
    ),

    path(
        "<int:pk>/",
        DocumentDetailAPIView.as_view(),
        name="document-detail",
    ),
]
