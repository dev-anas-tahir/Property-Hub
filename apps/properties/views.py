"""
This module contains class-based views for property-related operations such as
listing properties, viewing property details, creating new properties, editing existing properties,
and deleting properties within the Property Hub application.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.contrib import messages
from apps.properties.mixins import (
    DeletePropertyMixin,
    PropertyAccessMixin,
    PropertyFormHandlerMixin,
)
from apps.properties.models import Property, Favorite
from apps.properties.forms import PropertyForm
from apps.properties.utils import (
    get_properties_with_favorites,
    handle_document_download,
    render_property_template,
)


class PropertiesListView(ListView):
    model = Property
    template_name = "properties/list.html"
    context_object_name = "properties"
    paginate_by = 9

    def get_queryset(self):
        return get_properties_with_favorites(self.request.user)


class PropertyDetailView(DetailView, DeletePropertyMixin):
    model = Property
    template_name = "properties/detail.html"
    context_object_name = "property"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return render_property_template(
            request, "detail.html", property_obj=self.object
        )


class EditPropertyView(
    LoginRequiredMixin, PropertyAccessMixin, PropertyFormHandlerMixin, UpdateView
):
    model = Property
    form_class = PropertyForm
    template_name = "properties/edit.html"

    def get_success_url(self):
        return reverse_lazy("properties:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = self.process_property_form(self.request, form, instance=self.object)
        if response:
            return response
        return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the form errors.")
        return render_property_template(
            self.request, "edit.html", property_obj=self.object, form=form
        )


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        prop = get_object_or_404(Property, id=kwargs["pk"])
        fav, created = Favorite.objects.get_or_create(user=request.user, property=prop)
        if not created:
            fav.delete()
            messages.success(
                request, f"Property {prop.name} removed from your favorites."
            )
        else:
            messages.success(request, f"Property {prop.name} added to your favorites.")
        return redirect(
            request.META.get("HTTP_REFERER", reverse_lazy("properties:list"))
        )


class MyPropertiesListView(LoginRequiredMixin, ListView):
    model = Property
    template_name = "properties/myprops.html"
    context_object_name = "properties"
    paginate_by = 9

    def get_queryset(self):
        return Property.objects.filter(user=self.request.user)


class FavoritesListView(LoginRequiredMixin, ListView):
    model = Property
    template_name = "properties/favorites.html"
    context_object_name = "properties"
    paginate_by = 9

    def get_queryset(self):
        return (
            Property.objects.filter(favorited_by__user=self.request.user)
            .select_related("user")
            .prefetch_related("images")
            .distinct()
        )


class PropertyView(LoginRequiredMixin, PropertyFormHandlerMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        action = kwargs.get("action")

        if pk and action == "download":
            return handle_document_download(request, self.get_object(pk))

        if not pk:
            return render_property_template(request, "create.html", form=PropertyForm())

        raise PermissionDenied("Invalid request")

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        form = PropertyForm(
            request.POST, request.FILES, instance=self.get_object(pk) if pk else None
        )

        response = self.process_property_form(
            request, form, instance=self.get_object(pk) if pk else None
        )
        if response:
            return response

        messages.error(request, "Please correct the form errors.")

        return render_property_template(
            request, "edit.html" if pk else "create.html", form=form
        )
