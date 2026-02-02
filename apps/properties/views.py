"""
This module contains views for property-related operations.
All interactive functionality is handled by HTMX and Alpine.js.
"""

import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from apps.properties.utils import delete_property_and_assets

from apps.properties.models import Favorite, Property, PropertyImage
from apps.properties.utils import handle_document_download
from apps.properties.forms import PropertyForm
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse
from apps.properties.validations import phone_validator, cnic_validator



logger = logging.getLogger(__name__)


def properties_list_view(request):
    """Display paginated list of published properties with optional filters.

    Handles both standard and HTMX requests.
    For HTMX requests, returns only the property list partial.
    For standard requests, returns the full page template.

    Query Parameters:
        page (int): Page number for pagination (default: 1)
        favorites (str): Filter to show only favorited properties ('true')
        my_properties (str): Filter to show only user's own properties ('true')
    """
    # Check if this is an HTMX request
    is_htmx = request.headers.get("HX-Request") == "true"

    # Get filter parameters
    show_favorites = request.GET.get("favorites") == "true"
    show_my_properties = request.GET.get("my_properties") == "true"

    # Start with base queryset - published properties with related data for optimization
    properties = (
        Property.published.all().select_related("user").prefetch_related("images")
    )

    # Apply filters based on query parameters
    if request.user.is_authenticated:
        if show_favorites:
            # Filter to show only favorited properties
            favorited_property_ids = Favorite.objects.filter(
                user=request.user
            ).values_list("property_id", flat=True)
            properties = properties.filter(id__in=favorited_property_ids)

        if show_my_properties:
            # Filter to show only user's own properties
            properties = properties.filter(user=request.user)
    else:
        # If user is not authenticated, ignore filter parameters
        show_favorites = False
        show_my_properties = False

    # Get page number from query parameters
    page_number = request.GET.get("page", 1)

    # Create paginator (10 items per page)
    paginator = Paginator(properties, 10)
    page_obj = paginator.get_page(page_number)

    # Get favorited property IDs for the current user
    favorited_ids = set()
    if request.user.is_authenticated:
        favorited_ids = set(
            Favorite.objects.filter(user=request.user).values_list(
                "property_id", flat=True
            )
        )

    # Add is_favorited attribute to each property
    for prop in page_obj.object_list:
        prop.is_favorited = prop.id in favorited_ids

    context = {
        "page_obj": page_obj,
        "properties": page_obj.object_list,
        "show_favorites": show_favorites,
        "show_my_properties": show_my_properties,
    }

    # Return partial template for HTMX requests, full page for standard requests
    if is_htmx:
        return render(request, "_components/properties/property_grid.html", context)
    else:
        return render(request, "properties/list.html", context)


def property_detail_view(request, pk):
    """Display detailed property information.

    Loads property with related images and user data.
    Checks if property is published or if user is the owner.
    Returns 404 if property not found or not accessible.

    For HTMX requests, returns only the property detail partial.
    For standard requests, returns the full page template.
    """
    # Check if this is an HTMX request
    is_htmx = request.headers.get("HX-Request") == "true"

    # Load property with related data for optimization
    try:
        property_obj = (
            Property.objects.select_related("user")
            .prefetch_related("images")
            .get(pk=pk)
        )
    except Property.DoesNotExist:
        raise Http404("Property not found")

    # Check if property is accessible
    # Property must be published OR user must be the owner
    is_owner = request.user.is_authenticated and property_obj.user == request.user

    if not property_obj.is_published and not is_owner:
        raise Http404("Property not found")

    # Check favorite status for authenticated users
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user, property=property_obj
        ).exists()

    context = {
        "property": property_obj,
        "is_favorited": is_favorited,
        "is_owner": is_owner,
    }

    # Return partial template for HTMX requests, full page for standard requests
    if is_htmx:
        return render(request, "_components/properties/property_detail.html", context)
    else:
        return render(request, "properties/detail.html", context)


@login_required
def property_edit_view(request, pk):
    """Handle property editing with form and image management.

    GET: Display property form with existing data and images
    POST: Process form submission, validate, update property and images

    Handles:
        - Property field updates
        - Image uploads (new images)
        - Image deletion (via delete_image_ids parameter)
        - Document upload/removal
        - Ownership verification

    For HTMX requests:
        - Returns form partial with errors on validation failure
        - Returns HX-Redirect header on success
    For standard requests:
        - Returns full page with form on validation failure
        - Returns standard redirect on success
    """

    # Load existing property and check ownership
    property_obj = get_object_or_404(Property, pk=pk)
    if property_obj.user != request.user:
        raise PermissionDenied("You don't have permission to edit this property")

    # Check if this is an HTMX request
    is_htmx = request.headers.get("HX-Request") == "true"

    if request.method == "POST":
        # Create form instance with POST data and existing property instance
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)

        # Get new images and image deletion requests
        new_images = request.FILES.getlist("images")
        delete_image_ids = request.POST.getlist("delete_image_ids")
        remove_document = request.POST.get("remove_document") == "true"

        # Validate the main form
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save the property (this also handles document upload if present)
                    property_obj = form.save()

                    # Handle document removal
                    if remove_document and property_obj.documents:
                        property_obj.documents.delete(save=False)
                        property_obj.documents = None
                        property_obj.save()

                    # Handle image deletions
                    if delete_image_ids:
                        PropertyImage.objects.filter(
                            id__in=delete_image_ids, property=property_obj
                        ).delete()

                    # Handle new image uploads
                    if new_images:
                        # Check if property has any images left
                        existing_images_count = property_obj.images.count()

                        for idx, image_file in enumerate(new_images):
                            # Create PropertyImage instance
                            # Set first new image as primary only if no images exist
                            is_primary = idx == 0 and existing_images_count == 0
                            property_image = PropertyImage(
                                property=property_obj,
                                image=image_file,
                                is_primary=is_primary,
                            )
                            property_image.save()

                    # Add success message
                    messages.success(
                        request, f'Property "{property_obj.name}" updated successfully!'
                    )

                    # Return appropriate response based on request type
                    if is_htmx:
                        # Return HX-Redirect header for HTMX requests
                        response = HttpResponse()
                        response["HX-Redirect"] = reverse(
                            "properties:detail", args=[property_obj.pk]
                        )
                        return response
                    else:
                        # Standard redirect for non-HTMX requests
                        return redirect("properties:detail", pk=property_obj.pk)

            except Exception as e:
                # Log the error server-side
                logger.error(
                    f"Error updating property {property_obj.pk}: {str(e)}",
                    exc_info=True,
                )

                # Show generic error to user
                form.add_error(
                    None,
                    "An error occurred while updating the property. Please try again.",
                )

        # If form is invalid or save failed, return form with errors
        context = {
            "form": form,
            "property": property_obj,
            "is_edit_mode": True,
        }

        # Return partial template for HTMX, full page for standard requests
        if is_htmx:
            return render(request, "_components/properties/property_form.html", context)
        else:
            return render(request, "properties/edit.html", context)

    # GET request - display form with existing data
    form = PropertyForm(instance=property_obj)
    context = {
        "form": form,
        "property": property_obj,
        "is_edit_mode": True,
    }

    # Return partial template for HTMX, full page for standard requests
    if is_htmx:
        return render(request, "_components/properties/property_form.html", context)
    else:
        return render(request, "properties/edit.html", context)


@login_required
def my_properties_list_view(request):
    """Simple view to render the my properties list page with HTMX."""
    return render(request, "properties/myprops.html")


@login_required
def favorites_list_view(request):
    """Display user's favorite properties with pagination.

    All properties in this view are favorited by definition,
    so we set is_favorited=True for each property.
    """
    # Get favorited properties with related data for optimization
    favorite_properties = (
        Property.objects.filter(favorited_by__user=request.user)
        .distinct()
        .select_related("user")
        .prefetch_related("images")
    )

    # Get page number from query parameters
    page_number = request.GET.get("page", 1)

    # Create paginator (10 items per page)
    from django.core.paginator import Paginator

    paginator = Paginator(favorite_properties, 10)
    page_obj = paginator.get_page(page_number)

    # Set is_favorited=True for all properties (they're all favorites)
    for prop in page_obj.object_list:
        prop.is_favorited = True

    context = {
        "properties": page_obj.object_list,
        "page_obj": page_obj,
    }

    return render(request, "properties/favorites.html", context)


@login_required
def property_create_view(request):
    """Handle property creation with form and image uploads.

    GET: Display empty property form with image upload fields
    POST: Process form submission, validate, save property and images

    For HTMX requests:
        - Returns form partial with errors on validation failure
        - Returns HX-Redirect header on success
    For standard requests:
        - Returns full page with form on validation failure
        - Returns standard redirect on success
    """

    # Check if this is an HTMX request
    is_htmx = request.headers.get("HX-Request") == "true"

    if request.method == "POST":
        # Create form instances with POST data
        form = PropertyForm(request.POST, request.FILES)

        # Create a temporary property instance for the formset (not saved yet)
        property_instance = form.instance

        # Get image formset - we'll handle images manually from request.FILES
        # since formsets don't work well with HTMX file uploads
        images = request.FILES.getlist("images")

        # Validate the main form
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save the property and associate with current user
                    property_obj = form.save(commit=False)
                    property_obj.user = request.user
                    property_obj.save()

                    # Handle image uploads
                    if images:
                        for idx, image_file in enumerate(images):
                            # Create PropertyImage instance
                            property_image = PropertyImage(
                                property=property_obj,
                                image=image_file,
                                is_primary=(idx == 0),  # First image is primary
                            )
                            property_image.save()

                    # Add success message
                    messages.success(
                        request, f'Property "{property_obj.name}" created successfully!'
                    )

                    # Return appropriate response based on request type
                    if is_htmx:
                        # Return HX-Redirect header for HTMX requests
                        response = HttpResponse()
                        response["HX-Redirect"] = reverse(
                            "properties:detail", args=[property_obj.pk]
                        )
                        return response
                    else:
                        # Standard redirect for non-HTMX requests
                        return redirect("properties:detail", pk=property_obj.pk)

            except Exception as e:
                # Log the error server-side
                logger.error(f"Error creating property: {str(e)}", exc_info=True)
                # Show generic error to user
                form.add_error(
                    None,
                    "An error occurred while creating the property. Please try again.",
                )

        # If form is invalid or save failed, return form with errors
        context = {
            "form": form,
            "is_edit_mode": False,
        }

        # Return partial template for HTMX, full page for standard requests
        if is_htmx:
            return render(request, "_components/properties/property_form.html", context)
        else:
            return render(request, "properties/create.html", context)

    # GET request - display empty form
    form = PropertyForm()
    context = {
        "form": form,
        "is_edit_mode": False,
    }

    # Return partial template for HTMX, full page for standard requests
    if is_htmx:
        return render(request, "_components/properties/property_form.html", context)
    else:
        return render(request, "properties/create.html", context)


@login_required
def property_download_document_view(request, pk):
    """Handle document download for a property."""
    property_obj = get_object_or_404(Property, pk=pk)
    return handle_document_download(request, property_obj)


@login_required
def property_favorite_toggle_view(request, pk):
    """Toggle favorite status for a property.

    Handles POST requests to add/remove a property from user's favorites.
    Returns JSON response with updated favorite status.
    """
    # Only allow POST requests
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Get the property
    property_obj = get_object_or_404(Property, pk=pk)

    # Toggle favorite status
    favorite, created = Favorite.objects.get_or_create(
        user=request.user, property=property_obj
    )

    if not created:
        # Favorite already existed, so remove it
        favorite.delete()
        is_favorited = False
    else:
        # Favorite was just created
        is_favorited = True

    # Return JSON response
    return JsonResponse({"is_favorited": is_favorited})


@login_required
def property_validate_step_view(request):
    """Validate a specific step of the property form via AJAX."""

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    step = request.POST.get("step")
    if not step:
        return JsonResponse({"error": "Step parameter required"}, status=400)

    # Create form instance with POST data
    form = PropertyForm(request.POST, request.FILES)

    # Define which fields belong to each step
    step_fields = {
        "1": ["name", "property_type", "price", "full_address"],
        "2": ["bedrooms", "bathrooms", "area", "phone_number", "cnic"],
        "3": [],  # Images step - no validation needed
        "4": [],  # Review step - no validation needed
    }

    if step not in step_fields:
        return JsonResponse({"error": "Invalid step"}, status=400)

    # Get fields for this step
    fields_to_validate = step_fields[step]

    # Check if step has any fields to validate
    if not fields_to_validate:
        return JsonResponse({"valid": True})

    # Validate only the fields for this step
    errors = {}
    for field_name in fields_to_validate:
        if field_name in form.errors:
            errors[field_name] = form.errors[field_name]
        elif field_name in form.fields and form.fields[field_name].required:
            # Check if required field is empty
            value = request.POST.get(field_name, "").strip()
            if not value:
                errors[field_name] = [f"This field is required."]

    # Run custom field validation for this step
    try:
        if step == "1":
            # Validate step 1 fields
            if "price" in fields_to_validate and "price" not in errors:
                form.clean_price()
        elif step == "2":
            # Validate step 2 fields - phone and CNIC have custom validators
            if "phone_number" in fields_to_validate and "phone_number" not in errors:
                try:
                    phone_value = request.POST.get("phone_number", "").strip()
                    if phone_value:
                        from apps.properties.validations import phone_validator

                        phone_validator(phone_value)
                except ValidationError as e:
                    errors["phone_number"] = [str(e)]

            if "cnic" in fields_to_validate and "cnic" not in errors:
                try:
                    cnic_value = request.POST.get("cnic", "").strip()
                    if cnic_value:
                        from apps.properties.validations import cnic_validator

                        cnic_validator(cnic_value)
                except ValidationError as e:
                    errors["cnic"] = [str(e)]

    except ValidationError as e:
        # Handle any validation errors from clean methods
        if hasattr(e, "error_dict"):
            for field, field_errors in e.error_dict.items():
                if field in fields_to_validate:
                    errors[field] = [str(err) for err in field_errors]
        else:
            errors["__all__"] = [str(e)]

    if errors:
        return JsonResponse({"valid": False, "errors": errors})
    else:
        return JsonResponse({"valid": True})


@login_required
def property_delete_view(request, pk):
    """Delete a property and its associated assets.

    Handles POST/DELETE requests to delete a property.
    Checks user ownership before allowing deletion.
    Deletes associated images and documents.
    Returns HX-Redirect header to property list on success.
    """

    # Only allow POST or DELETE requests
    if request.method not in ["POST", "DELETE"]:
        return HttpResponse("Method not allowed", status=405)

    # Check if this is an HTMX request
    is_htmx = request.headers.get("HX-Request") == "true"

    # Load property and check ownership
    property_obj = get_object_or_404(Property, pk=pk)

    if property_obj.user != request.user:
        raise PermissionDenied("You don't have permission to delete this property")

    # Delete the property and its assets
    delete_property_and_assets(request, property_obj)

    # Return appropriate response based on request type
    if is_htmx:
        # Return HX-Redirect header for HTMX requests
        response = HttpResponse()
        response["HX-Redirect"] = reverse("properties:list")
        return response
    else:
        # Standard redirect for non-HTMX requests
        return redirect("properties:list")


def validate_phone_view(request):
    """Validate phone number format for real-time feedback.

    Handles POST requests with phone_number parameter.
    Returns error message HTML or empty response.
    """

    if request.method != "POST":
        return HttpResponse("", status=200)

    phone_number = request.POST.get("phone_number", "").strip()

    if not phone_number:
        return HttpResponse("", status=200)

    try:
        phone_validator(phone_number)
        # Valid phone number - return empty response
        return HttpResponse("", status=200)
    except ValidationError as e:
        # Invalid phone number - return error message
        error_html = f'<div class="invalid-feedback d-block">{e.message}</div>'
        return HttpResponse(error_html, status=200)


def validate_cnic_view(request):
    """Validate CNIC format for real-time feedback.

    Handles POST requests with cnic parameter.
    Returns error message HTML or empty response.
    """

    if request.method != "POST":
        return HttpResponse("", status=200)

    cnic = request.POST.get("cnic", "").strip()

    if not cnic:
        return HttpResponse("", status=200)

    try:
        cnic_validator(cnic)
        # Valid CNIC - return empty response
        return HttpResponse("", status=200)
    except ValidationError as e:
        # Invalid CNIC - return error message
        error_html = f'<div class="invalid-feedback d-block">{e.message}</div>'
        return HttpResponse(error_html, status=200)
