from django.http import (
    FileResponse,
    Http404,
)

from django.shortcuts import (
    get_object_or_404,
)

from rest_framework import generics
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.views import APIView

from .models import Document

from .serializers import (
    DocumentSerializer,
    DocumentDetailSerializer,
)

from .services.extraction import (
    process_document,
)


# =====================================================
# List / Upload
# =====================================================

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

        # Save the uploaded document

        document = serializer.save(
            user=self.request.user
        )

        # Extract and save its text

        process_document(
            document
        )


# =====================================================
# Detail / Rename / Delete
# =====================================================

class DocumentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = (
        DocumentDetailSerializer
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


# =====================================================
# Protected File Download
# =====================================================

class DocumentDownloadAPIView(
    APIView
):

    permission_classes = (
        IsAuthenticated,
    )

    def get(
        self,
        request,
        pk,
    ):

        document = get_object_or_404(
            Document,
            pk=pk,
            user=request.user,
        )

        try:
            file = document.file.open(
                "rb"
            )

        except OSError as exc:
            raise Http404(
                "Document file not found."
            ) from exc

        return FileResponse(
            file,
            as_attachment=True,
            filename=(
                document.original_filename
            ),
            content_type=(
                "application/octet-stream"
            ),
        )
