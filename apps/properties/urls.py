from django.urls import path

from apps.properties.views import (
    FavoritesListView,
    MyPropertiesListView,
    PropertyCreateView,
    PropertyDeleteView,
    PropertyDetailView,
    PropertyDownloadDocumentView,
    PropertyEditView,
    PropertyFavoriteToggleView,
    PropertyListView,
    PropertyValidateStepView,
    ValidateCNICView,
    ValidatePhoneView,
)

app_name = "properties"

urlpatterns = [
    path("create/", PropertyCreateView.as_view(), name="create"),
    path("", PropertyListView.as_view(), name="list"),
    path("<int:pk>/", PropertyDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", PropertyEditView.as_view(), name="edit"),
    path(
        "<int:pk>/download/",
        PropertyDownloadDocumentView.as_view(),
        name="download_document",
    ),
    path(
        "<int:pk>/favorite/",
        PropertyFavoriteToggleView.as_view(),
        name="favorite_toggle",
    ),
    path("<int:pk>/delete/", PropertyDeleteView.as_view(), name="delete"),
    path("myprops/", MyPropertiesListView.as_view(), name="myprops"),
    path("favorites/", FavoritesListView.as_view(), name="favorites"),
    # Validation endpoints
    path("validate/step/", PropertyValidateStepView.as_view(), name="validate_step"),
    path("validate/phone/", ValidatePhoneView.as_view(), name="validate_phone"),
    path("validate/cnic/", ValidateCNICView.as_view(), name="validate_cnic"),
]
