from django.conf import settings
from django.db import models


class Project(models.Model):
    STATUS_CHOICES = [("open", "Open"), ("closed", "Closed")]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True, default="")
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default="open")
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="participated_projects",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
