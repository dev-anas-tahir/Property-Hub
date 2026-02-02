"""
This module contains views for user-related operations such as
signing up, logging in, and profile management within the Property Hub application.
"""

from axes.handlers.proxy import AxesProxyHandler
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.users.forms import LoginForm, ProfileForm, SignupForm

# Get the user model dynamically
User = get_user_model()


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
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
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
        template = (
            "_components/forms/signup_form.html" if is_htmx else "users/signup.html"
        )
        return render(request, template, context)

    # GET request
    form = SignupForm()
    context = {"form": form}
    template = "_components/forms/signup_form.html" if is_htmx else "users/signup.html"
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
                "_components/forms/login_form.html" if is_htmx else "users/login.html"
            )
            return render(request, template, context)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            # Authenticate user
            user = authenticate(request, username=email, password=password)

            if user is not None:
                if user.is_active:
                    auth_login(
                        request,
                        user,
                        backend="django.contrib.auth.backends.ModelBackend",
                    )
                    messages.success(
                        request, f"Welcome back, {user.first_name or user.email}!"
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
                    form.add_error(None, "Invalid email or password.")

        # Return form with errors
        context = {"form": form}
        template = (
            "_components/forms/login_form.html" if is_htmx else "users/login.html"
        )
        return render(request, template, context)

    # GET request
    form = LoginForm()
    context = {"form": form}
    template = "_components/forms/login_form.html" if is_htmx else "users/login.html"
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
            "_components/forms/profile_form.html" if is_htmx else "users/profile.html"
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
    template = (
        "_components/forms/profile_form.html" if is_htmx else "users/profile.html"
    )
    return render(request, template, context)


@login_required
def password_change_view(request):
    """Simple view for rendering password change page with HTMX form."""
    return render(request, "users/password_change.html")


def logout_view(request):
    """Custom logout view that redirects home after logout."""
    logout(request)
    return redirect("properties:list")


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
