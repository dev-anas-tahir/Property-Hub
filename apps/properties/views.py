import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.properties.forms import PropertyForm
from apps.properties.models import Property
from apps.properties.selectors import (
    favorite_exists,
    favorite_ids_for_user,
    property_get_with_related,
    property_list_published,
)
from apps.properties.services import (
    favorite_toggle,
    property_create,
    property_delete,
    property_update,
)
from apps.shared.validators import cnic_validator, phone_validator

logger = logging.getLogger(__name__)


def properties_list_view(request):
    is_htmx = request.headers.get("HX-Request") == "true"

    show_favorites = request.GET.get("favorites") == "true"
    show_my_properties = request.GET.get("my_properties") == "true"

    user = request.user if request.user.is_authenticated else None
    properties = property_list_published(
        user=user,
        show_favorites=show_favorites,
        show_my_properties=show_my_properties,
    )

    if not request.user.is_authenticated:
        show_favorites = False
        show_my_properties = False

    page_number = request.GET.get("page", 1)
    paginator = Paginator(properties, 10)
    page_obj = paginator.get_page(page_number)

    favorited_ids = set()
    if request.user.is_authenticated:
        favorited_ids = favorite_ids_for_user(user=request.user)

    for prop in page_obj.object_list:
        prop.is_favorited = prop.id in favorited_ids

    context = {
        "page_obj": page_obj,
        "properties": page_obj.object_list,
        "show_favorites": show_favorites,
        "show_my_properties": show_my_properties,
    }

    if is_htmx:
        return render(request, "_components/properties/property_grid.html", context)
    return render(request, "properties/list.html", context)


def property_detail_view(request, pk):
    is_htmx = request.headers.get("HX-Request") == "true"

    property_obj = property_get_with_related(pk=pk)
    if property_obj is None:
        raise Http404("Property not found")

    is_owner = request.user.is_authenticated and property_obj.user == request.user
    if not property_obj.is_published and not is_owner:
        raise Http404("Property not found")

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = favorite_exists(user=request.user, property_obj=property_obj)

    context = {
        "property": property_obj,
        "is_favorited": is_favorited,
        "is_owner": is_owner,
    }

    if is_htmx:
        return render(request, "_components/properties/property_detail.html", context)
    return render(request, "properties/detail.html", context)


@login_required
def property_edit_view(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if property_obj.user != request.user:
        raise PermissionDenied("You don't have permission to edit this property")

    is_htmx = request.headers.get("HX-Request") == "true"

    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        new_images = request.FILES.getlist("images")
        delete_image_ids = request.POST.getlist("delete_image_ids")
        remove_document = request.POST.get("remove_document") == "true"

        if form.is_valid():
            try:
                property_obj = property_update(
                    property_obj=property_obj,
                    form_data=form.cleaned_data,
                    images=new_images,
                    delete_image_ids=delete_image_ids,
                    remove_document=remove_document,
                )
                messages.success(
                    request, f'Property "{property_obj.name}" updated successfully!'
                )
                if is_htmx:
                    response = HttpResponse()
                    response["HX-Redirect"] = reverse(
                        "properties:detail", args=[property_obj.pk]
                    )
                    return response
                return redirect("properties:detail", pk=property_obj.pk)
            except Exception as e:
                logger.error(
                    f"Error updating property {property_obj.pk}: {e}", exc_info=True
                )
                form.add_error(
                    None,
                    "An error occurred while updating the property. Please try again.",
                )

        context = {"form": form, "property": property_obj, "is_edit_mode": True}
        template = (
            "_components/properties/property_form.html"
            if is_htmx
            else "properties/edit.html"
        )
        return render(request, template, context)

    form = PropertyForm(instance=property_obj)
    context = {"form": form, "property": property_obj, "is_edit_mode": True}
    template = (
        "_components/properties/property_form.html"
        if is_htmx
        else "properties/edit.html"
    )
    return render(request, template, context)


@login_required
def my_properties_list_view(request):
    return render(request, "properties/myprops.html")


@login_required
def favorites_list_view(request):
    favorite_properties = (
        Property.objects.filter(favorited_by__user=request.user)
        .distinct()
        .select_related("user")
        .prefetch_related("images")
    )

    page_number = request.GET.get("page", 1)
    paginator = Paginator(favorite_properties, 10)
    page_obj = paginator.get_page(page_number)

    for prop in page_obj.object_list:
        prop.is_favorited = True

    context = {"properties": page_obj.object_list, "page_obj": page_obj}
    return render(request, "properties/favorites.html", context)


@login_required
def property_create_view(request):
    is_htmx = request.headers.get("HX-Request") == "true"

    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES)
        images = request.FILES.getlist("images")

        if form.is_valid():
            try:
                property_obj = property_create(
                    user=request.user, form_data=form.cleaned_data, images=images
                )
                messages.success(
                    request, f'Property "{property_obj.name}" created successfully!'
                )
                if is_htmx:
                    response = HttpResponse()
                    response["HX-Redirect"] = reverse(
                        "properties:detail", args=[property_obj.pk]
                    )
                    return response
                return redirect("properties:detail", pk=property_obj.pk)
            except Exception as e:
                logger.error(f"Error creating property: {e}", exc_info=True)
                form.add_error(
                    None,
                    "An error occurred while creating the property. Please try again.",
                )

        context = {"form": form, "is_edit_mode": False}
        template = (
            "_components/properties/property_form.html"
            if is_htmx
            else "properties/create.html"
        )
        return render(request, template, context)

    form = PropertyForm()
    context = {"form": form, "is_edit_mode": False}
    template = (
        "_components/properties/property_form.html"
        if is_htmx
        else "properties/create.html"
    )
    return render(request, template, context)


@login_required
def property_download_document_view(request, pk):
    import os

    property_obj = get_object_or_404(Property, pk=pk)

    if property_obj.user != request.user and not request.user.is_superuser:
        return HttpResponseForbidden(
            "You are not authorized to download this document."
        )
    if not property_obj.documents:
        return HttpResponseForbidden("No document available.")
    return FileResponse(
        property_obj.documents,
        as_attachment=True,
        filename=os.path.basename(str(property_obj.documents.name)),
    )


@login_required
def property_favorite_toggle_view(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    property_obj = get_object_or_404(Property, pk=pk)

    is_owner = property_obj.user == request.user
    if not property_obj.is_published and not is_owner:
        raise Http404("Property not found")

    is_favorited = favorite_toggle(user=request.user, property_obj=property_obj)
    return JsonResponse({"is_favorited": is_favorited})


@login_required
def property_validate_step_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    step = request.POST.get("step")
    if not step:
        return JsonResponse({"error": "Step parameter required"}, status=400)

    form = PropertyForm(request.POST, request.FILES)

    step_fields = {
        "1": ["name", "property_type", "price", "full_address"],
        "2": ["bedrooms", "bathrooms", "area", "phone_number", "cnic"],
        "3": [],
        "4": [],
    }

    if step not in step_fields:
        return JsonResponse({"error": "Invalid step"}, status=400)

    fields_to_validate = step_fields[step]
    if not fields_to_validate:
        return JsonResponse({"valid": True})

    errors = {}
    for field_name in fields_to_validate:
        if field_name in form.errors:
            errors[field_name] = form.errors[field_name]
        elif field_name in form.fields and form.fields[field_name].required:
            value = request.POST.get(field_name, "").strip()
            if not value:
                errors[field_name] = ["This field is required."]

    try:
        if step == "1":
            if "price" in fields_to_validate and "price" not in errors:
                form.clean_price()
        elif step == "2":
            if "phone_number" in fields_to_validate and "phone_number" not in errors:
                try:
                    phone_value = request.POST.get("phone_number", "").strip()
                    if phone_value:
                        phone_validator(phone_value)
                except ValidationError as e:
                    errors["phone_number"] = [str(e)]

            if "cnic" in fields_to_validate and "cnic" not in errors:
                try:
                    cnic_value = request.POST.get("cnic", "").strip()
                    if cnic_value:
                        cnic_validator(cnic_value)
                except ValidationError as e:
                    errors["cnic"] = [str(e)]

    except ValidationError as e:
        if hasattr(e, "error_dict"):
            for field, field_errors in e.error_dict.items():
                if field in fields_to_validate:
                    errors[field] = [str(err) for err in field_errors]
        else:
            errors["__all__"] = [str(e)]

    if errors:
        return JsonResponse({"valid": False, "errors": errors})
    return JsonResponse({"valid": True})


@login_required
def property_delete_view(request, pk):
    if request.method not in ["POST", "DELETE"]:
        return HttpResponse("Method not allowed", status=405)

    is_htmx = request.headers.get("HX-Request") == "true"

    property_obj = get_object_or_404(Property, pk=pk)

    if property_obj.user != request.user:
        raise PermissionDenied("You don't have permission to delete this property")

    property_delete(property_obj=property_obj)
    messages.success(request, "Property deleted successfully.")

    if is_htmx:
        response = HttpResponse()
        response["HX-Redirect"] = reverse("properties:list")
        return response
    return redirect("properties:list")


def validate_phone_view(request):
    if request.method != "POST":
        return HttpResponse("", status=200)

    phone_number = request.POST.get("phone_number", "").strip()
    if not phone_number:
        return HttpResponse("", status=200)

    try:
        phone_validator(phone_number)
        return HttpResponse("", status=200)
    except ValidationError as e:
        error_html = f'<div class="invalid-feedback d-block">{e.message}</div>'
        return HttpResponse(error_html, status=200)


def validate_cnic_view(request):
    if request.method != "POST":
        return HttpResponse("", status=200)

    cnic = request.POST.get("cnic", "").strip()
    if not cnic:
        return HttpResponse("", status=200)

    try:
        cnic_validator(cnic)
        return HttpResponse("", status=200)
    except ValidationError as e:
        error_html = f'<div class="invalid-feedback d-block">{e.message}</div>'
        return HttpResponse(error_html, status=200)
