from django_unicorn.components import UnicornView
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.urls import reverse
from apps.users.forms import validate_password_strength
from django.core.exceptions import ValidationError


class SignupFormView(UnicornView):
    username: str = ""
    email: str = ""
    password1: str = ""
    password2: str = ""
    first_name: str = ""
    last_name: str = ""
    errors: dict = {}
    is_loading: bool = False

    def updated_username(self, value):
        """Validate username availability in real-time."""
        if value:
            if User.objects.filter(username=value).exists():
                self.errors['username'] = "Username is already taken."
            else:
                if 'username' in self.errors:
                    del self.errors['username']

    def updated_email(self, value):
        """Validate email availability in real-time."""
        if value:
            if User.objects.filter(email=value).exists():
                self.errors['email'] = "Email is already in use."
            else:
                if 'email' in self.errors:
                    del self.errors['email']

    def updated_password1(self, value):
        """Validate password strength in real-time."""
        if value:
            try:
                validate_password_strength(value)
                if 'password1' in self.errors:
                    del self.errors['password1']
            except ValidationError as e:
                self.errors['password1'] = str(e.message)

    def validate_all(self):
        """Validate all fields before submission."""
        self.errors = {}

        # Required field validation
        if not self.username:
            self.errors['username'] = "Username is required."
        elif User.objects.filter(username=self.username).exists():
            self.errors['username'] = "Username is already taken."

        if not self.email:
            self.errors['email'] = "Email is required."
        elif User.objects.filter(email=self.email).exists():
            self.errors['email'] = "Email is already in use."

        if not self.password1:
            self.errors['password1'] = "Password is required."
        else:
            try:
                validate_password_strength(self.password1)
            except ValidationError as e:
                self.errors['password1'] = str(e.message)

        if not self.password2:
            self.errors['password2'] = "Password confirmation is required."
        elif self.password1 != self.password2:
            self.errors['password2'] = "Passwords do not match."

        return len(self.errors) == 0

    def submit(self):
        """Handle signup form submission."""
        self.is_loading = True

        if not self.validate_all():
            self.is_loading = False
            return

        try:
            # Create user
            user = User.objects.create_user(
                username=self.username,
                email=self.email,
                password=self.password1,
                first_name=self.first_name,
                last_name=self.last_name
            )

            # Auto-login user
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            return HttpResponseRedirect(reverse('properties:list'))

        except Exception as e:
            self.errors['non_field'] = f"An error occurred during signup: {str(e)}"
            self.is_loading = False
