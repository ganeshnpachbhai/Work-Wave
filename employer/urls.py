from django.urls import path
from .views import (
    employer_dashboard,
    applicants,
    update_application_status,
)

urlpatterns = [
    path("",employer_dashboard,name="employer_dashboard"),
    path("job/<int:job_id>/applicants/", applicants, name="applicants"),
    path(
        "application/<int:application_id>/status/",
        update_application_status,
        name="update_application_status",
    ),
]
