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
    SemanticSearchSerializer,
    DocumentQuestionSerializer
)

from .services.extraction import (
    process_document,
)
from .services.search import (
    semantic_search,
)

from .services.indexing_pipeline import (
    process_document_indexing,
)

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.services.rag_service import (
    RAGServiceError,
    answer_with_documents,
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
        # 1. Save the uploaded file.

        document = serializer.save(
            user=self.request.user
        )

        # 2. Extract and save the text.

        process_document(
            document
        )

        # 3. Create chunks and embeddings
        # only if text extraction succeeded.

        if document.extraction_status == "ready":
            process_document_indexing(
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


class DocumentSemanticSearchAPIView(
    APIView
):
    permission_classes = (
        IsAuthenticated,
    )

    def post(
            self,
            request,
    ):
        serializer = (
            SemanticSearchSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        query = (
            serializer.validated_data[
                "query"
            ]
        )

        limit = (
            serializer.validated_data[
                "limit"
            ]
        )

        results = semantic_search(
            user=request.user,
            query=query,
            limit=limit,
        )

        response_data = []

        for result in results:
            chunk = result["chunk"]

            response_data.append(
                {
                    "document_id":
                        chunk.document_id,

                    "document_title":
                        chunk.document.title,

                    "chunk_index":
                        chunk.chunk_index,

                    "score":
                        round(
                            result["score"],
                            6,
                        ),

                    "content":
                        chunk.content,
                }
            )

        return Response(
            {
                "query": query,
                "count": len(
                    response_data
                ),
                "results":
                    response_data,
            }
        )


class DocumentAskAPIView(APIView):
    permission_classes = (
        IsAuthenticated,
    )

    def post(self, request):
        serializer = (
            DocumentQuestionSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        question = (
            serializer.validated_data[
                "question"
            ]
        )

        limit = (
            serializer.validated_data[
                "limit"
            ]
        )

        min_score = (
            serializer.validated_data[
                "min_score"
            ]
        )

        try:
            result = answer_with_documents(
                user=request.user,
                question=question,
                limit=limit,
                min_score=min_score,
            )

        except RAGServiceError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=500,
            )

        return Response(result)
