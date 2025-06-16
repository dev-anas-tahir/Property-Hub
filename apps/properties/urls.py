"""
This module contains URL patterns for property-related operations.
"""

from django.urls import path
from apps.properties.views import PropertyView, PropertyDetailView, PropertiesListView, FavoritesListView, ToggleFavoriteView, EditPropertyView, MyPropertiesListView

app_name = "properties"

urlpatterns = [
    path("new/", PropertyView.as_view(), name="new"),
    path("", PropertiesListView.as_view(), name="list"),
    path("<int:pk>/", PropertyDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", EditPropertyView.as_view(), name="edit"),
    path("<int:pk>/download/", PropertyView.as_view(), {"action": "download"}, name="download_document"),
    path("myprops/", MyPropertiesListView.as_view(), name="myprops"),
    path("favorites/", FavoritesListView.as_view(), name="favorites"),
    path("<int:pk>/toggle_favorite/", ToggleFavoriteView.as_view(), name="toggle_favorite"),
]