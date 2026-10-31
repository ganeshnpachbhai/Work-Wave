from django.urls import path
from .views import download_application_resume

urlpatterns = [
    path(
        "<int:application_id>/resume/",
        download_application_resume,
        name="download_application_resume",
    ),
]
