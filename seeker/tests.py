from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from applications.models import Application
from employer.models import EmployerProfile
from jobs.models import Job
from seeker.models import SeekerProfile, Skill


class SeekerProfileTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="seeker_user",
            password="test-password",
        )
        UserProfile.objects.create(user=user, role="seeker")
        self.profile = SeekerProfile.objects.create(
            user=user,
            full_name="Alex Smith",
        )
        self.user = user
        self.client.force_login(user)

    def test_seeker_dashboard_renders(self):
        emp_user = get_user_model().objects.create_user(
            username="emp", password="password"
        )
        UserProfile.objects.create(user=emp_user, role="employer")
        employer = EmployerProfile.objects.create(
            user=emp_user, company_name="Tech Co"
        )
        job = Job.objects.create(
            employer=employer,
            title="Backend Dev",
            description="Django dev needed",
            location="Remote",
        )
        Application.objects.create(
            seeker=self.profile,
            job=job,
        )

        response = self.client.get(reverse("seeker_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, seeker_user!")
        self.assertContains(response, "Backend Dev")
        self.assertContains(response, "Tech Co")

    def test_edit_profile_get_and_post(self):
        # GET
        response = self.client.get(reverse("edit_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Profile")

        # POST with skills
        response = self.client.post(
            reverse("edit_profile"),
            {
                "full_name": "Alex J. Smith",
                "phone": "+1234567890",
                "location": "San Francisco, CA",
                "headline": "Lead Python Engineer",
                "bio": "Experienced backend architect.",
                "skills": "Python, Django, PostgreSQL, Docker",
                "education": "B.S. in Computer Science",
            },
        )
        self.assertRedirects(response, reverse("seeker_dashboard"))

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, "Alex J. Smith")
        self.assertEqual(self.profile.phone, "+1234567890")
        self.assertEqual(self.profile.location, "San Francisco, CA")
        self.assertEqual(self.profile.headline, "Lead Python Engineer")
        self.assertEqual(self.profile.bio, "Experienced backend architect.")
        self.assertEqual(self.profile.education, "B.S. in Computer Science")
        self.assertEqual(
            set(self.profile.skills.values_list("name", flat=True)),
            {"Python", "Django", "Postgresql", "Docker"},
        )
