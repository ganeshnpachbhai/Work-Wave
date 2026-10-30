from django.db import models
from django.db.models import Q
from seeker.models import SeekerProfile
from jobs.models import Job

# Create your models here.
class Application(models.Model):
    STATUS_CHOICE = [
        ("pending","Pending"),
        ("shortlisted","Shortlisted"),
        ("rejected","Rejected"),
        ("accepted","Accepted"),
    ]

    seeker = models.ForeignKey(
        SeekerProfile,
        on_delete=models.CASCADE,
        related_name="applications",

    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    resume = models.FileField(
        upload_to="application_resume/",
        blank=True,
        null=True
    )
    cover_letter = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        default="pending",
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["seeker","job"],
                name = "unique_seeker_job_application",
            ),
            models.CheckConstraint(
                condition=Q(status__in=[
                    "pending",
                    "shortlisted",
                    "rejected",
                    "accepted",
                ]),
                name = "valid_application_status",
            ),
        ]
    def __str__(self):
        return f"{self.seeker} - {self.job.title}"
