"""
This module contains views for property-related operations.
All interactive functionality is handled by Unicorn components.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import PermissionDenied
from apps.properties.models import Property
from apps.properties.utils import handle_document_download


def properties_list_view(request):
    """Simple view to render the property list page with Unicorn component."""
    return render(request, "properties/list.html")


def property_detail_view(request, pk):
    """Simple view to render the property detail page with Unicorn component."""
    return render(request, "properties/detail.html", {"property_id": pk})


@login_required
def property_edit_view(request, pk):
    """Simple view to render the property edit page with Unicorn component."""
    # Check ownership before rendering
    property_obj = get_object_or_404(Property, pk=pk)
    if property_obj.user != request.user:
        raise PermissionDenied("You don't have permission to edit this property")
    return render(request, "properties/edit.html", {"property_id": pk})


@login_required
def my_properties_list_view(request):
    """Simple view to render the my properties list page with Unicorn component."""
    return render(request, "properties/myprops.html")


@login_required
def favorites_list_view(request):
    """Simple view to render the favorites list page with Unicorn component."""
    return render(request, "properties/favorites.html")


@login_required
def property_create_view(request):
    """Simple view to render the property create page with Unicorn component."""
    return render(request, "properties/create.html")


@login_required
def property_download_document_view(request, pk):
    """Handle document download for a property."""
    property_obj = get_object_or_404(Property, pk=pk)
    return handle_document_download(request, property_obj)
