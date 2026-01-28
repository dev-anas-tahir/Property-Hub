"""
This module contains views for user-related operations such as
signing up, logging in, and profile management within the Property Hub application.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from axes.handlers.proxy import AxesProxyHandler

from apps.users.forms import LoginForm, SignupForm, ProfileForm


def signup_view(request):
    """
    Handle user signup with HTMX support.

    GET: Display signup form
    POST: Create new user and auto-login on success
    """
    is_htmx = request.headers.get("HX-Request") == "true"

    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            # Create new user
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
            )

            # Auto-login the user
            auth_login(
                request, user, backend="django.contrib.auth.backends.ModelBackend"
            )

            # Add success message
            messages.success(
                request,
                f"Welcome to PropertyHub, {user.first_name}! Your account has been created successfully.",
            )

            if is_htmx:
                # Return HX-Redirect header for HTMX requests
                response = HttpResponse()
                response["HX-Redirect"] = reverse("properties:list")
                return response
            else:
                return redirect("properties:list")

        # Return form with errors
        context = {"form": form}
        template = "partials/users/signup_form.html" if is_htmx else "users/signup.html"
        return render(request, template, context)

    # GET request
    form = SignupForm()
    context = {"form": form}
    template = "partials/users/signup_form.html" if is_htmx else "users/signup.html"
    return render(request, template, context)


def login_view(request):
    """
    Handle user login with HTMX support.

    GET: Display login form
    POST: Authenticate user and redirect on success
    """
    is_htmx = request.headers.get("HX-Request") == "true"

    if request.method == "POST":
        form = LoginForm(request.POST)

        # Check for django-axes lockout before authentication
        if AxesProxyHandler.is_locked(request):
            cooloff_time = getattr(settings, "AXES_COOLOFF_TIME", None)
            if cooloff_time:
                cooloff_seconds = int(cooloff_time.total_seconds())
                if cooloff_seconds < 60:
                    time_msg = f"{cooloff_seconds} seconds"
                elif cooloff_seconds < 3600:
                    time_msg = f"{cooloff_seconds // 60} minutes"
                else:
                    time_msg = f"{cooloff_seconds // 3600} hours"
                error_msg = f"Too many failed login attempts. Please try again after {time_msg}."
            else:
                error_msg = "Too many failed login attempts. Please contact support."

            form.add_error(None, error_msg)
            context = {"form": form}
            template = (
                "partials/users/login_form.html" if is_htmx else "users/login.html"
            )
            return render(request, template, context)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Authenticate user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    auth_login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )
                    messages.success(
                        request, f"Welcome back, {user.first_name or user.username}!"
                    )

                    if is_htmx:
                        # Return HX-Redirect header for HTMX requests
                        response = HttpResponse()
                        response["HX-Redirect"] = reverse("properties:list")
                        return response
                    else:
                        return redirect("properties:list")
                else:
                    form.add_error(None, "Your account has been disabled.")
            else:
                # Check if this failed attempt caused a lockout
                if AxesProxyHandler.is_locked(request):
                    cooloff_time = getattr(settings, "AXES_COOLOFF_TIME", None)
                    if cooloff_time:
                        cooloff_seconds = int(cooloff_time.total_seconds())
                        if cooloff_seconds < 60:
                            time_msg = f"{cooloff_seconds} seconds"
                        elif cooloff_seconds < 3600:
                            time_msg = f"{cooloff_seconds // 60} minutes"
                        else:
                            time_msg = f"{cooloff_seconds // 3600} hours"
                        error_msg = f"Too many failed login attempts. Your account has been temporarily locked for {time_msg}."
                    else:
                        error_msg = "Too many failed login attempts. Your account has been temporarily locked."
                    form.add_error(None, error_msg)
                else:
                    form.add_error(None, "Invalid username or password.")

        # Return form with errors
        context = {"form": form}
        template = "partials/users/login_form.html" if is_htmx else "users/login.html"
        return render(request, template, context)

    # GET request
    form = LoginForm()
    context = {"form": form}
    template = "partials/users/login_form.html" if is_htmx else "users/login.html"
    return render(request, template, context)


@login_required
def profile_view(request):
    """Simple view for rendering profile page with HTMX form."""
    return render(request, "users/profile.html")


@login_required
def profile_edit_view(request):
    """
    Handle user profile editing with HTMX support.

    GET: Display profile form with current data
    POST: Update user profile and redirect on success
    """
    is_htmx = request.headers.get("HX-Request") == "true"

    if request.method == "POST":
        form = ProfileForm(request.POST, user=request.user)

        if form.is_valid():
            # Update user profile
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.email = form.cleaned_data["email"]
            request.user.save()

            # Add success message
            messages.success(request, "Your profile has been updated successfully.")

            if is_htmx:
                # Return HX-Redirect header for HTMX requests
                response = HttpResponse()
                response["HX-Redirect"] = reverse("users:profile")
                return response
            else:
                return redirect("users:profile")

        # Return form with errors
        context = {"form": form}
        template = (
            "partials/users/profile_form.html" if is_htmx else "users/profile.html"
        )
        return render(request, template, context)

    # GET request - populate form with current user data
    form = ProfileForm(
        initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        },
        user=request.user,
    )
    context = {"form": form}
    template = "partials/users/profile_form.html" if is_htmx else "users/profile.html"
    return render(request, template, context)


@login_required
def password_change_view(request):
    """Simple view for rendering password change page with HTMX form."""
    return render(request, "users/password_change.html")


def logout_view(request):
    """Custom logout view that redirects home after logout."""
    logout(request)
    return redirect("properties:list")


def validate_username_view(request):
    """Validate username availability for real-time feedback.

    Handles POST requests with username parameter.
    Returns error message HTML or empty response.
    """
    if request.method != "POST":
        return HttpResponse("", status=200)

    username = request.POST.get("username", "").strip()

    if not username:
        return HttpResponse("", status=200)

    # Check if username already exists
    if User.objects.filter(username=username).exists():
        error_html = '<div class="invalid-feedback d-block">This username is already taken.</div>'
        return HttpResponse(error_html, status=200)

    # Username is available - return empty response
    return HttpResponse("", status=200)


def validate_email_view(request):
    """Validate email uniqueness for real-time feedback.

    Handles POST requests with email parameter.
    Returns error message HTML or empty response.
    """
    if request.method != "POST":
        return HttpResponse("", status=200)

    email = request.POST.get("email", "").strip().lower()

    if not email:
        return HttpResponse("", status=200)

    # Check if email already exists
    if User.objects.filter(email=email).exists():
        error_html = '<div class="invalid-feedback d-block">This email address is already registered.</div>'
        return HttpResponse(error_html, status=200)

    # Email is available - return empty response
    return HttpResponse("", status=200)
