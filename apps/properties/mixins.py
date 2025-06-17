"""
This module contains mixins for property-related operations i.e deleting a property.
"""

from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from apps.properties.models import Property
from django.shortcuts import get_object_or_404
from apps.properties.utils import (
    handle_document_removal,
    handle_image_deletion,
    handle_image_upload,
    delete_property_and_assets,
)


class PropertyAccessMixin:
    """Provides get_object with ownership enforcement."""

    def get_object(self, pk=None):
        obj = get_object_or_404(Property, pk=pk or self.kwargs.get("pk"))
        if obj.user != self.request.user:
            raise HttpResponseForbidden("Not allowed")
        return obj


class DeletePropertyMixin:
    """Handles property deletion logic, only for owner."""

    def post(self, request, *args, **kwargs):
        if request.POST.get("_method") == "DELETE":
            return self.delete(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        prop = get_object_or_404(Property, pk=self.kwargs.get("pk"))
        if not request.user.is_authenticated or prop.user != request.user:
            return HttpResponseForbidden("Not allowed")
        delete_property_and_assets(request, prop)
        return redirect("properties:list")


class PropertyFormHandlerMixin:
    """Handles media cleanup/upload and messaging around property forms."""
    def process_property_form(self, request, form, instance=None):
        """
        Process a property form for creation or update.

        Args:
            request: The HTTP request object.
            form: The PropertyForm instance.
            instance: The Property instance for updates, or None for creation.

        Returns:
            HttpResponse (redirect on success) or None (on failure).
        """
        if not form.is_valid():
            return None

        # Check for image errors before saving
        image_errors = handle_image_upload(request, instance)
        if image_errors:
            for error in image_errors:
                form.add_error(None, error)
            return None

        with transaction.atomic():
            prop = form.save(commit=False)
            if instance:
                prop.id = instance.id  # Preserve ID for updates
            prop.user = request.user
            prop.save()
            form.save_m2m()  # Save many-to-many fields if any

            # Handle document and image operations
            handle_document_removal(request, prop, form)
            handle_image_deletion(request, prop)
            handle_image_upload(request, prop)  # Re-run to save valid images
            
            action = "updated" if instance else "created"
            messages.success(request, f"Property {action} successfully.")
            return redirect("properties:detail", pk=prop.pk)