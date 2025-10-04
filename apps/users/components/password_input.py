from django_unicorn.components import UnicornView


class PasswordInputView(UnicornView):
    field_id: str = ""
    field_label: str = "Password"
    show: bool = False

    def mount(self):
        # Ensure field_label is a string to avoid serialization issues
        if hasattr(self.field_label, '__str__'):
            self.field_label = str(self.field_label)
        print(f"Component mounted: show={self.show}")

    def toggle(self):
        self.show = not self.show
        print(f"Toggle called: show={self.show}")
