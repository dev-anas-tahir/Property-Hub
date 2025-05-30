"""
This module contains class-based views for property-related operations such as
listing properties, viewing property details, creating new properties, editing existing properties,
and deleting properties within the Property Hub application.
"""

from .models import Property
from .forms import PropertyForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseNotAllowed

class PropertiesListView(ListView):
    """View for listing all properties."""
    model = Property
    template_name = "properties/list.html"
    context_object_name = "properties"

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)
    

class PropertyDetailView(DetailView):
    """View for viewing a specific property."""
    model = Property
    template_name = "properties/detail.html"
    context_object_name = "property"

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
