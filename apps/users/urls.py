from django.urls import path
from apps.users.views import SignUpView, CustomLoginView, UpdateProfileView, CustomLogoutView 

app_name = "users"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("profile/", UpdateProfileView.as_view(), name="profile"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
]