"""
This module contains utility functions for property-related operations.
"""

import os
from typing import Optional
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.models import User
from apps.properties.forms import PropertyForm
from apps.properties.models import Property, PropertyImage
from django.http import HttpResponseForbidden, FileResponse
from django.db.models import QuerySet, BooleanField, Value, Case, When


def get_properties_with_favorites(user: Optional[User] = None) -> QuerySet:
    """
    Retrieve properties with favorite status annotation for a user.

    Args:
        user: The user to check favorite status for, or None for unauthenticated users.

    Returns:
        QuerySet with properties annotated with is_favorited boolean.
    """
    queryset = Property.objects.select_related("user").prefetch_related("images")

    if user and user.is_authenticated:
        queryset = queryset.annotate(
            is_favorited=Case(
                When(favorited_by__user=user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).distinct()
    else:
        queryset = queryset.annotate(is_favorited=Value(False))

    return queryset


def handle_document_download(request, property_obj: Property) -> FileResponse:
    """
    Handle document download with permission checks and file response.

    Args:
        request: The HTTP request object.
        property_obj: The Property instance to download the document for.

    Returns:
        FileResponse if authorized and document exists, else HttpResponseForbidden.
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


def handle_document_removal(request, property_obj: Property, form: PropertyForm):
    """
    Handle document removal from the form.

    Args:
        request: The HTTP request object.
        property_obj: The Property instance.
        form: The PropertyForm instance.
    """
    if request.POST.get("remove_document") and property_obj.documents:
        property_obj.documents.delete(save=False)
        form.instance.documents = None


def handle_image_deletion(request, property_obj: Property):
    """
    Handle image deletion from the form.

    Args:
        request: The HTTP request object.
        property_obj: The Property instance.
    """
    image_ids = request.POST.getlist("delete_images")
    for image_id in image_ids:
        try:
            img = PropertyImage.objects.get(id=image_id, property=property_obj)
            img.image.delete(save=False)
            img.delete()
        except PropertyImage.DoesNotExist:
            continue


def handle_image_upload(request, property_obj: Property):
    """
    Handle multiple image uploads for a property with validation and messaging.

    Args:
        request: The HTTP request object containing FILES.
        property_obj: The Property instance to associate images with.
    """
    images = request.FILES.getlist("images")
    if not images:
        return

    allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    max_size = 5 * 1024 * 1024  # 5MB
    max_files = 10

    if len(images) > max_files:
        messages.warning(
            request,
            f"Maximum {max_files} images allowed. Only first {max_files} processed.",
        )
        images = images[:max_files]

    valid_images = []
    for img in images:
        if not img or img.size == 0:
            messages.warning(
                request, f"Image {img.name} is invalid or empty. Skipping."
            )
            continue
        if img.size > max_size:
            messages.warning(
                request, f"Image {img.name} is too large (max 5MB). Skipping."
            )
            continue
        ext = os.path.splitext(img.name.lower())[1]
        if ext not in allowed_extensions:
            messages.warning(
                request,
                f"Image {img.name} has invalid format. Allowed: JPG, PNG, GIF, WebP. Skipping.",
            )
            continue
        valid_images.append(PropertyImage(property=property_obj, image=img))

    if valid_images:
        PropertyImage.objects.bulk_create(valid_images)
        if not property_obj.images.filter(is_primary=True).exists():
            first_img = property_obj.images.first()
            if first_img:
                first_img.is_primary = True
                first_img.save()
        messages.success(request, f"{len(valid_images)} images uploaded successfully.")


def render_property_template(
    request,
    template_name: str,
    property_obj: Optional[Property] = None,
    form: Optional[PropertyForm] = None,
):
    """
    Render a property-related template with appropriate context.

    Args:
        request: The HTTP request object.
        template_name: The name of the template to render (e.g., 'detail.html', 'new.html').
        property_obj: The Property instance for detail view, or None for create form.
        form: The PropertyForm instance for create/edit views, or None for detail view.

    Returns:
        HttpResponse with the rendered template.
    """
    context = {}
    if property_obj:
        context["property"] = property_obj
        if request.user.is_authenticated:
            context["is_favorited"] = property_obj.favorited_by.filter(
                user=request.user
            ).exists()
    if form:
        context["form"] = form
        if template_name == "new.html":
            context["title"] = "Create New Property"

    return render(request, f"properties/{template_name}", context)
