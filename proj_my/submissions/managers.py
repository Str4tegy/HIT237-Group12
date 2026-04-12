"""
submissions/managers.py

Custom QuerySet manager for AudioSubmission.
"""

from django.db import models
from django.db.models import Avg, Count, Q


class AudioSubmissionQuerySet(models.QuerySet):
    """
    Custom QuerySet for AudioSubmission.

    Methods are chainable — e.g.:
      AudioSubmission.objects.visible().by_species(species).recent()

    This chainability is the key advantage over plain manager methods.
    """

    def visible(self):
        """
        Returns only submissions that are publicly visible.
        Excludes entries hidden by moderators (is_visible=False).

        Used by: all public-facing views
        """
        return self.filter(is_visible=True)

    def flagged(self):
        """
        Returns submissions that have at least one open flag.

        Uses a subquery via filter on the reverse FK rather than
        a Python-level loop — single DB query.

        Used by: FlagQueueView context, moderator dashboard
        """
        from .models import SubmissionFlag
        return self.filter(
            flags__status=SubmissionFlag.OPEN
        ).distinct()

    def by_species(self, species):
        """
        Filters submissions to a single species.

        Used by: SpeciesDetailView, SubmissionListView ?species= filter
        """
        return self.filter(species=species)

    def by_submitter(self, user):
        """
        Filters submissions to a single user.

        Used by: submitter profile snippet in SubmissionDetailView
        """
        return self.filter(submitter=user)

    def recent(self, count=10):
        """
        Returns the most recently created submissions, capped at count.

        Used by: HomeView timeline feed, SpeciesDetailView recent panel
        """
        return self.order_by("-created_at")[:count]

    def high_confidence(self, threshold=80):
        """
        Returns submissions with a confidence score at or above threshold.

        Used by: potential future 'verified sightings' filter
        Default threshold of 80 matches the 'High' confidence_label
        defined on AudioSubmission.confidence_label property.
        """
        return self.filter(confidence_score__gte=threshold)

    def with_flag_counts(self):
        """
        Annotates each submission with the number of open flags it has.

        Returns: QuerySet with added field `open_flag_count` (int)

        Used by: FlagQueueView to show flag severity at a glance
        Demonstrates: annotation — a QuerySet API beyond basic filtering
        """
        from .models import SubmissionFlag
        return self.annotate(
            open_flag_count=Count(
                "flags",
                filter=Q(flags__status=SubmissionFlag.OPEN),
            )
        )

    def with_stats(self):
        """
        Annotates each submission with aggregate stats:
          - total_flags: total number of flags ever raised
          - avg_confidence: not per-submission but useful on species-level
            querysets (see SpeciesListView annotation)

        Used by: moderator review to assess submission quality
        Demonstrates: multi-field annotation with Count and Avg
        """
        return self.annotate(
            total_flags=Count("flags", distinct=True),
        )

    def for_public_display(self):
        """
        Convenience method combining the most common public view filters:
          visible + select_related for performance.

        Used by: HomeView, SubmissionListView
        Demonstrates: composed QuerySet methods — DRY
        """
        return (
            self.visible()
            .select_related("species", "submitter", "species__taxonomic_class")
            .order_by("-created_at")
        )


class AudioSubmissionManager(models.Manager):
    """
    Custom manager that returns AudioSubmissionQuerySet.

    Attaching this as AudioSubmission.objects means all the QuerySet
    methods above are available directly:
      AudioSubmission.objects.visible()
      AudioSubmission.objects.flagged()
      AudioSubmission.objects.for_public_display()
    """

    def get_queryset(self):
        return AudioSubmissionQuerySet(self.model, using=self._db)

    # ------------------------------------------------------------------ #
    # Convenience shortcuts on the manager itself                         #
    # (delegates to QuerySet methods)                                     #
    # ------------------------------------------------------------------ #

    def visible(self):
        return self.get_queryset().visible()

    def flagged(self):
        return self.get_queryset().flagged()

    def for_public_display(self):
        return self.get_queryset().for_public_display()

    def recent(self, count=10):
        return self.get_queryset().visible().recent(count)
