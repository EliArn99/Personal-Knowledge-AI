from django.urls import path

from .views import (
    DocumentListCreateAPIView,
    DocumentDetailAPIView,
    DocumentDownloadAPIView,
    DocumentSemanticSearchAPIView,
    DocumentAskAPIView
)

urlpatterns = [
    path(
        "",
        DocumentListCreateAPIView.as_view(),
        name="document-list-create",
    ),

    path(
        "search/",
        DocumentSemanticSearchAPIView.as_view(),
        name="document-semantic-search",
    ),

    path(
        "ask/",
        DocumentAskAPIView.as_view(),
        name="document-ask",
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
