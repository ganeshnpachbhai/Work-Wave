from django.conf import settings
from django.db import models

# Create your models here.


class UserProfile(models.Model):
    ROLE_CHOICE = [
        ("seeker", "Job seeker"),
        ("employer", "Employer"),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile",)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICE,
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"

