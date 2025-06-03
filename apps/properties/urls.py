from django.urls import path
from .views import PropertiesListView, PropertyDetailView, NewPropertyView, EditPropertyView, DeletePropertyView, ToggleFavoriteView, FavoritesListView

app_name = "properties"

urlpatterns = [
    path("", PropertiesListView.as_view(), name="list"),
    path("new/", NewPropertyView.as_view(), name="new"),
    path("<int:pk>/", PropertyDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", EditPropertyView.as_view(), name="edit"),
    path("<int:pk>/delete/", DeletePropertyView.as_view(), name="delete"),
    path("favorites/", FavoritesListView.as_view(), name="favorites"),
    path("<int:pk>/toggle_favorite/", ToggleFavoriteView.as_view(), name="toggle_favorite"),
]
