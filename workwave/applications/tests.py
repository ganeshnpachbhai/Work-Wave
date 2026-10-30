from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from accounts.models import UserProfile
from applications.models import Application
from employer.models import EmployerProfile
from jobs.models import Job
from seeker.models import SeekerProfile


class ApplicationModelTests(TestCase):
    def setUp(self):
        emp_user = get_user_model().objects.create_user(username="emp", password="pw")
        UserProfile.objects.create(user=emp_user, role="employer")
        employer = EmployerProfile.objects.create(user=emp_user, company_name="Tech Co")
        self.job = Job.objects.create(
            employer=employer,
            title="Software Engineer",
            description="Build apps",
            location="Remote",
        )

        seeker_user = get_user_model().objects.create_user(username="seeker", password="pw")
        UserProfile.objects.create(user=seeker_user, role="seeker")
        self.seeker = SeekerProfile.objects.create(user=seeker_user, full_name="Jane Doe")

    def test_unique_application_constraint(self):
        Application.objects.create(seeker=self.seeker, job=self.job)
        with self.assertRaises(IntegrityError):
            Application.objects.create(seeker=self.seeker, job=self.job)

    def test_application_str(self):
        app = Application.objects.create(seeker=self.seeker, job=self.job)
        self.assertEqual(str(app), f"{self.seeker} - {self.job.title}")
