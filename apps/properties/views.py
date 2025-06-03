"""
This module contains class-based views for property-related operations such as
listing properties, viewing property details, creating new properties, editing existing properties,
and deleting properties within the Property Hub application.
"""

from .models import Property, Favorite
from django.views import View
from .forms import PropertyForm
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import HttpResponseNotAllowed
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404

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
                Favorite.objects
                .filter(user=self.request.user)
                .values_list('property_id', flat=True)
            )
            # Annotate each Property instance with an `is_favorited` boolean
            for prop in qs:
                prop.is_favorited = (prop.id in favorited_ids)
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
            context['is_favorited'] = self.object.favorited_by.filter(user=self.request.user).exists()
        return context

class NewPropertyView(LoginRequiredMixin, CreateView):
    """View for creating a new property."""
    model = Property
    form_class = PropertyForm
    template_name = "properties/new.html"

    def get_success_url(self):
        return reverse_lazy("properties:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EditPropertyView(LoginRequiredMixin, UpdateView):
    """View for editing an existing property."""
    model = Property
    form_class = PropertyForm
    template_name = "properties/edit.html"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("properties:detail", kwargs={"pk": self.object.pk})

class DeletePropertyView(LoginRequiredMixin, DeleteView):
    """View for deleting a property."""
    model = Property    

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])

    def get_success_url(self):
        return reverse_lazy("properties:list")

class ToggleFavoriteView(LoginRequiredMixin, View):
    """Toggle a property’s favorite status on any HTTP method."""
    def dispatch(self, request, *args, **kwargs):
        prop = get_object_or_404(Property, id=kwargs['pk'])
        fav, created = Favorite.objects.get_or_create(user=request.user, property=prop)
        if not created:
            fav.delete()
        return redirect(request.META.get('HTTP_REFERER', 'properties:list'))

class FavoritesListView(LoginRequiredMixin, ListView):
    """View for listing all favorite properties."""
    model = Property
    template_name = "properties/favorites.html"
    context_object_name = "properties"

    def get_queryset(self):
        # Get properties that have been favorited by the current user
        favorites = Favorite.objects.filter(user=self.request.user).select_related('property')
        return [favorite.property for favorite in favorites]
