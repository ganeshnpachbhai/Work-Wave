from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from applications.models import Application
from jobs.models import Job
from seeker.models import SeekerProfile
from .models import EmployerProfile


class EmployerDashboardTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="employer",
            password="test-password",
        )
        UserProfile.objects.create(user=user, role="employer")
        employer = EmployerProfile.objects.create(
            user=user,
            company_name="WorkWave",
        )
        job = Job.objects.create(
            employer=employer,
            title="Software Engineer",
            description="Build useful software.",
            location="Remote",
        )
        self.job_id = job.pk
        self.employer_user = user
        self.employer = employer
        self.client.force_login(user)

    def test_dashboard_renders_applicants_link(self):
        response = self.client.get(reverse("employer_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("applicants", args=[self.job_id]))

    def test_applicants_view_renders_correctly(self):
        seeker_user = get_user_model().objects.create_user(
            username="candidate1",
            password="test-password",
            email="candidate1@example.com",
        )
        UserProfile.objects.create(user=seeker_user, role="seeker")
        seeker_profile = SeekerProfile.objects.create(
            user=seeker_user,
            full_name="Jane Doe",
            education="B.S. CS",
        )
        job = Job.objects.get(pk=self.job_id)
        application = Application.objects.create(
            seeker=seeker_profile,
            job=job,
            status="pending",
        )

        response = self.client.get(reverse("applicants", args=[self.job_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "candidate1@example.com")
        self.assertContains(response, reverse("update_application_status", args=[application.id]))

    def test_update_application_status(self):
        seeker_user = get_user_model().objects.create_user(
            username="candidate2",
            password="test-password",
        )
        UserProfile.objects.create(user=seeker_user, role="seeker")
        seeker_profile = SeekerProfile.objects.create(user=seeker_user)
        job = Job.objects.get(pk=self.job_id)
        application = Application.objects.create(
            seeker=seeker_profile,
            job=job,
            status="pending",
        )

        response = self.client.post(
            reverse("update_application_status", args=[application.id]),
            {"status": "shortlisted"},
        )
        self.assertRedirects(response, reverse("applicants", args=[self.job_id]))
        application.refresh_from_db()
        self.assertEqual(application.status, "shortlisted")
