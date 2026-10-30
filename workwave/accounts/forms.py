from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _


class SecureAuthenticationForm(AuthenticationForm):
    """
    Hardened authentication form that prevents username enumeration.
    Always produces identical, uniform error messaging whether username or password is invalid.
    """
    error_messages = {
        "invalid_login": _(
            "Invalid username or password. Please verify your credentials and try again."
        ),
        "inactive": _("This account is currently inactive. Please contact support."),
    }


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[
            ("seeker", "Job Seeker"),
            ("employer", "Employer"),
        ],
        widget=forms.RadioSelect,
    )

    company_name = forms.CharField(
        max_length=150,
        required=False,
        label="Company Name",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "role",
            "company_name",
            "password1",
            "password2",
        ]

    def clean(self):
        cleaned_data = super().clean()
        role = self.cleaned_data.get("role")
        company_name = self.cleaned_data.get("company_name")

        if role not in ["seeker", "employer"]:
            self.add_error("role", "Invalid role selected.")

        if role == "employer" and not company_name:
            self.add_error(
                "company_name",
                "Company name is required for employers.",
            )
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        # STRICT PRIVILEGE ESCALATION PREVENTION:
        # Public signups can NEVER be granted staff or superuser privileges.
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()
        return user
