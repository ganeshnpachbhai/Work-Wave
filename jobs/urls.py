from django.urls import path
from .views import (
    home,
    job_detail,
    job_list,
    close_job,
    edit_job,
    create_job,
    apply_job,
)

urlpatterns = [
    path("", home, name="home"),
    path("jobs/", job_list, name="job_list"),
    path("jobs/<int:job_id>/", job_detail, name="job_detail"),
    path("jobs/<int:job_id>/edit/", edit_job, name="edit_job"),
    path("jobs/create/", create_job, name="create_job"),
    path("jobs/<int:job_id>/close/", close_job, name="close_job"),
    path("jobs/<int:job_id>/apply/", apply_job, name="apply_job"),
]
