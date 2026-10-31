from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import UserProfile
from accounts.security_tests import WorkWaveSecurityTests
from employer.models import EmployerProfile
from seeker.models import SeekerProfile


class LogoutCsrfTests(TestCase):
    def test_logout_accepts_a_fresh_csrf_token(self):
        user = get_user_model().objects.create_user(
            username="logout-test",
            password="test-password",
        )
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)

        client.get("/")
        token_response = client.get(reverse("csrf_token"))
        self.assertEqual(token_response.status_code, 200)

        response = client.post(
            reverse("logout"),
            {"csrfmiddlewaretoken": token_response.json()["csrfToken"]},
        )

        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", client.session)


class AccountAuthAndDashboardTests(TestCase):
    def test_signup_get_renders_form(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create your account")

    def test_signup_post_invalid_retains_errors(self):
        # Employer without company name should fail validation and show error
        response = self.client.post(reverse("signup"), {
            "username": "employer1",
            "email": "emp@test.com",
            "role": "employer",
            "company_name": "",
            "password1": "Password123!",
            "password2": "Password123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Company name is required for employers.")

    def test_signup_post_valid_seeker(self):
        response = self.client.post(reverse("signup"), {
            "username": "seeker1",
            "email": "seeker@test.com",
            "role": "seeker",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertRedirects(response, reverse("dashboard"), target_status_code=302)
        user = get_user_model().objects.get(username="seeker1")
        self.assertEqual(user.profile.role, "seeker")
        self.assertTrue(SeekerProfile.objects.filter(user=user).exists())

    def test_signup_post_valid_employer(self):
        response = self.client.post(reverse("signup"), {
            "username": "emp1",
            "email": "emp@test.com",
            "role": "employer",
            "company_name": "Acme Corp",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertRedirects(response, reverse("dashboard"), target_status_code=302)
        user = get_user_model().objects.get(username="emp1")
        self.assertEqual(user.profile.role, "employer")
        self.assertEqual(user.employer_profile.company_name, "Acme Corp")

    def test_dashboard_redirects_seeker(self):
        user = get_user_model().objects.create_user(username="s1", password="pw")
        UserProfile.objects.create(user=user, role="seeker")
        SeekerProfile.objects.create(user=user)
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("seeker_dashboard"))

    def test_dashboard_redirects_employer(self):
        user = get_user_model().objects.create_user(username="e1", password="pw")
        UserProfile.objects.create(user=user, role="employer")
        EmployerProfile.objects.create(user=user, company_name="Test")
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("employer_dashboard"))
