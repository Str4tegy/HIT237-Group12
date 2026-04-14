from django.db import models


class Species(models.Model):
    scientific_name = models.CharField(max_length=255)
    common_name = models.CharField(max_length=255, blank=True)
    taxon_class = models.CharField(max_length=100, blank=True)
    conservation_status = models.CharField(max_length=100, blank=True)
    is_endemic = models.BooleanField(default=False)
    reference_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['common_name', 'scientific_name']

    def __str__(self):
        return self.common_name or self.scientific_name
