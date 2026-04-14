from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from animals_proj.submissions.models import Submission


class Flag(models.Model):
    class Decision(models.TextChoices):
        PENDING = 'pending', 'Pending'
        DISMISSED = 'dismissed', 'Dismissed'
        MARK_UNDER_REVIEW = 'mark_under_review', 'Marked under review'
        REMOVE_SUBMISSION = 'remove_submission', 'Submission removed'

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='flags')
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='flags')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    reviewer_notes = models.TextField(blank=True)
    decision = models.CharField(max_length=25, choices=Decision.choices, default=Decision.PENDING)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_flags',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Flag {self.pk} on Submission {self.submission_id}'

    def apply_decision(self, reviewer, notes, decision):
        self.reviewed = True
        self.reviewer_notes = notes
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.decision = decision

        if decision == self.Decision.DISMISSED:
            self.submission.status = Submission.Status.PUBLIC
        elif decision == self.Decision.MARK_UNDER_REVIEW:
            self.submission.status = Submission.Status.UNDER_REVIEW
        elif decision == self.Decision.REMOVE_SUBMISSION:
            self.submission.status = Submission.Status.REMOVED
        else:
            self.submission.status = Submission.Status.FLAGGED

        self.submission.save(update_fields=['status'])
        self.save()
