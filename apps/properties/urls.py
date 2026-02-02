from django.urls import path

from apps.properties.views import (
    favorites_list_view,
    my_properties_list_view,
    properties_list_view,
    property_create_view,
    property_delete_view,
    property_detail_view,
    property_download_document_view,
    property_edit_view,
    property_favorite_toggle_view,
    property_validate_step_view,
    validate_cnic_view,
    validate_phone_view,
)

app_name = "properties"

urlpatterns = [
    path("create/", property_create_view, name="create"),
    path("", properties_list_view, name="list"),
    path("<int:pk>/", property_detail_view, name="detail"),
    path("<int:pk>/edit/", property_edit_view, name="edit"),
    path(
        "<int:pk>/download/", property_download_document_view, name="download_document"
    ),
    path("<int:pk>/favorite/", property_favorite_toggle_view, name="favorite_toggle"),
    path("<int:pk>/delete/", property_delete_view, name="delete"),
    path("myprops/", my_properties_list_view, name="myprops"),
    path("favorites/", favorites_list_view, name="favorites"),
    # Validation endpoints
    path("validate/step/", property_validate_step_view, name="validate_step"),
    path("validate/phone/", validate_phone_view, name="validate_phone"),
    path("validate/cnic/", validate_cnic_view, name="validate_cnic"),
]
