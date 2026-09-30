from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.ai.services.ai_service import (
    AIServiceError,
    generate_chat_response,
)

from apps.ai.services.rag_service import (
    RAGServiceError,
    answer_with_documents,
)

from .models import Chat, Message
from .serializers import (
    ChatSerializer,
    MessageSerializer,
)
from .utils import generate_chat_title


class ChatListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = ChatSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        return Chat.objects.filter(
            user=self.request.user
        )

    def perform_create(
        self,
        serializer,
    ):
        serializer.save(
            user=self.request.user
        )


class ChatDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = ChatSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        return Chat.objects.filter(
            user=self.request.user
        )


class ChatMessageListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = MessageSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_chat(self):
        return get_object_or_404(
            Chat,
            pk=self.kwargs["chat_id"],
            user=self.request.user,
        )

    def get_queryset(self):
        return Message.objects.filter(
            chat=self.get_chat()
        )

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        chat = self.get_chat()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        # =====================================================
        # 1. Save user message
        # =====================================================

        user_message = serializer.save(
            chat=chat,
            role=Message.Role.USER,
        )

        # =====================================================
        # 2. Automatic chat title
        # =====================================================

        is_first_user_message = (
            not chat.messages.filter(
                role=Message.Role.USER
            )
            .exclude(
                pk=user_message.pk
            )
            .exists()
        )

        if (
            chat.title == "New Chat"
            and is_first_user_message
        ):
            chat.title = (
                generate_chat_title(
                    user_message.content
                )
            )

            chat.save(
                update_fields=[
                    "title",
                    "updated_at",
                ]
            )

        # =====================================================
        # 3. Try RAG first
        # =====================================================

        assistant_content = None
        assistant_sources = []

        try:
            rag_result = (
                answer_with_documents(
                    user=request.user,
                    question=(
                        user_message.content
                    ),
                    limit=5,
                    min_score=0.30,
                )
            )

        except RAGServiceError:
            rag_result = None

        # =====================================================
        # 4. Use RAG answer if relevant sources were found
        # =====================================================

        if (
            rag_result
            and rag_result["sources"]
        ):
            assistant_content = (
                rag_result["answer"]
            )

            assistant_sources = (
                rag_result["sources"]
            )

        # =====================================================
        # 5. Fallback to normal AI chat
        # =====================================================

        else:
            history_messages = list(
                chat.messages
                .order_by(
                    "-created_at"
                )[:20]
            )

            history_messages.reverse()

            history = [
                {
                    "role":
                        message.role,

                    "content":
                        message.content,
                }

                for message
                in history_messages
            ]

            try:
                assistant_content = (
                    generate_chat_response(
                        history
                    )
                )

            except AIServiceError as exc:
                return Response(
                    {
                        "detail":
                            str(exc),

                        "user_message":
                            MessageSerializer(
                                user_message
                            ).data,
                    },
                    status=(
                        status
                        .HTTP_502_BAD_GATEWAY
                    ),
                )

        # =====================================================
        # 6. Save assistant message
        # =====================================================

        assistant_message = (
            Message.objects.create(
                chat=chat,
                role=(
                    Message.Role.ASSISTANT
                ),
                content=(
                    assistant_content
                ),
                sources=(
                    assistant_sources
                ),
            )
        )

        # Updates Chat.updated_at

        chat.save()

        # =====================================================
        # 7. Return both messages
        # =====================================================

        return Response(
            {
                "user_message":
                    MessageSerializer(
                        user_message
                    ).data,

                "assistant_message":
                    MessageSerializer(
                        assistant_message
                    ).data,
            },
            status=(
                status.HTTP_201_CREATED
            ),
        )
