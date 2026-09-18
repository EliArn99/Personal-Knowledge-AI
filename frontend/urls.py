from django.urls import path
from apps.frontend.views import library_view

from .views import (
    chat_view,
    home_view,
    login_view,
    register_view,
)

urlpatterns = [
    path(
        "",
        home_view,
        name="home",
    ),

    path(
        "login/",
        login_view,
        name="login",
    ),

    path(
        "register/",
        register_view,
        name="register",
    ),

    path(
        "chat/",
        chat_view,
        name="chat",
    ),

    path(
        "library/",
        library_view,
        name="library",
    ),
]
