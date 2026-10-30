from django.db import models
from django.conf import settings

# Create your models here.

# Skills
class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# Seeker Profile
class SeekerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seeker_profile')
    full_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=150, blank=True)
    headline = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profile', blank=True, null=True)
    resume = models.FileField(upload_to='resume/', blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True, related_name="profiles")
    education = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or self.user.username

    @property
    def pending_applications_count(self):
        return self.applications.filter(status="pending").count()

    @property
    def shortlisted_applications_count(self):
        return self.applications.filter(status="shortlisted").count()

    @property
    def accepted_applications_count(self):
        return self.applications.filter(status="accepted").count()

    @property
    def rejected_applications_count(self):
        return self.applications.filter(status="rejected").count()

    @property
    def profile_completion_percentage(self):
        score = 0
        if self.phone or self.location:
            score += 25
        if self.education:
            score += 25
        if self.skills.exists():
            score += 25
        if self.resume:
            score += 25
        return score

    @property
    def initials(self):
        if self.full_name:
            parts = self.full_name.strip().split()
            if len(parts) >= 2:
                return f"{parts[0][0]}{parts[1][0]}".upper()
            return parts[0][0].upper()
        return self.user.username[0].upper()
