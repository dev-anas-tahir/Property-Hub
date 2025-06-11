"""
This module contains template filters for form fields.
"""

from django import template
from django.forms import CheckboxInput, RadioSelect

register = template.Library()

@register.filter
def add_class(field, css_class):
    """
    Adds a CSS class to the widget of a form field.
    
    Args:
        field: The form field to add the class to
        css_class (str): The CSS class(es) to add
        
    Returns:
        The field with the updated widget attributes
        
    Usage:
        {{ field|add_class:"form-control" }}
        {{ field|add_class:"form-check-input" }}
    """
    if not field:
        return ''
        
    # Handle both BoundField and widget directly
    widget = field.field.widget if hasattr(field, 'field') else field
    
    # Handle different widget types
    if isinstance(widget, (CheckboxInput, RadioSelect)):
        # For checkboxes and radio buttons, we might want different handling
        css_class = f'form-check-input {css_class}'
    
    # Handle existing classes
    attrs = widget.attrs
    existing_class = attrs.get('class', '').split()
    
    # Add new class if not already present
    for cls in css_class.split():
        if cls not in existing_class:
            existing_class.append(cls)
    
    attrs['class'] = ' '.join(existing_class).strip()
    return field
