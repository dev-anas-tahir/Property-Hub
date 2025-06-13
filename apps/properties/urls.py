"""
This module contains URL patterns for property-related operations.
"""

from django.urls import path
from apps.properties.views import PropertyView, PropertiesListView, FavoritesListView, ToggleFavoriteView, EditPropertyView
# from apps.properties.views import (
#     PropertyView,
#     PropertiesListView,
#     PropertyDetailView,
#     NewPropertyView,
#     EditPropertyView,
#     DeletePropertyView,
#     ToggleFavoriteView,
#     FavoritesListView,
#     PropertyDocumentDownloadView,
# )

app_name = "properties"

# urlpatterns = [
#     path("", PropertiesListView.as_view(), name="list"),
#     path("new/", NewPropertyView.as_view(), name="new"),
#     path("<int:pk>/", PropertyDetailView.as_view(), name="detail"),
#     path(
#         "<int:pk>/download/",
#         PropertyDocumentDownloadView.as_view(),
#         name="download_document",
#     ),
#     path("<int:pk>/edit/", EditPropertyView.as_view(), name="edit"),
#     path("<int:pk>/delete/", DeletePropertyView.as_view(), name="delete"),
#     path("favorites/", FavoritesListView.as_view(), name="favorites"),
#     path(
#         "<int:pk>/toggle_favorite/",
#         ToggleFavoriteView.as_view(),
#         name="toggle_favorite",
#     ),
# ]

urlpatterns = [
    path("", PropertiesListView.as_view(), name="list"),
    path("favorites/", FavoritesListView.as_view(), name="favorites"),
    path("<int:pk>/toggle_favorite/", ToggleFavoriteView.as_view(), name="toggle_favorite"),

    # Unified view handling the following:
    path("new/", PropertyView.as_view(), name="new"),                          # GET (form), POST (create)
    path("<int:pk>/", PropertyView.as_view(), name="detail"),                  # GET (detail), POST (update)
    path("<int:pk>/edit/", EditPropertyView.as_view(), name="edit"),           # POST with pk = update fallback route
    path("<int:pk>/delete/", PropertyView.as_view(), name="delete"),           # DELETE
    path("<int:pk>/download/", PropertyView.as_view(), {"action": "download"}, name="download_document"),
]