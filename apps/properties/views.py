from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Property
from .forms import PropertyForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from typing import override

# Create your views here.

class PropertiesListView(ListView):
    model = Property
    template_name = "properties/list.html"
    context_object_name = "properties"
    allow_empty = True

class PropertyDetailView(DetailView):
    model = Property
    template_name = "properties/detail.html"
    context_object_name = "property"

class NewPropertyView(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = "properties/new.html"

    def get_success_url(self):
        return reverse_lazy("properties:list")

    @override
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EditPropertyView(LoginRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = "properties/edit.html"

    @override
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    @override
    def get_success_url(self):
        return reverse_lazy("properties:detail", kwargs={"pk": self.object.pk})