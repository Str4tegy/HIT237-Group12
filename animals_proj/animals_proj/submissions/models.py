from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse

from animals_proj.species.models import Species


class SubmissionQuerySet(models.QuerySet):
    def public(self):
        return self.exclude(status=Submission.Status.REMOVED)

    def visible_to(self, user):
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return self
        return self.public()

    def for_owner(self, user):
        return self.filter(submitter=user)

    def recent(self):
        return self.order_by('-created_at')

    def search(self, term):
        if not term:
            return self
        return self.filter(
            Q(species__common_name__icontains=term)
            | Q(species__scientific_name__icontains=term)
            | Q(submitter__username__icontains=term)
            | Q(notes__icontains=term)
        )


class Submission(models.Model):
    class Status(models.TextChoices):
        PUBLIC = 'public', 'Public'
        FLAGGED = 'flagged', 'Flagged'
        UNDER_REVIEW = 'under_review', 'Under review'
        REMOVED = 'removed', 'Removed'

    species = models.ForeignKey(Species, on_delete=models.SET_NULL, null=True, related_name='submissions')
    submitter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submissions')
    audio = models.FileField(upload_to='audio/')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    confidence = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Enter a confidence score from 0 to 100.',
    )
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLIC)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SubmissionQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Submission {self.pk} - {self.species}'

    def get_absolute_url(self):
        return reverse('submissions:detail', kwargs={'pk': self.pk})

    def can_edit(self, user):
        return bool(user.is_authenticated and (user.is_staff or user.is_superuser or self.submitter_id == user.id))

    @property
    def coordinate_string(self):
        if self.latitude is None or self.longitude is None:
            return ''
        return f'{self.latitude}, {self.longitude}'
