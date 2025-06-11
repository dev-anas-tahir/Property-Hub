"""
This module contains class-based views for property-related operations such as
listing properties, viewing property details, creating new properties, editing existing properties,
and deleting properties within the Property Hub application.
"""

from apps.properties.models import Property, Favorite, PropertyImage
from django.views import View
from apps.properties.forms import PropertyForm
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import HttpResponseNotAllowed, HttpResponseForbidden, FileResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib import messages


class PropertiesListView(ListView):
    """View for listing all properties."""

    model = Property
    template_name = "properties/list.html"
    context_object_name = "properties"

    def get_queryset(self):
        qs = super().get_queryset().filter(is_published=True)

        if self.request.user.is_authenticated:
            # Pull all property IDs that this user has favorited
            favorited_ids = set(
                Favorite.objects.filter(user=self.request.user).values_list(
                    "property_id", flat=True
                )
            )
            # Annotate each Property instance with an `is_favorited` boolean
            for prop in qs:
                prop.is_favorited = prop.id in favorited_ids
        else:
            # If the user is not authenticated, none are favorited
            for prop in qs:
                prop.is_favorited = False

        return qs


class PropertyDetailView(DetailView):
    """View for viewing a specific property."""

    model = Property
    template_name = "properties/detail.html"
    context_object_name = "property"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["is_favorited"] = self.object.favorited_by.filter(
                user=self.request.user
            ).exists()
        return context


class PropertyDocumentDownloadView(LoginRequiredMixin, DetailView):
    """View for downloading a property's document securely."""

    model = Property

    def get(self, request, *args, **kwargs):
        property_obj = self.get_object()
        # Restrict access to the property owner or superuser
        if property_obj.user != request.user and not request.user.is_superuser:
            return HttpResponseForbidden(
                "You are not authorized to download this document."
            )
        if not property_obj.documents:
            return HttpResponseForbidden("No document available for this property.")
        return FileResponse(
            property_obj.documents,
            as_attachment=True,
            filename=property_obj.documents.name.split("/")[-1],
        )


class NewPropertyView(LoginRequiredMixin, CreateView):
    """View for creating a new property with multiple image uploads."""

    model = Property
    form_class = PropertyForm
    template_name = "properties/new.html"
    success_url = reverse_lazy("properties:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create New Property"
        return context

    @transaction.atomic
    def form_valid(self, form):
        # Set the user before saving
        form.instance.user = self.request.user

        try:
            # Save the property first to get an ID
            self.object = form.save()

            # Handle multiple image uploads
            images = self.request.FILES.getlist("images")

            if images:
                # Validate images
                valid_images = []
                max_size = 5 * 1024 * 1024  # 5MB limit
                max_files = 10  # Maximum number of files
                allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

                if len(images) > max_files:
                    messages.warning(
                        self.request,
                        f"You can upload maximum {max_files} images. Only the first {max_files} will be processed.",
                    )
                    images = images[:max_files]

                for image in images:
                    if not image or image.size == 0:
                        continue

                    # Check file size
                    if image.size > max_size:
                        messages.warning(
                            self.request,
                            f"Image {image.name} is too large (max 5MB). Skipping.",
                        )
                        continue

                    # Check file extension
                    import os

                    ext = os.path.splitext(image.name.lower())[1]
                    if ext not in allowed_extensions:
                        messages.warning(
                            self.request,
                            f"Image {image.name} has invalid format. Allowed: JPG, PNG, GIF, WebP. Skipping.",
                        )
                        continue

                    valid_images.append(image)

                if valid_images:
                    # Create PropertyImage instances
                    property_images = []
                    for image in valid_images:
                        property_images.append(
                            PropertyImage(property=self.object, image=image)
                        )

                    # Bulk create for better performance
                    PropertyImage.objects.bulk_create(property_images)

                    # Set the first uploaded image as primary if none exists
                    if not self.object.images.filter(is_primary=True).exists():
                        first_image = self.object.images.first()
                        if first_image:
                            first_image.is_primary = True
                            first_image.save()

                    messages.success(
                        self.request,
                        f"Property created successfully with {len(valid_images)} images!",
                    )
                else:
                    messages.success(
                        self.request,
                        "Property created successfully! No valid images were uploaded.",
                    )
            else:
                messages.success(self.request, "Property created successfully!")

            return super().form_valid(form)

        except Exception as e:
            # If anything goes wrong, the transaction will be rolled back
            messages.error(self.request, f"Error creating property: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below and try again.")
        return super().form_invalid(form)


class EditPropertyView(LoginRequiredMixin, UpdateView):
    """View for editing a property."""

    model = Property
    form_class = PropertyForm
    template_name = "properties/edit.html"

    def get_success_url(self):
        return reverse_lazy("properties:detail", kwargs={"pk": self.object.pk})

    def get_queryset(self):
        return Property.objects.filter(user=self.request.user)

    def form_valid(self, form):
        # Handle document deletion
        if self.request.POST.get("remove_document"):
            if self.object.documents:
                self.object.documents.delete()
                self.object.documents = None
                form.instance.documents = None

        # Handle image deletions
        delete_image_ids = self.request.POST.getlist("delete_images")

        # delete from media/images/
        for delete_image_id in delete_image_ids:
            image = PropertyImage.objects.get(id=delete_image_id)
            image.image.delete()
            image.delete()

        # Handle new image uploads
        images = self.request.FILES.getlist("images")

        if images:
            # Validate images
            valid_images = []
            max_size = 5 * 1024 * 1024  # 5MB limit
            max_files = 10  # Maximum number of files
            allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

            if len(images) > max_files:
                messages.warning(
                    self.request,
                    f"You can upload maximum {max_files} images. Only the first {max_files} will be processed.",
                )
                images = images[:max_files]

            for image in images:
                if not image or image.size == 0:
                    continue

                # Check file size
                if image.size > max_size:
                    messages.warning(
                        self.request,
                        f"Image {image.name} is too large (max 5MB). Skipping.",
                    )
                    continue

                # Check file extension
                import os

                ext = os.path.splitext(image.name.lower())[1]
                if ext not in allowed_extensions:
                    messages.warning(
                        self.request,
                        f"Image {image.name} has invalid format. Allowed: JPG, PNG, GIF, WebP. Skipping.",
                    )
                    continue

                valid_images.append(image)

                if valid_images:
                    # Create PropertyImage instances
                    property_images = []
                    for image in valid_images:
                        property_images.append(
                            PropertyImage(property=self.object, image=image)
                        )

                    # Bulk create for better performance
                    PropertyImage.objects.bulk_create(property_images)

                    # Set the first uploaded image as primary if none exists
                    if not self.object.images.filter(is_primary=True).exists():
                        first_image = self.object.images.first()
                        if first_image:
                            first_image.is_primary = True
                            first_image.save()

        self.object = form.save()
        return super().form_valid(form)


class DeletePropertyView(LoginRequiredMixin, DeleteView):
    """View for deleting a property and its associated files."""

    model = Property
    success_url = reverse_lazy("properties:list")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])


class ToggleFavoriteView(LoginRequiredMixin, View):
    """Toggle a property’s favorite status on any HTTP method."""

    def dispatch(self, request, *args, **kwargs):
        prop = get_object_or_404(Property, id=kwargs["pk"])
        fav, created = Favorite.objects.get_or_create(user=request.user, property=prop)
        if not created:
            fav.delete()
        return redirect(request.META.get("HTTP_REFERER", "properties:list"))


class FavoritesListView(LoginRequiredMixin, ListView):
    """View for listing all favorite properties."""

    model = Property
    template_name = "properties/favorites.html"
    context_object_name = "properties"

    def get_queryset(self):
        # Get properties that have been favorited by the current user
        favorites = Favorite.objects.filter(user=self.request.user).select_related(
            "property"
        )
        return [favorite.property for favorite in favorites]
