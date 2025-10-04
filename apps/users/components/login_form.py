from django_unicorn.components import UnicornView
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect


class LoginFormView(UnicornView):
    username: str = ""
    password: str = ""
    errors: dict = {}
    is_loading: bool = False

    def submit(self):
        """Handle login form submission."""
        self.is_loading = True
        self.errors = {}

        # Validate required fields
        if not self.username:
            self.errors['username'] = "Username is required."
        if not self.password:
            self.errors['password'] = "Password is required."

        if self.errors:
            self.is_loading = False
            return

        # Authenticate user
        user = authenticate(
            self.request,
            username=self.username,
            password=self.password
        )

        if user is not None:
            login(self.request, user)
            return redirect('properties:list')
        else:
            self.errors['non_field'] = "Invalid username or password."
            self.is_loading = False
