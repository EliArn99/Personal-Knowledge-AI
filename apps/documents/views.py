from rest_framework import generics
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework.permissions import (
    IsAuthenticated,
)

from .models import Document
from .serializers import (
    DocumentSerializer,
)


class DocumentListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = (
        DocumentSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def get_queryset(self):
        return Document.objects.filter(
            user=self.request.user
        )

    def perform_create(
            self,
            serializer,
    ):
        serializer.save(
            user=self.request.user
        )


class DocumentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = (
        DocumentSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def get_queryset(self):
        return Document.objects.filter(
            user=self.request.user
        )
