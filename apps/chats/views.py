from email import message

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.ai.services.openai_service import (
    AIServiceError,
    generate_chat_response,
)

from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer


class ChatListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Chat.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class ChatDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Chat.objects.filter(
            user=self.request.user
        )


class ChatMessageListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated,)

    def get_chat(self):
        return get_object_or_404(
            Chat,
            pk=self.kwargs["chat_id"],
            user=self.request.user,
        )

    def get_queryset(self):
        chat = self.get_chat()

        return Message.objects.filter(
            chat=chat
        )

    def create(self, request, *args, **kwargs):
        chat = self.get_chat()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user_message = serializer.save(
            chat=chat,
            role=Message.Role.USER,
        )

        history_messages = list(
            chat.messages
            .order_by("-created_at")[:20]
        )

        history_messages.reverse()

        history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in history_messages
        ]

        try:
            ai_answer = generate_chat_response(
                history
            )

        except AIServiceError as exc:
            return Response(
                {
                    "detail": str(exc),
                    "user_message": MessageSerializer(
                        user_message
                    ).data,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        assistant_message = Message.objects.create(
            chat=chat,
            role=Message.Role.ASSISTANT,
            content=ai_answer,
        )

        chat.save(
            update_fields=["updated_at"]
        )

        return Response(
            {
                "user_message": MessageSerializer(
                    user_message
                ).data,

                "assistant_message": MessageSerializer(
                    assistant_message
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )
