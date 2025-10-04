"""
This module contains views for user-related operations such as
signing up, logging in, and profile management within the Property Hub application.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


def signup_view(request):
    """Simple view for rendering signup page with Unicorn component."""
    return render(request, "users/signup.html")


def login_view(request):
    """Simple view for rendering login page with Unicorn component."""
    return render(request, "users/login.html")


@login_required
def profile_view(request):
    """Simple view for rendering profile page with Unicorn component."""
    return render(request, "users/profile.html")


@login_required
def password_change_view(request):
    """Simple view for rendering password change page with Unicorn component."""
    return render(request, "users/password_change.html")


def logout_view(request):
    """Custom logout view that redirects home after logout."""
    logout(request)
    return redirect("properties:list")
