from django.conf import settings
from django.db import models

# Create your models here.


class EmployerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employer_profile")
    company_name = models.CharField(max_length=150,)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.company_name

    @property
    def total_jobs_count(self):
        return self.jobs.count()

    @property
    def active_jobs_count(self):
        return self.jobs.filter(is_active=True).count()

    @property
    def closed_jobs_count(self):
        return self.jobs.filter(is_active=False).count()

    @property
    def total_applications_count(self):
        from applications.models import Application
        return Application.objects.filter(job__employer=self).count()

    @property
    def initials(self):
        if self.company_name:
            words = self.company_name.strip().split()
            if len(words) >= 2:
                return f"{words[0][0]}{words[1][0]}".upper()
            return words[0][:2].upper()
        return "CO"
