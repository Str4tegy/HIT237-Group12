from django.db import models
from django.contrib.auth.models import User
from animals_proj.species.models import Species


class Submission(models.Model):
    STATUS_CHOICES = [
        ('public', 'Public'),
        ('flagged', 'Flagged'),
        ('under_review', 'Under review'),
        ('removed', 'Removed'),
    ]

    species = models.ForeignKey(Species, on_delete=models.SET_NULL, null=True, related_name='submissions')
    submitter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submissions')
    audio = models.FileField(upload_to='audio/')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    confidence = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Submission {self.pk} - {self.species}"
