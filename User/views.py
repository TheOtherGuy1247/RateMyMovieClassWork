from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView

from .forms import SignUpForm

def home(request):
    return render(request, "home.html")


def get_next_url(request):
    """
    Where to go after signing up.

    Uses ?next= (or the hidden "next" field) when it points to a page on THIS
    site, e.g. the movie the visitor wanted to review. Anything else, including
    links to other websites, falls back to LOGIN_REDIRECT_URL (the homepage).
    """
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    is_safe = url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    )
    return next_url if is_safe else settings.LOGIN_REDIRECT_URL


def signup(request):
    # Already logged in? Nothing to sign up for.
    if request.user.is_authenticated:
        return redirect(get_next_url(request))

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()        # new row in auth_user, password hashed
            login(request, user)      # log them straight in
            messages.success(request, f"Welcome, {user.username}! You're logged in.")
            return redirect(get_next_url(request))
    else:
        form = SignUpForm()

    context = {
        "form": form,
        "next": request.POST.get("next") or request.GET.get("next", ""),
    }
    return render(request, "registration/signup.html", context)



class UsersingupView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')