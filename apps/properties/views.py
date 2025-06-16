"""
This module contains class-based views for property-related operations such as
listing properties, viewing property details, creating new properties, editing existing properties,
and deleting properties within the Property Hub application.
"""

from django.views import View
from django.db import transaction
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from apps.properties.forms import PropertyForm
from apps.properties.models import Property, Favorite
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView
from apps.properties.utils import (
    get_properties_with_favorites,
    handle_document_download,
    handle_document_removal,
    handle_image_deletion,
    handle_image_upload,
    render_property_template,
)

class PropertiesListView(ListView):
    """View for listing all properties."""
    model = Property
    template_name = "properties/list.html"
    context_object_name = "properties"

    def get_queryset(self):
        return get_properties_with_favorites(self.request.user)

class PropertyDetailView(DetailView):
    """View for viewing a specific property."""
    model = Property
    template_name = "properties/detail.html"
    context_object_name = "property"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return render_property_template(request, "detail.html", property_obj=self.object)

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
        messages.success(self.request, "Property updated successfully.")
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

class MyPropertiesListView(LoginRequiredMixin, ListView):
    """View for listing all properties created by the user."""
    model = Property
    template_name = "properties/myprops.html"
    context_object_name = "properties"

    def get_queryset(self):
        return Property.objects.filter(user=self.request.user)

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
    - GET: create form / download
    - POST: create or update property
    - DELETE: delete a property
    """
    def get_object(self, pk):
        return get_object_or_404(Property, pk=pk)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        action = kwargs.get("action")

        if pk and action == "download":
            return handle_document_download(request, self.get_object(pk))
        
        if not pk:
            return render_property_template(request, "new.html", form=PropertyForm())
        
        return HttpResponseForbidden("Invalid request")

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.POST.get("_method") == "DELETE":
            return self.delete(request, *args, **kwargs)

        pk = kwargs.get("pk")
        if pk:
            prop = self.get_object(pk)
            if prop.user != request.user:
                return HttpResponseForbidden("Not allowed")
            form = PropertyForm(request.POST, request.FILES, instance=prop)
        else:
            form = PropertyForm(request.POST, request.FILES)

        if form.is_valid():
            form.instance.user = request.user
            prop = form.save()
            handle_document_removal(request, prop, form)
            handle_image_deletion(request, prop)
            handle_image_upload(request, prop)
            messages.success(request, f"Property {'updated' if pk else 'created'} successfully.")
            return redirect("properties:detail", pk=prop.pk)
        
        messages.error(request, "Please correct the form errors.")
        return render_property_template(
            request,
            "edit.html" if pk else "new.html",
            form=form
        )

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        prop = self.get_object(kwargs.get("pk"))
        if prop.user != request.user:
            return HttpResponseForbidden("Not allowed")
        
        for img in prop.images.all():
            img.image.delete(save=False)
            img.delete()
        
        if prop.documents:
            prop.documents.delete(save=False)
        
        prop.delete()
        messages.success(request, "Property deleted successfully.")
        return redirect("properties:list")