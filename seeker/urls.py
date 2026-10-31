from django.urls import path
from .views import (
    seeker_dashboard,
    edit_profile,
    download_profile_resume,
)

urlpatterns = [
    path("", seeker_dashboard, name="seeker_dashboard"),
    path("profile/", edit_profile, name="edit_profile"),
    path("resume/", download_profile_resume, name="download_profile_resume"),
]
