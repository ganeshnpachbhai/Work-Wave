"""
WorkWave Security Verification Suite.
Automated tests covering all 12 mandatory security scenarios:
1. Invalid superuser login rejection.
2. Valid seeker login and role dispatch.
3. Valid employer login and role dispatch.
4. Seeker accessing superuser/admin view -> 403 Forbidden.
5. Employer accessing superuser/admin view -> 403 Forbidden.
6. Seeker editing another user's profile blocked (ownership isolation).
7. Employer editing another employer's job -> 403 Forbidden (IDOR defense).
8. Employer viewing another employer's applicants -> 403 Forbidden (IDOR defense).
9. Unauthenticated user accessing protected page -> 302 Redirect to login.
10. Repeated failed login attempts triggering brute-force lockout (429).
11. Unauthorized resume download -> 403 Forbidden (PII protection).
12. Public signup attempting privilege escalation (is_staff/is_superuser) -> neutralized.
"""

from io import BytesIO
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from accounts.rate_limit import clear_failed_attempts
from applications.models import Application
from employer.models import EmployerProfile
from jobs.models import Job
from seeker.models import SeekerProfile


class WorkWaveSecurityTests(TestCase):
    def setUp(self):
        cache.clear()
        self.User = get_user_model()

        # Superuser account
        self.superuser = self.User.objects.create_superuser(
            username="security_admin",
            email="admin@workwave.test",
            password="SuperSecretAdminPass123!",
        )

        # Seeker 1 account
        self.seeker1_user = self.User.objects.create_user(
            username="seeker_alpha",
            email="seeker1@workwave.test",
            password="SeekerPass123!",
        )
        UserProfile.objects.create(user=self.seeker1_user, role="seeker")
        self.seeker1_profile = SeekerProfile.objects.create(
            user=self.seeker1_user,
            full_name="Alpha Seeker",
            phone="+1234567890",
        )

        # Seeker 2 account
        self.seeker2_user = self.User.objects.create_user(
            username="seeker_beta",
            email="seeker2@workwave.test",
            password="SeekerPass123!",
        )
        UserProfile.objects.create(user=self.seeker2_user, role="seeker")
        self.seeker2_profile = SeekerProfile.objects.create(
            user=self.seeker2_user,
            full_name="Beta Seeker",
            phone="+9876543210",
        )

        # Employer 1 account
        self.employer1_user = self.User.objects.create_user(
            username="employer_one",
            email="emp1@workwave.test",
            password="EmployerPass123!",
        )
        UserProfile.objects.create(user=self.employer1_user, role="employer")
        self.employer1_profile = EmployerProfile.objects.create(
            user=self.employer1_user,
            company_name="Apex Corp",
        )

        # Employer 2 account
        self.employer2_user = self.User.objects.create_user(
            username="employer_two",
            email="emp2@workwave.test",
            password="EmployerPass123!",
        )
        UserProfile.objects.create(user=self.employer2_user, role="employer")
        self.employer2_profile = EmployerProfile.objects.create(
            user=self.employer2_user,
            company_name="Vanguard Industries",
        )

        # Job owned by Employer 1
        self.job1 = Job.objects.create(
            employer=self.employer1_profile,
            title="Senior Security Architect",
            description="Protect high-scale distributed systems.",
            location="Remote",
            job_type="full_time",
        )

        # Application submitted by Seeker 1 to Job 1 with a mock resume
        dummy_resume = SimpleUploadedFile(
            "resume.pdf",
            b"%PDF-1.4 Mock resume content for security audit testing",
            content_type="application/pdf",
        )
        self.application1 = Application.objects.create(
            seeker=self.seeker1_profile,
            job=self.job1,
            resume=dummy_resume,
            status="pending",
        )

    def tearDown(self):
        cache.clear()

    # --------------------------------------------------------------------------
    # Scenario 1: Invalid superuser login rejection
    # --------------------------------------------------------------------------
    def test_01_invalid_superuser_login_rejection(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "security_admin",
                "password": "WrongAdminPassword123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")
        self.assertNotIn("_auth_user_id", self.client.session)

    # --------------------------------------------------------------------------
    # Scenario 2: Valid seeker login
    # --------------------------------------------------------------------------
    def test_02_valid_seeker_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "seeker_alpha",
                "password": "SeekerPass123!",
            },
        )
        self.assertRedirects(response, reverse("dashboard"), target_status_code=302)
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.seeker1_user.id,
        )
        dash_response = self.client.get(reverse("dashboard"))
        self.assertRedirects(dash_response, reverse("seeker_dashboard"))

    # --------------------------------------------------------------------------
    # Scenario 3: Valid employer login
    # --------------------------------------------------------------------------
    def test_03_valid_employer_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "employer_one",
                "password": "EmployerPass123!",
            },
        )
        self.assertRedirects(response, reverse("dashboard"), target_status_code=302)
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.employer1_user.id,
        )
        dash_response = self.client.get(reverse("dashboard"))
        self.assertRedirects(dash_response, reverse("employer_dashboard"))

    # --------------------------------------------------------------------------
    # Scenario 4: Seeker accessing superuser/admin view -> 403 Forbidden
    # --------------------------------------------------------------------------
    def test_04_seeker_accessing_superuser_admin_view_returns_403(self):
        self.client.force_login(self.seeker1_user)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 403)

    # --------------------------------------------------------------------------
    # Scenario 5: Employer accessing superuser/admin view -> 403 Forbidden
    # --------------------------------------------------------------------------
    def test_05_employer_accessing_superuser_admin_view_returns_403(self):
        self.client.force_login(self.employer1_user)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 403)

    # --------------------------------------------------------------------------
    # Scenario 6: Seeker editing another user's profile -> blocked
    # --------------------------------------------------------------------------
    def test_06_seeker_editing_another_user_profile_blocked(self):
        self.client.force_login(self.seeker1_user)
        original_beta_phone = self.seeker2_profile.phone

        # Seeker 1 submits an edit to profile endpoint
        response = self.client.post(
            reverse("edit_profile"),
            {
                "full_name": "Tampered Name",
                "phone": "+9999999999",
                "location": "Tampered City",
                "headline": "Hacker",
                "bio": "Unauthorized overwrite attempt",
                "education": "None",
            },
        )
        self.assertRedirects(response, reverse("seeker_dashboard"))

        # Verify Seeker 2's profile was NOT altered
        self.seeker2_profile.refresh_from_db()
        self.assertEqual(self.seeker2_profile.phone, original_beta_phone)
        self.assertEqual(self.seeker2_profile.full_name, "Beta Seeker")

        # Verify Seeker 1's profile WAS updated
        self.seeker1_profile.refresh_from_db()
        self.assertEqual(self.seeker1_profile.full_name, "Tampered Name")

    # --------------------------------------------------------------------------
    # Scenario 7: Employer editing another employer's job -> 403 Forbidden
    # --------------------------------------------------------------------------
    def test_07_employer_editing_another_employer_job_forbidden(self):
        # Employer 2 attempts to edit Job 1 (owned by Employer 1)
        self.client.force_login(self.employer2_user)
        response = self.client.get(reverse("edit_job", args=[self.job1.id]))
        self.assertEqual(response.status_code, 403)

        post_response = self.client.post(
            reverse("edit_job", args=[self.job1.id]),
            {
                "title": "Malicious Job Hijack",
                "description": "Tampered description",
                "location": "Nowhere",
                "job_type": "full_time",
            },
        )
        self.assertEqual(post_response.status_code, 403)
        self.job1.refresh_from_db()
        self.assertEqual(self.job1.title, "Senior Security Architect")

    # --------------------------------------------------------------------------
    # Scenario 8: Employer viewing another employer's applicants -> 403 Forbidden
    # --------------------------------------------------------------------------
    def test_08_employer_viewing_another_employer_applicants_forbidden(self):
        # Employer 2 attempts to view applicants of Employer 1's Job 1
        self.client.force_login(self.employer2_user)
        response = self.client.get(reverse("applicants", args=[self.job1.id]))
        self.assertEqual(response.status_code, 403)

    # --------------------------------------------------------------------------
    # Scenario 9: Unauthenticated user accessing protected page -> 302 to login
    # --------------------------------------------------------------------------
    def test_09_unauthenticated_user_accessing_protected_page_redirects(self):
        protected_urls = [
            reverse("seeker_dashboard"),
            reverse("employer_dashboard"),
            reverse("create_job"),
            reverse("admin_dashboard"),
            reverse("edit_profile"),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                302,
                f"URL {url} failed to redirect unauthenticated user.",
            )
            self.assertIn(reverse("login"), response.url)

    # --------------------------------------------------------------------------
    # Scenario 10: Repeated failed login attempts triggering lockout
    # --------------------------------------------------------------------------
    def test_10_repeated_failed_login_attempts_trigger_lockout(self):
        # Send 5 failed login attempts
        for i in range(5):
            res = self.client.post(
                reverse("login"),
                {
                    "username": "bruteforce_target",
                    "password": f"WrongPass{i}!",
                },
            )
            self.assertIn(res.status_code, [200, 429])

        # 6th attempt must be rejected by rate limiter with 429
        lockout_res = self.client.post(
            reverse("login"),
            {
                "username": "bruteforce_target",
                "password": "AnotherWrongPassword!",
            },
        )
        self.assertEqual(lockout_res.status_code, 429)
        self.assertContains(
            lockout_res,
            "Too many failed login attempts",
            status_code=429,
        )

    # --------------------------------------------------------------------------
    # Scenario 11: Unauthorized resume download -> 403 Forbidden
    # --------------------------------------------------------------------------
    def test_11_unauthorized_resume_download_forbidden(self):
        # An unrelated seeker (seeker_beta) attempts to download seeker_alpha's resume
        self.client.force_login(self.seeker2_user)
        response = self.client.get(
            reverse("download_application_resume", args=[self.application1.id])
        )
        self.assertEqual(response.status_code, 403)

        # An unrelated employer (employer_two) attempts to download it
        self.client.force_login(self.employer2_user)
        response = self.client.get(
            reverse("download_application_resume", args=[self.application1.id])
        )
        self.assertEqual(response.status_code, 403)

        # The legitimate employer (employer_one) CAN access it
        self.client.force_login(self.employer1_user)
        response = self.client.get(
            reverse("download_application_resume", args=[self.application1.id])
        )
        self.assertEqual(response.status_code, 200)

        # The applicant themselves (seeker_alpha) CAN access it
        self.client.force_login(self.seeker1_user)
        response = self.client.get(
            reverse("download_application_resume", args=[self.application1.id])
        )
        self.assertEqual(response.status_code, 200)

    # --------------------------------------------------------------------------
    # Scenario 12: Signup attempting privilege escalation -> neutralized
    # --------------------------------------------------------------------------
    def test_12_signup_privilege_escalation_attempt_neutralized(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "privilege_attacker",
                "email": "attacker@workwave.test",
                "role": "seeker",
                "password1": "SecureAttackerPass123!",
                "password2": "SecureAttackerPass123!",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        self.assertRedirects(response, reverse("dashboard"), target_status_code=302)

        created_user = self.User.objects.get(username="privilege_attacker")
        # Ensure staff and superuser flags are strictly False
        self.assertFalse(created_user.is_staff)
        self.assertFalse(created_user.is_superuser)
