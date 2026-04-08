"""
accounts/models.py

Custom User model extending AbstractUser.

Pana's responsibility:
  - Role-based user model (Guest, Citizen Scientist, Researcher, Moderator, Admin)
  - Uses Django's built-in auth framework rather than duplicating it

Django philosophy demonstrated:
  - DRY: Reuses AbstractUser instead of reimplementing auth from scratch
  - Explicit is better than implicit: Role choices are defined as class-level
    constants with clear string labels, not magic integers
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extended user model with role-based access control.

    Roles determine what a user can do across the platform:
      GUEST           - unauthenticated; read-only via views (not stored)
      CITIZEN_SCIENTIST - can submit, edit/delete own entries, flag anomalies
      RESEARCHER      - same permissions as citizen scientist (distinguished
                        for display and future permission extensions)
      MODERATOR       - can review and action flagged entries
      ADMIN           - full CRUD over all content and user records

    The role field is checked explicitly in views and mixins (see views.py)
    rather than relying on Django's permission system implicitly — this
    satisfies the "Explicit is better than implicit" philosophy and makes
    the access model easy to audit.
    """

    # Role constants — reference these in views/mixins, never raw strings
    CITIZEN_SCIENTIST = "citizen_scientist"
    RESEARCHER = "researcher"
    MODERATOR = "moderator"
    ADMIN = "admin"

    ROLE_CHOICES = [
        (CITIZEN_SCIENTIST, "Citizen Scientist"),
        (RESEARCHER, "Researcher"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Admin"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=CITIZEN_SCIENTIST,
    )

    bio = models.TextField(
        blank=True,
        help_text="Short profile bio shown on the submitter profile page.",
    )

    organisation = models.CharField(
        max_length=200,
        blank=True,
        help_text="Research institution or community group (optional).",
    )

    # ------------------------------------------------------------------ #
    # Convenience properties — keeps role logic out of templates and views #
    # ------------------------------------------------------------------ #

    @property
    def is_moderator(self) -> bool:
        return self.role in (self.MODERATOR, self.ADMIN)

    @property
    def is_researcher_or_above(self) -> bool:
        return self.role in (
            self.RESEARCHER,
            self.CITIZEN_SCIENTIST,
            self.MODERATOR,
            self.ADMIN,
        )

    @property
    def is_admin(self) -> bool:
        return self.role == self.ADMIN

    def can_edit(self, submission) -> bool:
        """
        Returns True if this user may edit the given submission.

        Centralised here so the rule is never duplicated across views.
        Referenced in: submissions/views.py (SubmissionUpdateView.get_queryset)
        """
        return self.is_admin or submission.submitter == self

    def can_delete(self, submission) -> bool:
        """Same ownership rule as can_edit."""
        return self.can_edit(submission)

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["username"]
