from django_unicorn.components import UnicornView


class FormFieldView(UnicornView):
    """Reusable form field wrapper component with error display."""
    
    label: str = ""
    field_name: str = ""
    field_type: str = "text"  # text, textarea, select, checkbox, file, email, number, tel
    value: str = ""
    placeholder: str = ""
    required: bool = False
    error: str = ""
    help_text: str = ""
    options: list = []  # For select fields: [{'value': 'val', 'label': 'Label'}]
    rows: int = 3  # For textarea
    accept: str = ""  # For file input
    disabled: bool = False
    readonly: bool = False
    min_value: str = ""  # For number input
    max_value: str = ""  # For number input
    pattern: str = ""  # For validation pattern
    
    @property
    def has_error(self) -> bool:
        """Check if field has an error."""
        return bool(self.error)
    
    @property
    def field_class(self) -> str:
        """Get the CSS class for the field based on validation state."""
        base_class = "form-control"
        if self.field_type == "checkbox":
            base_class = "form-check-input"
        
        if self.has_error:
            return f"{base_class} is-invalid"
        return base_class
    
    @property
    def input_id(self) -> str:
        """Generate a unique ID for the input field."""
        return f"field_{self.field_name}"
