from django_unicorn.components import UnicornView
from django.contrib.auth import update_session_auth_hash
from apps.users.forms import validate_password_strength
from django.core.exceptions import ValidationError


class PasswordChangeFormView(UnicornView):
    old_password: str = ""
    new_password1: str = ""
    new_password2: str = ""
    errors: dict = {}
    is_loading: bool = False
    success_message: str = ""
    show_confirm_modal: bool = False

    def updated_new_password1(self, value):
        """Validate password strength in real-time."""
        if value:
            try:
                validate_password_strength(value)
                if 'new_password1' in self.errors:
                    del self.errors['new_password1']
            except ValidationError as e:
                self.errors['new_password1'] = str(e.message)

    def validate_all(self):
        """Validate all fields before submission."""
        self.errors = {}

        if not self.old_password:
            self.errors['old_password'] = "Current password is required."
        elif not self.request.user.check_password(self.old_password):
            self.errors['old_password'] = "Current password is incorrect."

        if not self.new_password1:
            self.errors['new_password1'] = "New password is required."
        else:
            try:
                validate_password_strength(self.new_password1)
            except ValidationError as e:
                self.errors['new_password1'] = str(e.message)

        if not self.new_password2:
            self.errors['new_password2'] = "Password confirmation is required."
        elif self.new_password1 != self.new_password2:
            self.errors['new_password2'] = "Passwords do not match."

        return len(self.errors) == 0

    def show_modal(self):
        """Show confirmation modal."""
        self.show_confirm_modal = True

    def hide_modal(self):
        """Hide confirmation modal."""
        self.show_confirm_modal = False

    def submit(self):
        """Handle password change submission."""
        self.is_loading = True
        self.success_message = ""
        self.show_confirm_modal = False

        if not self.validate_all():
            self.is_loading = False
            return

        try:
            user = self.request.user
            user.set_password(self.new_password1)
            user.save()

            # Update session to prevent logout
            update_session_auth_hash(self.request, user)

            self.success_message = "Password changed successfully!"
            
            # Clear form fields
            self.old_password = ""
            self.new_password1 = ""
            self.new_password2 = ""
            
            self.is_loading = False

        except Exception as e:
            self.errors['non_field'] = f"An error occurred: {str(e)}"
            self.is_loading = False
