from django.db import models
from employer.models import EmployerProfile

# Create your models here.


class Job(models.Model):
    JOB_TYPE = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("internship", "Internship"),
        ("remote", "Remote"),
        ("contract", "Contract",)
    ]

    employer = models.ForeignKey(
        EmployerProfile,
        on_delete=models.CASCADE,
        related_name="jobs",
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=150)
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE,
        default="full_time",
    )
    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(
        auto_now_add=True,
    )
    deadline = models.DateField(null=True,blank=True)

    class Meta:
        ordering = ["-posted_at"]
    def __str__(self):
        return self.title
