from django.urls import path
from .views import PropertiesListView, PropertyDetailView, NewPropertyView, EditPropertyView

app_name = "properties"

urlpatterns = [
    path("", PropertiesListView.as_view(), name="list"),
    path("new", NewPropertyView.as_view(), name="new"),
    path("<int:pk>", PropertyDetailView.as_view(), name="detail"),
    path("<int:pk>/edit", EditPropertyView.as_view(), name="edit"),
]
