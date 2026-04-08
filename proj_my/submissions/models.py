"""
submissions/models.py

Data models for user-submitted audio recording entries.

Pana's responsibility:
  - AudioSubmission: the core entry model
  - SubmissionFlag: the anomaly flagging model (through-style relationship)

Django philosophy demonstrated:
  - DRY: Validation logic (confidence score range, coordinate bounds)
    lives in model clean() methods — never duplicated in views or forms
  - Loose coupling: This app imports from species and accounts, but
    moderation imports from here — dependency direction is one-way
  - Explicit is better than implicit: FlagStatus choices are string
    constants defined on the model, making the state machine auditable
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from species.models import Species


class AudioSubmission(models.Model):
    """
    A single user-submitted audio recording of a species call.

    Relationships:
      - User (FK): many submissions → one submitter
      - Species (FK): many submissions → one species
      - SubmissionFlag (reverse FK): one submission ← many flags

    Key design decisions:
      - Audio stored as FileField (not URLField) so files are managed
        by Django's storage backend — swappable to S3 without model changes
      - Coordinates stored as DecimalField pairs (not PostGIS geometry)
        to avoid a PostGIS dependency; sufficient for this use case
      - confidence_score stored as integer 1–100 to avoid float precision
        issues when filtering/sorting
    """

    # ------------------------------------------------------------------ #
    # Core fields                                                         #
    # ------------------------------------------------------------------ #
    submitter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
        help_text="The verified user who submitted this entry.",
    )
    species = models.ForeignKey(
        Species,
        on_delete=models.PROTECT,   # Don't delete submissions if species is removed
        related_name="submissions",
    )

    # ------------------------------------------------------------------ #
    # Audio recording                                                     #
    # ------------------------------------------------------------------ #
    audio_file = models.FileField(
        upload_to="submissions/audio/%Y/%m/",
        help_text="Audio recording of the species call (MP3, WAV, OGG).",
    )

    # ------------------------------------------------------------------ #
    # Capture metadata                                                    #
    # ------------------------------------------------------------------ #
    captured_at = models.DateTimeField(
        help_text="Date and time the recording was made (UTC).",
    )

    # Coordinates — WGS84 decimal degrees
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Recording location latitude (decimal degrees, WGS84).",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Recording location longitude (decimal degrees, WGS84).",
    )
    location_notes = models.CharField(
        max_length=300,
        blank=True,
        help_text="Optional plain-text location description (e.g. 'Litchfield NP, near Florence Falls').",
    )

    # ------------------------------------------------------------------ #
    # Confidence score                                                    #
    # Submitter's certainty of the species identification, 1–100         #
    # ------------------------------------------------------------------ #
    confidence_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="How certain are you of the species ID? (1 = uncertain, 100 = certain)",
    )

    # ------------------------------------------------------------------ #
    # Entry content                                                       #
    # ------------------------------------------------------------------ #
    notes = models.TextField(
        blank=True,
        help_text="Additional observations about the recording or conditions.",
    )

    # ------------------------------------------------------------------ #
    # Timestamps                                                          #
    # ------------------------------------------------------------------ #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------ #
    # Soft visibility flag (set by moderators, not deleted outright)     #
    # ------------------------------------------------------------------ #
    is_visible = models.BooleanField(
        default=True,
        help_text="Hidden submissions are removed from public views but not deleted.",
    )

    # ------------------------------------------------------------------ #
    # Model methods                                                       #
    # ------------------------------------------------------------------ #

    def get_absolute_url(self) -> str:
        return reverse("submissions:detail", kwargs={"pk": self.pk})

    @property
    def coordinates_display(self) -> str:
        """Copyable coordinate string for the GPS copy button."""
        return f"{self.latitude}, {self.longitude}"

    @property
    def confidence_label(self) -> str:
        """
        Human-readable confidence tier.
        Centralised here so templates never contain branching logic.
        """
        if self.confidence_score >= 80:
            return "High"
        elif self.confidence_score >= 50:
            return "Medium"
        return "Low"

    @property
    def is_flagged(self) -> bool:
        """True if any open flag exists for this submission."""
        return self.flags.filter(status=SubmissionFlag.OPEN).exists()

    def clean(self):
        """
        Model-level validation — enforces NT coordinate bounds.

        NT bounding box (approximate):
          Latitude:  -26.0 to -10.9
          Longitude: 129.0 to 138.1

        This validation runs on form save and admin save.
        DRY: defined once here, not repeated in views or forms.
        """
        errors = {}

        if self.latitude is not None:
            if not (-26.0 <= float(self.latitude) <= -10.9):
                errors["latitude"] = (
                    "Latitude must be within the Northern Territory "
                    "(approx. -26.0 to -10.9)."
                )

        if self.longitude is not None:
            if not (129.0 <= float(self.longitude) <= 138.1):
                errors["longitude"] = (
                    "Longitude must be within the Northern Territory "
                    "(approx. 129.0 to 138.1)."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return (
            f"{self.species.common_name} — {self.submitter.username} "
            f"@ {self.captured_at:%Y-%m-%d %H:%M}"
        )

    class Meta:
        verbose_name = "Audio Submission"
        verbose_name_plural = "Audio Submissions"
        ordering = ["-created_at"]    # Most recent first for the home page feed
        indexes = [
            models.Index(fields=["-created_at"], name="idx_submission_created"),
            models.Index(fields=["species"], name="idx_submission_species"),
            models.Index(fields=["submitter"], name="idx_submission_submitter"),
            models.Index(fields=["captured_at"], name="idx_submission_captured"),
            # Composite index for the database page filter (species + time)
            models.Index(
                fields=["species", "-captured_at"],
                name="idx_submission_species_captured",
            ),
        ]


class SubmissionFlag(models.Model):
    """
    An anomaly flag raised against a single AudioSubmission.

    Represents the moderation workflow state machine:
      OPEN → REVIEWED (moderator takes action, either DISMISSED or ACTIONED)

    Relationships:
      - AudioSubmission (FK): many flags → one submission
      - reporter (FK → User): many flags → one reporter
      - reviewed_by (FK → User, nullable): assigned when status changes

    Design note: kept as a standalone model rather than a boolean on
    AudioSubmission so that multiple flags from different users are
    preserved and the moderation history is auditable.
    """

    # ------------------------------------------------------------------ #
    # Flag status — the state machine                                     #
    # ------------------------------------------------------------------ #
    OPEN = "open"
    DISMISSED = "dismissed"
    ACTIONED = "actioned"

    STATUS_CHOICES = [
        (OPEN, "Open — awaiting moderator review"),
        (DISMISSED, "Dismissed — not an anomaly"),
        (ACTIONED, "Actioned — submission updated or hidden"),
    ]

    # ------------------------------------------------------------------ #
    # Reason categories (optional, helps moderators triage)              #
    # ------------------------------------------------------------------ #
    OUT_OF_RANGE = "out_of_range"
    WRONG_SPECIES = "wrong_species"
    AUDIO_QUALITY = "audio_quality"
    DUPLICATE = "duplicate"
    OTHER = "other"

    REASON_CHOICES = [
        (OUT_OF_RANGE, "Species recorded outside known habitat"),
        (WRONG_SPECIES, "Incorrect species identification"),
        (AUDIO_QUALITY, "Audio too poor to verify"),
        (DUPLICATE, "Possible duplicate entry"),
        (OTHER, "Other (see notes)"),
    ]

    # ------------------------------------------------------------------ #
    # Fields                                                              #
    # ------------------------------------------------------------------ #
    submission = models.ForeignKey(
        AudioSubmission,
        on_delete=models.CASCADE,
        related_name="flags",
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reported_flags",
    )
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        default=OTHER,
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional detail about why this entry was flagged.",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=OPEN,
    )

    # Populated when a moderator reviews the flag
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_flags",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    moderator_notes = models.TextField(
        blank=True,
        help_text="Moderator's explanation of the action taken.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------ #
    # Model methods                                                       #
    # ------------------------------------------------------------------ #

    def clean(self):
        """
        A user cannot flag their own submission.
        Centralised here (DRY) — not repeated in the flag form view.
        """
        if self.reporter and self.submission.submitter == self.reporter:
            raise ValidationError(
                "You cannot flag your own submission."
            )

    def __str__(self) -> str:
        return (
            f"Flag on '{self.submission}' by {self.reporter} "
            f"[{self.get_status_display()}]"
        )

    class Meta:
        verbose_name = "Submission Flag"
        verbose_name_plural = "Submission Flags"
        ordering = ["-created_at"]
        # Prevent the same user flagging the same submission twice
        unique_together = [["submission", "reporter"]]
        indexes = [
            models.Index(fields=["status"], name="idx_flag_status"),
            models.Index(fields=["submission", "status"], name="idx_flag_submission_status"),
        ]
