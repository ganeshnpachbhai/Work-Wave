from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from .forms import SignUpForm, SecureAuthenticationForm
from .models import UserProfile
from .decorators import superuser_required
from .rate_limit import (
    is_locked_out,
    record_failed_attempt,
    clear_failed_attempts,
)
from seeker.models import SeekerProfile
from employer.models import EmployerProfile
from jobs.models import Job
from applications.models import Application


def signup(request):
    """
    Public registration endpoint.
    Strictly isolated to 'seeker' or 'employer' accounts.
    Privilege escalation to staff or superuser is strictly prohibited.
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()

                UserProfile.objects.create(
                    user=user,
                    role=form.cleaned_data["role"],
                )

                if form.cleaned_data["role"] == "seeker":
                    SeekerProfile.objects.create(user=user)
                else:
                    EmployerProfile.objects.create(
                        user=user,
                        company_name=form.cleaned_data["company_name"],
                    )

                login(request, user)
                messages.success(request, "Account created successfully!")
                return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


class PortalLoginView(LoginView):
    """
    Hardened login view with:
    1. Uniform error messaging (anti-enumeration).
    2. IP and username brute-force rate limiting.
    3. Temporary lockout protection against automated credential stuffing.
    """
    template_name = "accounts/login.html"
    form_class = SecureAuthenticationForm
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            username = request.POST.get("username", "").strip()
            locked, remaining = is_locked_out(request, username)
            if locked:
                form = self.get_form()
                form.add_error(
                    None,
                    f"Too many failed login attempts. Account temporarily locked for security. "
                    f"Please try again in {max(1, remaining // 60)} minute(s).",
                )
                return self.render_to_response(
                    self.get_context_data(form=form),
                    status=429,
                )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Clear rate-limiting records on successful login
        username = form.get_user().username
        clear_failed_attempts(self.request, username)
        return super().form_valid(form)

    def form_invalid(self, form):
        # Record failed authentication attempt
        username = self.request.POST.get("username", "").strip()
        locked, remaining = record_failed_attempt(self.request, username)
        if locked:
            form.add_error(
                None,
                f"Too many failed login attempts. Account temporarily locked for security. "
                f"Please try again in {max(1, remaining // 60)} minute(s).",
            )
            return self.render_to_response(
                self.get_context_data(form=form),
                status=429,
            )
        return super().form_invalid(form)


@login_required
@require_GET
@never_cache
def csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})


@login_required
def dashboard(request):
    """
    Central routing hub after authentication.
    Superusers -> custom admin dashboard
    Staff -> Django Admin
    Seekers -> seeker_dashboard
    Employers -> employer_dashboard
    """
    user = request.user

    if user.is_superuser:
        return redirect("admin_dashboard")

    if user.is_staff:
        return redirect("/admin/")

    if not hasattr(user, "profile"):
        messages.error(request, "Your account profile is missing.")
        return redirect("home")

    if user.profile.role == "seeker":
        return redirect("seeker_dashboard")

    if user.profile.role == "employer":
        return redirect("employer_dashboard")

    return redirect("home")


@superuser_required
def admin_dashboard(request):
    """
    Custom administrative monitoring dashboard.
    Strictly protected: only users with is_superuser=True are authorized.
    Regular users, employers, and seekers will receive HTTP 403 Forbidden.
    """
    total_users = User.objects.count()
    total_seekers = SeekerProfile.objects.count()
    total_employers = EmployerProfile.objects.count()
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    total_applications = Application.objects.count()

    recent_users = User.objects.select_related("profile").order_by("-date_joined")[:8]
    recent_jobs = Job.objects.select_related("employer").order_by("-posted_at")[:6]

    context = {
        "total_users": total_users,
        "total_seekers": total_seekers,
        "total_employers": total_employers,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applications": total_applications,
        "recent_users": recent_users,
        "recent_jobs": recent_jobs,
    }
    return render(request, "accounts/admin_dashboard.html", context)
