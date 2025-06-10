from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    """
    Adds a CSS class to the widget of a form field.
    """
    if not hasattr(field, 'as_widget'):
        return field
    return field.as_widget(attrs={"class": css_class})

@register.filter
def filename(value):
    return value.split('/')[-1] if value else ''