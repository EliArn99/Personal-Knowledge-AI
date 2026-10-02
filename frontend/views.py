from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def home_view(request):
    if request.user.is_authenticated:
        return redirect("chat")

    return redirect("login")


@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return redirect("chat")

    return render(
        request,
        "frontend/login.html",
    )


@ensure_csrf_cookie
def register_view(request):
    if request.user.is_authenticated:
        return redirect("chat")

    return render(
        request,
        "frontend/register.html",
    )


@login_required(login_url="/login/")
@ensure_csrf_cookie
def chat_view(request):
    return render(
        request,
        "frontend/chat.html",
    )


@login_required(login_url="/login/")
@ensure_csrf_cookie
def library_view(request):
    return render(
        request,
        "frontend/library.html",
    )

@login_required
def document_detail_page(
    request,
    document_id,
):
    return render(
        request,
        "frontend/document_detail.html",
        {
            "document_id": document_id,
        },
    )
