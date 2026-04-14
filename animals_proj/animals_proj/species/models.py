from django.db import models
from django.urls import reverse


class Species(models.Model):
    scientific_name = models.CharField(max_length=255)
    common_name = models.CharField(max_length=255, blank=True)
    taxon_class = models.CharField(max_length=100, blank=True)
    conservation_status = models.CharField(max_length=100, blank=True)
    is_endemic = models.BooleanField(default=False)
    reference_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    reference_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    reference_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['common_name', 'scientific_name']

    def __str__(self):
        return self.common_name or self.scientific_name

    def get_absolute_url(self):
        return reverse('species:detail', kwargs={'pk': self.pk})

    @property
    def coordinate_string(self):
        if self.reference_latitude is None or self.reference_longitude is None:
            return ''
        return f'{self.reference_latitude}, {self.reference_longitude}'
