"""
This module contains class-based views for property-related operations such as
listing properties, viewing property details, creating new properties, editing existing properties,
and deleting properties within the Property Hub application.
"""

import os
from apps.properties.models import Property, Favorite
from apps.properties.utils import (
    get_properties_with_favorites,
    handle_document_removal,
    handle_image_deletion,
    handle_image_upload,
)
from django.views import View
from apps.properties.forms import PropertyForm
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseForbidden, FileResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
)
from django.db import transaction
from django.contrib import messages


class PropertiesListView(ListView):
    """View for listing all properties."""

    model = Property
    template_name = "properties/list.html"
    context_object_name = "properties"

    def get_queryset(self):
        qs = get_properties_with_favorites(self.request.user)
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
        handle_document_removal(self.request, self.object, form)
        handle_image_deletion(self.request, self.object)
        self.object = form.save()
        handle_image_upload(self.request, self.object)
        return super().form_valid(form)


class ToggleFavoriteView(LoginRequiredMixin, View):
    """Toggle a property’s favorite status on any HTTP method."""

    def post(self, request, *args, **kwargs):
        prop = get_object_or_404(Property, id=kwargs["pk"])
        fav, created = Favorite.objects.get_or_create(user=request.user, property=prop)
        if not created:
            fav.delete()
        return redirect(
            request.META.get("HTTP_REFERER", reverse_lazy("properties:list"))
        )


class FavoritesListView(LoginRequiredMixin, ListView):
    """Simplified but optimized version of the favorites list view."""

    model = Property
    template_name = "properties/favorites.html"
    context_object_name = "properties"

    def get_queryset(self):
        return (
            Property.objects.filter(favorited_by__user=self.request.user)
            .select_related("user")
            .prefetch_related("images")
            .distinct()
        )


class PropertyView(LoginRequiredMixin, View):
    """
    Unified view to handle:
    - GET: property list / detail / download / create form
    - POST: create or update property
    - DELETE: delete a property
    """

    def get_object(self, pk):
        return get_object_or_404(Property, pk=pk)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        action = kwargs.get("action")

        if pk and action == "download":
            prop = self.get_object(pk)
            if prop.user != request.user and not request.user.is_superuser:
                return HttpResponseForbidden(
                    "You are not authorized to download this document."
                )
            if not prop.documents:
                return HttpResponseForbidden("No document available.")
            return FileResponse(
                prop.documents,
                as_attachment=True,
                filename=os.path.basename(prop.documents.name),
            )

        elif pk:
            # Detail view
            prop = self.get_object(pk)
            is_favorited = prop.favorited_by.filter(user=request.user).exists()
            return render(
                request,
                "properties/detail.html",
                {"property": prop, "is_favorited": is_favorited},
            )
        else:
            # Create form view
            form = PropertyForm()
            return render(
                request,
                "properties/new.html",
                {"form": form, "title": "Create New Property"},
            )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.method == "POST" and "_method" in request.POST:
            return self.delete(request, *args, **kwargs)
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.user = request.user
            prop = form.save()
            handle_image_upload(request, prop)
            messages.success(request, "Property created successfully.")
            return redirect("properties:detail", pk=prop.pk)
        else:
            messages.error(request, "Please correct the form errors.")
            return render(request, "properties/new.html", {"form": form})

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        prop = self.get_object(pk)

        if prop.user != request.user:
            return HttpResponseForbidden("Not allowed")

        for img in prop.images.all():
            img.image.delete(save=False)
            img.delete()

        if prop.documents:
            prop.documents.delete(save=False)

        prop.delete()
        messages.success(request, "Property deleted successfully.")
        return redirect(reverse_lazy("properties:list"))
