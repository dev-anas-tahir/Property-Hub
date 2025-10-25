"""
This module contains utility functions for property-related operations.
"""

import os
from django.contrib import messages
from apps.properties.models import Property
from django.http import HttpResponseForbidden, FileResponse

def handle_document_download(request, property_obj: Property) -> FileResponse:
    """
    Handle document download with permission checks and file response.
    """
    if property_obj.user != request.user and not request.user.is_superuser:
        return HttpResponseForbidden(
            "You are not authorized to download this document."
        )
    if not property_obj.documents:
        return HttpResponseForbidden("No document available.")
    return FileResponse(
        property_obj.documents,
        as_attachment=True,
        filename=os.path.basename(property_obj.documents.name),
    )




def delete_property_and_assets(request, property_obj: Property):
    """
    Delete a property and its associated images and documents.

    Args:
        request: The HTTP request object for messaging.
        property_obj: The Property instance to delete.
    """
    for img in property_obj.images.all():
        img.image.delete(save=False)

    if property_obj.documents:
        property_obj.documents.delete(save=False)

    property_obj.delete()
    messages.success(request, "Property deleted successfully.")
