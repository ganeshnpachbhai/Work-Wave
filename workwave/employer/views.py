from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import employer_required
from jobs.models import Job
from applications.models import Application


@employer_required
def employer_dashboard(request):
    employer = request.user.employer_profile

    jobs = Job.objects.filter(employer=employer)
    context = {
        "employer": employer,
        "jobs": jobs,
        "job_count": jobs.count()
    }

    return render(request, "employer/dashboard.html", context)


@employer_required
def applicants(request, job_id):
    """
    Renders applicants for a job.
    Strictly verifies ownership:
    If the job belongs to another employer, raises PermissionDenied (HTTP 403).
    """
    job = get_object_or_404(Job, pk=job_id)
    if job.employer != request.user.employer_profile:
        raise PermissionDenied("You do not have permission to view applicants for this job.")

    applications = Application.objects.filter(
        job=job
    ).select_related("seeker", "seeker__user")
    context = {
        "job": job,
        "applications": applications,
        "status_choices": Application.STATUS_CHOICE,
    }

    return render(request, "employer/applicants.html", context)


@employer_required
def update_application_status(request, application_id):
    """
    Updates the status of an application.
    Strictly verifies ownership:
    If the application's job belongs to another employer, raises PermissionDenied (HTTP 403).
    """
    if request.method != "POST":
        return redirect("employer_dashboard")
    
    application = get_object_or_404(Application, pk=application_id)
    if application.job.employer != request.user.employer_profile:
        raise PermissionDenied("You do not have permission to modify this application.")

    allowed_statuses = {
        "pending",
        "shortlisted",
        "rejected",
        "accepted",
    }

    new_status = request.POST.get("status")

    if new_status in allowed_statuses:
        application.status = new_status
        application.save(update_fields=["status"])
        messages.success(request, "Application status updated.")

    return redirect("applicants", job_id=application.job_id)
