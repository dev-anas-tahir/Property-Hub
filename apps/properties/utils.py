"""
This module contains utility functions for property-related operations.
"""

import os
from typing import Optional
from django.contrib import messages
from django.contrib.auth.models import User
from apps.properties.models import Property, PropertyImage
from django.db.models import QuerySet, BooleanField, Value, Case, When


def get_properties_with_favorites(user: Optional[User] = None) -> QuerySet:
    """
    Most efficient version using conditional annotation.
    """

    queryset = Property.objects.select_related().prefetch_related()

    if user and user.is_authenticated:
        queryset = queryset.annotate(
            is_favorited=Case(
                When(favorited_by__user=user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        ).distinct()  # Important: prevent duplicates from JOIN
    else:
        queryset = queryset.annotate(is_favorited=Value(False))

    return queryset


def handle_document_removal(request, prop, form):
    """
    Handle document removal from the form.
    """
    if request.POST.get("remove_document") and prop.documents:
        prop.documents.delete(save=False)
        form.instance.documents = None


def handle_image_deletion(request, prop):
    """
    Handle image deletion from the form.
    """
    image_ids = request.POST.getlist("delete_images")
    for image_id in image_ids:
        try:
            img = PropertyImage.objects.get(id=image_id, property=prop)
            img.image.delete(save=False)
            img.delete()
        except PropertyImage.DoesNotExist:
            continue


def handle_image_upload(request, prop):
    images = request.FILES.getlist("images")
    if not images:
        return

    allowed_exts = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    max_size = 5 * 1024 * 1024
    max_files = 10

    if len(images) > max_files:
        messages.warning(
            request,
            f"Max {max_files} images allowed. Only first {max_files} processed.",
        )
        images = images[:max_files]

    valid_images = []
    for img in images:
        if not img or img.size == 0 or img.size > max_size:
            continue
        ext = os.path.splitext(img.name.lower())[1]
        if ext not in allowed_exts:
            continue
        valid_images.append(img)

    instances = [PropertyImage(property=prop, image=img) for img in valid_images]
    PropertyImage.objects.bulk_create(instances)

    if not prop.images.filter(is_primary=True).exists():
        first_img = prop.images.first()
        if first_img:
            first_img.is_primary = True
            first_img.save()
