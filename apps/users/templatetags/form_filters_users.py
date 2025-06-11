"""
This module contains template filters for form fields.
"""

from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    """
    Adds a CSS class to the widget of a form field.
    Usage: {{ field|add_class:"form-control" }}
    """
    if not hasattr(field, 'field'):
        return field
        
    if 'class' in field.widget.attrs:
        field.widget.attrs['class'] = f"{field.widget.attrs.get('class', '')} {css_class}"
    else:
        field.widget.attrs['class'] = css_class
    return field
