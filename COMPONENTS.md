# Django Unicorn Components Reference

This document provides comprehensive documentation for all Django Unicorn components in the Property Hub application.

## Table of Contents

- [Shared Components](#shared-components)
  - [Pagination](#pagination)
  - [Alert Message](#alert-message)
  - [Form Field](#form-field)
  - [Loading Spinner](#loading-spinner)
- [Property Components](#property-components)
  - [Property List](#property-list)
  - [Property Card](#property-card)
  - [Property Detail](#property-detail)
  - [Property Form](#property-form)
  - [Favorite Button](#favorite-button)
  - [Image Carousel](#image-carousel)
  - [Delete Modal](#delete-modal)
- [User Components](#user-components)
  - [Login Form](#login-form)
  - [Signup Form](#signup-form)
  - [Profile Form](#profile-form)
  - [Password Change Form](#password-change-form)
  - [Password Input](#password-input)

---

## Shared Components

### Pagination

**Location:** `apps/shared/components/pagination.py`

**Purpose:** Reusable pagination component for navigating through pages of content.

**Props:**
- `current_page` (int): The currently active page number (default: 1)
- `total_pages` (int): Total number of pages available (default: 1)
- `is_loading` (bool): Loading state indicator (default: False)

**Methods:**
- `next_page()`: Navigate to the next page
- `previous_page()`: Navigate to the previous page
- `go_to_page(page: int)`: Navigate to a specific page number

**Properties:**
- `has_previous` (bool): Returns True if there is a previous page
- `has_next` (bool): Returns True if there is a next page
- `page_range` (list): Returns a list of page numbers to display (max 5 pages)

**Events Emitted:**
- `page_changed`: Emitted when page changes, passes `page` parameter

**Usage Example:**
```html
<!-- In parent template -->
{% unicorn 'pagination' current_page=page total_pages=total_pages %}
```

```python
# In parent component
def page_changed(self, page: int):
    """Handle page change event from pagination component."""
    self.current_page = page
    self.load_data()
```

---

### Alert Message

**Location:** `apps/shared/components/alert_message.py`

**Purpose:** Display toast/alert messages for user notifications.

**Props:**
- `message` (str): The message text to display
- `message_type` (str): Type of alert - "success", "error", "warning", or "info" (default: "info")
- `show` (bool): Whether the alert is visible (default: False)
- `auto_dismiss` (int): Time in milliseconds before auto-dismissing (0 = no auto-dismiss, default: 5000)

**Methods:**
- `display(message: str, message_type: str = "info", auto_dismiss: int = 5000)`: Show an alert message
- `dismiss()`: Manually dismiss the alert

**Properties:**
- `alert_class` (str): Returns Bootstrap alert class based on message type
- `icon_class` (str): Returns Bootstrap icon class based on message type

**Usage Example:**
```html
<!-- In base template for global alerts -->
{% unicorn 'alert_message' %}
```

```python
# From any component
self.call('display', message="Property saved successfully!", message_type="success")
```

---

### Form Field

**Location:** `apps/shared/components/form_field.py`

**Purpose:** Reusable form field wrapper with error display and validation states.

**Props:**
- `label` (str): Field label text
- `field_name` (str): Name attribute for the input field
- `field_type` (str): Type of input - "text", "textarea", "select", "checkbox", "file", "email", "number", "tel" (default: "text")
- `value` (str): Current field value
- `placeholder` (str): Placeholder text
- `required` (bool): Whether field is required (default: False)
- `error` (str): Error message to display
- `help_text` (str): Help text to display below field
- `options` (list): Options for select fields - `[{'value': 'val', 'label': 'Label'}]`
- `rows` (int): Number of rows for textarea (default: 3)
- `accept` (str): File types accepted for file input
- `disabled` (bool): Whether field is disabled (default: False)
- `readonly` (bool): Whether field is readonly (default: False)
- `min_value` (str): Minimum value for number input
- `max_value` (str): Maximum value for number input
- `pattern` (str): Validation pattern

**Properties:**
- `has_error` (bool): Returns True if field has an error
- `field_class` (str): Returns CSS class with validation state
- `input_id` (str): Returns unique ID for the input field

**Usage Example:**
```html
{% unicorn 'form_field' 
    label="Property Name" 
    field_name="name" 
    field_type="text" 
    value=name 
    error=errors.name 
    required=True 
%}
```

---

### Loading Spinner

**Location:** `apps/shared/components/loading_spinner.py`

**Purpose:** Display loading indicators with different styles.

**Props:**
- `style` (str): Spinner style - "inline", "overlay", or "button" (default: "inline")
- `size` (str): Spinner size - "sm", "md", or "lg" (default: "md")
- `text` (str): Loading text to display (default: "Loading...")
- `show` (bool): Whether spinner is visible (default: True)
- `color` (str): Bootstrap color - "primary", "secondary", "success", "danger", "warning", "info", "light", "dark" (default: "primary")

**Properties:**
- `spinner_class` (str): Returns spinner CSS classes based on size and color
- `container_class` (str): Returns container CSS classes based on style

**Usage Example:**
```html
<!-- Inline spinner -->
{% unicorn 'loading_spinner' style="inline" text="Loading properties..." %}

<!-- Overlay spinner -->
<div unicorn:loading>
    {% unicorn 'loading_spinner' style="overlay" %}
</div>

<!-- Button spinner -->
<button unicorn:loading.attr="disabled">
    <span unicorn:loading>
        {% unicorn 'loading_spinner' style="button" size="sm" %}
    </span>
    Save
</button>
```

---

## Property Components

### Property List

**Location:** `apps/properties/components/property_list.py`

**Purpose:** Display a paginated list of properties with filtering capabilities.

**Props:**
- `current_page` (int): Current page number (default: 1)
- `per_page` (int): Number of properties per page (default: 9)
- `total_pages` (int): Total number of pages (default: 1)
- `total_count` (int): Total number of properties (default: 0)
- `show_favorites_only` (bool): Filter to show only favorited properties (default: False)
- `show_my_properties` (bool): Filter to show only user's properties (default: False)
- `properties` (list): List of property IDs to display
- `is_loading` (bool): Loading state (default: False)

**Methods:**
- `mount()`: Initialize component and load properties
- `load_properties()`: Load properties based on filters and pagination
- `page_changed(page: int)`: Handle page change from pagination component
- `next_page()`: Navigate to next page
- `previous_page()`: Navigate to previous page
- `go_to_page(page: int)`: Navigate to specific page
- `refresh_list()`: Refresh the property list
- `property_favorited(property_id: int, is_favorited: bool)`: Handle favorite toggle events

**Properties:**
- `has_properties` (bool): Returns True if there are properties to display
- `empty_message` (str): Returns appropriate empty state message based on filters

**Usage Example:**
```html
<!-- All properties -->
{% unicorn 'property_list' %}

<!-- Favorites only -->
{% unicorn 'property_list' show_favorites_only=True %}

<!-- My properties -->
{% unicorn 'property_list' show_my_properties=True %}
```

---

### Property Card

**Location:** `apps/properties/components/property_card.py`

**Purpose:** Display a property card with summary information.

**Props:**
- `property_id` (int): ID of the property to display
- `property_data` (dict): Property data dictionary
- `is_favorited` (bool): Whether property is favorited by current user (default: False)
- `show_actions` (bool): Whether to show action buttons (default: True)
- `is_owner` (bool): Whether current user owns the property (default: False)

**Methods:**
- `mount()`: Initialize and load property data
- `load_property()`: Load property data with related images and user
- `property_favorited(property_id, is_favorited)`: Handle favorite toggle from child component

**Usage Example:**
```html
{% for property_id in properties %}
    {% unicorn 'property_card' property_id=property_id %}
{% endfor %}
```

---

### Property Detail

**Location:** `apps/properties/components/property_detail.py`

**Purpose:** Display comprehensive property details with actions.

**Props:**
- `property_id` (int): ID of the property to display
- `property` (Property): Property model instance
- `is_favorited` (bool): Whether property is favorited (default: False)
- `is_owner` (bool): Whether current user owns the property (default: False)
- `show_delete_modal` (bool): Whether delete modal is visible (default: False)
- `is_loading` (bool): Loading state (default: False)

**Methods:**
- `mount()`: Initialize and load property data
- `load_property()`: Load property with all related data
- `check_ownership()`: Check if current user owns the property
- `check_favorite_status()`: Check if property is favorited
- `toggle_favorite()`: Toggle favorite status
- `show_delete_confirmation()`: Show delete confirmation modal
- `cancel_delete()`: Cancel delete and hide modal
- `delete_property()`: Delete property and redirect to list

**Usage Example:**
```html
{% unicorn 'property_detail' property_id=property.id %}
```

---

### Property Form

**Location:** `apps/properties/components/property_form.py`

**Purpose:** Handle property creation and editing with validation.

**Props:**
- `property_id` (int): ID of property to edit (None for create mode)
- `name` (str): Property name
- `description` (str): Property description
- `full_address` (str): Full address
- `phone_number` (str): Contact phone number
- `cnic` (str): CNIC number
- `property_type` (str): Type of property ("House" or "Plot")
- `price` (str): Property price
- `is_published` (bool): Whether property is published (default: False)
- `images_to_upload` (list): Images to upload
- `images_preview` (list): Image preview data
- `existing_images` (list): Existing images for edit mode
- `images_to_delete` (list): Image IDs marked for deletion
- `document_file`: Document file to upload
- `remove_document` (bool): Whether to remove existing document (default: False)
- `current_document_name` (str): Name of current document
- `errors` (dict): Validation errors
- `is_loading` (bool): Loading state (default: False)
- `is_edit_mode` (bool): Whether in edit mode (default: False)

**Methods:**
- `mount()`: Initialize and load property data for edit mode
- `load_property()`: Load existing property data
- `updated_phone_number(value)`: Real-time phone validation
- `updated_cnic(value)`: Real-time CNIC validation
- `updated_price(value)`: Real-time price validation
- `toggle_image_delete(image_id)`: Toggle image for deletion
- `validate_all()`: Comprehensive validation before save
- `save()`: Save property with all related data

**Usage Example:**
```html
<!-- Create mode -->
{% unicorn 'property_form' %}

<!-- Edit mode -->
{% unicorn 'property_form' property_id=property.id %}
```

---

### Favorite Button

**Location:** `apps/properties/components/favorite_button.py`

**Purpose:** Toggle favorite status of a property.

**Props:**
- `property_id` (int): ID of the property
- `is_favorited` (bool): Current favorite status (default: False)
- `is_loading` (bool): Loading state (default: False)

**Methods:**
- `mount()`: Initialize and check favorite status
- `check_favorite_status()`: Check if property is favorited
- `toggle()`: Toggle favorite status

**Events Emitted:**
- `property_favorited`: Emitted when favorite is toggled, passes `property_id` and `is_favorited`

**Usage Example:**
```html
{% unicorn 'favorite_button' property_id=property.id %}
```

```python
# In parent component
def property_favorited(self, property_id: int, is_favorited: bool):
    """Handle favorite toggle event."""
    if self.show_favorites_only and not is_favorited:
        self.load_properties()
```

---

### Image Carousel

**Location:** `apps/properties/components/image_carousel.py`

**Purpose:** Display property images in an interactive carousel.

**Props:**
- `property_id` (int): ID of the property
- `images` (list): List of image dictionaries with 'id', 'url', and 'is_primary'
- `current_index` (int): Index of currently displayed image (default: 0)

**Methods:**
- `mount()`: Load images when component mounts
- `load_images()`: Load all images for the property
- `next_image()`: Navigate to next image
- `previous_image()`: Navigate to previous image
- `go_to_image(index: int)`: Navigate to specific image
- `handle_keydown(key: str)`: Handle keyboard navigation (ArrowLeft/ArrowRight)

**Usage Example:**
```html
{% unicorn 'image_carousel' property_id=property.id %}
```

---

### Delete Modal

**Location:** `apps/properties/components/delete_modal.py`

**Purpose:** Display confirmation modal for delete actions.

**Props:**
- `show` (bool): Whether modal is visible (default: False)
- `item_name` (str): Name of item to delete
- `item_type` (str): Type of item (default: "item")

**Methods:**
- `show_modal(item_name: str = "", item_type: str = "item")`: Show the modal
- `hide_modal()`: Hide the modal
- `cancel()`: Cancel delete and hide modal
- `confirm()`: Confirm delete and emit event

**Events Emitted:**
- `delete_confirmed`: Emitted when delete is confirmed

**Usage Example:**
```html
{% unicorn 'delete_modal' show=show_delete_modal item_name=property.name item_type="property" %}
```

```python
# In parent component
def delete_confirmed(self):
    """Handle delete confirmation."""
    # Perform delete operation
    pass
```

---

## User Components

### Login Form

**Location:** `apps/users/components/login_form.py`

**Purpose:** Handle user authentication.

**Props:**
- `username` (str): Username input
- `password` (str): Password input
- `errors` (dict): Validation errors
- `is_loading` (bool): Loading state (default: False)

**Methods:**
- `submit()`: Handle login form submission

**Usage Example:**
```html
{% unicorn 'login_form' %}
```

---

### Signup Form

**Location:** `apps/users/components/signup_form.py`

**Purpose:** Handle user registration with real-time validation.

**Props:**
- `username` (str): Username input
- `email` (str): Email input
- `password1` (str): Password input
- `password2` (str): Password confirmation
- `first_name` (str): First name (optional)
- `last_name` (str): Last name (optional)
- `errors` (dict): Validation errors
- `is_loading` (bool): Loading state (default: False)

**Methods:**
- `updated_username(value)`: Real-time username availability check
- `updated_email(value)`: Real-time email availability check
- `updated_password1(value)`: Real-time password strength validation
- `validate_all()`: Comprehensive validation before submission
- `submit()`: Handle signup form submission

**Usage Example:**
```html
{% unicorn 'signup_form' %}
```

---

### Profile Form

**Location:** `apps/users/components/profile_form.py`

**Purpose:** Edit user profile information.

**Props:**
- `username` (str): Username
- `email` (str): Email
- `first_name` (str): First name
- `last_name` (str): Last name
- `errors` (dict): Validation errors
- `is_loading` (bool): Loading state (default: False)
- `success_message` (str): Success message
- `show_confirm_modal` (bool): Whether confirmation modal is visible (default: False)

**Methods:**
- `mount()`: Load current user data
- `updated_username(value)`: Real-time username uniqueness check
- `updated_email(value)`: Real-time email uniqueness check
- `validate_all()`: Validate all fields before saving
- `show_modal()`: Show confirmation modal
- `hide_modal()`: Hide confirmation modal
- `save()`: Save profile changes

**Usage Example:**
```html
{% unicorn 'profile_form' %}
```

---

### Password Change Form

**Location:** `apps/users/components/password_change_form.py`

**Purpose:** Change user password with validation.

**Props:**
- `old_password` (str): Current password
- `new_password1` (str): New password
- `new_password2` (str): New password confirmation
- `errors` (dict): Validation errors
- `is_loading` (bool): Loading state (default: False)
- `success_message` (str): Success message
- `show_confirm_modal` (bool): Whether confirmation modal is visible (default: False)

**Methods:**
- `updated_new_password1(value)`: Real-time password strength validation
- `validate_all()`: Validate all fields before submission
- `show_modal()`: Show confirmation modal
- `hide_modal()`: Hide confirmation modal
- `submit()`: Handle password change submission

**Usage Example:**
```html
{% unicorn 'password_change_form' %}
```

---

### Password Input

**Location:** `apps/users/components/password_input.py`

**Purpose:** Password input field with show/hide toggle.

**Props:**
- `field_id` (str): ID for the password field
- `field_label` (str): Label text (default: "Password")
- `show` (bool): Whether password is visible (default: False)

**Methods:**
- `mount()`: Initialize component
- `toggle()`: Toggle password visibility

**Usage Example:**
```html
{% unicorn 'password_input' field_id="password" field_label="Password" %}
```

---

## Component Communication

### Parent-Child Communication

Components communicate through events using the `call()` method:

```python
# Child component emits event
self.call('event_name', param1=value1, param2=value2)

# Parent component handles event
def event_name(self, param1, param2):
    # Handle event
    pass
```

### Common Event Patterns

1. **Pagination**: `page_changed` event with `page` parameter
2. **Favorites**: `property_favorited` event with `property_id` and `is_favorited` parameters
3. **Delete**: `delete_confirmed` event (no parameters)
4. **Refresh**: `refresh_list` event (no parameters)

---

## Best Practices

1. **Always validate on the server**: Never trust client-side validation alone
2. **Use loading states**: Provide visual feedback during async operations
3. **Handle errors gracefully**: Display user-friendly error messages
4. **Emit events for parent updates**: Keep parent components in sync
5. **Use transactions**: Wrap database operations in transactions for data integrity
6. **Optimize queries**: Use `select_related()` and `prefetch_related()` to reduce database queries
7. **Check permissions**: Always verify user permissions before sensitive operations
8. **Provide empty states**: Show helpful messages when no data is available

---

## Troubleshooting

### Component not updating
- Ensure property names match between Python and template
- Check that methods are not returning values (except for redirects)
- Verify that `unicorn:model` bindings are correct

### Events not firing
- Ensure parent component has a method matching the event name
- Check that `call()` is being invoked with correct event name
- Verify parent component is properly mounted

### Validation not working
- Check that validation methods are named `updated_<field_name>`
- Ensure validation errors are stored in `self.errors` dict
- Verify error display in template

### File uploads not working
- Ensure form has `enctype="multipart/form-data"`
- Access files via `self.request.FILES`
- Validate file types and sizes server-side

---

## Additional Resources

- [Django Unicorn Documentation](https://www.django-unicorn.com/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [Django Documentation](https://docs.djangoproject.com/)
