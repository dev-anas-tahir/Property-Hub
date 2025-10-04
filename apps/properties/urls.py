from django.urls import path
from apps.properties.views import (
    property_detail_view,
    properties_list_view,
    favorites_list_view,
    my_properties_list_view,
    property_create_view,
    property_edit_view,
    property_download_document_view,
)

app_name = "properties"

urlpatterns = [
    path("create/", property_create_view, name="create"),
    path("", properties_list_view, name="list"),
    path("<int:pk>/", property_detail_view, name="detail"),
    path("<int:pk>/edit/", property_edit_view, name="edit"),
    path("<int:pk>/download/", property_download_document_view, name="download_document"),
    path("myprops/", my_properties_list_view, name="myprops"),
    path("favorites/", favorites_list_view, name="favorites"),
]