"""
submissions/migrations/0001_initial.py

Creates AudioSubmission and SubmissionFlag tables.
Depends on accounts and species migrations running first.
"""

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("species", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AudioSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("submitter", models.ForeignKey(
                    help_text="The verified user who submitted this entry.",
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="submissions",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("species", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="submissions",
                    to="species.species",
                )),
                ("audio_file", models.FileField(
                    help_text="Audio recording of the species call (MP3, WAV, OGG).",
                    upload_to="submissions/audio/%Y/%m/",
                )),
                ("captured_at", models.DateTimeField(
                    help_text="Date and time the recording was made (UTC).",
                )),
                ("latitude", models.DecimalField(
                    decimal_places=6,
                    help_text="Recording location latitude (decimal degrees, WGS84).",
                    max_digits=9,
                )),
                ("longitude", models.DecimalField(
                    decimal_places=6,
                    help_text="Recording location longitude (decimal degrees, WGS84).",
                    max_digits=9,
                )),
                ("location_notes", models.CharField(
                    blank=True,
                    help_text="Optional plain-text location description.",
                    max_length=300,
                )),
                ("confidence_score", models.PositiveSmallIntegerField(
                    help_text="How certain are you of the species ID? (1 = uncertain, 100 = certain)",
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(100),
                    ],
                )),
                ("notes", models.TextField(
                    blank=True,
                    help_text="Additional observations about the recording or conditions.",
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_visible", models.BooleanField(
                    default=True,
                    help_text="Hidden submissions are removed from public views but not deleted.",
                )),
            ],
            options={
                "verbose_name": "Audio Submission",
                "verbose_name_plural": "Audio Submissions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SubmissionFlag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("submission", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="flags",
                    to="submissions.audiosubmission",
                )),
                ("reporter", models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="reported_flags",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("reason", models.CharField(
                    choices=[
                        ("out_of_range", "Species recorded outside known habitat"),
                        ("wrong_species", "Incorrect species identification"),
                        ("audio_quality", "Audio too poor to verify"),
                        ("duplicate", "Possible duplicate entry"),
                        ("other", "Other (see notes)"),
                    ],
                    default="other",
                    max_length=20,
                )),
                ("notes", models.TextField(
                    blank=True,
                    help_text="Additional detail about why this entry was flagged.",
                )),
                ("status", models.CharField(
                    choices=[
                        ("open", "Open — awaiting moderator review"),
                        ("dismissed", "Dismissed — not an anomaly"),
                        ("actioned", "Actioned — submission updated or hidden"),
                    ],
                    default="open",
                    max_length=10,
                )),
                ("reviewed_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="reviewed_flags",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("moderator_notes", models.TextField(
                    blank=True,
                    help_text="Moderator's explanation of the action taken.",
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Submission Flag",
                "verbose_name_plural": "Submission Flags",
                "ordering": ["-created_at"],
            },
        ),
        # Indexes
        migrations.AddIndex(
            model_name="audiosubmission",
            index=models.Index(fields=["-created_at"], name="idx_submission_created"),
        ),
        migrations.AddIndex(
            model_name="audiosubmission",
            index=models.Index(fields=["species"], name="idx_submission_species"),
        ),
        migrations.AddIndex(
            model_name="audiosubmission",
            index=models.Index(fields=["submitter"], name="idx_submission_submitter"),
        ),
        migrations.AddIndex(
            model_name="audiosubmission",
            index=models.Index(fields=["captured_at"], name="idx_submission_captured"),
        ),
        migrations.AddIndex(
            model_name="audiosubmission",
            index=models.Index(
                fields=["species", "-captured_at"],
                name="idx_submission_species_captured",
            ),
        ),
        migrations.AddIndex(
            model_name="submissionflag",
            index=models.Index(fields=["status"], name="idx_flag_status"),
        ),
        migrations.AddIndex(
            model_name="submissionflag",
            index=models.Index(
                fields=["submission", "status"],
                name="idx_flag_submission_status",
            ),
        ),
        # Constraints
        migrations.AlterUniqueTogether(
            name="submissionflag",
            unique_together={("submission", "reporter")},
        ),
    ]
