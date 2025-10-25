from django_unicorn.components import UnicornView
from django.contrib.auth.models import User


class ProfileFormView(UnicornView):
    username: str = ""
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    errors: dict = {}
    is_loading: bool = False
    success_message: str = ""
    show_confirm_modal: bool = False

    def mount(self):
        """Load current user data."""
        if self.request.user.is_authenticated:
            user = self.request.user
            self.username = user.username
            self.email = user.email
            self.first_name = user.first_name or ""
            self.last_name = user.last_name or ""

    def updated_username(self, value):
        """Validate username uniqueness in real-time."""
        if value and value != self.request.user.username:
            if User.objects.filter(username=value).exists():
                self.errors['username'] = "Username is already taken."
            else:
                if 'username' in self.errors:
                    del self.errors['username']

    def updated_email(self, value):
        """Validate email uniqueness in real-time."""
        if value and value != self.request.user.email:
            if User.objects.filter(email=value).exists():
                self.errors['email'] = "Email is already in use."
            else:
                if 'email' in self.errors:
                    del self.errors['email']

    def validate_all(self):
        """Validate all fields before saving."""
        self.errors = {}

        if not self.username:
            self.errors['username'] = "Username is required."
        elif self.username != self.request.user.username:
            if User.objects.filter(username=self.username).exists():
                self.errors['username'] = "Username is already taken."

        if not self.email:
            self.errors['email'] = "Email is required."
        elif self.email != self.request.user.email:
            if User.objects.filter(email=self.email).exists():
                self.errors['email'] = "Email is already in use."

        return len(self.errors) == 0

    def show_modal(self):
        """Show confirmation modal."""
        self.show_confirm_modal = True

    def hide_modal(self):
        """Hide confirmation modal."""
        self.show_confirm_modal = False

    def save(self):
        """Save profile changes."""
        self.is_loading = True
        self.success_message = ""
        self.show_confirm_modal = False

        if not self.validate_all():
            self.is_loading = False
            return

        try:
            user = self.request.user
            user.username = self.username
            user.email = self.email
            user.first_name = self.first_name
            user.last_name = self.last_name
            user.save()

            self.success_message = "Profile updated successfully!"
            self.is_loading = False

        except Exception as e:
            self.errors['non_field'] = f"An error occurred: {str(e)}"
            self.is_loading = False
