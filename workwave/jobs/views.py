from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import employer_required, seeker_required
from employer.models import EmployerProfile
from seeker.models import SeekerProfile
from .models import Job
from .forms import JobForm
from applications.models import Application
from applications.forms import ApplicationForm

# Create your views here.


def home(request):
    jobs = Job.objects.filter(is_active=True).select_related("employer")[:6]
    return render(request, "home.html", {"jobs": jobs})


def job_list(request):
    jobs = Job.objects.filter(is_active=True).select_related("employer")

    query = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()
    job_type = request.GET.get("job_type", "").strip()

    if query:
        jobs = jobs.filter(title__icontains=query)

    if location:
        jobs = jobs.filter(location__icontains=location)

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    context = {
        "jobs": jobs,
        "query": query,
        "location": location,
        "job_type": job_type,
        "job_types": Job.JOB_TYPE,
    }

    return render(request, "jobs/list.html", context)


def job_detail(request, job_id):
    job = get_object_or_404(
        Job.objects.select_related("employer"),
        pk=job_id,
        is_active=True,
    )

    already_applied = False
    if (request.user.is_authenticated and hasattr(request.user, "profile") and request.user.profile.role == "seeker"):
        already_applied = Application.objects.filter(
            job=job,
            seeker__user=request.user,
        ).exists()

    context = {
        "job": job,
        "already_applied": already_applied,
    }
    return render(request, "jobs/detail.html", context)


@employer_required
def create_job(request):
    if request.method == "POST":
        form = JobForm(request.POST)

        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user.employer_profile
            job.save()

            messages.success(request, "Job posted successfully!")
            return redirect("employer_dashboard")
    else:
        form = JobForm()

    context = {
        "form": form,
        "page_title": "Post a Job"
    }
    return render(request, "jobs/form.html", context)


@employer_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if job.employer != request.user.employer_profile:
        raise PermissionDenied("You do not have permission to edit this job.")

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)

        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect("employer_dashboard")
    else:
        form = JobForm(instance=job)

    context = {
        "form": form,
        "page_title": "Edit Job",
    }
    return render(request, "jobs/form.html", context)


@employer_required
def close_job(request, job_id):
    if request.method == "POST":
        job = get_object_or_404(Job, pk=job_id)
        if job.employer != request.user.employer_profile:
            raise PermissionDenied("You do not have permission to close this job.")

        job.is_active = False
        job.save(update_fields=['is_active'])
        messages.success(request, "Job closed successfully!")

    return redirect("employer_dashboard")


@seeker_required
def apply_job(request, job_id):
    job = get_object_or_404(
        Job,
        pk=job_id,
        is_active=True
    )
    seeker = request.user.seeker_profile

    if Application.objects.filter(job=job, seeker=seeker).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect("job_detail", job_id=job.id)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():
                    application = form.save(commit=False)
                    application.job = job
                    application.seeker = seeker

                    if not application.resume and seeker.resume:
                        application.resume = seeker.resume

                    application.save()
                messages.success(
                    request, "Application submitted successfully!")
                return redirect("job_detail", job_id=job.id)
            except IntegrityError:
                messages.info(
                    request, "You have already applied for this job.")
                return redirect("seeker_dashboard")
    else:
        form = ApplicationForm()

    context = {
        "form": form,
        "job": job,
    }
    return render(request, "applications/apply.html", context)
