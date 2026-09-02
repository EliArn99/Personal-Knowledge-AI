from django.urls import path

from .views import (
    ChatDetailAPIView,
    ChatListCreateAPIView,
    ChatMessageListCreateAPIView,
)


urlpatterns = [
    path(
        "",
        ChatListCreateAPIView.as_view(),
        name="chat-list-create",
    ),

    path(
        "<int:pk>/",
        ChatDetailAPIView.as_view(),
        name="chat-detail",
    ),

    path(
        "<int:chat_id>/messages/",
        ChatMessageListCreateAPIView.as_view(),
        name="chat-message-list-create",
    ),
]