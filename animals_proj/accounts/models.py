from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    affiliation = models.CharField(max_length=255, blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile: {self.user.username}"
