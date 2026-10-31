import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect

from accounts.decorators import seeker_required
from .models import SeekerProfile, Skill
from applications.models import Application
from workwave.validators import validate_resume_file, validate_profile_photo


@seeker_required
def seeker_dashboard(request):
    profile = request.user.seeker_profile

    applications = Application.objects.filter(
        seeker=profile
    ).select_related("job", "job__employer")
    context = {
        "profile": profile,
        "applications": applications,
    }

    return render(request, "seeker/dashboard.html", context)


@seeker_required
def edit_profile(request):
    profile = request.user.seeker_profile

    if request.method == "POST":
        profile.full_name = request.POST.get("full_name", "").strip()
        profile.phone = request.POST.get("phone", "").strip()
        profile.location = request.POST.get("location", "").strip()
        profile.headline = request.POST.get("headline", "").strip()
        profile.bio = request.POST.get("bio", "").strip()
        profile.education = request.POST.get("education", "").strip()

        skills_raw = request.POST.get("skills", "").strip()
        skill_names = [s.strip().title() for s in skills_raw.split(",") if s.strip()]
        skills = []
        for name in skill_names:
            skill, _ = Skill.objects.get_or_create(name=name)
            skills.append(skill)
        profile.skills.set(skills)

        uploaded_profile_photo = request.FILES.get("profile_photo")
        if uploaded_profile_photo:
            try:
                validate_profile_photo(uploaded_profile_photo)
                profile.profile_photo = uploaded_profile_photo
            except ValidationError as err:
                messages.error(request, err.message)
                return redirect("edit_profile")

        uploaded_resume = request.FILES.get("resume")
        if uploaded_resume:
            try:
                validate_resume_file(uploaded_resume)
                profile.resume = uploaded_resume
            except ValidationError as err:
                messages.error(request, err.message)
                return redirect("edit_profile")

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("seeker_dashboard")

    skills_text = ", ".join(profile.skills.values_list("name", flat=True))
    return render(request, "seeker/profile.html", {
        "profile": profile,
        "skills_text": skills_text,
    })


@login_required
def download_profile_resume(request):
    """
    Secure authenticated endpoint for candidate profile resume access.
    Guards confidential PII: Only the profile owner or superusers can access.
    """
    user = request.user

    if user.is_superuser:
        profile = SeekerProfile.objects.filter(resume__isnull=False).exclude(resume="").first()
        if not profile:
            raise Http404("No profile resumes found on system.")
    elif hasattr(user, "seeker_profile"):
        profile = user.seeker_profile
    else:
        raise PermissionDenied("Only job seekers are authorized to access their profile resume.")

    if not profile.resume:
        raise Http404("No resume uploaded to this profile.")

    try:
        response = FileResponse(profile.resume.open("rb"), content_type="application/octet-stream")
        filename = os.path.basename(profile.resume.name)
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
    except (FileNotFoundError, ValueError):
        raise Http404("Resume file could not be found.")
