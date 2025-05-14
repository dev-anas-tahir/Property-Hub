"""
This module contains class-based views for user-related operations such as
signing up, logging in, and profile management within the Property Hub application.
"""

from typing import override
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from apps.users.forms import SignUpForm, UpdateProfileForm


# Create your views here.
class SignUpView(CreateView):
    """View for handling user sign-up."""

    form_class = SignUpForm
    success_url = reverse_lazy("users:login")
    template_name = "users/signup.html"

    @override
    def form_valid(self, form):
        """Override form_valid to save the user and redirect to log in."""
        user = form.save()
        login(self.request, user)
        return redirect("users:login")


class CustomLoginView(LoginView):
    """View for handling user login and on success redirection to home"""

    template_name = "users/login.html"

    @override
    def get_success_url(self):
        """Override get_success_url to redirect to home."""
        return reverse_lazy("users:profile")


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    """View for updating user profile."""

    model = User
    form_class = UpdateProfileForm
    template_name = "users/profile.html"

    @override
    def get_object(self, queryset=None):
        """Override get_object to return the current user."""
        return self.request.user

    @override
    def get_success_url(self):
        """Override get_success_url to redirect to profile."""
        return reverse_lazy("users:profile")


class CustomLogoutView(LogoutView):
    """Custom logout view that redirects home after logout."""

    @staticmethod
    def dispatch(request, *args, **kwargs):
        logout(request)
        return redirect("users:login")
