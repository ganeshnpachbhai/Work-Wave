from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from applications.models import Application
from employer.models import EmployerProfile
from seeker.models import SeekerProfile
from .models import Job


class JobTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="employer",
            password="test-password",
        )
        UserProfile.objects.create(user=user, role="employer")
        self.employer = EmployerProfile.objects.create(
            user=user,
            company_name="WorkWave",
        )
        self.job = Job.objects.create(
            employer=self.employer,
            title="Python Developer",
            description="Build great web apps with Django.",
            location="Remote",
            job_type="full_time",
            salary_min=80000,
            salary_max=120000,
        )
        self.client.force_login(user)

    def test_home_page_renders_jobs(self):
        self.client.logout()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Developer")
        self.assertContains(response, "WorkWave")

    def test_job_list_filtering(self):
        self.client.logout()
        response = self.client.get(reverse("job_list"), {"q": "Python"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Developer")

        response_nomatch = self.client.get(reverse("job_list"), {"q": "Astronaut"})
        self.assertEqual(response_nomatch.status_code, 200)
        self.assertContains(response_nomatch, "No matching jobs found")

    def test_job_detail_renders_without_crashing(self):
        self.client.logout()
        response = self.client.get(reverse("job_detail", args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Developer")
        self.assertContains(response, "Login to Apply")

    def test_job_detail_as_seeker(self):
        seeker_user = get_user_model().objects.create_user(
            username="seeker_user", password="password123"
        )
        UserProfile.objects.create(user=seeker_user, role="seeker")
        SeekerProfile.objects.create(user=seeker_user)
        self.client.force_login(seeker_user)

        response = self.client.get(reverse("job_detail", args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apply Now")

    def test_create_job_page_renders_form_fields(self):
        response = self.client.get(reverse("create_job"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post a Job")
        self.assertContains(response, "Title")
        self.assertContains(response, "Description")
        self.assertContains(response, "Location")
        self.assertContains(response, "Job type")

    def test_close_job_deactivates_job_and_redirects(self):
        response = self.client.post(reverse("close_job", args=[self.job.pk]))
        self.assertRedirects(response, reverse("employer_dashboard"))
        self.job.refresh_from_db()
        self.assertFalse(self.job.is_active)

    def test_apply_job_get_and_post(self):
        seeker_user = get_user_model().objects.create_user(
            username="applicant", password="password123"
        )
        UserProfile.objects.create(user=seeker_user, role="seeker")
        SeekerProfile.objects.create(user=seeker_user)
        self.client.force_login(seeker_user)

        # GET request to apply_job must return 200, not None
        response = self.client.get(reverse("apply_job", args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apply for Python Developer")

        # POST request creates Application
        response = self.client.post(
            reverse("apply_job", args=[self.job.id]),
            {"cover_letter": "I would love to join."},
        )
        self.assertRedirects(response, reverse("job_detail", args=[self.job.id]))
        self.assertTrue(
            Application.objects.filter(job=self.job, seeker__user=seeker_user).exists()
        )

        # Re-applying should redirect with info message
        response_reapply = self.client.get(reverse("apply_job", args=[self.job.id]))
        self.assertRedirects(response_reapply, reverse("job_detail", args=[self.job.id]))
