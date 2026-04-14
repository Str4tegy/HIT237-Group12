from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    class Role(models.TextChoices):
        CITIZEN_SCIENTIST = 'citizen_scientist', 'Citizen Scientist'
        RESEARCHER = 'researcher', 'Researcher'
        MODERATOR = 'moderator', 'Moderator'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    affiliation = models.CharField(max_length=255, blank=True)
    verified = models.BooleanField(default=False)
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.CITIZEN_SCIENTIST)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f"Profile: {self.user.username}"

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR
