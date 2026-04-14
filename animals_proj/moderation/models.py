from django.db import models
from django.contrib.auth.models import User
from animals_proj.submissions.models import Submission


class Flag(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='flags')
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='flags')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    reviewer_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Flag {self.pk} on Submission {self.submission_id}"
