import os
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from .models import Application


@login_required
def download_application_resume(request, application_id):
    """
    Secure endpoint for downloading candidate application resumes.
    Enforces strict access control and ownership verification:
    - Permitted: The applicant who submitted the resume.
    - Permitted: The employer who posted the job receiving the application.
    - Permitted: An authorized platform superuser.
    - Denied: Any other user (unrelated seekers, competing employers) receives HTTP 403 PermissionDenied.
    """
    application = get_object_or_404(
        Application.objects.select_related("seeker__user", "job__employer__user"),
        pk=application_id,
    )
    user = request.user

    is_applicant = (application.seeker.user_id == user.id)
    is_job_employer = (application.job.employer.user_id == user.id)
    is_admin = user.is_superuser

    if not (is_applicant or is_job_employer or is_admin):
        raise PermissionDenied("You do not have permission to view or download this candidate's resume.")

    file_to_serve = application.resume or application.seeker.resume
    if not file_to_serve:
        raise Http404("No resume attached to this application.")

    try:
        response = FileResponse(file_to_serve.open("rb"), content_type="application/octet-stream")
        filename = os.path.basename(file_to_serve.name)
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
    except (FileNotFoundError, ValueError):
        raise Http404("Resume file could not be found on storage.")
