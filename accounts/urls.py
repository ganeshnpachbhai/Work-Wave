from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    signup,
    dashboard,
    PortalLoginView,
    csrf_token,
    admin_dashboard,
)

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", PortalLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("csrf-token/", csrf_token, name="csrf_token"),
    path("dashboard/", dashboard, name="dashboard"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
]
