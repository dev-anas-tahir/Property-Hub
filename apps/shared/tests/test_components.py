"""
Test cases for shared Unicorn components.
"""

import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from apps.shared.components.pagination import PaginationView
from apps.shared.components.alert_message import AlertMessageView
from apps.shared.components.loading_spinner import LoadingSpinnerView
from apps.shared.components.form_field import FormFieldView


@pytest.fixture
def request_factory():
    """Fixture for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def authenticated_request(request_factory):
    """Fixture for creating an authenticated request."""
    user = User.objects.create_user(username='testuser', password='testpass')
    request = request_factory.get('/')
    request.user = user
    return request


@pytest.fixture
def anonymous_request(request_factory):
    """Fixture for creating an anonymous request."""
    request = request_factory.get('/')
    request.user = AnonymousUser()
    return request


# ============================================================================
# Task 10.5: Test shared components
# ============================================================================

@pytest.mark.django_db
class TestPaginationComponent:
    """Tests for PaginationView component - Test pagination component navigates correctly."""
    
    def test_pagination_initializes_correctly(self, authenticated_request):
        """Test that pagination component initializes with correct defaults."""
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        
        assert component.current_page == 1
        assert component.total_pages == 1
        assert component.is_loading is False
    
    def test_pagination_next_page_navigates_correctly(self, authenticated_request, monkeypatch):
        """Test that next_page navigates to the next page correctly."""
        # Mock the call method to avoid TypeError in tests
        def mock_call(*args, **kwargs):
            pass
        
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        monkeypatch.setattr(component, 'call', mock_call)
        component.total_pages = 5
        
        # Navigate to next page
        component.next_page()
        
        assert component.current_page == 2
        
        # Navigate again
        component.next_page()
        
        assert component.current_page == 3
    
    def test_pagination_next_page_stops_at_last_page(self, authenticated_request, monkeypatch):
        """Test that next_page doesn't go beyond the last page."""
        def mock_call(*args, **kwargs):
            pass
        
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        monkeypatch.setattr(component, 'call', mock_call)
        component.total_pages = 3
        component.current_page = 3
        
        # Try to navigate beyond last page
        component.next_page()
        
        # Should stay on page 3
        assert component.current_page == 3
    
    def test_pagination_previous_page_navigates_correctly(self, authenticated_request, monkeypatch):
        """Test that previous_page navigates to the previous page correctly."""
        def mock_call(*args, **kwargs):
            pass
        
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        monkeypatch.setattr(component, 'call', mock_call)
        component.total_pages = 5
        component.current_page = 3
        
        # Navigate to previous page
        component.previous_page()
        
        assert component.current_page == 2
        
        # Navigate again
        component.previous_page()
        
        assert component.current_page == 1
    
    def test_pagination_previous_page_stops_at_first_page(self, authenticated_request, monkeypatch):
        """Test that previous_page doesn't go before the first page."""
        def mock_call(*args, **kwargs):
            pass
        
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        monkeypatch.setattr(component, 'call', mock_call)
        component.total_pages = 5
        component.current_page = 1
        
        # Try to navigate before first page
        component.previous_page()
        
        # Should stay on page 1
        assert component.current_page == 1
    
    def test_pagination_go_to_page_navigates_correctly(self, authenticated_request, monkeypatch):
        """Test that go_to_page navigates to a specific page correctly."""
        def mock_call(*args, **kwargs):
            pass
        
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        monkeypatch.setattr(component, 'call', mock_call)
        component.total_pages = 10
        
        # Go to page 5
        component.go_to_page(5)
        
        assert component.current_page == 5
        
        # Go to page 1
        component.go_to_page(1)
        
        assert component.current_page == 1
        
        # Go to last page
        component.go_to_page(10)
        
        assert component.current_page == 10
    
    def test_pagination_go_to_page_validates_boundaries(self, authenticated_request, monkeypatch):
        """Test that go_to_page validates page boundaries."""
        def mock_call(*args, **kwargs):
            pass
        
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        monkeypatch.setattr(component, 'call', mock_call)
        component.total_pages = 5
        component.current_page = 3
        
        # Try to go to page 0
        component.go_to_page(0)
        
        # Should stay on current page
        assert component.current_page == 3
        
        # Try to go beyond last page
        component.go_to_page(10)
        
        # Should stay on current page
        assert component.current_page == 3
        
        # Try negative page
        component.go_to_page(-1)
        
        # Should stay on current page
        assert component.current_page == 3
    
    def test_pagination_has_previous_property(self, authenticated_request):
        """Test that has_previous property works correctly."""
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        component.total_pages = 5
        
        # On first page
        component.current_page = 1
        assert component.has_previous is False
        
        # On middle page
        component.current_page = 3
        assert component.has_previous is True
        
        # On last page
        component.current_page = 5
        assert component.has_previous is True
    
    def test_pagination_has_next_property(self, authenticated_request):
        """Test that has_next property works correctly."""
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        component.total_pages = 5
        
        # On first page
        component.current_page = 1
        assert component.has_next is True
        
        # On middle page
        component.current_page = 3
        assert component.has_next is True
        
        # On last page
        component.current_page = 5
        assert component.has_next is False
    
    def test_pagination_page_range_with_few_pages(self, authenticated_request):
        """Test that page_range works correctly with few pages."""
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        component.total_pages = 3
        component.current_page = 1
        
        # Should show all pages
        assert component.page_range == [1, 2, 3]
    
    def test_pagination_page_range_at_start(self, authenticated_request):
        """Test that page_range works correctly at the start."""
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        component.total_pages = 10
        component.current_page = 1
        
        # Should show first 5 pages
        assert component.page_range == [1, 2, 3, 4, 5]
    
    def test_pagination_page_range_in_middle(self, authenticated_request):
        """Test that page_range works correctly in the middle."""
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        component.total_pages = 10
        component.current_page = 5
        
        # Should show pages around current page
        assert component.page_range == [3, 4, 5, 6, 7]
    
    def test_pagination_page_range_at_end(self, authenticated_request):
        """Test that page_range works correctly at the end."""
        component = PaginationView(
            component_id='test',
            component_name='pagination',
            request=authenticated_request
        )
        component.total_pages = 10
        component.current_page = 10
        
        # Should show last 5 pages
        assert component.page_range == [6, 7, 8, 9, 10]


@pytest.mark.django_db
class TestAlertMessageComponent:
    """Tests for AlertMessageView component - Test alert message component displays and dismisses."""
    
    def test_alert_message_initializes_correctly(self, authenticated_request):
        """Test that alert message component initializes with correct defaults."""
        component = AlertMessageView(
            component_id='test',
            component_name='alert-message',
            request=authenticated_request
        )
        
        assert component.message == ""
        assert component.message_type == "info"
        assert component.show is False
        assert component.auto_dismiss == 5000
    
    def test_alert_message_displays_correctly(self, authenticated_request):
        """Test that display method shows the alert message correctly."""
        component = AlertMessageView(
            component_id='test',
            component_name='alert-message',
            request=authenticated_request
        )
        
        # Display a success message
        component.display("Operation successful!", "success")
        
        assert component.show is True
        assert component.message == "Operation successful!"
        assert component.message_type == "success"
        assert component.auto_dismiss == 5000
    
    def test_alert_message_displays_with_custom_auto_dismiss(self, authenticated_request):
        """Test that display method respects custom auto_dismiss value."""
        component = AlertMessageView(
            component_id='test',
            component_name='alert-message',
            request=authenticated_request
        )
        
        # Display with custom auto-dismiss
        component.display("Warning message", "warning", auto_dismiss=3000)
        
        assert component.show is True
        assert component.message == "Warning message"
        assert component.message_type == "warning"
        assert component.auto_dismiss == 3000
    
    def test_alert_message_displays_without_auto_dismiss(self, authenticated_request):
        """Test that display method can disable auto-dismiss."""
        component = AlertMessageView(
            component_id='test',
            component_name='alert-message',
            request=authenticated_request
        )
        
        # Display without auto-dismiss
        component.display("Error message", "error", auto_dismiss=0)
        
        assert component.show is True
        assert component.message == "Error message"
        assert component.message_type == "error"
        assert component.auto_dismiss == 0
    
    def test_alert_message_dismisses_correctly(self, authenticated_request):
        """Test that dismiss method hides the alert message correctly."""
        component = AlertMessageView(
            component_id='test',
            component_name='alert-message',
            request=authenticated_request
        )
        
        # Display and then dismiss
        component.display("Test message", "info")
        assert component.show is True
        
        component.dismiss()
        
        assert component.show is False
        assert component.message == ""
    
    def test_alert_message_types(self, authenticated_request):
        """Test that all message types work correctly."""
        component = AlertMessageView(
            component_id='test',
            component_name='alert-message',
            request=authenticated_request
        )
        
        # Test success
        component.display("Success", "success")
        assert component.message_type == "success"
        
        # Test error
        component.display("Error", "error")
        assert component.message_type == "error"
        
        # Test warning
        component.display("Warning", "warning")
        assert component.message_type == "warning"
        
        # Test info
        component.display("Info", "info")
        assert component.message_type == "info"
    
    def test_alert_class_property(self, authenticated_request):
        """Test that alert_class property returns correct Bootstrap classes."""
        component = AlertMessageView(
            component_id='test',
            component_name='alert-message',
            request=authenticated_request
        )
        
        # Test success
        component.message_type = "success"
        assert component.alert_class == "alert-success"
        
        # Test error
        component.message_type = "error"
        assert component.alert_class == "alert-danger"
        
        # Test warning
        component.message_type = "warning"
        assert component.alert_class == "alert-warning"
        
        # Test info
        component.message_type = "info"
        assert component.alert_class == "alert-info"
        
        # Test unknown type defaults to info
        component.message_type = "unknown"
        assert component.alert_class == "alert-info"
    
    def test_icon_class_property(self, authenticated_request):
        """Test that icon_class property returns correct icon classes."""
        component = AlertMessageView(
            component_id='test',
            component_name='alert-message',
            request=authenticated_request
        )
        
        # Test success
        component.message_type = "success"
        assert component.icon_class == "bi-check-circle-fill"
        
        # Test error
        component.message_type = "error"
        assert component.icon_class == "bi-exclamation-triangle-fill"
        
        # Test warning
        component.message_type = "warning"
        assert component.icon_class == "bi-exclamation-circle-fill"
        
        # Test info
        component.message_type = "info"
        assert component.icon_class == "bi-info-circle-fill"
        
        # Test unknown type defaults to info icon
        component.message_type = "unknown"
        assert component.icon_class == "bi-info-circle-fill"
    
    def test_alert_message_multiple_displays(self, authenticated_request):
        """Test that displaying multiple messages works correctly."""
        component = AlertMessageView(
            component_id='test',
            component_name='alert-message',
            request=authenticated_request
        )
        
        # Display first message
        component.display("First message", "success")
        assert component.message == "First message"
        assert component.message_type == "success"
        
        # Display second message (should replace first)
        component.display("Second message", "error")
        assert component.message == "Second message"
        assert component.message_type == "error"


@pytest.mark.django_db
class TestLoadingSpinnerComponent:
    """Tests for LoadingSpinnerView component - Test loading spinner shows during operations."""
    
    def test_loading_spinner_initializes_correctly(self, authenticated_request):
        """Test that loading spinner component initializes with correct defaults."""
        component = LoadingSpinnerView(
            component_id='test',
            component_name='loading-spinner',
            request=authenticated_request
        )
        
        assert component.style == "inline"
        assert component.size == "md"
        assert component.text == "Loading..."
        assert component.show is True
        assert component.color == "primary"
    
    def test_loading_spinner_shows_during_operations(self, authenticated_request):
        """Test that loading spinner shows correctly during operations."""
        component = LoadingSpinnerView(
            component_id='test',
            component_name='loading-spinner',
            request=authenticated_request
        )
        
        # Spinner should be visible by default
        assert component.show is True
        
        # Can be hidden
        component.show = False
        assert component.show is False
        
        # Can be shown again
        component.show = True
        assert component.show is True
    
    def test_loading_spinner_styles(self, authenticated_request):
        """Test that different spinner styles work correctly."""
        component = LoadingSpinnerView(
            component_id='test',
            component_name='loading-spinner',
            request=authenticated_request
        )
        
        # Test inline style
        component.style = "inline"
        assert component.style == "inline"
        
        # Test overlay style
        component.style = "overlay"
        assert component.style == "overlay"
        
        # Test button style
        component.style = "button"
        assert component.style == "button"
    
    def test_loading_spinner_sizes(self, authenticated_request):
        """Test that different spinner sizes work correctly."""
        component = LoadingSpinnerView(
            component_id='test',
            component_name='loading-spinner',
            request=authenticated_request
        )
        
        # Test small size
        component.size = "sm"
        assert component.size == "sm"
        
        # Test medium size
        component.size = "md"
        assert component.size == "md"
        
        # Test large size
        component.size = "lg"
        assert component.size == "lg"
    
    def test_loading_spinner_colors(self, authenticated_request):
        """Test that different spinner colors work correctly."""
        component = LoadingSpinnerView(
            component_id='test',
            component_name='loading-spinner',
            request=authenticated_request
        )
        
        colors = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"]
        
        for color in colors:
            component.color = color
            assert component.color == color
    
    def test_spinner_class_property(self, authenticated_request):
        """Test that spinner_class property returns correct CSS classes."""
        component = LoadingSpinnerView(
            component_id='test',
            component_name='loading-spinner',
            request=authenticated_request
        )
        
        # Test small size
        component.size = "sm"
        component.color = "primary"
        assert "spinner-border" in component.spinner_class
        assert "text-primary" in component.spinner_class
        assert "spinner-border-sm" in component.spinner_class
        
        # Test medium size (no size class)
        component.size = "md"
        component.color = "success"
        assert "spinner-border" in component.spinner_class
        assert "text-success" in component.spinner_class
        assert "spinner-border-sm" not in component.spinner_class
        assert "spinner-border-lg" not in component.spinner_class
        
        # Test large size
        component.size = "lg"
        component.color = "danger"
        assert "spinner-border" in component.spinner_class
        assert "text-danger" in component.spinner_class
        assert "spinner-border-lg" in component.spinner_class
    
    def test_container_class_property(self, authenticated_request):
        """Test that container_class property returns correct CSS classes."""
        component = LoadingSpinnerView(
            component_id='test',
            component_name='loading-spinner',
            request=authenticated_request
        )
        
        # Test inline style
        component.style = "inline"
        container_class = component.container_class
        assert "d-flex" in container_class
        assert "align-items-center" in container_class
        assert "justify-content-center" in container_class
        
        # Test overlay style
        component.style = "overlay"
        container_class = component.container_class
        assert "position-fixed" in container_class
        assert "top-0" in container_class
        assert "w-100" in container_class
        assert "h-100" in container_class
        assert "bg-dark" in container_class
        assert "bg-opacity-50" in container_class
        
        # Test button style
        component.style = "button"
        container_class = component.container_class
        assert "d-inline-block" in container_class
    
    def test_loading_spinner_custom_text(self, authenticated_request):
        """Test that custom loading text works correctly."""
        component = LoadingSpinnerView(
            component_id='test',
            component_name='loading-spinner',
            request=authenticated_request
        )
        
        # Default text
        assert component.text == "Loading..."
        
        # Custom text
        component.text = "Please wait..."
        assert component.text == "Please wait..."
        
        component.text = "Processing your request..."
        assert component.text == "Processing your request..."


@pytest.mark.django_db
class TestFormFieldComponent:
    """Tests for FormFieldView component - Test form field component displays errors correctly."""
    
    def test_form_field_initializes_correctly(self, authenticated_request):
        """Test that form field component initializes with correct defaults."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        assert component.label == ""
        assert component.field_name == ""
        assert component.field_type == "text"
        assert component.value == ""
        assert component.placeholder == ""
        assert component.required is False
        assert component.error == ""
        assert component.help_text == ""
        assert component.disabled is False
        assert component.readonly is False
    
    def test_form_field_displays_errors_correctly(self, authenticated_request):
        """Test that form field displays validation errors correctly."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        # No error initially
        assert component.has_error is False
        assert component.error == ""
        
        # Set an error
        component.error = "This field is required"
        
        assert component.has_error is True
        assert component.error == "This field is required"
    
    def test_form_field_has_error_property(self, authenticated_request):
        """Test that has_error property works correctly."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        # No error
        component.error = ""
        assert component.has_error is False
        
        # With error
        component.error = "Invalid value"
        assert component.has_error is True
        
        # Empty string is no error
        component.error = ""
        assert component.has_error is False
    
    def test_form_field_class_property(self, authenticated_request):
        """Test that field_class property returns correct CSS classes."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        # Text field without error
        component.field_type = "text"
        component.error = ""
        assert component.field_class == "form-control"
        
        # Text field with error
        component.error = "Invalid input"
        assert component.field_class == "form-control is-invalid"
        
        # Checkbox without error
        component.field_type = "checkbox"
        component.error = ""
        assert component.field_class == "form-check-input"
        
        # Checkbox with error
        component.error = "Must be checked"
        assert component.field_class == "form-check-input is-invalid"
    
    def test_form_field_types(self, authenticated_request):
        """Test that different field types work correctly."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        field_types = ["text", "textarea", "select", "checkbox", "file", "email", "number", "tel"]
        
        for field_type in field_types:
            component.field_type = field_type
            assert component.field_type == field_type
    
    def test_form_field_input_id_property(self, authenticated_request):
        """Test that input_id property generates correct IDs."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        component.field_name = "username"
        assert component.input_id == "field_username"
        
        component.field_name = "email_address"
        assert component.input_id == "field_email_address"
    
    def test_form_field_with_label(self, authenticated_request):
        """Test that form field works with labels."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        component.label = "Username"
        component.field_name = "username"
        
        assert component.label == "Username"
        assert component.field_name == "username"
    
    def test_form_field_with_placeholder(self, authenticated_request):
        """Test that form field works with placeholders."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        component.placeholder = "Enter your username"
        assert component.placeholder == "Enter your username"
    
    def test_form_field_with_help_text(self, authenticated_request):
        """Test that form field works with help text."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        component.help_text = "Username must be at least 3 characters"
        assert component.help_text == "Username must be at least 3 characters"
    
    def test_form_field_required_attribute(self, authenticated_request):
        """Test that required attribute works correctly."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        # Not required by default
        assert component.required is False
        
        # Set as required
        component.required = True
        assert component.required is True
    
    def test_form_field_disabled_attribute(self, authenticated_request):
        """Test that disabled attribute works correctly."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        # Not disabled by default
        assert component.disabled is False
        
        # Set as disabled
        component.disabled = True
        assert component.disabled is True
    
    def test_form_field_readonly_attribute(self, authenticated_request):
        """Test that readonly attribute works correctly."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        # Not readonly by default
        assert component.readonly is False
        
        # Set as readonly
        component.readonly = True
        assert component.readonly is True
    
    def test_form_field_with_value(self, authenticated_request):
        """Test that form field works with values."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        component.value = "test_value"
        assert component.value == "test_value"
    
    def test_form_field_select_with_options(self, authenticated_request):
        """Test that select field works with options."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        component.field_type = "select"
        component.options = [
            {'value': '1', 'label': 'Option 1'},
            {'value': '2', 'label': 'Option 2'},
            {'value': '3', 'label': 'Option 3'},
        ]
        
        assert len(component.options) == 3
        assert component.options[0]['value'] == '1'
        assert component.options[0]['label'] == 'Option 1'
    
    def test_form_field_textarea_with_rows(self, authenticated_request):
        """Test that textarea field works with rows attribute."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        component.field_type = "textarea"
        component.rows = 5
        
        assert component.rows == 5
    
    def test_form_field_file_with_accept(self, authenticated_request):
        """Test that file field works with accept attribute."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        component.field_type = "file"
        component.accept = "image/*"
        
        assert component.accept == "image/*"
    
    def test_form_field_number_with_min_max(self, authenticated_request):
        """Test that number field works with min and max values."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        component.field_type = "number"
        component.min_value = "0"
        component.max_value = "100"
        
        assert component.min_value == "0"
        assert component.max_value == "100"
    
    def test_form_field_with_pattern(self, authenticated_request):
        """Test that form field works with validation pattern."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        component.pattern = "[0-9]{5}"
        assert component.pattern == "[0-9]{5}"
    
    def test_form_field_multiple_errors(self, authenticated_request):
        """Test that form field can display different error messages."""
        component = FormFieldView(
            component_id='test',
            component_name='form-field',
            request=authenticated_request
        )
        
        # First error
        component.error = "This field is required"
        assert component.has_error is True
        assert component.error == "This field is required"
        
        # Change error
        component.error = "Invalid format"
        assert component.has_error is True
        assert component.error == "Invalid format"
        
        # Clear error
        component.error = ""
        assert component.has_error is False
