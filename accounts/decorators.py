from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(role):
    """
    Ensures that only authenticated users with the matching profile role can access the view.
    Staff or superusers attempting to access role-specific endpoints are denied (HTTP 403).
    Users without the required role are denied (HTTP 403).
    """
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user

            if user.is_superuser or user.is_staff:
                raise PermissionDenied("Staff and superusers cannot access standard portal dashboards.")

            if not hasattr(user, "profile"):
                raise PermissionDenied("Account profile not initialized.")

            if user.profile.role != role:
                raise PermissionDenied(f"Access denied. '{role}' role required.")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def superuser_required(view_func):
    """
    Strict superuser access control.
    Unauthenticated users are redirected to LOGIN_URL (HTTP 302).
    Authenticated non-superusers (including seekers and employers) receive HTTP 403 PermissionDenied.
    """
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("Superuser privileges required to access this resource.")
        return view_func(request, *args, **kwargs)
    return wrapper


seeker_required = role_required("seeker")
employer_required = role_required("employer")
