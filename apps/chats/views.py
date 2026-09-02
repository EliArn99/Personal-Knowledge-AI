from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

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


class ChatMessageListCreateAPIView(generics.ListCreateAPIView):
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

    def perform_create(self, serializer):
        chat = self.get_chat()

        serializer.save(
            chat=chat,
            role=Message.Role.USER,
        )
